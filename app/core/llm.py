import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def groq_chat(system_prompt: str, user_prompt: str, temperature=0.3, max_tokens=500):
    """Appel GROQ fiable, robuste, compatible tous usages."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        r = requests.post(GROQ_URL, headers=headers, json=payload)
        r.raise_for_status()
    except Exception as e:
        print("❌ Erreur API GROQ :", e)
        print("Payload envoyé :", payload)
        return ""

    data = r.json()

    try:
        return data["choices"][0]["message"]["content"]
    except:
        return ""
