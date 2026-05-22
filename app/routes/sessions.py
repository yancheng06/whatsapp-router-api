from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models import Message, Session
from app.schemas import MessageOut, SessionOut

router = APIRouter()


@router.get(
    "/sessions",
    response_model=List[SessionOut],
    summary="List all sessions",
)
def list_sessions(db: DBSession = Depends(get_db)):
    return db.query(Session).order_by(Session.last_active.desc()).all()


@router.get(
    "/sessions/{session_id}/messages",
    response_model=List[MessageOut],
    summary="List all messages in a session",
)
def list_messages(session_id: int, db: DBSession = Depends(get_db)):
    session = db.get(Session, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found.",
        )
    return (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )
