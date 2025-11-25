from flask import Blueprint, render_template, jsonify
from agents.rss_reader import RSSReader
from agents.llm_processor import LLMProcessor

newsletter_bp = Blueprint("newsletter", __name__)

@newsletter_bp.route("/")
def index():
    return render_template("newsletter.html")

@newsletter_bp.route("/run", methods=["POST"])
def run_newsletter():
    rss = RSSReader()
    articles = rss.fetch_articles(days=3)

    processor = LLMProcessor()
    summaries = [processor.summarize_article(a) for a in articles]

    return render_template("partials/summaries.html", summaries=summaries)
