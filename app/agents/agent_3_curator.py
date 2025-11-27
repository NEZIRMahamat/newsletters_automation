import json
import re
from typing import List, Dict

from app.core.llm import groq_chat
from app.core.config import SELECTION_PATH
from app.core.logging_utils import setup_logger

logger = setup_logger(__name__)

SYSTEM = """
Tu es un éditeur spécialisé dans la veille IA.
Tu dois sélectionner les meilleurs articles, enlever les doublons
et renvoyer STRICTEMENT un JSON valide du format :

{
  "indices_selection": [0,2,4],
  "index_audio": 2
}

PAS DE TEXTE AVANT.
PAS DE TEXTE APRÈS.
"""


PROMPT = """
Voici les articles indexés :

{articles}

Choisis :
- les articles les plus pertinents
- maximum 10
- renvoie STRICTEMENT un JSON valide.
"""


def _extract_json(raw: str) -> dict:
    """Récupère un JSON même si le LLM met du texte avant/après."""
    try:
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            return json.loads(match.group(0))
    except:
        pass
    return {}


def choisir_selection(articles: List[Dict]) -> Dict:
    """Retourne :
    - indices_selection : liste d'indices
    - index_audio : indice principal
    """

    try:
        prompt = PROMPT.format(articles=json.dumps(articles, ensure_ascii=False))
        rep = groq_chat(SYSTEM, prompt, temperature=0.2, max_tokens=600)

        if not rep:
            raise ValueError("Réponse vide du LLM")

        data = _extract_json(rep)

        if not data:
            raise ValueError("JSON impossible à extraire")

        indices = [
            i for i in data.get("indices_selection", [])
            if isinstance(i, int) and 0 <= i < len(articles)
        ]

        if not indices:
            indices = list(range(min(5, len(articles))))

        audio_idx = data.get("index_audio", indices[0])
        if audio_idx not in indices:
            audio_idx = indices[0]

        result = {
            "indices_selection": indices,
            "index_audio": audio_idx,
        }

        SELECTION_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

        logger.info("✔ Sélection IA générée")
        return result

    except Exception as e:
        logger.error("❌ Curator IA erreur : %s", e)
        logger.warning("➡ Fallback automatique utilisé")

        fallback = {
            "indices_selection": list(range(min(5, len(articles)))),
            "index_audio": 0
        }
        SELECTION_PATH.write_text(json.dumps(fallback, indent=2, ensure_ascii=False), encoding="utf-8")
        return fallback
