from __future__ import annotations
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.ai_service import get_ai_service
from app.core.cache import cache_result

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
@cache_result(ttl=300)
async def chat_endpoint(request: ChatRequest):
    try:
        provider = _resolve_provider(request.model)
        service = get_ai_service(provider)
        result = await service.chat(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return ChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


@router.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    try:
        provider = _resolve_provider(request.model)
        service = get_ai_service(provider)

        async def event_generator():
            async for chunk in service.stream_chat(
                model=request.model,
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


def _resolve_provider(model: str) -> str:
    if model.startswith("gpt") or model.startswith("text-embedding") or model.startswith("o1") or model.startswith("o3"):
        return "openai"
    elif model.startswith("claude"):
        return "anthropic"
    elif model.startswith("llama") or model.startswith("mistral") or model.startswith("gemma"):
        return "ollama"
    else:
        return "openai"
