import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import chat, embeddings, health, agents, sessions, tools, mcp
from app.core.rate_limiter import RateLimitMiddleware

logger = logging.getLogger("fastapi-ai-kit")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI AI Kit (Agent Backend)...")
    yield
    logger.info("Shutting down FastAPI AI Kit...")


app = FastAPI(
    title="FastAPI AI Kit",
    description="Production-ready FastAPI Agent Backend with multi-provider AI, MCP SSE, agent execution, session memory, and tool registry",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(",") if settings.allowed_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.rate_limit_enabled:
    app.add_middleware(RateLimitMiddleware)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(
        "%s %s -> %d (%.3fs)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(embeddings.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(tools.router, prefix="/api/v1")
app.include_router(mcp.router, prefix="/api/v1")
