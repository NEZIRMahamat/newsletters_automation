from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional

from agents.rss_reader import fetch_all_articles, ArticleBrut, AVAILABLE_DOMAINS
from agents.llm_groq import enrich_article_with_groq, ArticleEnrichi
from config.settings import settings
from agents.newsletter_config_agent import NewsletterConfigAgent

app = FastAPI()

# Variables globales pour user_id simple (peut être remplacé par authentification)
CURRENT_USER_ID = "default"


@app.get("/")
def read_root():
    """Redirige vers la page de configuration"""
    return RedirectResponse(url="/config-page", status_code=302)


# ==================== Endpoints UI Pages ====================

@app.get("/config-page", response_class=HTMLResponse)
def serve_config_page():
    """Serve la page de configuration (Page 1)"""
    return load_html_template("config.html")


@app.get("/newsletter", response_class=HTMLResponse)
def serve_newsletter_page():
    """Serve la page de newsletter avec articles (Page 2)"""
    return load_html_template("newsletter.html")


# ==================== Endpoints RSS ====================

@app.get("/rss-test", response_model=List[ArticleBrut])
def read_rss_articles(domain: Optional[str] = None, limit: int = 10):
    """
    Endpoint de test pour voir les articles bruts récupérés depuis les flux RSS IA.
    
    Params:
    - domain: Domaine optionnel ("ia_generale", "ml", "nlp", etc.)
    - limit: Nombre d'articles (1-50)
    """
    articles = fetch_all_articles(domain=domain, limit=limit)
    return articles


@app.get("/rss-enriched-test", response_model=List[ArticleEnrichi])
def read_enriched_articles(domain: Optional[str] = None, limit: int = 5):
    """
    Endpoint de test pour voir les articles enrichis par Groq (résumé + tags + classification).
    On limite à quelques articles pour les tests.
    """
    articles = fetch_all_articles(domain=domain, limit=limit)
    selected = articles[:limit]

    enriched: List[ArticleEnrichi] = []
    for art in selected:
        try:
            enriched_article = enrich_article_with_groq(art)
            enriched.append(enriched_article)
        except Exception as e:
            print("Erreur lors de l'enrichissement d'un article:", e)

    return enriched


# ==================== Endpoints Configuration Newsletter ====================

@app.get("/api/domains")
def get_available_domains():
    """Retourne la liste des domaines disponibles."""
    return {"domains": AVAILABLE_DOMAINS}


@app.get("/api/config")
def get_user_config():
    """Récupère la configuration actuelle de l'utilisateur."""
    agent = NewsletterConfigAgent(CURRENT_USER_ID)
    config = agent.get_config()
    return config.model_dump()


@app.post("/api/config")
def update_user_config(
    domain: Optional[str] = Query(None),
    num_articles: Optional[int] = Query(None),
    frequency: Optional[str] = Query(None),
    use_llm: Optional[bool] = Query(None),
):
    """
    Met à jour la configuration de l'utilisateur.
    
    Params:
    - domain: "ia_generale", "ml", "nlp", "computer_vision", "robotique", "security", "data_science"
    - num_articles: 1-50
    - frequency: "daily", "weekly", "monthly"
    """
    agent = NewsletterConfigAgent(CURRENT_USER_ID)
    try:
        updated_config = agent.update_config(
            domain=domain,
            num_articles=num_articles,
            frequency=frequency
            , use_llm=use_llm
        )
        return {"success": True, "config": updated_config.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/articles", response_model=List[ArticleEnrichi])
def get_articles_for_user(enrich: bool = True):
    """
    Récupère les articles selon la configuration de l'utilisateur.
    
    Params:
    - enrich: Si True, enrichit les articles avec Groq.
    """
    agent = NewsletterConfigAgent(CURRENT_USER_ID)
    articles = agent.get_articles(enrich=enrich)
    return articles


@app.get("/api/articles-html", response_class=HTMLResponse)
def get_articles_html_for_htmx(enrich: bool = True):
    """
    Retourne les articles au format HTML pour HTMX.
    Utilisé par la page newsletter pour afficher les articles.
    """
    agent = NewsletterConfigAgent(CURRENT_USER_ID)
    articles = agent.get_articles(enrich=enrich)
    
    if not articles:
        return """
        <div class="empty">
            <div class="empty-icon">📭</div>
            <h2>Aucun article trouvé</h2>
            <p>Essayez de modifier vos paramètres et actualisez.</p>
        </div>
        """
    
    html = '<div class="articles-container">'
    for article in articles:
        if isinstance(article, ArticleEnrichi):
            html += render_article_card(article)
        else:
            html += render_article_card_raw(article)
    html += '</div>'
    
    return html


@app.get("/api/debug-articles")
def debug_articles(domain: Optional[str] = None):
    """Endpoint de debug pour comprendre le filtrage par mot-clé.
    Retourne le nombre total d'articles récupérés et combien correspondent au mot-clé.
    """
    # Récupérer un grand nombre d'articles depuis toutes les sources
    all_articles = fetch_all_articles(domain=None, limit=200)

    if not domain or not domain.strip():
        return {
            "domain": domain,
            "total_fetched": len(all_articles),
            "matched": None,
            "sample_titles": [a.title for a in all_articles[:10]],
            "llm_used": bool(settings.groq_api_key),
        }

    keyword = domain.lower().strip()
    matched = []
    for a in all_articles:
        fields = [a.title or "", a.summary or "", a.raw_content or ""]
        joined = "\n".join(fields).lower()
        if keyword in joined:
            matched.append(a)

    response = {
        "domain": domain,
        "total_fetched": len(all_articles),
        "matched": len(matched),
        "sample_matched_titles": [a.title for a in matched[:10]],
        "sample_other_titles": [a.title for a in all_articles[:10]],
        "llm_used": bool(settings.groq_api_key),
    }

    # If LLM enabled, return additional llm selection details
    if settings.groq_api_key:
        try:
            from agents.llm_groq import filter_articles_with_llm
            llm_selected = filter_articles_with_llm(all_articles, domain, max_results=20)
            response["llm_selected_count"] = len(llm_selected)
            response["llm_selected_titles"] = [a.title for a in llm_selected[:10]]
        except Exception as e:
            response["llm_error"] = str(e)

    return response


# ==================== Helper Functions ====================

def load_html_template(filename: str) -> str:
    """Charge un template HTML."""
    try:
        with open(f"ui/templates/{filename}", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Template not found</h1>"


def render_article_card(article: ArticleEnrichi) -> str:
    """Rend une carte d'article enrichi en HTML."""
    tags_html = " ".join([f"<span class='tag'>{tag}</span>" for tag in article.tags])
    
    return f"""
    <div class='article-card'>
        <h3><a href='{article.link}' target='_blank'>{article.title}</a></h3>
        <div class='meta'>
            <span class='source'>{article.source}</span>
            {f"<span class='date'>📅 {article.published_at}</span>" if article.published_at else ""}
        </div>
        <p class='short-summary'>{article.short_summary}</p>
        <details>
            <summary>Voir le résumé détaillé</summary>
            <p>{article.detailed_summary}</p>
        </details>
        {f"<div class='tags'>{tags_html}</div>" if article.tags else ""}
        <div class='score'>
            <span class='score-value'>⭐ {article.score_global}/100</span>
            <span class='score-details'>{article.score_details}</span>
        </div>
        <a href='{article.link}' target='_blank' class='read-more'>Lire l'article complet</a>
    </div>
    """


def render_article_card_raw(article: ArticleBrut) -> str:
    """Rend une carte d'article brut en HTML."""
    return f"""
    <div class='article-card'>
        <h3><a href='{article.link}' target='_blank'>{article.title}</a></h3>
        <div class='meta'>
            <span class='source'>{article.source}</span>
            {f"<span class='date'>📅 {article.published_at}</span>" if article.published_at else ""}
        </div>
        <p class='short-summary'>{article.summary or "Pas de résumé disponible"}</p>
        <a href='{article.link}' target='_blank' class='read-more'>Lire l'article complet</a>
    </div>
    """
