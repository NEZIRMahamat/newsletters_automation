import base64
import requests
from app.core.llm import groq_chat
from app.core.config import AUDIO_PATH, GROQ_API_KEY
from app.core.logging_utils import setup_logger

logger = setup_logger(__name__)

TTS_URL = "https://api.groq.com/openai/v1/audio/speech"

SYSTEM = """
Tu es un présentateur professionnel.
Écris un script de capsule audio (2 minutes max), clair et direct,
sans phrases du type "cet article dit".
"""

USER = """
Titre : {titre}
Source : {source}
Résumé : {resume}

Écris un script dynamique et informatif.
"""


def generer_script_audio(article):
    prompt = USER.format(
        titre=article.get("titre",""),
        source=article.get("source",""),
        resume=article.get("resume",""),
    )
    return groq_chat(SYSTEM, prompt, temperature=0.4, max_tokens=500)


def generer_audio(script: str):
    if not script:
        script = "Bienvenue dans votre capsule audio Flash AI."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini-tts",
        "input": script,
        "voice": "alloy",
        "format": "mp3"
    }

    logger.info("🎤 Envoi au TTS Groq…")

    r = requests.post(TTS_URL, json=payload, headers=headers)

    if r.status_code != 200:
        logger.error("❌ Erreur Groq TTS : %s", r.text)
        return

    AUDIO_PATH.write_bytes(r.content)
    logger.info("🎧 Audio généré → %s", AUDIO_PATH)
