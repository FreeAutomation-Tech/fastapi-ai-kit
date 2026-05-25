import json
import uuid
from typing import AsyncGenerator

from app.config import settings
from app.models.schemas import Message
from app.services.ai_service import AIProvider


class AnthropicProvider(AIProvider):

    def __init__(self):
        self.base_url = "https://api.anthropic.com"
        self.api_key = settings.anthropic_api_key

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

    async def chat(
        self,
        model: str,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> dict:
        import urllib.request

        system_msg = None
        chat_messages = []
        for m in messages:
            if m.role == "system" and system_msg is None:
                system_msg = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        body_dict = {
            "model": model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_msg:
            body_dict["system"] = system_msg

        body = json.dumps(body_dict).encode()

        req = urllib.request.Request(
            f"{self.base_url}/v1/messages",
            data=body,
            headers=self._headers(),
            method="POST",
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())

        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

        usage = data.get("usage", {})
        return {
            "id": data.get("id", f"msg-{uuid.uuid4().hex[:12]}"),
            "model": data.get("model", model),
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": data.get("stop_reason", "end_turn"),
                }
            ],
            "usage": {
                "prompt_tokens": usage.get("input_tokens", 0),
                "completion_tokens": usage.get("output_tokens", 0),
                "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            },
        }

    async def stream_chat(
        self,
        model: str,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> AsyncGenerator[str, None]:
        import http.client

        system_msg = None
        chat_messages = []
        for m in messages:
            if m.role == "system" and system_msg is None:
                system_msg = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})

        body_dict = {
            "model": model,
            "messages": chat_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        if system_msg:
            body_dict["system"] = system_msg

        body = json.dumps(body_dict)

        conn = http.client.HTTPSConnection("api.anthropic.com")
        try:
            conn.request(
                "POST",
                "/v1/messages",
                body=body,
                headers=self._headers(),
            )
            resp = conn.getresponse()

            while chunk := resp.readline():
                line = chunk.decode("utf-8").strip()
                if not line or line.startswith(":"):
                    continue
                if line.startswith("data: "):
                    data_str = line[6:]
                    try:
                        data = json.loads(data_str)
                        if data.get("type") == "content_block_delta":
                            delta = data.get("delta", {})
                            if delta.get("type") == "text_delta":
                                text = delta.get("text", "")
                                if text:
                                    yield text
                    except json.JSONDecodeError:
                        continue
        finally:
            conn.close()

    async def embed(self, model: str, input: str | list[str]) -> dict:
        raise NotImplementedError("Anthropic does not support embeddings")
