import math

from fastapi import APIRouter, HTTPException

from app.models.schemas import EmbeddingRequest, EmbeddingResponse, SimilarityRequest, SimilarityResponse
from app.services.ai_service import get_ai_service

router = APIRouter(tags=["embeddings"])


@router.post("/embeddings", response_model=EmbeddingResponse)
async def embeddings_endpoint(request: EmbeddingRequest):
    try:
        provider = _resolve_provider(request.model)
        service = get_ai_service(provider)
        result = await service.embed(model=request.model, input=request.input)
        return EmbeddingResponse(**result)
    except NotImplementedError:
        raise HTTPException(status_code=400, detail="Embeddings not supported by this provider")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Embedding service error: {str(e)}")


@router.post("/embeddings/similarity", response_model=SimilarityResponse)
async def similarity_endpoint(request: SimilarityRequest):
    try:
        provider = _resolve_provider(request.model)
        service = get_ai_service(provider)
        result = await service.embed(model=request.model, input=request.input)
        embeddings = result["embeddings"]

        similarity = cosine_similarity(embeddings[0], embeddings[1])

        return SimilarityResponse(
            similarity=similarity,
            embeddings=embeddings,
        )
    except NotImplementedError:
        raise HTTPException(status_code=400, detail="Embeddings not supported by this provider")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Similarity computation error: {str(e)}")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _resolve_provider(model: str) -> str:
    if model.startswith("text-embedding") or model.startswith("gpt"):
        return "openai"
    elif model.startswith("claude"):
        return "anthropic"
    else:
        return "openai"
