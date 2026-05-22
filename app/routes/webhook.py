from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession

from app.auth import verify_token
from app.database import get_db
from app.models import Message, Session
from app.schemas import IncomingMessage, WebhookResponse
from app.agent_router import classify_agent
from app.reply_generator import generate_reply

router = APIRouter()


@router.post(
    "/whatsapp",
    response_model=WebhookResponse,
    summary="Receive an incoming WhatsApp-style message",
)
async def receive_message(
    payload: IncomingMessage,
    _: None = Depends(verify_token),
    db: DBSession = Depends(get_db),
):
    """
    1. Classify the message → agent type
    2. Get or create a session for the user
    3. Save the user message (reject duplicates via event_id)
    4. Generate a reply
    5. Save the assistant reply
    6. Return the full result
    """

    # ── 1. Classify ──────────────────────────────────────────────────────────
    agent = classify_agent(payload.message)

    # ── 2. Session: reuse latest open session for this user + agent ──────────
    session = (
        db.query(Session)
        .filter(Session.user_id == payload.user_id, Session.agent == agent)
        .order_by(Session.last_active.desc())
        .first()
    )
    if not session:
        session = Session(user_id=payload.user_id, agent=agent)
        db.add(session)
        db.flush()  # get session.id before committing

    session.last_active = datetime.utcnow()

    # ── 3. Save user message (unique constraint guards against duplicate event_ids) ──
    user_msg = Message(
        session_id=session.id,
        role="user",
        content=payload.message,
        event_id=payload.event_id,
    )
    db.add(user_msg)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Event '{payload.event_id}' has already been processed.",
        )

    # ── 4. Generate reply ────────────────────────────────────────────────────
    reply_text = await generate_reply(agent, payload.message)

    # ── 5. Save assistant reply ──────────────────────────────────────────────
    assistant_msg = Message(
        session_id=session.id,
        role="assistant",
        content=reply_text,
        event_id=None,  # replies don't carry an event_id
    )
    db.add(assistant_msg)
    db.commit()

    return WebhookResponse(
        session_id=session.id,
        agent=agent,
        user_message=payload.message,
        reply=reply_text,
    )
