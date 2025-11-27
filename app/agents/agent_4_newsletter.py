from datetime import datetime
from app.core.config import NEWSLETTER_HTML_PATH
from app.core.logging_utils import setup_logger

logger = setup_logger(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Flash AI – Newsletter</title>
<style>
body {{
  background: #f5f7fa;
  font-family: Arial, sans-serif;
}}
.container {{
  max-width: 700px;
  margin: auto;
  background: white;
  padding: 25px;
  border-radius: 14px;
  border: 1px solid #ddd;
}}
.article {{
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}}
.title {{
  font-size: 18px;
  font-weight: bold;
}}
.source {{
  font-size: 12px;
  color: #777;
}}
.resume {{
  margin-top: 6px;
  font-size: 14px;
}}
.blog {{
  margin-top: 25px;
  padding: 15px;
  background: #eef5ff;
  border-radius: 10px;
  text-align: center;
}}
.blog a {{
  color: #0056d6;
  font-weight: bold;
}}
</style>
</head>
<body>
<div class="container">

<h2>🔥 Flash AI – Top 3 du jour</h2>
<p>Veille générée automatiquement – {date}</p>

{articles_html}

<div class="blog">
➡️ <a target="_blank" href="{blog_url}">Lire toute la veille sur le blog</a>
</div>

</div>
</body>
</html>
"""

def generer_newsletter(enriched, indices_top3, index_audio, blog_url):
    articles_html = ""

    for idx in indices_top3:
        a = enriched[idx]
        articles_html += f"""
        <div class="article">
            <div class="title">{a['titre']}</div>
            <div class="source">{a.get('source','')}</div>
            <div class="resume">{a.get('resume','')}</div>
            <a target="_blank" href="{a['url']}">Lire l'article complet</a>
        </div>
        """

    html = TEMPLATE.format(
        date=datetime.now().strftime("%d/%m/%Y"),
        articles_html=articles_html,
        blog_url=blog_url,
    )

    NEWSLETTER_HTML_PATH.write_text(html, encoding="utf-8")
    logger.info("✔ Newsletter générée → %s", NEWSLETTER_HTML_PATH)
