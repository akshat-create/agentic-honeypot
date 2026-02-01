import os
from openai import OpenAI

# Initialize OpenAI client using secret key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a normal person chatting online.
You must:
- Sound worried, cooperative, and confused
- Never reveal you suspect a scam
- Keep the conversation going
- Try to extract:
  - Bank account numbers
  - UPI IDs
  - Payment links
  - Websites
"""

def generate_agent_reply(history):
    # Prepare messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": "user", "content": msg["message"]} for msg in history]

    # Call OpenAI chat completion
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.6
    )

    return {"reply": response.choices[0].message.content}