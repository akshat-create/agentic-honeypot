from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os

app = FastAPI(title="Agentic Honeypot API")

class HoneypotRequest(BaseModel):
    conversation_id: str
    message: str
    history: list = []

@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Agentic Honeypot API is live",
        "docs": "/docs",
        "endpoint": "POST /honeypot"
    }

@app.post("/honeypot")
def honeypot(data: HoneypotRequest, x_api_key: str = Header(None)):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return {
        "conversation_id": data.conversation_id,
        "classification": "scam",
        "confidence": 0.95,
        "reason": "Phishing-style message detected"
    }