import asyncio
import json
import uuid

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.agents.registry import tool_registry

router = APIRouter(tags=["mcp"])

_sse_clients: dict[str, asyncio.Queue] = {}


@router.get("/mcp/sse")
async def mcp_sse(request: Request):
    client_id = uuid.uuid4().hex[:8]
    queue: asyncio.Queue = asyncio.Queue()
    _sse_clients[client_id] = queue

    async def event_generator():
        try:
            await queue.put(f"event: endpoint\ndata: /api/v1/mcp/message?client_id={client_id}\n\n")
            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield msg
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            _sse_clients.pop(client_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/mcp/message")
async def mcp_message(request: Request, client_id: str = ""):
    if client_id not in _sse_clients:
        raise HTTPException(status_code=404, detail="SSE connection not found")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    method = body.get("method", "")
    msg_id = body.get("id", str(uuid.uuid4().hex[:8]))

    if method == "tools/list":
        tools = tool_registry.list_tools()
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"tools": tools},
        }
    elif method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        tool = tool_registry.get(tool_name)
        if not tool:
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32602, "message": f"Unknown tool: {tool_name}"},
            }
        else:
            try:
                result = await tool.run(**arguments)
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": result}]},
                }
            except Exception as e:
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32603, "message": str(e)},
                }
    elif method == "resources/list":
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"resources": []},
        }
    else:
        response = {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    await _sse_clients[client_id].put(f"data: {json.dumps(response)}\n\n")
    return {"status": "sent"}
