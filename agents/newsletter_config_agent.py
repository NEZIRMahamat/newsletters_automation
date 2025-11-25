"""
Agent de configuration de la newsletter.
Permet de gérer les préférences utilisateur (domaine, fréquence, nb articles).
"""

from typing import List, Optional, Union
from pydantic import BaseModel

from db.newsletter_config import load_config, update_config, DEFAULT_CONFIG
from agents.rss_reader import AVAILABLE_DOMAINS, fetch_all_articles, ArticleBrut
from agents.llm_groq import enrich_article_with_groq, ArticleEnrichi, filter_articles_with_llm


class NewsletterConfig(BaseModel):
    """Configuration de la newsletter utilisateur."""
    domain: str  # "ia_generale", "ml", "nlp", etc.
    num_articles: int  # Nombre d'articles (1-50)
    frequency: str  # "daily", "weekly", "monthly"
    last_sent: Optional[str] = None
    use_llm: bool = True


class NewsletterConfigAgent:
    """Agent pour gérer la configuration de la newsletter."""
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
    
    def get_config(self) -> NewsletterConfig:
        """Récupère la configuration actuelle."""
        config_dict = load_config(self.user_id)
        return NewsletterConfig(**config_dict)
    
    def update_config(self, 
                      domain: Optional[str] = None,
                      num_articles: Optional[int] = None,
                      frequency: Optional[str] = None,
                      use_llm: Optional[bool] = None) -> NewsletterConfig:
        """Met à jour la configuration."""
        updates = {}
        
        # Accepter un domaine texte libre (pas de validation stricte)
        if domain is not None:
            domain = domain.strip()
            if not domain:
                raise ValueError("Le domaine ne peut pas être vide")
            updates["domain"] = domain
        
        # Valider le nombre d'articles
        if num_articles is not None:
            if not (1 <= num_articles <= 50):
                raise ValueError("Nombre d'articles doit être entre 1 et 50")
            updates["num_articles"] = num_articles
        
        # Valider la fréquence
        if frequency is not None:
            if frequency not in ["daily", "weekly", "monthly"]:
                raise ValueError("Fréquence doit être 'daily', 'weekly' ou 'monthly'")
            updates["frequency"] = frequency

        # Valider use_llm si présent
        if use_llm is not None:
            updates["use_llm"] = bool(use_llm)
        
        config_dict = update_config(updates, self.user_id)
        return NewsletterConfig(**config_dict)
    
    def get_articles(self, enrich: bool = False) -> List[Union[ArticleBrut, ArticleEnrichi]]:
        """
        Récupère les articles selon la config actuelle.
        
        Args:
            enrich: Si True, enrichit les articles avec Groq.
        
        Returns:
            Liste d'articles bruts ou enrichis.
        """
        config = self.get_config()
        articles = fetch_all_articles(domain=None if config.domain and config.domain not in AVAILABLE_DOMAINS else config.domain, limit=200)

        # Si domaine saisi est texte libre (non dans AVAILABLE_DOMAINS), on fait un filtrage sémantique LLM
        if config.domain and config.domain not in AVAILABLE_DOMAINS and config.use_llm:
            try:
                # filter_articles_with_llm renvoie une sous-liste
                filtered = filter_articles_with_llm(articles, config.domain, max_results=config.num_articles)
                print(f"LLM selection used for domain='{config.domain}'; initial={len(articles)} selected={len(filtered)}")
                articles = filtered
            except Exception as e:
                print("Erreur filtrage LLM, fallback au filtrage classique:", e)
                # fallback: keyword filter via existing fetch
                keyword = config.domain.lower()
                articles = [a for a in articles if keyword in (a.title or "").lower() or keyword in (a.summary or "").lower()][:config.num_articles]
        else:
            # Limit by config.num_articles
            articles = articles[:config.num_articles]
        
        if not enrich:
            return articles
        
        # Enrichir avec Groq
        enriched = []
        for art in articles:
            try:
                enriched_article = enrich_article_with_groq(art)
                enriched.append(enriched_article)
            except Exception as e:
                print(f"Erreur lors de l'enrichissement de {art.title}: {e}")
        
        return enriched
    
    @staticmethod
    def get_available_domains() -> List[str]:
        """Retourne la liste des domaines disponibles."""
        return AVAILABLE_DOMAINS
    
    @staticmethod
    def get_default_config() -> NewsletterConfig:
        """Retourne la configuration par défaut."""
        return NewsletterConfig(**DEFAULT_CONFIG)
