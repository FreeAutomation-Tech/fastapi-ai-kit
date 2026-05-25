from abc import ABC, abstractmethod
from typing import AsyncGenerator

from app.models.schemas import Message


class AIProvider(ABC):

    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> dict:
        ...

    @abstractmethod
    async def stream_chat(
        self,
        model: str,
        messages: list[Message],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> AsyncGenerator[str, None]:
        ...

    @abstractmethod
    async def embed(self, model: str, input: str | list[str]) -> dict:
        ...


def get_ai_service(provider: str) -> AIProvider:
    if provider == "openai":
        from app.services.openai_service import OpenAIProvider
        return OpenAIProvider()
    elif provider == "anthropic":
        from app.services.anthropic_service import AnthropicProvider
        return AnthropicProvider()
    elif provider == "ollama":
        from app.services.openai_service import OpenAIProvider
        return OpenAIProvider(base_url="http://localhost:11434/v1")
    else:
        raise ValueError(f"Unsupported provider: {provider}")
