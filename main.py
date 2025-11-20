from fastapi import FastAPI
from typing import List

from agents.rss_reader import fetch_all_articles, ArticleBrut
from agents.llm_groq import enrich_article_with_groq, ArticleEnrichi

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Multi-agent IA Newsletter API – OK"}


@app.get("/rss-test", response_model=List[ArticleBrut])
def read_rss_articles():
    """
    Endpoint de test pour voir les articles bruts récupérés depuis les flux RSS IA.
    """
    articles = fetch_all_articles()
    return articles[:10]


@app.get("/rss-enriched-test", response_model=List[ArticleEnrichi])
def read_enriched_articles():
    """
    Endpoint de test pour voir les articles enrichis par Groq (résumé + tags + classification).
    On limite à quelques articles pour les tests.
    """
    articles = fetch_all_articles()
    selected = articles[:3]  # on limite à 3 pour le moment

    enriched: List[ArticleEnrichi] = []
    for art in selected:
        try:
            enriched_article = enrich_article_with_groq(art)
            enriched.append(enriched_article)
        except Exception as e:
            print("Erreur lors de l'enrichissement d'un article:", e)

    return enriched
