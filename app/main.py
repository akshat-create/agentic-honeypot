from fastapi import FastAPI, Request, Header, HTTPException
from typing import Optional

app = FastAPI(title="Agentic Honeypot API")

API_KEY = "MY_SECRET_KEY"


def verify_key(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@app.get("/")
def root():
    return {
        "message": "✅ Agentic Honeypot API is running.",
        "usage": "POST / with x-api-key header"
    }


@app.post("/")
async def honeypot(request: Request, x_api_key: Optional[str] = Header(None)):
    verify_key(x_api_key)

    try:
        body = await request.json()
    except:
        body = {}

    text = ""

    if isinstance(body, dict):
        if "message" in body:
            if isinstance(body["message"], dict):
                text = body["message"].get("text", "")
            elif isinstance(body["message"], str):
                text = body["message"]
        elif "text" in body:
            text = body["text"]

    scam_words = ["otp", "verify", "blocked", "urgent", "bank", "account"]
    is_scam = any(word in text.lower() for word in scam_words)

    reply = "Scam detected. Do not respond to this message." if is_scam else "Message appears safe."

    return {
        "status": "success",
        "reply": reply
    }


@app.post("/honeypot")
async def honeypot_alt(request: Request, x_api_key: Optional[str] = Header(None)):
    return await honeypot(request, x_api_key)