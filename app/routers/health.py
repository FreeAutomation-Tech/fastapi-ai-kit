import time

from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])

_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    uptime = time.time() - _start_time
    return HealthResponse(
        status="ok",
        version="0.2.0",
        uptime=round(uptime, 2),
    )
