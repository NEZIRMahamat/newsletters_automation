import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.oauth2 import service_account
from googleapiclient.discovery import build

from app.core.config import EMAIL_DRAFT_PATH, BLOG_PUBLIC_URL
from app.core.user_config import load_user_config
from app.core.llm import groq_chat
from app.core.logging_utils import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------------------------------
# 🌍 Gmail API (100% fiable, pas de port SMTP)
# ---------------------------------------------------------------------
SERVICE_ACCOUNT_FILE = "app/credentials/gmail_service.json"
EMAIL_SENDER = "wasswasss435@gmail.com"
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def gmail_service():
    """Connexion Gmail API avec délégation."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    delegated = creds.with_subject(EMAIL_SENDER)
    return build("gmail", "v1", credentials=delegated)


# ---------------------------------------------------------------------
# 📨 TEMPLATE EMAIL HTML PRO
# ---------------------------------------------------------------------
EMAIL_TEMPLATE = """
<html>
<body style="font-family: Arial; background:#f3f4f6; padding:20px;">
<div style="max-width:700px; margin:auto; background:white; padding:25px; border-radius:16px;">

<h2 style="color:#111827;">🔥 Flash AI — Top 3 IA de la semaine</h2>

<p style="font-size:14px; color:#374151; line-height:1.6;">
{intro}
</p>

{articles_html}

<hr style="margin-top:30px;margin-bottom:30px;">

<div style="text-align:center;">
<a href="{blog_url}" style="background:#0f172a; color:white; padding:12px 18px;
border-radius:8px; text-decoration:none; font-size:15px;">
📘 Lire la veille complète (Blog Flash AI)
</a>
</div>

<p style="font-size:12px; color:#9ca3af; margin-top:25px;">
Email généré automatiquement par Flash AI.
</p>

</div>
</body>
</html>
"""


# ---------------------------------------------------------------------
# 🔧 Carte HTML pour chaque article
# ---------------------------------------------------------------------
def build_article_html(article):
    img = ""
    if article.get("image"):
        img = f"""
        <img src="{article['image']}" 
             style="width:100%; border-radius:10px; margin-bottom:10px;" />
        """

    return f"""
    <div style="margin-bottom:28px; padding-bottom:18px; border-bottom:1px solid #e5e7eb;">
        {img}
        <h3 style="margin:0; color:#0f172a; font-size:17px;">{article['titre']}</h3>
        <p style="font-size:14px; color:#374151; line-height:1.5;">
            {article['resume']}
        </p>
        <a href="{article['url']}"
           style="background:#2563eb; padding:8px 14px; color:white; 
                  text-decoration:none; border-radius:6px;
                  font-size:13px;">
           Lire l'article →
        </a>
    </div>
    """


# ---------------------------------------------------------------------
# 🤖 Prompt LLM pour intro email
# ---------------------------------------------------------------------
SYSTEM = """
Tu écris un paragraphe d'introduction pour un email professionnel de veille en IA.
Tu expliques les informations directement sans phrases comme "cet article dit".
Style clair, concis, informatif.
"""

USER = """
Voici les 3 articles IA sélectionnés :

{block}

Écris une introduction de 5 à 7 lignes.
"""


# ---------------------------------------------------------------------
# 🚀 Génération + Envoi
# ---------------------------------------------------------------------
def generer_email_top3(enriched, top3, idx_audio):

    # 1) Construire texte pour LLM
    block = ""
    for idx in top3:
        a = enriched[idx]
        block += f"- {a['titre']}\n{a['resume']}\n\n"

    intro = groq_chat(SYSTEM, USER.format(block=block), temperature=0.2, max_tokens=400)
    if not intro:
        intro = "Voici les actualités IA importantes de la semaine."

    EMAIL_DRAFT_PATH.write_text(intro, encoding="utf-8")

    # 2) HTML articles
    articles_html = ""
    for idx in top3:
        articles_html += build_article_html(enriched[idx])

    # 3) HTML final
    html_email = EMAIL_TEMPLATE.format(
        intro=intro,
        articles_html=articles_html,
        blog_url=BLOG_PUBLIC_URL
    )

    # 4) Destinataires
    cfg = load_user_config()
    recipients = cfg.get("emails_destinataires", [])
    if not recipients:
        logger.warning("❌ Aucun destinataire d'email configuré.")
        return

    # 5) Build email
    msg = MIMEMultipart("alternative")
    msg["to"] = ", ".join(recipients)
    msg["from"] = EMAIL_SENDER
    msg["subject"] = "🔥 Flash AI – Top 3 IA"

    msg.attach(MIMEText(intro, "plain", _charset="utf-8"))
    msg.attach(MIMEText(html_email, "html", _charset="utf-8"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    # 6) Envoi Gmail API
    try:
        gmail_service().users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        logger.info("📧 Email envoyé via Gmail API.")
    except Exception as e:
        logger.error("❌ Erreur Gmail API : %s", e)
