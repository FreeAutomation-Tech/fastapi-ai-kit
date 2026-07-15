import json
import time
import uuid
from typing import AsyncGenerator, Optional

from app.agents.registry import tool_registry
from app.config import settings
from app.memory.store import session_store
from app.models.schemas import Message
from app.services.ai_service import get_ai_service

_AGENT_SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.
You can use tools to help answer questions. Available tools:

{tools_description}

To use a tool, respond with a JSON block like this:
```tool
{{"name": "tool_name", "arguments": {{"arg1": "value1"}}}}
```

After receiving the tool result, continue the conversation naturally."""


def _resolve_provider(model: str) -> str:
    if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        return "openai"
    elif model.startswith("claude"):
        return "anthropic"
    elif model.startswith("llama") or model.startswith("mistral") or model.startswith("gemma"):
        return "ollama"
    return settings.default_provider


async def execute_agent(
    session_id: str,
    message: str,
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> dict:
    session = session_store.get_session(session_id)
    if not session:
        return {"error": "Session not found", "status": "error"}

    session_store.add_message(session_id, "user", message)
    history = session_store.get_messages(session_id)
    tools_desc = "\n".join(
        f"- {t['name']}: {t['description']}" for t in tool_registry.list_tools()
    )
    system_prompt = _AGENT_SYSTEM_PROMPT.format(tools_description=tools_desc)

    provider = _resolve_provider(model)
    service = get_ai_service(provider)

    messages_for_llm = [Message(role="system", content=system_prompt)] + history

    max_iterations = getattr(settings, "agent_max_iterations", 5)
    tool_results = []

    for iteration in range(max_iterations):
        result = await service.chat(
            model=model,
            messages=messages_for_llm,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = result["choices"][0]["message"]["content"]

        tool_call = _parse_tool_call(content)
        if not tool_call:
            clean_content = _strip_tool_blocks(content)
            session_store.add_message(session_id, "assistant", clean_content)
            return {
                "session_id": session_id,
                "response": clean_content,
                "tool_calls": tool_results,
                "iterations": iteration + 1,
                "status": "success",
            }

        tool_name = tool_call["name"]
        tool_args = tool_call.get("arguments", {})
        tool = tool_registry.get(tool_name)
        if not tool:
            tool_result = f"Error: Unknown tool '{tool_name}'"
        else:
            try:
                tool_result = await tool.run(**tool_args)
            except Exception as e:
                tool_result = f"Error executing {tool_name}: {e}"

        tool_results.append({"tool": tool_name, "arguments": tool_args, "result": tool_result})

        messages_for_llm.append(Message(role="assistant", content=content))
        messages_for_llm.append(Message(role="tool", content=tool_result))

    return {
        "session_id": session_id,
        "response": "Max iterations reached without final answer.",
        "tool_calls": tool_results,
        "iterations": max_iterations,
        "status": "max_iterations",
    }


async def stream_agent(
    session_id: str,
    message: str,
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int = 2000,
) -> AsyncGenerator[str, None]:
    session = session_store.get_session(session_id)
    if not session:
        yield json.dumps({"type": "error", "content": "Session not found"})
        return

    session_store.add_message(session_id, "user", message)
    history = session_store.get_messages(session_id)
    tools_desc = "\n".join(
        f"- {t['name']}: {t['description']}" for t in tool_registry.list_tools()
    )
    system_prompt = _AGENT_SYSTEM_PROMPT.format(tools_description=tools_desc)

    provider = _resolve_provider(model)
    service = get_ai_service(provider)

    messages_for_llm = [Message(role="system", content=system_prompt)] + history

    full_response = ""
    async for chunk in service.stream_chat(
        model=model,
        messages=messages_for_llm,
        temperature=temperature,
        max_tokens=max_tokens,
    ):
        full_response += chunk
        yield json.dumps({"type": "chunk", "content": chunk})

    session_store.add_message(session_id, "assistant", full_response)
    yield json.dumps({"type": "done", "content": full_response})


def _parse_tool_call(content: str) -> Optional[dict]:
    import re
    match = re.search(r'```tool\s*\n?(.*?)\n?```', content, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(1).strip())
    except json.JSONDecodeError:
        return None


def _strip_tool_blocks(content: str) -> str:
    import re
    return re.sub(r'```tool\s*\n?.*?\n?```\s*', '', content, flags=re.DOTALL).strip()
