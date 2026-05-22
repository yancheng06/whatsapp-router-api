# WhatsApp Agent API

A Python/FastAPI backend that:
- Receives incoming chat messages
- Routes them to the right agent (sales, support, or general)
- Generates a reply via Claude (or a built-in mock fallback)
- Saves every conversation to SQLite
- Exposes read endpoints to browse saved sessions and messages

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```
WEBHOOK_SECRET_TOKEN=supersecret123
```

Optionally add your Anthropic API key for real AI replies:

```
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Start the server

```bash
python run.py
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `WEBHOOK_SECRET_TOKEN` | **Yes** | Bearer token that protects `POST /webhook/whatsapp` |
| `ANTHROPIC_API_KEY` | No | If set, Claude generates replies; otherwise a mock reply is used |
| `DATABASE_URL` | No | Defaults to `sqlite:///./conversations.db`; supports PostgreSQL DSNs |

---

## Endpoints

### `POST /webhook/whatsapp` — receive a message
Protected by `Authorization: Bearer <WEBHOOK_SECRET_TOKEN>`.

**Request body:**
```json
{
  "event_id": "evt_001",
  "user_id": "user_123",
  "message": "I want to know the price"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Authorization: Bearer supersecret123" \
  -H "Content-Type: application/json" \
  -d '{"event_id":"evt_001","user_id":"user_123","message":"I want to know the price"}'
```

**Response:**
```json
{
  "session_id": 1,
  "agent": "sales",
  "user_message": "I want to know the price",
  "reply": "Thanks for your interest! Could you share a bit more about what you're looking for?"
}
```

---

### `POST /simulate` — demo helper (no auth required)

Sends a test message into the system with a randomly generated `event_id`.

**Request body (all fields optional):**
```json
{
  "user_id": "demo_user",
  "message": "I want to know the price"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/simulate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo_user","message":"I want to know the price"}'
```

---

### `GET /sessions` — list all sessions

```bash
curl http://localhost:8000/sessions
```

**Response:**
```json
[
  { "id": 1, "user_id": "demo_user", "agent": "sales", "last_active": "2024-01-01T12:00:00" }
]
```

---

### `GET /sessions/{session_id}/messages` — list messages in a session

```bash
curl http://localhost:8000/sessions/1/messages
```

**Response:**
```json
[
  { "id": 1, "session_id": 1, "role": "user",      "content": "I want to know the price", "event_id": "evt_001", "created_at": "..." },
  { "id": 2, "session_id": 1, "role": "assistant", "content": "Thanks for your interest...", "event_id": null,    "created_at": "..." }
]
```

---

## Agent Routing Logic

| Agent | Triggered when message contains |
|---|---|
| `sales` | buy, price, pricing, cost, how much, purchase, order, product, plan, quote, discount, offer, interested, package, subscription |
| `support` | problem, issue, bug, error, broken, not working, complaint, help, fix, failed, trouble, wrong, crash, stuck, cannot, can't, unable |
| `general` | anything else |

---

## Duplicate Handling

The `event_id` column has a `UNIQUE` constraint.  
Sending the same `event_id` twice returns **409 Conflict** — the message is not saved again.

---

## Project Structure

```
whatsapp-agent-api/
├── app/
│   ├── main.py            # FastAPI app + router registration
│   ├── database.py        # SQLAlchemy engine + session factory
│   ├── models.py          # Session + Message ORM models
│   ├── schemas.py         # Pydantic request/response models
│   ├── agent_router.py    # Keyword-based agent classifier
│   ├── reply_generator.py # Anthropic API call + mock fallback
│   ├── auth.py            # Bearer token dependency
│   └── routes/
│       ├── webhook.py     # POST /webhook/whatsapp
│       ├── simulate.py    # POST /simulate
│       └── sessions.py    # GET /sessions, GET /sessions/{id}/messages
├── run.py                 # Entry point (loads .env, starts uvicorn)
├── requirements.txt
├── .env.example
└── README.md
```
