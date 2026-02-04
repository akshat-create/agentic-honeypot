from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
from app.agent import analyze_message

app = FastAPI(title="Agentic Honeypot API")

API_KEY = os.getenv("API_KEY", "MY_SECRET_KEY")


class IncomingMessage(BaseModel):
    sessionId: str
    message: dict
    conversationHistory: list = []
    metadata: dict = {}


@app.get("/")
def root():
    return {"status": "success", "reply": "Agentic Honeypot API is running"}


@app.post("/")
def honeypot_root(payload: IncomingMessage, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    text = payload.message.get("text", "")

    result = analyze_message(text)

    reply_text = (
        "Scam detected. Do not respond to this message."
        if result["classification"] == "scam"
        else "Message looks safe."
    )

    return {
        "status": "success",
        "reply": reply_text
    }


@app.post("/honeypot")
def honeypot(payload: IncomingMessage, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    text = payload.message.get("text", "")

    result = analyze_message(text)

    reply_text = (
        "Scam detected. Do not respond to this message."
        if result["classification"] == "scam"
        else "Message looks safe."
    )

    return {
        "status": "success",
        "reply": reply_text
    }