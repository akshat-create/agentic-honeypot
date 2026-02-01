import re

def extract_intelligence(text: str):
    return {
        "upi_ids": re.findall(r"\b[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}\b", text),
        "bank_accounts": re.findall(r"\b\d{9,18}\b", text),
        "phishing_urls": re.findall(r"https?://[^\s]+", text)
    }
