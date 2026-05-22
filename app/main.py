from fastapi import FastAPI
from app.database import Base, engine
from app.routes import webhook, simulate, sessions

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="WhatsApp Agent API",
    description="Routes incoming messages to sales, support, or general agents and saves conversations.",
    version="1.0.0",
)

app.include_router(webhook.router, prefix="/webhook", tags=["Webhook"])
app.include_router(simulate.router, tags=["Simulate"])
app.include_router(sessions.router, tags=["Sessions"])


@app.get("/")
def root():
    return {"status": "ok", "message": "WhatsApp Agent API is running."}
