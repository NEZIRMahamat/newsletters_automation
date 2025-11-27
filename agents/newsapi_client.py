import requests
from typing import List
from datetime import datetime
from config.settings import settings
from agents.rss_reader import ArticleBrut

NEWSAPI_ENDPOINT = "https://newsapi.org/v2/everything"


def _convert_item_to_article(item: dict) -> ArticleBrut:
    published_at = None
    if item.get("publishedAt"):
        try:
            published_at = datetime.fromisoformat(item["publishedAt"].replace("Z", "+00:00"))
        except:
            pass
    
    return ArticleBrut(
        source=item.get("source", {}).get("name", "NewsAPI"),
        title=item.get("title", "Sans titre"),
        link=item.get("url", ""),
        summary=item.get("description"),
        raw_content=item.get("content"),
        published_at=published_at
    )


def fetch_newsapi(query: str, page_size: int = 20) -> List[ArticleBrut]:
    if not settings.newsapi_api_key:
        return []

    params = {
        "q": query,
        "pageSize": page_size,
        "language": "fr",
        "sortBy": "relevancy",
    }

    headers = {"X-Api-Key": settings.newsapi_api_key}

    try:
        r = requests.get(NEWSAPI_ENDPOINT, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        items = data.get("articles", [])
        return [_convert_item_to_article(a) for a in items]
    except Exception as e:
        print("NewsAPI ERROR:", e)
        return []
