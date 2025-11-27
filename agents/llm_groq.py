import json
from typing import List, Optional
import difflib
import time

from pydantic import BaseModel, ValidationError
from groq import Groq
import httpx

from config.settings import settings
from agents.rss_reader import ArticleBrut


# Modèle de sortie enrichie (Agent 2 + Agent 3 fusionnés)
class ArticleEnrichi(BaseModel):
    source: str
    title: str
    link: str
    published_at: Optional[str] = None

    short_summary: str
    detailed_summary: str
    tags: List[str]
    type_contenu: str  # "news" | "recherche" | "tuto" | "produit" | "opinion"
    audience: str      # "débutant" | "intermédiaire" | "expert"

    # Partie scoring (ex-Agent 3)
    score_global: int          # 0 à 100
    score_details: str         # explication courte de la note


# Client Groq global avec timeout
try:
    client = Groq(
        api_key=settings.groq_api_key,
        timeout=httpx.Timeout(30.0, connect=10.0)
    )
except Exception as e:
    print(f"Erreur initialisation client Groq: {e}")
    client = None


def enrich_article_with_groq(article: ArticleBrut, max_retries: int = 2) -> ArticleEnrichi:
    """
    Appelle Groq pour :
      - résumer l'article (court + long)
      - générer des tags
      - classifier le type de contenu
      - évaluer l'audience cible
      - calculer un score global de pertinence (0-100)
    Retourne un ArticleEnrichi.
    """
    if not client or not settings.groq_api_key:
        raise Exception("Client Groq non initialisé ou clé API manquante")

    # On construit le contexte texte qu'on envoie au modèle
    base_text = f"Titre: {article.title}\n\n"
    if article.summary:
        base_text += f"Résumé RSS: {article.summary}\n\n"
    if article.raw_content:
        # Limiter le contenu brut pour éviter les timeouts
        content = article.raw_content[:2000] if len(article.raw_content) > 2000 else article.raw_content
        base_text += f"Contenu brut: {content}\n\n"

    system_prompt = (
        "Tu es un assistant expert en intelligence artificielle. "
        "On te donne un article (titre + résumé + contenu) lié à l'IA. "
        "Tu dois produire un objet JSON STRICT avec les clés suivantes :\n"
        "- short_summary : résumé très court (3 phrases max) en français\n"
        "- detailed_summary : résumé détaillé (10-15 lignes) en français\n"
        "- tags : liste de 3 à 8 mots-clés en français\n"
        "- type_contenu : une valeur parmi [\"news\", \"recherche\", \"tuto\", \"produit\", \"opinion\"]\n"
        "- audience : une valeur parmi [\"débutant\", \"intermédiaire\", \"expert\"]\n"
        "- score_global : entier entre 0 et 100 qui mesure l'intérêt de l'article pour une newsletter hebdomadaire sur l'IA "
        "(qualité, fraîcheur, pertinence, utilité pour des équipes en entreprise)\n"
        "- score_details : courte explication (2 à 4 phrases) de la note donnée\n\n"
        "IMPORTANT : réponds STRICTEMENT en JSON valide, sans texte avant ou après."
    )

    # Retry logic
    last_error = None
    for attempt in range(max_retries):
        try:
            # Appel Groq (modèle à jour)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": base_text},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                timeout=30.0
            )
            break  # Si succès, sortir de la boucle
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Backoff: 2s, 4s
                print(f"Erreur Groq (tentative {attempt + 1}/{max_retries}): {e}. Retry dans {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise Exception(f"Échec après {max_retries} tentatives: {last_error}")

    raw_content = completion.choices[0].message.content

    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError as e:
        print("Erreur de parsing JSON depuis Groq:", e)
        print("Contenu brut reçu :", raw_content)
        raise

    try:
        article_enrichi = ArticleEnrichi(
            source=article.source,
            title=article.title,
            link=article.link,
            published_at=article.published_at.isoformat() if article.published_at else None,
            short_summary=data.get("short_summary", ""),
            detailed_summary=data.get("detailed_summary", ""),
            tags=data.get("tags", []),
            type_contenu=data.get("type_contenu", "news"),
            audience=data.get("audience", "débutant"),
            score_global=int(data.get("score_global", 0)),
            score_details=data.get("score_details", ""),
        )
    except ValidationError as e:
        print("Erreur de validation Pydantic ArticleEnrichi:", e)
        print("Données JSON:", data)
        raise

    return article_enrichi


def filter_articles_with_llm(articles: List[ArticleBrut], user_query: str, max_results: int = 10, min_score: int = 30) -> List[ArticleBrut]:
    """
    Utilise le LLM pour sélectionner les articles les plus pertinents selon le domaine/mot-clé saisi par l'utilisateur.
    Retourne une liste d'ArticleBrut (max_results).
    Si l'API Groq n'est pas configurée, on retourne un fallback (premiers articles).
    """
    # Guard: si pas de clé Groq, fallback
    if not settings.groq_api_key:
        return articles[:max_results]

    if not articles or not user_query:
        return articles[:max_results]

    # On prend seulement les premiers 40 articles pour limiter la taille du prompt
    sample_articles = articles[:40]

    # Préparer le texte des articles (titre + résumé court)
    articles_text = "\n".join([
        f"- Titre: {a.title}\nRésumé: {a.summary or ''}" for a in sample_articles
    ])

    # On numérote les articles et prépare un prompt demandant un JSON d'indices/score
    enumerated = []
    for i, a in enumerate(sample_articles):
        enumerated.append(f"INDEX: {i}\nTitre: {a.title}\nRésumé: {a.summary or ''}\n")
    enumerated_text = "\n".join(enumerated)

    prompt = f"""
Tu es un assistant expert en sélection d'articles. On te donne une liste d'articles (INDEX, titre + résumé) et un sujet.
Ta tâche : pour le sujet donné, renvoyer un objet JSON array contenant les articles pertinents. Chaque élément doit être de la forme : {"index": <INDEX>, "score": <SCORE>}.
Score : entier entre 0 (pas pertinent) et 100 (très pertinent).
Retourne uniquement un JSON array (ex: [{"index": 0, "score": 90}, {"index": 4, "score": 75}]) trié par score décroissant.
Sujet: {user_query}

Liste d'articles:
{enumerated_text}

Règles :
- Ne renvoie que du JSON valide. Pas d'explication textuelle.
- Ne retourne que les articles pertinents ; si ton score est < {min_score} considère-le comme non pertinent.
- Si tu ne trouves rien, retourne un tableau vide []
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un assistant qui sélectionne les articles les plus pertinents pour un sujet donné."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=512,
        )

        raw_content = completion.choices[0].message.content
        try:
            json_data = json.loads(raw_content)
        except Exception:
            # Si JSON non valide, tenter fallback sur matching par mot clé
            json_data = None

        matched = []
        if json_data and isinstance(json_data, list):
            # json_data should be a list of objects with 'index' and 'score'
            indices = []
            for el in json_data:
                if isinstance(el, dict) and 'index' in el:
                    try:
                        idx = int(el['index'])
                        score = int(el.get('score', 0))
                        if 0 <= idx < len(sample_articles):
                            if score >= min_score:
                                indices.append((idx, score))
                    except Exception:
                        continue
            # Sort by score desc, take max_results
            indices.sort(key=lambda x: x[1], reverse=True)
            chosen = [sample_articles[i] for i, s in indices[:max_results]]
            matched = chosen
            # Logging
            print(f"LLM selection JSON indices: {indices}")
        else:
            # Fallback behavior: perform fuzzy/substring matching on titles
            raw = completion.choices[0].message.content.strip()
            # old behavior: try to parse possibly titles separated by ';'
            titles = [t.strip() for t in raw.split(';') if t.strip()]
            for a in sample_articles:
                atitle = a.title.strip().lower()
                for t in titles:
                    tnorm = t.strip().lower()
                    if tnorm == atitle or tnorm in atitle or atitle in tnorm:
                        matched.append(a)
                        break
                    ratio = difflib.SequenceMatcher(None, tnorm, atitle).ratio()
                    if ratio >= 0.75:
                        matched.append(a)
                        break

        # Si aucun match exact, essayer substring naive
        if not matched:
            keyword = user_query.lower()
            matched = [a for a in sample_articles if keyword in (a.title or '').lower() or keyword in (a.summary or '').lower()]

        return matched[:max_results] if matched else articles[:max_results]
    except Exception as e:
        print("LLM filtering error:", e)
        # en cas d'erreur, fallback
        return articles[:max_results]
