from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(title="Agentic Honeypot API")

API_KEY = os.getenv("API_KEY", "MY_SECRET_KEY")


# -------- Request Models (GUVI format) --------
class Message(BaseModel):
    sender: str
    text: str
    timestamp: int


class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None


class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[dict] = []
    metadata: Optional[Metadata] = None


# -------- Root Health Check --------
@app.get("/")
def root():
    return {
        "message": "✅ Agentic Honeypot API is running.",
        "usage": "POST to /"
    }


# -------- Main Endpoint (GUVI Tester Hits This) --------
@app.post("/")
def honeypot(
    payload: HoneypotRequest,
    x_api_key: str = Header(..., alias="x-api-key")
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    text = payload.message.text.lower()

    scam_keywords = ["otp", "verify", "blocked", "account", "bank", "urgent", "click"]

    if any(word in text for word in scam_keywords):
        reply = "Scam detected. Do not respond to this message."
    else:
        reply = "Message appears safe."

    return {
        "status": "success",
        "reply": reply
    }