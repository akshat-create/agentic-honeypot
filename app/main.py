from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from app.detector import detect_scam
from app.agent import generate_agent_reply
from app.extractor import extract_intelligence
from app.memory import get_memory, add_message

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = FastAPI()

class MessageRequest(BaseModel):
    conversation_id: str
    message: str
    history: list = []

@app.post("/honeypot")
async def honeypot(req: MessageRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    convo_id = req.conversation_id
    msg = req.message

    add_message(convo_id, "scammer", msg)
    history = get_memory(convo_id)

    is_scam = detect_scam(msg)

    if is_scam:
        reply = generate_agent_reply(history)
        add_message(convo_id, "agent", reply)

        intel = extract_intelligence(msg + " " + reply)

        return {
            "is_scam": True,
            "agent_engaged": True,
            "reply": reply,
            "intelligence": intel,
            "metrics": {
                "turns": len(history),
                "confidence": 0.95
            }
        }

    return {
        "is_scam": False,
        "agent_engaged": False,
        "reply": "Okay",
        "intelligence": {},
        "metrics": {"turns": len(history)}
    }