from flask import Blueprint, render_template, jsonify, request
from agents.rss_reader import RSSReader
from agents.llm_processor import LLMProcessor
import logging

logger = logging.getLogger(__name__)
newsletter_bp = Blueprint("newsletter", __name__)

@newsletter_bp.route("/")
def index():
    return render_template("newsletter.html")

@newsletter_bp.route("/run", methods=["POST"])
def run_newsletter():
    try:
        rss = RSSReader()
        articles = rss.fetch_articles(days=3)

        if not articles:
            return render_template("partials/summaries.html", summaries=[])

        processor = LLMProcessor()
        summaries = []
        
        for article in articles[:10]:  # Limit to 10 articles for performance
            try:
                summary = processor.summarize_article(article)
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Error processing article {article.get('title', 'Unknown')}: {e}")
                continue

        return render_template("partials/summaries.html", summaries=summaries)
    
    except Exception as e:
        logger.error(f"Error in run_newsletter: {e}")
        return render_template("partials/error.html", error=str(e)), 500
