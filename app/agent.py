import os
import openai

# Load key from environment
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY not found. Make sure it is set in .env")

openai.api_key = OPENAI_KEY

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
    """
    Generates a reply using OpenAI GPT-4.1-mini
    """
    # Format messages for OpenAI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history:
        # Convert 'agent' role to 'user' so OpenAI interprets previous agent replies correctly
        role = "user" if h["role"] == "agent" else "assistant"
        messages.append({"role": role, "content": h["content"]})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.6
        )
        return response.choices[0].message["content"]
    except Exception as e:
        print("OpenAI API Error:", e)
        return "Sorry, something went wrong. Can you repeat?"