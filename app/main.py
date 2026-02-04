from fastapi import FastAPI, Header, HTTPException, Request
import os

app = FastAPI(title="Agentic Honeypot API")

API_KEY = os.getenv("API_KEY", "MY_SECRET_KEY")


@app.get("/")
def root():
    return {
        "message": "✅ Agentic Honeypot API is running.",
        "usage": "POST to /"
    }


@app.post("/")
async def honeypot(request: Request, x_api_key: str = Header(..., alias="x-api-key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    body = await request.json()

    # Try to extract message text safely from ANY structure
    text = ""
    try:
        if isinstance(body.get("message"), dict):
            text = body["message"].get("text", "")
        elif isinstance(body.get("message"), str):
            text = body["message"]
    except:
        text = ""

    text = text.lower()

    scam_keywords = ["otp", "verify", "blocked", "account", "bank", "urgent", "click"]

    if any(word in text for word in scam_keywords):
        reply = "Scam detected. Do not respond to this message."
    else:
        reply = "Message appears safe."

    return {
        "status": "success",
        "reply": reply
    }