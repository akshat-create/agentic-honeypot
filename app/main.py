from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
from app.agent import analyze_message

app = FastAPI(title="Agentic Honeypot API")

# --------------------
# Models
# --------------------

class MessageObj(BaseModel):
    sender: Optional[str] = "user"
    text: str
    timestamp: Optional[int] = 0

class HoneypotRequest(BaseModel):
    sessionId: str
    message: MessageObj
    conversationHistory: Optional[List[Any]] = []
    metadata: Optional[Dict[str, Any]] = {}

# --------------------
# Root health check
# --------------------

@app.get("/")
def root():
    return {
        "message": "✅ Agentic Honeypot API is running.",
        "usage": "POST to / or /honeypot"
    }

# --------------------
# Core handler (shared)
# --------------------

def handle_request(payload: HoneypotRequest):
    result = analyze_message(payload.message.text)

    if result["classification"] == "scam":
        reply = "Scam detected. Do not respond to this message."
    else:
        reply = "This message looks safe."

    return {
        "status": "success",
        "classification": result["classification"],
        "confidence": result["confidence"],
        "reply": reply
    }

# --------------------
# Accept POST on /
# --------------------

@app.post("/")
def detect_root(
    payload: HoneypotRequest,
    x_api_key: Optional[str] = Header(None)
):
    return handle_request(payload)

# --------------------
# Accept POST on /honeypot
# --------------------

@app.post("/honeypot")
def detect_honeypot(
    payload: HoneypotRequest,
    x_api_key: Optional[str] = Header(None)
):
    return handle_request(payload)