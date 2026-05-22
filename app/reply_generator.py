import os
import logging
import httpx

logger = logging.getLogger(__name__)

FALLBACK_REPLIES = {
    "sales": "Thanks for your interest! Could you share a bit more about what you're looking for?",
    "support": "Sorry to hear you're facing this issue. Could you describe it in a bit more detail so we can help?",
    "general": "Happy to help! What would you like to know?",
}

SYSTEM_PROMPTS = {
    "sales": (
        "You are a friendly sales assistant. "
        "Your goal is to understand the customer's needs and guide them toward the right product or plan. "
        "Keep replies short (2-3 sentences), warm, and helpful."
    ),
    "support": (
        "You are a patient support agent. "
        "Your goal is to understand the customer's problem and reassure them that you will help. "
        "Keep replies short (2-3 sentences) and empathetic."
    ),
    "general": (
        "You are a helpful assistant. "
        "Answer the customer's question concisely and politely. "
        "Keep replies short (2-3 sentences)."
    ),
}


async def generate_reply(agent: str, user_message: str) -> str:
    """
    Attempt to generate a reply via the Anthropic API.
    Returns a fallback string on any failure.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not api_key:
        logger.info("ANTHROPIC_API_KEY not set — using mock reply.")
        return FALLBACK_REPLIES[agent]

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 256,
                    "system": SYSTEM_PROMPTS[agent],
                    "messages": [{"role": "user", "content": user_message}],
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"].strip()

    except Exception as exc:
        logger.warning("Anthropic API call failed (%s) — using mock reply.", exc)
        return FALLBACK_REPLIES[agent]
