from pathlib import Path
from typing import List, Dict
from datetime import datetime

from app.core.logging_utils import setup_logger
from app.core.config import DATA_DIR

logger = setup_logger(__name__)

SITE_DIR = DATA_DIR / "site"
SITE_DIR.mkdir(exist_ok=True)


# ------------- TEMPLATE GÉNÉRAL -------------- #

BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<div class="navbar">
    <a href="index.html" class="logo">⚡ Flash AI</a>
    <div class="nav-links">
        {menu}
    </div>
</div>

<div class="content">
    {content}
</div>

<div class="footer">Site généré automatiquement – {date}</div>
</body>
</html>
"""


# ------------- PAGE ARTICLE -------------- #

ARTICLE_TEMPLATE = """
<h1 class="article-title">{titre}</h1>
<p class="article-meta">{theme} · {source} · {date_publication}</p>

{image}

<p class="article-resume">{resume}</p>

<p>
    <a href="{url}" target="_blank">📎 Lire l’article original</a>
</p>
"""


# ------------- PAGE THÈME -------------- #

THEME_TEMPLATE = """
<h2 class="theme-title">Thème : {theme}</h2>

<div class="article-grid">
{articles}
</div>
"""


# ------------- INDEX PAGE -------------- #

INDEX_TEMPLATE = """
<h1 class="home-title">🔥 Flash AI – Veille automatique</h1>
<p class="home-subtitle">Sélection IA & Tech enrichie par agents intelligents.</p>

<h2>Articles récents</h2>

<div class="article-grid">
{articles}
</div>
"""


# ------------- CARTE ARTICLE -------------- #

CARD_TEMPLATE = """
<a href="{page_name}">
<div class="card">
    {image}
    <h3>{titre}</h3>
    <p class="card-meta">{theme} · {source}</p>
    <p class="card-resume">{resume}</p>
</div>
</a>
"""


# ------------- CSS GÉNÉRÉ -------------- #

CSS_CONTENT = """
body {
    font-family: Arial, sans-serif;
    background: #f5f7fa;
    margin: 0; padding: 0;
}
.navbar {
    background: #111827;
    color: #f3f4f6;
    padding: 15px 25px;
    display: flex;
    justify-content: space-between;
}
.navbar .logo {
    font-size: 20px;
    color: #f3f4f6;
    text-decoration: none;
}
.nav-links a {
    color: #9ca3af;
    margin-left: 20px;
    text-decoration: none;
}
.content {
    padding: 25px;
    max-width: 960px;
    margin: 0 auto;
    background: white;
}
.footer {
    text-align: center;
    padding: 15px;
    margin-top: 30px;
    background: #e5e7eb;
}
.card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px;
}
.card img {
    max-width: 100%;
    border-radius: 6px;
}
.article-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 15px;
}
.article-title {
    font-size: 30px;
}
.article-meta {
    color: #6b7280;
}
"""


# ------------- BUILD SITE -------------- #

def build_static_site(articles: List[Dict], indices: List[int]):
    logger.info("📦 Génération du site statique…")

    # 1) Écrire CSS
    (SITE_DIR / "styles.css").write_text(CSS_CONTENT, encoding="utf-8")

    # 2) Pages par article
    menu_html = ""
    themes = {}

    for idx in indices:
        a = articles[idx]
        theme = a.get("theme", "Autres")
        themes.setdefault(theme, []).append(idx)

        img_html = f'<img src="{a["image"]}" />' if a.get("image") else ""

        page_name = f"article_{idx}.html"
        page_html = BASE_TEMPLATE.format(
            title=a["titre"],
            menu="",  # sera rempli plus tard
            date=datetime.now().strftime("%d/%m/%Y"),
            content=ARTICLE_TEMPLATE.format(
                titre=a["titre"],
                theme=a.get("theme", ""),
                source=a.get("source", ""),
                resume=a.get("resume", ""),
                date_publication=a.get("date_publication", ""),
                url=a.get("url", ""),
                image=img_html
            )
        )

        (SITE_DIR / page_name).write_text(page_html, encoding="utf-8")

    # 3) Pages par thème
    for theme, idxs in themes.items():
        cards = []

        for idx in idxs:
            a = articles[idx]
            page_name = f"article_{idx}.html"
            img_html = f'<img src="{a["image"]}" />' if a.get("image") else ""

            cards.append(CARD_TEMPLATE.format(
                titre=a["titre"],
                theme=a.get("theme", ""),
                source=a.get("source", ""),
                resume=a.get("resume", "")[:140] + "...",
                image=img_html,
                page_name=page_name
            ))

        theme_page = BASE_TEMPLATE.format(
            title=f"Thème : {theme}",
            menu="",
            date=datetime.now().strftime("%d/%m/%Y"),
            content=THEME_TEMPLATE.format(
                theme=theme,
                articles="\n".join(cards)
            )
        )

        page_name = f"theme_{theme.replace(' ','_')}.html"
        (SITE_DIR / page_name).write_text(theme_page, encoding="utf-8")

    # 4) Page d’accueil
    cards = []

    for idx in indices:
        a = articles[idx]
        img_html = f'<img src="{a["image"]}" />' if a.get("image") else ""
        page_name = f"article_{idx}.html"

        cards.append(CARD_TEMPLATE.format(
            titre=a["titre"],
            theme=a.get("theme", ""),
            source=a.get("source", ""),
            resume=a.get("resume", "")[:140] + "...",
            image=img_html,
            page_name=page_name
        ))

    index_html = BASE_TEMPLATE.format(
        title="Flash AI – Accueil",
        menu="",
        date=datetime.now().strftime("%d/%m/%Y"),
        content=INDEX_TEMPLATE.format(articles="\n".join(cards))
    )

    (SITE_DIR / "index.html").write_text(index_html, encoding="utf-8")

    logger.info("🎉 Site statique généré → %s", SITE_DIR)
