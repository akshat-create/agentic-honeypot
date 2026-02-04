def analyze_message(text: str):
    scam_keywords = ["otp", "bank", "blocked", "verify", "urgent", "account"]

    text_lower = text.lower()
    score = sum(word in text_lower for word in scam_keywords)

    if score >= 2:
        return {
            "classification": "scam",
            "confidence": 0.9,
            "reason": "Suspicious banking or phishing keywords detected"
        }
    else:
        return {
            "classification": "legit",
            "confidence": 0.9,
            "reason": "No scam indicators found"
        }