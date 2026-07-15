from fastapi import APIRouter

from app.agents.registry import tool_registry
from app.models.schemas import ToolInfo

router = APIRouter(tags=["tools"])


@router.get("/tools", response_model=list[ToolInfo])
async def list_tools():
    return [ToolInfo(**t) for t in tool_registry.list_tools()]
