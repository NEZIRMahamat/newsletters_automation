import feedparser
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class ArticleBrut(BaseModel):
    source: str
    title: str
    link: str
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    raw_content: Optional[str] = None


# Pour l'instant on met quelques flux IA "génériques".
# Tu pourras les adapter plus tard avec des sources plus ciblées.
RSS_SOURCES = [
    "https://export.arxiv.org/rss/cs.AI",   # Arxiv IA
    "https://export.arxiv.org/rss/cs.LG",   # Arxiv machine learning
]


def fetch_rss(url: str) -> List[ArticleBrut]:
    feed = feedparser.parse(url)
    articles: List[ArticleBrut] = []

    for entry in feed.entries:
        # Gestion de la date
        published_at = None
        if hasattr(entry, "published_parsed") and entry.published_parsed is not None:
            published_at = datetime(
                year=entry.published_parsed.tm_year,
                month=entry.published_parsed.tm_mon,
                day=entry.published_parsed.tm_mday,
                hour=entry.published_parsed.tm_hour,
                minute=entry.published_parsed.tm_min,
                second=entry.published_parsed.tm_sec,
            )

        # Contenu brut si dispo
        raw_content = None
        if hasattr(entry, "content") and entry.content:
            raw_content = entry.content[0].value

        article = ArticleBrut(
            source=getattr(feed.feed, "title", url),
            title=getattr(entry, "title", "Sans titre"),
            link=getattr(entry, "link", ""),
            summary=getattr(entry, "summary", None),
            published_at=published_at,
            raw_content=raw_content,
        )
        articles.append(article)

    return articles


def fetch_all_articles() -> List[ArticleBrut]:
    """Récupère tous les articles de toutes les sources RSS définies."""
    all_articles: List[ArticleBrut] = []
    for url in RSS_SOURCES:
        try:
            articles = fetch_rss(url)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Erreur lors de la récupération du flux {url}: {e}")
    return all_articles
