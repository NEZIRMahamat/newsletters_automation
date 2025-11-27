from typing import List, Dict
from datetime import datetime
import base64

from app.core.config import BLOG_HTML_PATH, AUDIO_PATH
from app.core.logging_utils import setup_logger

logger = setup_logger(__name__)


BLOG_TEMPLATE = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Flash AI – Veille IA</title>
<style>
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #020617;
  color: #e5e7eb;
  margin: 0;
}}
a {{ color: inherit; text-decoration: none; }}
.container {{
  max-width: 1120px;
  margin: 0 auto;
  padding: 32px 16px 48px 16px;
}}
.header {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 24px;
}}
.logo {{
  font-size: 26px;
  font-weight: 900;
}}
.date {{
  font-size: 13px;
  color: #9ca3af;
}}
.section-title {{
  font-size: 20px;
  font-weight: 700;
  margin: 32px 0 12px 0;
}}
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}}
.card {{
  background: #020617;
  border-radius: 14px;
  padding: 12px;
  border: 1px solid #1f2937;
  box-shadow: 0 10px 25px rgba(15,23,42,0.6);
}}
.card img {{
  width: 100%;
  max-height: 170px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 8px;
}}
.card-title {{
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}}
.card-meta {{
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 6px;
}}
.card-resume {{
  font-size: 13px;
  color: #d1d5db;
  margin-bottom: 8px;
}}
.more-link {{
  font-size: 13px;
  color: #60a5fa;
}}
.audio-block {{
  background: #020617;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid #1f2937;
  margin-bottom: 28px;
}}
.audio-title {{
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 4px;
}}
.audio-sub {{
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 8px;
}}
.audio-block audio {{
  width: 100%;
}}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">⚡ Flash AI</div>
    <div class="date">Veille du {date}</div>
  </div>

  {audio_block}

  {content}
</div>
</body>
</html>
"""


def _audio_block() -> str:
    """Intègre la capsule audio si elle existe."""
    if not AUDIO_PATH.exists():
        return ""
    try:
        data = AUDIO_PATH.read_bytes()
        b64 = base64.b64encode(data).decode("ascii")
        return f"""
        <div class="audio-block">
          <div class="audio-title">🎧 Capsule audio de la semaine</div>
          <div class="audio-sub">Résumé oral de l'information principale en IA.</div>
          <audio controls>
            <source src="data:audio/mpeg;base64,{b64}" type="audio/mpeg">
          </audio>
        </div>
        """
    except Exception as e:
        logger.error("Erreur intégration audio dans le blog : %s", e)
        return ""


def _label_soustheme(st: str) -> str:
    """Nettoie les noms de sous-thèmes pour les titres de section."""
    if not st:
        return "IA – Divers"
    st_low = st.lower()
    mapping = {
        "llm": "LLM & modèles de langage",
        "machine learning": "Machine learning",
        "deep learning": "Deep learning",
        "nlp": "NLP & langage",
        "vision": "Vision par ordinateur",
        "robotique": "Robotique & IA embarquée",
        "cloud ai": "Cloud & plateformes IA",
        "sécurité ia": "Sécurité, risques & IA safety",
        "chips": "Chips & hardware IA",
        "chips & hardware ia": "Chips & hardware IA",
        "recherche ia": "Recherche & papiers IA",
        "produits ia": "Produits & fonctionnalités IA",
        "ia générative": "IA générative (texte, image, vidéo)",
        "ia & société": "IA & société",
    }
    for key, label in mapping.items():
        if key in st_low:
            return label
    return st  # fallback brut


def generer_blog(articles: List[Dict], indices_selection: List[int], index_audio: int):
    """
    Génère le blog complet :
    - groupement par sous-thème IA
    - tri par importance
    - images conservées
    - cartes propres
    """

    if not articles:
        logger.warning("Aucun article pour générer le blog.")
        return

    # On travaille sur tous les articles enrichis, pas seulement la sélection,
    # mais tu peux aussi limiter à indices_selection si tu veux.
    dedup = {}
    for art in articles:
        key = art.get("url")
        if key and key not in dedup:
            dedup[key] = art

    # Regrouper par sous-thème
    grouped = {}
    for art in dedup.values():
        st = art.get("sous_theme") or "IA – Divers"
        label = _label_soustheme(st)
        grouped.setdefault(label, []).append(art)

    # Tri interne par importance décroissante
    for label, lst in grouped.items():
        grouped[label] = sorted(lst, key=lambda a: a.get("importance", 3), reverse=True)

    sections_html = []

    for label, lst in grouped.items():
        cards = []
        for a in lst:
            img_html = ""
            if a.get("image"):
                img_html = f'<img src="{a["image"]}" alt="visuel article" />'

            meta = a.get("source", "")
            resume = (a.get("resume") or "").strip()
            if len(resume) > 600:
                resume = resume[:600] + "…"

            cards.append(
                f"""
                <a href="{a['url']}" target="_blank">
                  <div class="card">
                    {img_html}
                    <div class="card-title">{a['titre']}</div>
                    <div class="card-meta">{meta}</div>
                    <div class="card-resume">{resume}</div>
                    <div class="more-link">Lire l'article d'origine</div>
                  </div>
                </a>
                """
            )

        sections_html.append(
            f"""
            <div class="section">
              <div class="section-title">{label}</div>
              <div class="grid">
                {''.join(cards)}
              </div>
            </div>
            """
        )

    html = BLOG_TEMPLATE.format(
        date=datetime.now().strftime("%d/%m/%Y"),
        audio_block=_audio_block(),
        content="\n".join(sections_html),
    )

    BLOG_HTML_PATH.write_text(html, encoding="utf-8")
    logger.info("✔ Blog HTML généré → %s", BLOG_HTML_PATH)
