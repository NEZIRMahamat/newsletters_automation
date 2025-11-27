import json
import re

from app.core.llm import groq_chat
from app.core.logging_utils import setup_logger

logger = setup_logger(__name__)

# Dictionnaire de correspondance rapide
KEYWORDS = {
    "ai": "intelligence artificielle",
    "ia": "intelligence artificielle",
    "artificial intelligence": "intelligence artificielle",
    "machine learning": "machine learning",
    "ml": "machine learning",
    "deep learning": "deep learning",
    "deeplearning": "deep learning",
    "data": "data",
    "data science": "data science",
    "llm": "modèles de langage",
    "gpt": "modèles de langage",
    "chatgpt": "modèles de langage",
    "openai": "intelligence artificielle",
    "google ai": "intelligence artificielle",
    "anthropic": "intelligence artificielle",
    "cloud": "cloud",
    "aws": "cloud",
    "azure": "cloud",
    "gcp": "cloud",
}


def _keyword_detection(text: str):
    """Détection locale sans LLM : fiable et immédiate."""
    text_low = text.lower()
    detected = []

    for key, theme in KEYWORDS.items():
        if key in text_low:
            if theme not in detected:
                detected.append(theme)

    return detected


SYSTEM = """
Tu es un classificateur de thèmes spécialisé en IA et technologie.
Tu renvoies STRICTEMENT un JSON valide du format :

{
  "themes": ["intelligence artificielle", "machine learning"]
}

PAS de texte, PAS d'explications.
"""

USER = """
Voici un texte à analyser :

"{texte}"

Détecte les thèmes principaux, uniquement les thèmes (pas de résumé).
"""


def detect_themes(texte: str):
    """Détection robuste : keywords → puis LLM."""
    if not texte or texte.strip() == "":
        return []

    # 1) Pré-détection ultra-fiable
    base = _keyword_detection(texte)

    # Si on a déjà des thèmes → on les renvoie sans LLM
    if base:
        return base

    # 2) Sinon → fallback LLM
    rep = groq_chat(SYSTEM, USER.format(texte=texte), temperature=0.1, max_tokens=150)

    if not rep:
        logger.error("❌ Aucune réponse du LLM")
        return []

    # Extraire JSON
    match = re.search(r"\{[\s\S]*\}", rep)
    if not match:
        logger.error("❌ JSON introuvable dans : %s", rep)
        return []

    try:
        data = json.loads(match.group(0))
        themes = data.get("themes", [])
    except Exception:
        logger.error("JSON invalide : %s", rep)
        themes = []

    return themes
