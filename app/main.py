from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Any, Dict

app = FastAPI(title="Agentic Honeypot API")

API_KEY = "MY_SECRET_KEY"


# ---------- AUTH ----------
async def verify_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


# ---------- ROOT HEALTH ----------
@app.get("/")
def root():
    return {
        "message": "✅ Agentic Honeypot API is running.",
        "usage": "POST / with x-api-key header"
    }


# ---------- UNIVERSAL POST HANDLER ----------
@app.post("/")
async def honeypot_root(request: Request, x_api_key: Optional[str] = Header(None)):
    await verify_key(x_api_key)
    body = await request.json()

    # Accept ANY format GUVI sends
    text = "Hello"

    try:
        if isinstance(body, dict):
            if "message" in body:
                if isinstance(body["message"], dict):
                    text = body["message"].get("text", "")
                elif isinstance(body["message"], str):
                    text = body["message"]
            elif "text" in body:
                text = body["text"]
    except:
        pass

    # Simple honeypot logic
    scam_words = ["otp", "verify", "blocked", "urgent", "bank", "account"]
    is_scam = any(word in text.lower() for word in scam_words)

    if is_scam:
        reply = "Scam detected. Do not respond to this message."
    else:
        reply = "Message appears safe."

    return {
        "status": "success",
        "reply": reply
    }


# ---------- BACKWARD COMPATIBILITY ----------
@app.post("/honeypot")
async def honeypot_alt(request: Request, x_api_key: Optional[str] = Header(None)):
    return await honeypot_root(request, x_api_key)