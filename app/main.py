from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

app = FastAPI(title="Agentic Honeypot API")

API_KEY = os.getenv("API_KEY", "MY_SECRET_KEY")

# ---------- Models ----------

class IncomingMessage(BaseModel):
    sender: Optional[str] = None
    text: Optional[str] = None
    timestamp: Optional[int] = None

class HoneypotRequest(BaseModel):
    sessionId: Optional[str] = None
    message: Optional[Any] = None
    conversationHistory: Optional[list] = []

# ---------- Routes ----------

@app.get("/")
def root():
    return {
        "message": "✅ Agentic Honeypot API is running.",
        "usage": "POST to /"
    }

@app.post("/")
def honeypot(
    body: HoneypotRequest,
    x_api_key: str = Header(...)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # Extract message text (supports both formats)
    text = None
    if isinstance(body.message, dict):
        text = body.message.get("text")
    elif isinstance(body.message, str):
        text = body.message

    if not text:
        raise HTTPException(status_code=400, detail="Invalid message format")

    scam_keywords = ["otp", "blocked", "verify", "bank", "urgent", "account"]

    is_scam = any(word in text.lower() for word in scam_keywords)

    if is_scam:
        reply = "Scam detected. Do not respond to this message."
    else:
        reply = "Message appears safe."

    return {
        "status": "success",
        "reply": reply
    }