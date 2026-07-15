import time
import uuid
from typing import Optional

from app.models.schemas import Message


class SessionStore:
    def __init__(self, ttl: int = 3600):
        self._sessions: dict[str, dict] = {}
        self._messages: dict[str, list[Message]] = {}
        self._ttl = ttl

    def create_session(self, meta: Optional[dict] = None) -> dict:
        session_id = uuid.uuid4().hex[:16]
        now = time.time()
        session = {
            "id": session_id,
            "created_at": now,
            "updated_at": now,
            "message_count": 0,
            "meta": meta or {},
        }
        self._sessions[session_id] = session
        self._messages[session_id] = []
        return session

    def get_session(self, session_id: str) -> Optional[dict]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        if time.time() - session["updated_at"] > self._ttl:
            self.delete_session(session_id)
            return None
        return session

    def list_sessions(self) -> list[dict]:
        now = time.time()
        active = []
        for sid, session in list(self._sessions.items()):
            if now - session["updated_at"] > self._ttl:
                self.delete_session(sid)
            else:
                active.append(session)
        return sorted(active, key=lambda s: s["updated_at"], reverse=True)

    def delete_session(self, session_id: str) -> bool:
        self._messages.pop(session_id, None)
        return self._sessions.pop(session_id, None) is not None

    def add_message(self, session_id: str, role: str, content: str) -> Optional[Message]:
        session = self.get_session(session_id)
        if not session:
            return None
        msg = Message(role=role, content=content)
        self._messages[session_id].append(msg)
        session["message_count"] = len(self._messages[session_id])
        session["updated_at"] = time.time()
        return msg

    def get_messages(self, session_id: str) -> list[Message]:
        session = self.get_session(session_id)
        if not session:
            return []
        return self._messages.get(session_id, [])

    def clear_expired(self):
        now = time.time()
        for sid, session in list(self._sessions.items()):
            if now - session["updated_at"] > self._ttl:
                self.delete_session(sid)


session_store = SessionStore()
