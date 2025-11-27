import json
import re
from typing import List, Dict

from app.core.llm import groq_chat
from app.core.config import ENRICHED_PATH
from app.core.logging_utils import setup_logger

logger = setup_logger(__name__)

SYSTEM = """
Tu es un expert en intelligence artificielle.
Pour chaque article, tu dois produire un JSON STRICTEMENT VALIDE avec :

- "resume_detaille" : un résumé riche, informatif, précis (5 à 10 lignes),
  qui explique directement les informations clés. Tu ne dois JAMAIS écrire
  "l'article dit", "ce papier explique", "cet article raconte", etc.
  Tu rédiges comme si TU expliquais directement le contenu.

- "sous_theme" : un seul sous-thème parmi :
  ["LLM", "machine learning", "deep learning", "NLP", "vision", "robotique",
   "cloud AI", "sécurité IA", "chips & hardware IA", "recherche IA", "produits IA", "IA générative", "IA & société"]

- "importance" : entier de 1 (peu important) à 5 (très important) pour une veille IA.

- "tags": liste de 2 à 5 mots-clés courts (en français).

FORMAT EXACT attendu :

{
  "resume_detaille": "...",
  "sous_theme": "...",
  "importance": 4,
  "tags": ["...", "..."]
}

Tu ne renvoies QUE ce JSON, sans texte autour.
"""

USER_TEMPLATE = """
Titre : {titre}
Source : {source}
Résumé brut (venant du flux) :
{resume}

Explique le contenu de façon claire et détaillée, en suivant STRICTEMENT le format JSON demandé.
"""


def _extract_json_block(text: str) -> dict:
    """Essaye d'extraire un bloc JSON valide depuis la réponse du LLM."""
    try:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return {}
        return json.loads(match.group(0))
    except Exception:
        return {}


def analyser_article(article: Dict) -> Dict:
    """Analyse un article avec le LLM : résumé + sous-thème + importance."""
    user = USER_TEMPLATE.format(
        titre=article.get("titre", ""),
        source=article.get("source", ""),
        resume=article.get("resume", ""),
    )

    rep = groq_chat(SYSTEM, user, temperature=0.3, max_tokens=550)

    if not rep:
        logger.warning("Réponse LLM vide, fallback pour : %s", article.get("titre", ""))
        enriched = dict(article)
        enriched.setdefault("sous_theme", "IA – Divers")
        enriched.setdefault("importance", 3)
        enriched["resume"] = article.get("resume", "")
        enriched.setdefault("tags", [])
        return enriched

    data = _extract_json_block(rep)
    if not data:
        logger.warning("JSON LLM invalide, fallback pour : %s", article.get("titre", ""))
        enriched = dict(article)
        enriched.setdefault("sous_theme", "IA – Divers")
        enriched.setdefault("importance", 3)
        enriched["resume"] = article.get("resume", "")
        enriched.setdefault("tags", [])
        return enriched

    enriched = dict(article)
    enriched["resume"] = data.get("resume_detaille", article.get("resume", ""))
    enriched["sous_theme"] = data.get("sous_theme", "IA – Divers")
    enriched["importance"] = int(data.get("importance", 3))
    enriched["tags"] = data.get("tags", [])

    return enriched


def analyser_articles(articles: List[Dict]) -> List[Dict]:
    """Analyse toute la liste d'articles, sauvegarde en JSON."""
    enriched = []

    total = len(articles)
    for i, art in enumerate(articles, start=1):
        logger.info("🧠 Analyse LLM %d/%d", i, total)
        enr = analyser_article(art)
        enriched.append(enr)

    ENRICHED_PATH.write_text(json.dumps(enriched, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("✔ Articles enrichis sauvegardés → %s", ENRICHED_PATH)
    return enriched
