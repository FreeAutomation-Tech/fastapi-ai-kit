from fastapi import APIRouter, HTTPException

from app.memory.store import session_store
from app.models.schemas import SessionCreateResponse, SessionDetail, Message

router = APIRouter(tags=["sessions"])


@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session():
    session = session_store.create_session()
    return SessionCreateResponse(
        session_id=session["id"],
        created_at=session["created_at"],
    )


@router.get("/sessions", response_model=list[SessionDetail])
async def list_sessions():
    return [SessionDetail(**s) for s in session_store.list_sessions()]


@router.get("/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str):
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionDetail(**session)


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if not session_store.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted", "session_id": session_id}


@router.get("/sessions/{session_id}/messages", response_model=list[Message])
async def get_session_messages(session_id: str):
    messages = session_store.get_messages(session_id)
    if not session_store.get_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return messages
