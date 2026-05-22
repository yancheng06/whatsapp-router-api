import os
import uuid

import httpx
from fastapi import APIRouter, Request
from app.schemas import SimulateRequest, WebhookResponse

router = APIRouter()


@router.post(
    "/simulate",
    response_model=WebhookResponse,
    summary="Simulate an incoming message (demo helper — no auth needed)",
)
async def simulate(payload: SimulateRequest, request: Request):
    """
    Sends a test message into the /webhook/whatsapp endpoint on your behalf.
    Generates a unique event_id automatically so you can call it repeatedly.
    """
    token = os.getenv("WEBHOOK_SECRET_TOKEN", "")
    base_url = str(request.base_url).rstrip("/")

    auto_event_id = f"sim_{uuid.uuid4().hex[:8]}"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/webhook/whatsapp",
            json={
                "event_id": auto_event_id,
                "user_id": payload.user_id,
                "message": payload.message,
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )

    return response.json()
