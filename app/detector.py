def detect_scam(message: str) -> bool:
    keywords = [
        "blocked", "suspended", "verify", "urgent",
        "otp", "account", "kyc", "refund", "upi",
        "bank", "click", "limited"
    ]

    msg = message.lower()
    return any(word in msg for word in keywords)