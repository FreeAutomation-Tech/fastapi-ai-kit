import json
import uuid
import urllib.parse
import urllib.request
from typing import AsyncGenerator

from app.config import settings
from app.models.schemas import Message
from app.services.ai_service import AIProvider


class OpenAIProvider(AIProvider):

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or "https://api.openai.com").rstrip("/")
        self.api_key = settings.openai_api_key

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    async def chat(
        self,
        model: str,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> dict:
        body = json.dumps({
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }).encode()

        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=body,
            headers=self._headers(),
            method="POST",
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())

        return {
            "id": data.get("id", f"chat-cmpl-{uuid.uuid4().hex[:12]}"),
            "model": data.get("model", model),
            "choices": [
                {
                    "index": c["index"],
                    "message": {
                        "role": c["message"]["role"],
                        "content": c["message"]["content"],
                    },
                    "finish_reason": c.get("finish_reason", "stop"),
                }
                for c in data.get("choices", [])
            ],
            "usage": data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}),
        }

    async def stream_chat(
        self,
        model: str,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> AsyncGenerator[str, None]:
        import http.client

        body = json.dumps({
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        })

        parsed = urllib.parse.urlparse(self.base_url)
        conn_class = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
        conn = conn_class(parsed.netloc)

        try:
            path = (parsed.path.rstrip("/") + "/v1/chat/completions") if parsed.path else "/v1/chat/completions"
            conn.request(
                "POST",
                path,
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
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
        finally:
            conn.close()

    async def embed(self, model: str, input: Union[str, List[str]]) -> dict:
        body = json.dumps({
            "model": model,
            "input": input,
        }).encode()

        req = urllib.request.Request(
            f"{self.base_url}/v1/embeddings",
            data=body,
            headers=self._headers(),
            method="POST",
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())

        return {
            "model": data.get("model", model),
            "embeddings": [d["embedding"] for d in data.get("data", [])],
            "usage": data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}),
        }
