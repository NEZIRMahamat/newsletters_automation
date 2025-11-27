import feedparser
import requests
import hashlib
import json
import time

from app.core.config import RAW_PATH, NEWSAPI_KEY
from app.core.logging_utils import setup_logger

logger = setup_logger(__name__)

# 🌐 Flux IA (ta liste)
IA_FEEDS = [
    "https://openai.com/blog/rss.xml",
    "https://ai.googleblog.com/atom.xml",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://meta.ai/blog/rss/",
    "https://stability.ai/blog?format=rss",
    "https://huggingface.co/blog/feed.xml",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/ArtificialIntelligence.xml",
    "https://www.technologyreview.com/feed/",
    "https://www.semianalysis.com/feed",
]


def _hash(text: str) -> str:
    """Hash MD5 pour supprimer les doublons (URL)."""
    return hashlib.md5((text or "").encode("utf-8")).hexdigest()


def collect_from_rss(max_items: int = 20):
    """
    Collecte RSS sur les flux IA.
    Ne gère QUE le thème 'intelligence artificielle'.
    """
    articles = []

    for url in IA_FEEDS:
        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:max_items]:
                link = entry.get("link", "")
                if not link:
                    continue

                # Essai de récupérer une image
                image = None
                if "media_content" in entry:
                    mc = entry.get("media_content", [])
                    if mc and isinstance(mc, list):
                        image = mc[0].get("url")
                elif "links" in entry:
                    for l in entry.links:
                        if l.get("type", "").startswith("image"):
                            image = l.get("href")
                            break

                articles.append(
                    {
                        "titre": entry.get("title", "").strip(),
                        "resume": entry.get("summary", "").strip(),
                        "url": link,
                        "source": (entry.get("source") or {}).get("title", "") or "RSS IA",
                        "image": image,
                        "theme": "intelligence artificielle",
                        "hash": _hash(link),
                    }
                )

        except Exception as e:
            logger.error("❌ Erreur RSS %s : %s", url, e)

    return articles


def collect_from_newsapi(max_items: int = 20):
    """
    Complément via NewsAPI sur le thème IA.
    """
    if not NEWSAPI_KEY:
        logger.warning("NEWSAPI_KEY manquante → NewsAPI désactivé.")
        return []

    params = {
        "q": "artificial intelligence OR AI OR \"large language model\" OR LLM",
        "language": "en",  # tu peux ajouter 'fr' si tu veux du FR
        "pageSize": max_items,
        "sortBy": "publishedAt",
        "apiKey": NEWSAPI_KEY,
    }

    try:
        r = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.error("❌ Erreur NewsAPI : %s", e)
        return []

    articles = []
    for art in data.get("articles", []):
        url = art.get("url", "")
        if not url:
            continue

        articles.append(
            {
                "titre": (art.get("title") or "").strip(),
                "resume": (art.get("description") or "").strip(),
                "url": url,
                "source": art.get("source", {}).get("name", "NewsAPI"),
                "image": art.get("urlToImage"),
                "theme": "intelligence artificielle",
                "hash": _hash(url),
            }
        )

    return articles


def collecter_news(themes, max_par_flux: int = 20):
    """
    Collecteur principal.
    On ignore les thèmes de la config et on fait une veille IA globale :
    - RSS IA
    - + NewsAPI IA
    - suppression des doublons par URL
    """

    logger.info("📡 Collecte IA (RSS + NewsAPI)…")

    rss_articles = collect_from_rss(max_par_flux)
    news_articles = collect_from_newsapi(max_par_flux)

    combined = rss_articles + news_articles

    unique = []
    seen = set()

    for art in combined:
        h = art["hash"]
        if h not in seen:
            seen.add(h)
            unique.append(art)

    RAW_PATH.write_text(json.dumps(unique, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info("✔ %d articles IA collectés.", len(unique))
    return unique
