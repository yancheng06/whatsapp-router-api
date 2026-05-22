"""
Agent routing: classifies an incoming message as one of:
  - sales    → buying / pricing / product interest
  - support  → problems / issues / complaints
  - general  → anything else
"""

SALES_KEYWORDS = [
    "buy", "price", "pricing", "cost", "cost?", "how much", "purchase",
    "order", "product", "plan", "plans", "quote", "discount", "offer",
    "interested", "package", "packages", "subscription",
]

SUPPORT_KEYWORDS = [
    "problem", "issue", "bug", "error", "broken", "not working",
    "doesn't work", "complaint", "help", "support", "fix", "failed",
    "trouble", "wrong", "crash", "stuck", "cannot", "can't", "unable",
]


def classify_agent(message: str) -> str:
    """Return 'sales', 'support', or 'general' based on message content."""
    lower = message.lower()

    if any(kw in lower for kw in SUPPORT_KEYWORDS):
        return "support"

    if any(kw in lower for kw in SALES_KEYWORDS):
        return "sales"

    return "general"
