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


# Flux RSS organisés par domaine

RSS_SOURCES_BY_DOMAIN = {
    "ia_generale": [
        "https://export.arxiv.org/rss/cs.AI",
        "https://export.arxiv.org/rss/cs.LG",
        "https://feeds.feedburner.com/venturebeat/SZYF",
        "https://www.lemondeinformatique.fr/flux-rss/thematique/ia/",
        "https://www.technologyreview.com/feed/",
        "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
        "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
        "https://www.01net.com/feed/",
    ],
    "ml": [
        "https://export.arxiv.org/rss/cs.LG",
        "https://export.arxiv.org/rss/stat.ML",
        "https://machinelearningmastery.com/blog/feed/",
        "https://www.datasciencecentral.com/main/feed",
        "https://www.kdnuggets.com/feed",
    ],
    "nlp": [
        "https://export.arxiv.org/rss/cs.CL",
        "https://nlp.stanford.edu/rss.xml",
        "https://towardsdatascience.com/tagged/nlp/rss",
    ],
    "computer_vision": [
        "https://export.arxiv.org/rss/cs.CV",
        "https://www.computervision.news/rss.xml",
        "https://www.analyticsvidhya.com/blog/category/computer-vision/feed/",
    ],
    "robotique": [
        "https://export.arxiv.org/rss/cs.RO",
        "https://spectrum.ieee.org/rss/robotics/fulltext",
        "https://www.roboticsbusinessreview.com/feed/",
    ],
    "security": [
        "https://export.arxiv.org/rss/cs.CR",
        "https://www.zdnet.com/topic/security/rss.xml",
        "https://www.lemondeinformatique.fr/flux-rss/thematique/securite/",
        "https://www.securityweek.com/rss",
    ],
    "data_science": [
        "https://export.arxiv.org/rss/cs.LG",
        "https://export.arxiv.org/rss/stat.ML",
        "https://www.datasciencecentral.com/main/feed",
        "https://www.kdnuggets.com/feed",
        "https://www.analyticsvidhya.com/blog/feed/",
    ],
    "business": [
        "https://www.lesechos.fr/rss/rss_tech.xml",
        "https://www.forbes.com/technology/feed/",
        "https://www.bloomberg.com/feed/podcast/etf-report.xml",
        "https://www.businessinsider.fr/rss",
    ],
    "mode": [
        "https://www.vogue.fr/rss.xml",
        "https://www.elle.fr/Mode/Mode-Actu/rss",
        "https://www.fashionnetwork.com/rss_fr/news.xml",
        "https://www.lofficiel.com/rss.xml",
    ],
    "actualites": [
        "https://www.lemonde.fr/rss/une.xml",
        "https://www.francetvinfo.fr/titres.rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://www.bbc.co.uk/news/10628494",
        "https://www.courrierinternational.com/feed/all.xml",
    ],
    "tech": [
        "https://www.clubic.com/feed/news.rss",
        "https://www.zdnet.fr/feeds/rss/zdnet_rss.xml",
        "https://www.01net.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
    ],
}

# Domaines disponibles
AVAILABLE_DOMAINS = list(RSS_SOURCES_BY_DOMAIN.keys())

# Par défaut, si aucun domaine spécifié, on retourne tous les flux
RSS_SOURCES = [
    url for domain_urls in RSS_SOURCES_BY_DOMAIN.values()
    for url in domain_urls
]


def fetch_rss(url: str, timeout: int = 10) -> List[ArticleBrut]:
    try:
        # Parse with timeout to avoid hanging
        import socket
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        feed = feedparser.parse(url)
        socket.setdefaulttimeout(original_timeout)
    except Exception as e:
        print(f"Timeout/error fetching {url}: {e}")
        return []
    
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


def fetch_all_articles(domain: Optional[str] = None, limit: int = 50) -> List[ArticleBrut]:
    """
    Récupère tous les articles de toutes les sources RSS définies.
    
    Args:
        domain: Domaine optionnel ("ia_generale", "ml", "nlp", "computer_vision", "robotique", "security", "data_science").
                Si None, retourne tous les articles.
        limit: Nombre maximum d'articles à retourner. Default: 50.
    
    Returns:
        Liste d'ArticleBrut, limité à `limit` articles.
    """
    all_articles: List[ArticleBrut] = []
    
    # Déterminer les sources à fetcher et récupérer les articles
    # Cas 1: domaine correspond à une clé connue (ex: 'ml', 'nlp') -> on ne fetch que ces sources
    if domain and domain in RSS_SOURCES_BY_DOMAIN:
        sources = RSS_SOURCES_BY_DOMAIN[domain]
        for url in sources:
            try:
                articles = fetch_rss(url, timeout=10)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Erreur lors de la récupération du flux {url}: {e}")

        # Trier par date décroissante et limiter
        all_articles.sort(
            key=lambda a: a.published_at if a.published_at else datetime.min,
            reverse=True
        )
        return all_articles[:limit]

    # Cas 2: domaine non fourni ou texte libre -> on fetch toutes les sources
    sources = RSS_SOURCES
    for url in sources:
        try:
            articles = fetch_rss(url, timeout=10)
            all_articles.extend(articles)
        except Exception as e:
            print(f"Erreur lors de la récupération du flux {url}: {e}")

    # Si l'utilisateur a fourni un texte libre (mot-clé), on filtre les articles
    if domain and domain.strip():
        keyword = domain.lower().strip()

        def matches_keyword(article: ArticleBrut) -> bool:
            fields = [article.title or "", article.summary or "", article.raw_content or ""]
            for f in fields:
                if keyword in f.lower():
                    return True
            return False

        filtered = [a for a in all_articles if matches_keyword(a)]

        # Si aucun résultat trouvé, on garde l'ensemble (fallback), sinon on utilise filtré
        all_articles = filtered if filtered else all_articles

    # Dédupliquer par lien (pour éviter doublons provenant de plusieurs sources)
    unique = {}
    for art in all_articles:
        if art.link:
            unique[art.link] = art
        else:
            # fallback: basé sur titre si pas de lien
            unique[f"title::{art.title}"] = art

    all_articles = list(unique.values())

    # Trier par date décroissante et limiter
    all_articles.sort(
        key=lambda a: a.published_at if a.published_at else datetime.min,
        reverse=True
    )

    return all_articles[:limit]
