from app.agents.agent_1_collector import collecter_news
from app.agents.agent_2_analysis import analyser_articles
from app.agents.agent_3_curator import choisir_selection
from app.agents.agent_4_newsletter import generer_newsletter
from app.agents.agent_4_blog import generer_blog
from app.agents.agent_5_audio import generer_script_audio, generer_audio
from app.agents.agent_6_email import generer_email_top3
from app.agents.agent_7_static_site import build_static_site

from app.core.user_config import load_user_config
from app.core.config import BLOG_PUBLIC_URL
from app.core.logging_utils import setup_logger

logger = setup_logger("pipeline")

def pipeline_hebdomadaire(max_par_flux=20):
    logger.info("🚀 Début pipeline…")

    config = load_user_config()
    themes = config.get("themes_actifs", [])

    # 1) Collecte
    raw = collecter_news(themes, max_par_flux=max_par_flux)
    if not raw:
        logger.warning("❌ Aucun article collecté")
        return

    # 2) Analyse
    enriched = analyser_articles(raw)

    # 3) Sélection IA
    sel = choisir_selection(enriched)
    indices = sel["indices_selection"]
    idx_audio = sel["index_audio"]
    top3 = indices[:3]

    # 4) Génération audio
    script = generer_script_audio(enriched[idx_audio])
    generer_audio(script)

    # 5) Newsletter (avec blog_url obligatoire)
    generer_newsletter(enriched, top3, idx_audio, blog_url=BLOG_PUBLIC_URL)

    # 6) Blog
    generer_blog(enriched, indices, idx_audio)

    # 7) Email réel
    generer_email_top3(enriched, top3, idx_audio)

    # 8) Site statique
    build_static_site(enriched, indices)

    logger.info("🎉 Pipeline terminée")
