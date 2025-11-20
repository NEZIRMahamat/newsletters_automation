import json
from typing import List, Optional

from pydantic import BaseModel, ValidationError
from groq import Groq

from config.settings import settings
from agents.rss_reader import ArticleBrut


# Modèle de sortie enrichie (Agent 2 + Agent 3 fusionnés)
class ArticleEnrichi(BaseModel):
    source: str
    title: str
    link: str
    published_at: Optional[str] = None

    short_summary: str
    detailed_summary: str
    tags: List[str]
    type_contenu: str  # "news" | "recherche" | "tuto" | "produit" | "opinion"
    audience: str      # "débutant" | "intermédiaire" | "expert"

    # Partie scoring (ex-Agent 3)
    score_global: int          # 0 à 100
    score_details: str         # explication courte de la note


# Client Groq global
client = Groq(api_key=settings.groq_api_key)


def enrich_article_with_groq(article: ArticleBrut) -> ArticleEnrichi:
    """
    Appelle Groq pour :
      - résumer l'article (court + long)
      - générer des tags
      - classifier le type de contenu
      - évaluer l'audience cible
      - calculer un score global de pertinence (0-100)
    Retourne un ArticleEnrichi.
    """

    # On construit le contexte texte qu'on envoie au modèle
    base_text = f"Titre: {article.title}\n\n"
    if article.summary:
        base_text += f"Résumé RSS: {article.summary}\n\n"
    if article.raw_content:
        base_text += f"Contenu brut: {article.raw_content}\n\n"

    system_prompt = (
        "Tu es un assistant expert en intelligence artificielle. "
        "On te donne un article (titre + résumé + contenu) lié à l'IA. "
        "Tu dois produire un objet JSON STRICT avec les clés suivantes :\n"
        "- short_summary : résumé très court (3 phrases max) en français\n"
        "- detailed_summary : résumé détaillé (10-15 lignes) en français\n"
        "- tags : liste de 3 à 8 mots-clés en français\n"
        "- type_contenu : une valeur parmi [\"news\", \"recherche\", \"tuto\", \"produit\", \"opinion\"]\n"
        "- audience : une valeur parmi [\"débutant\", \"intermédiaire\", \"expert\"]\n"
        "- score_global : entier entre 0 et 100 qui mesure l'intérêt de l'article pour une newsletter hebdomadaire sur l'IA "
        "(qualité, fraîcheur, pertinence, utilité pour des équipes en entreprise)\n"
        "- score_details : courte explication (2 à 4 phrases) de la note donnée\n\n"
        "IMPORTANT : réponds STRICTEMENT en JSON valide, sans texte avant ou après."
    )

    # Appel Groq (modèle à jour)
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # modèle recommandé chez Groq
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": base_text},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    raw_content = completion.choices[0].message.content

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        print("Erreur de parsing JSON depuis Groq:", e)
        print("Contenu brut reçu :", raw_content)
        raise

    try:
        article_enrichi = ArticleEnrichi(
            source=article.source,
            title=article.title,
            link=article.link,
            published_at=article.published_at.isoformat() if article.published_at else None,
            short_summary=data.get("short_summary", ""),
            detailed_summary=data.get("detailed_summary", ""),
            tags=data.get("tags", []),
            type_contenu=data.get("type_contenu", "news"),
            audience=data.get("audience", "débutant"),
            score_global=int(data.get("score_global", 0)),
            score_details=data.get("score_details", ""),
        )
    except ValidationError as e:
        print("Erreur de validation Pydantic ArticleEnrichi:", e)
        print("Données JSON:", data)
        raise

    return article_enrichi
