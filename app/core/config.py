import os
from pathlib import Path
from dotenv import load_dotenv
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

load_dotenv(BASE_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "True") == "True"
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ➕ URL publique du blog (pour le lien dans la newsletter)
BLOG_PUBLIC_URL = os.getenv("BLOG_PUBLIC_URL", "")

RAW_PATH = DATA_DIR / "raw_articles.json"
ENRICHED_PATH = DATA_DIR / "articles_enrichis.json"
SELECTION_PATH = DATA_DIR / "selection.json"
NEWSLETTER_HTML_PATH = DATA_DIR / "newsletter.html"
AUDIO_PATH = DATA_DIR / "capsule.mp3"
BLOG_HTML_PATH = DATA_DIR / "blog.html"
EMAIL_DRAFT_PATH = DATA_DIR / "email_draft.txt"

# Dossier site statique
SITE_DIR = DATA_DIR / "site"
SITE_DIR.mkdir(exist_ok=True, parents=True)

RSS_FEEDS = {
    "actualité": [
        "https://www.lemonde.fr/rss/une.xml",
        "http://feeds.bbci.co.uk/news/rss.xml",
        "http://rss.cnn.com/rss/edition.rss",
        "https://www.france24.com/fr/actualites/rss",
        "https://www.reuters.com/news/world/rss",
    ],
    "politique": [
        "https://www.lemonde.fr/politique/rss.xml",
        "https://www.france24.com/fr/politique/rss",
        "https://www.reuters.com/politics/rss",
    ],
    "international": [
        "https://www.theguardian.com/world/rss",
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.france24.com/fr/monde/rss",
        "https://www.reuters.com/world/rss",
    ],
    "usa": [
        "https://www.reuters.com/world/us/rss",
        "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
        "http://rss.cnn.com/rss/edition_us.rss",
    ],
    "intelligence artificielle": [
        "https://openai.com/blog/rss.xml",
        "https://ai.googleblog.com/atom.xml",
        "https://www.technologyreview.com/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://www.semianalysis.com/feed",
        "https://www.nvidia.com/en-us/research/feed/",
    ],
    "technologie": [
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed",
        "https://www.technologyreview.com/feed/",
        "https://www.theguardian.com/uk/technology/rss",
    ],
    "jeux vidéo": [
        "https://www.jeuxvideo.com/rss/rss.xml",
        "https://www.ign.com/rss",
        "https://kotaku.com/rss",
        "https://www.pcgamer.com/rss/",
    ],
    "crypto": [
        "https://cointelegraph.com/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://decrypt.co/feed",
    ],
    "économie": [
        "https://www.lemonde.fr/economie/rss.xml",
        "https://www.reuters.com/finance/rss",
    ],
    "finance": [
        "https://www.boursorama.com/breves/feed/",
        "https://www.reuters.com/markets/rss",
    ],
    "aviation": [
        "https://simpleflying.com/feed/",
        "https://www.journal-aviation.com/rss/actualites.xml",
        "https://airinsight.com/feed/",
    ],
    "urbanisme": [
        "https://www.urbanews.fr/feed/",
        "https://www.lemoniteur.fr/rss/amenagement-urbanisme",
    ],
    "immobilier": [
        "https://www.businessimmo.com/rss",
        "https://www.batiactu.com/rss/",
        "https://www.lemonde.fr/immobilier/rss.xml",
    ],
    "environnement": [
        "https://www.lemonde.fr/planete/rss.xml",
        "https://www.france24.com/fr/environnement/rss",
        "https://www.sciencedaily.com/rss/earth_climate.xml",
    ],
    "sport": [
        "https://www.lequipe.fr/rss/actu_rss.xml",
        "https://www.france24.com/fr/sports/rss",
        "https://www.eurosport.fr/rss.xml",
    ],
    "culture": [
        "https://www.telerama.fr/rss.xml",
        "https://www.france24.com/fr/culture/rss",
    ],
    "people": [
        "https://www.voici.fr/rss",
        "https://www.gala.fr/feed",
    ],
}
