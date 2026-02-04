from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(title="Agentic Honeypot API")

API_KEY = os.getenv("API_KEY", "MY_SECRET_KEY")

# ----------- Models (GUVI Format) -----------

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
    conversationHistory: List = []
    metadata: Optional[Metadata] = None

# ----------- Routes -----------

@app.get("/")
def root():
    return {"message": "✅ Agentic Honeypot API is running."}

@app.post("/")
def detect_scam(data: HoneypotRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    text = data.message.text.lower()

    scam_keywords = ["otp", "blocked", "verify", "urgent", "account", "bank"]

    is_scam = any(word in text for word in scam_keywords)

    if is_scam:
        reply = "Scam detected. Do not respond to this message."
    else:
        reply = "This message appears safe."

    return {
        "status": "success",
        "reply": reply
    }