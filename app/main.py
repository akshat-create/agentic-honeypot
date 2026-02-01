from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
from app.agent import generate_agent_reply

app = FastAPI(title="Agentic Honeypot API")

class HoneypotRequest(BaseModel):
    conversation_id: str
    message: str
    history: list = []

# Root route for Render homepage
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "✅ Agentic Honeypot API is live",
        "docs": "/docs",
        "endpoint": "POST /honeypot"
    }

# Honeypot POST endpoint
@app.post("/honeypot")
def honeypot(
    data: HoneypotRequest,
    x_api_key: str = Header(None)
):
    # Check hackathon API key
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    # Call your agent logic
    reply = generate_agent_reply(data.history)
    return reply