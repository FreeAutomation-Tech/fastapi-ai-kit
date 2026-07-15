from fastapi import APIRouter, HTTPException

from app.agents.executor import execute_agent, stream_agent
from app.models.schemas import AgentExecuteRequest, AgentExecuteResponse

router = APIRouter(tags=["agents"])


@router.post("/agents/execute", response_model=AgentExecuteResponse)
async def agent_execute(request: AgentExecuteRequest):
    try:
        result = await execute_agent(
            session_id=request.session_id,
            message=request.message,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return AgentExecuteResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Agent execution error: {str(e)}")


@router.post("/agents/stream")
async def agent_stream(request: AgentExecuteRequest):
    from fastapi.responses import StreamingResponse

    try:
        return StreamingResponse(
            stream_agent(
                session_id=request.session_id,
                message=request.message,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Agent stream error: {str(e)}")
