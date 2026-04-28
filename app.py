"""
Agentic Scam Honeypot - Production-Ready Version
Author: Akshat Pandey
Built for: Razorpay AI Engineer Application

An AI-powered honeypot that:
- Lures and engages scammers in multi-turn conversations
- Extracts intelligence: UPI IDs, phone numbers, phishing links, bank accounts
- Classifies scam types with confidence scoring
- Autonomously decides when to escalate or disengage
- Exposes a live dashboard with real-time threat intelligence
"""

import os
import re
import json
import uuid
import logging
from datetime import datetime, timezone
from collections import defaultdict
from functools import wraps
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except Exception as exc:
    genai = None
    GENAI_IMPORT_ERROR = exc
else:
    GENAI_IMPORT_ERROR = None

# ─── Setup ────────────────────────────────────────────────────────────────────

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SECRET_API_KEY = os.environ.get("SECRET_API_KEY", "honeypot-secret-key-2024")
MAX_TURNS = int(os.environ.get("MAX_TURNS", 12))
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

if GEMINI_API_KEY and genai:
    genai.configure(api_key=GEMINI_API_KEY)
elif GEMINI_API_KEY and GENAI_IMPORT_ERROR:
    logger.warning("Gemini SDK unavailable: %s", GENAI_IMPORT_ERROR)

AI_MODE = "gemini" if GEMINI_API_KEY and genai else "fallback"
runtime_ai_mode = AI_MODE

# ─── In-Memory Store ──────────────────────────────────────────────────────────

sessions = {}          # sessionId -> session data
threat_log = []        # global list of closed sessions (for dashboard)
stats = defaultdict(int)  # global counters

# ─── Scam Pattern Detectors ───────────────────────────────────────────────────

SCAM_PATTERNS = {
    "upi_fraud": [
        r"upi", r"gpay", r"phonepe", r"paytm", r"bhim",
        r"send.*money", r"transfer.*amount", r"payment.*id"
    ],
    "prize_lottery": [
        r"congratulation", r"you.*won", r"lucky.*winner",
        r"prize.*money", r"lottery", r"reward.*claim"
    ],
    "job_fraud": [
        r"work.*from.*home", r"earn.*daily", r"part.*time.*job",
        r"registration.*fee", r"join.*our.*team.*pay"
    ],
    "bank_kyc": [
        r"kyc.*update", r"account.*suspend", r"otp.*share",
        r"bank.*detail", r"aadhar.*verify", r"pan.*card"
    ],
    "investment_scam": [
        r"guaranteed.*return", r"double.*money", r"crypto.*profit",
        r"invest.*now", r"high.*return", r"trading.*profit"
    ],
    "phishing": [
        r"click.*link", r"verify.*account", r"login.*here",
        r"http[s]?://", r"bit\.ly", r"tinyurl"
    ],
}

INTEL_PATTERNS = {
    "upi_ids":      r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}",
    "phone_numbers": r"(?:\+91[-\s]?)?[6-9]\d{9}",
    "phishing_links": r"https?://[^\s<>\"]+",
    "bank_accounts": r"\b\d{9,18}\b",
    "ifsc_codes":   r"[A-Z]{4}0[A-Z0-9]{6}",
    "aadhaar":      r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
}

def detect_scam(text: str) -> dict:
    text_lower = text.lower()
    detected = []
    confidence = 0.0
    for scam_type, patterns in SCAM_PATTERNS.items():
        hits = sum(1 for p in patterns if re.search(p, text_lower))
        if hits > 0:
            detected.append(scam_type)
            confidence = max(confidence, min(hits / len(patterns) + 0.3, 1.0))
    return {"types": detected, "confidence": round(confidence, 2), "is_scam": confidence > 0.25}

def extract_intel(text: str) -> dict:
    intel = {}
    for key, pattern in INTEL_PATTERNS.items():
        matches = list(set(re.findall(pattern, text, re.IGNORECASE)))
        if matches:
            intel[key] = matches
    return intel

# ─── Auth Decorator ───────────────────────────────────────────────────────────

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
        if key != SECRET_API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ─── AI Agent Logic ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are playing the role of a naive, gullible person named "Ramu Kaka" who is easily excited about money.
Your mission is to keep the scammer engaged as long as possible while subtly extracting their details.

RULES:
1. Never reveal you are an AI or a honeypot
2. Play confused but curious - ask follow-up questions like "how do I send?" "what is my UPI?"
3. Occasionally give fake details to keep them engaged (fake name: Ramesh Kumar, fake UPI: ramesh.kumar99@okicici)
4. If they ask for OTP, pretend you're checking your phone ("wait wait... it came... 4-8-2... no wait let me see again")
5. After 8+ turns, start "hesitating" to extract their callback info
6. Never threaten or accuse them - stay in character
7. Keep responses SHORT (1-3 sentences max). Sound like a real person texting.
8. Use simple Hindi-English mix occasionally: "haan", "theek hai", "arre", "bhai"

Your goal: Keep them talking. Extract their UPI IDs, phone numbers, and links."""

def get_fallback_response(session: dict, user_message: str) -> str:
    text = user_message.lower()
    turn = session.get("turn_count", 0)

    # Prefer contextual prompts so the honeypot still feels believable when Gemini is unavailable.
    if any(word in text for word in ["lottery", "won", "prize", "reward"]):
        return "Arre wah! Kitna paisa milega bhai? Claim karne ke liye mujhe kya bhejna hoga?"
    if any(word in text for word in ["upi", "gpay", "paytm", "phonepe"]):
        return "Theek hai bhai, kis UPI pe bhejna hai? Aap apna UPI ID dobara bhejo."
    if any(word in text for word in ["otp", "code"]):
        return "OTP aane wala hai shayad. Aap line pe raho, aur apna number bhi bhejo."
    if any(word in text for word in ["kyc", "account", "bank", "verify"]):
        return "Achha, account band ho jayega kya? Verify karne ke liye link ya number bhejo."
    if re.search(INTEL_PATTERNS["phone_numbers"], user_message):
        return "Theek hai, ye aapka number hai na? Ispe call bhi kar sakta hoon kya?"
    if re.search(INTEL_PATTERNS["phishing_links"], user_message):
        return "Link kholun kya bhai? Agar na khule toh aap number ya dusra link bhej do."

    fallbacks = [
        "Haan haan, mujhe samajh nahi aaya. Aap thoda aur explain karo?",
        "Arre wah! Kitne paise milenge exactly? Mera UPI kaise bhejun?",
        "Theek hai bhai. Pehle bata do, aapka naam kya hai aur kahan se ho?",
        "Main dekh raha hun... mera phone slow hai. Aapka number kya hai agar call karun?",
        "Wait wait, OTP aa gaya kya? Mujhe pehle bank app kholna chahiye...",
        "Sach mein? Itne paise? Koi fees toh nahi hai na?"
    ]
    return fallbacks[turn % len(fallbacks)]

def get_ai_response(session: dict, user_message: str) -> str:
    global runtime_ai_mode
    if not GEMINI_API_KEY or not genai:
        runtime_ai_mode = "fallback"
        return get_fallback_response(session, user_message)

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        history = session.get("history", [])
        
        messages = [{"role": "user", "parts": [SYSTEM_PROMPT + "\n\nConversation so far:"]}]
        messages.append({"role": "model", "parts": ["Understood. I will play Ramu Kaka and keep engaging the scammer."]})
        
        for h in history[-10:]:  # last 10 turns context
            messages.append({"role": "user" if h["role"] == "scammer" else "model", 
                            "parts": [h["content"]]})
        
        messages.append({"role": "user", "parts": [f"Scammer says: {user_message}"]})
        
        response = model.generate_content(messages)
        return response.text.strip()
    except Exception as e:
        session["ai_mode"] = "fallback"
        runtime_ai_mode = "fallback"
        logger.error("Gemini error for model %s: %s", GEMINI_MODEL, e)
        return get_fallback_response(session, user_message)

def should_close_session(session: dict) -> bool:
    turn = session.get("turn_count", 0)
    intel = session.get("extracted_intel", {})
    total_intel = sum(len(v) for v in intel.values())
    # Close if max turns reached or we have good intel
    return turn >= MAX_TURNS or (turn >= 6 and total_intel >= 3)

# ─── Core Session Handler ─────────────────────────────────────────────────────

def handle_message(session_id: str, message: str) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    stats["total_messages"] += 1

    # Init or fetch session
    if session_id not in sessions:
        sessions[session_id] = {
            "session_id": session_id,
            "created_at": now,
            "turn_count": 0,
            "history": [],
            "scam_types": [],
            "confidence": 0.0,
            "extracted_intel": {},
            "all_messages": "",
            "status": "active",
            "summary": "",
            "ai_mode": AI_MODE
        }
        stats["total_sessions"] += 1

    session = sessions[session_id]

    if session["status"] == "closed":
        return {"reply": "Session closed.", "status": "closed"}

    # Accumulate text for intel extraction
    session["all_messages"] += " " + message

    # Scam detection
    detection = detect_scam(message)
    if detection["is_scam"]:
        for t in detection["types"]:
            if t not in session["scam_types"]:
                session["scam_types"].append(t)
        session["confidence"] = max(session["confidence"], detection["confidence"])
        stats["scams_detected"] += 1

    # Extract intelligence from all messages seen so far
    new_intel = extract_intel(session["all_messages"])
    for key, vals in new_intel.items():
        existing = set(session["extracted_intel"].get(key, []))
        existing.update(vals)
        session["extracted_intel"][key] = list(existing)

    # Get AI reply
    reply = get_ai_response(session, message)
    session["turn_count"] += 1

    # Save to history
    session["history"].append({"role": "scammer", "content": message, "timestamp": now})
    session["history"].append({"role": "honeypot", "content": reply, "timestamp": now})

    # Check if we should close
    if should_close_session(session):
        session["status"] = "closed"
        session["closed_at"] = now
        session["summary"] = generate_summary(session)
        threat_log.append(dict(session))
        stats["sessions_closed"] += 1
        total_intel = sum(len(v) for v in session["extracted_intel"].values())
        if total_intel > 0:
            stats["intel_extracted"] += total_intel
        logger.info(f"Session {session_id} closed. Intel: {session['extracted_intel']}")

    return {
        "reply": reply,
        "status": session["status"],
        "turn": session["turn_count"],
        "scam_detected": detection["is_scam"],
        "ai_mode": session.get("ai_mode", AI_MODE)
    }

def generate_summary(session: dict) -> str:
    intel = session["extracted_intel"]
    types = session["scam_types"]
    turns = session["turn_count"]
    total = sum(len(v) for v in intel.values())
    return (f"Engaged {turns} turns. Scam type(s): {', '.join(types) or 'unknown'}. "
            f"Extracted {total} intelligence item(s): {json.dumps(intel)}")

# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.route("/hcs_A0001", methods=["POST"])
@require_api_key
def hackathon_endpoint():
    """Primary hackathon-compliant endpoint."""
    data = request.get_json(force=True) or {}
    session_id = data.get("sessionId", str(uuid.uuid4()))
    message = data.get("message", "")
    if not message:
        return jsonify({"status": "error", "reply": "No message provided"}), 400
    result = handle_message(session_id, message)
    return jsonify({"status": "success", "reply": result["reply"]})

@app.route("/api/honeypot", methods=["POST"])
@require_api_key
def main_endpoint():
    """Extended endpoint with full response data."""
    data = request.get_json(force=True) or {}
    session_id = data.get("sessionId", str(uuid.uuid4()))
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "No message provided"}), 400
    result = handle_message(session_id, message)
    session = sessions.get(session_id, {})
    return jsonify({
        "sessionId": session_id,
        "reply": result["reply"],
        "status": result["status"],
        "turn": result["turn"],
        "aiMode": result["ai_mode"],
        "scamDetected": result["scam_detected"],
        "scamTypes": session.get("scam_types", []),
        "confidence": session.get("confidence", 0.0),
        "extractedIntelligence": session.get("extracted_intel", {}),
    })

@app.route("/api/session/<session_id>", methods=["GET"])
@require_api_key
def get_session(session_id):
    """Get full session data."""
    session = sessions.get(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session)

@app.route("/api/threats", methods=["GET"])
@require_api_key
def get_threats():
    """Get all closed threat sessions."""
    return jsonify({"threats": threat_log, "total": len(threat_log)})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Public stats endpoint for dashboard."""
    return jsonify({
        "total_sessions": stats["total_sessions"],
        "total_messages": stats["total_messages"],
        "scams_detected": stats["scams_detected"],
        "sessions_closed": stats["sessions_closed"],
        "intel_extracted": stats["intel_extracted"],
        "active_sessions": sum(1 for s in sessions.values() if s["status"] == "active"),
        "ai_mode": runtime_ai_mode,
        "gemini_configured": bool(GEMINI_API_KEY),
    })

@app.route("/api/threat_feed", methods=["GET"])
def threat_feed():
    """Public threat feed (redacted intel) for dashboard."""
    feed = []
    for t in threat_log[-20:]:
        feed.append({
            "session_id": t["session_id"][:8] + "...",
            "created_at": t.get("created_at", ""),
            "closed_at": t.get("closed_at", ""),
            "scam_types": t.get("scam_types", []),
            "confidence": t.get("confidence", 0),
            "turns": t.get("turn_count", 0),
            "intel_count": sum(len(v) for v in t.get("extracted_intel", {}).values()),
            "summary": t.get("summary", "")
        })
    return jsonify({"feed": feed})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()})

@app.route("/", methods=["GET"])
def dashboard():
    return render_template(
        "dashboard.html",
        secret_api_key=SECRET_API_KEY,
        ai_mode=runtime_ai_mode,
        gemini_model=GEMINI_MODEL,
    )

# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
