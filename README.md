# Agentic Honeypot

An AI-assisted scam intelligence demo that detects scam messages, keeps the scammer engaged, extracts useful indicators, and displays everything in a live dashboard.

The app works in two modes:
- `Gemini mode` when a valid Gemini API key is available
- `Fallback mode` when Gemini is unavailable or rate-limited

Fallback mode is fully usable for demos and portfolio uploads. Scam detection, indicator extraction, session tracking, and the dashboard still work without any paid API.

## Features

- Detects common scam categories:
  - UPI fraud
  - prize / lottery scams
  - job fraud
  - bank KYC scams
  - investment scams
  - phishing
- Extracts indicators from messages:
  - UPI IDs
  - phone numbers
  - phishing links
  - bank account-like number strings
  - IFSC patterns
  - Aadhaar-like patterns
- Live dashboard with:
  - threat feed
  - simulator panel
  - extracted intelligence view
  - fallback / Gemini status indicator
- API endpoints for hackathon-style integration

## Tech Stack

- Python 3.12
- Flask
- Google Gemini API via `google-generativeai`
- Vanilla HTML, CSS, and JavaScript

## Project Structure

```text
.
├── app.py
├── Procfile
├── README.md
├── requirements.txt
├── runtime.txt
└── templates/
    └── dashboard.html
```

## Local Setup

### 1. Create a virtual environment

```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your env file

```bash
cp .env.example .env
```

Default `.env.example`:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash-lite
SECRET_API_KEY=honeypot-local-2026
MAX_TURNS=12
PORT=5000
```

If you do not want to use Gemini, leave `GEMINI_API_KEY` empty.

### 4. Run the app

```bash
python app.py
```

If port `5000` is already in use:

```bash
PORT=5003 python app.py
```

Then open:

```text
http://localhost:5000
```

or

```text
http://localhost:5003
```

## API Endpoints

### Main honeypot endpoint

```text
POST /api/honeypot
```

Headers:

```text
X-API-Key: <SECRET_API_KEY>
Content-Type: application/json
```

Body:

```json
{
  "sessionId": "test-001",
  "message": "Congratulations! You have won Rs 50,000 lottery. Send your UPI ID to claim."
}
```

### Other endpoints

- `POST /hcs_A0001`
- `GET /api/session/<session_id>`
- `GET /api/threats`
- `GET /api/stats`
- `GET /api/threat_feed`
- `GET /health`
- `GET /`

## Example Test Message

```text
Congratulations! You have won Rs 50,000 lottery. Send your UPI ID to claim.
```

Other useful demo messages:

```text
Sir your bank KYC is expired. Verify now at http://secure-verify-bank.net/login
```

```text
Work from home job available. Earn Rs 5000 daily. Registration fee only Rs 499. Pay on jobshelp@paytm
```

```text
Invest Rs 1000 today and get Rs 10000 in 7 days guaranteed. Call 9876543210 now.
```

## Deployment

This repo is ready for simple deployment platforms like Render.

### Render settings

- Build command:

```bash
pip install -r requirements.txt
```

- Start command:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
```

### Required environment variables

- `SECRET_API_KEY`
- `MAX_TURNS`
- `PORT`

Optional:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`

## Notes

- Recommended Python version: `3.10` to `3.12`
- Python `3.14+` may install successfully but can break older Gemini SDK flows
- If Gemini is unavailable, the app automatically uses local fallback replies
- `.env` is ignored by Git and should not be uploaded

## GitHub Upload Checklist

- `.env` stays local only
- `.venv/` and `.venv312/` are ignored
- `README.md` is updated
- `runtime.txt` is included for Python version pinning
- `Procfile` is included for deployment

## Disclaimer

This project is for cybersecurity research, education, and demo use only. Do not use it to target real people outside controlled and lawful environments.
