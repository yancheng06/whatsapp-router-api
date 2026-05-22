from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# ── Incoming webhook payload ──────────────────────────────────────────────────

class IncomingMessage(BaseModel):
    event_id: str
    user_id: str
    message: str


# ── API responses ─────────────────────────────────────────────────────────────

class MessageOut(BaseModel):
    id: int
    session_id: int
    role: str
    content: str
    event_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: int
    user_id: str
    agent: str
    last_active: datetime

    class Config:
        from_attributes = True


class WebhookResponse(BaseModel):
    session_id: int
    agent: str
    user_message: str
    reply: str


class SimulateRequest(BaseModel):
    user_id: str = "demo_user"
    message: str = "I want to know the price"
