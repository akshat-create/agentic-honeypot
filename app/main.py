from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.agent import analyze_message

app = FastAPI(title="Agentic Honeypot API")

class MessageObj(BaseModel):
    sender: Optional[str] = "user"
    text: str
    timestamp: Optional[int] = 0

class HoneypotRequest(BaseModel):
    sessionId: str
    message: MessageObj
    conversationHistory: Optional[List[Any]] = []
    metadata: Optional[Dict[str, Any]] = {}

@app.get("/")
def root():
    return {
        "message": "✅ Agentic Honeypot API is running.",
        "usage": "POST to / or /honeypot"
    }

def process(payload: HoneypotRequest):
    result = analyze_message(payload.message.text)
    reply = "Scam detected. Do not respond." if result["classification"] == "scam" else "This looks safe."
    return {
        "status": "success",
        "classification": result["classification"],
        "confidence": result["confidence"],
        "reply": reply
    }

@app.post("/")
def detect_root(payload: HoneypotRequest):
    return process(payload)

@app.post("/honeypot")
def detect_honeypot(payload: HoneypotRequest):
    return process(payload)