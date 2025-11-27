import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

from app.core.config import EMAIL_DRAFT_PATH, BLOG_PUBLIC_URL
from app.core.user_config import load_user_config, get_all_emails_from_csv
from app.core.llm import groq_chat
from app.core.logging_utils import setup_logger

load_dotenv()
logger = setup_logger(__name__)

# ---------------------------------------------------------------------
# 🌍 SMTP2GO Configuration (API REST + SMTP fallback)
# ---------------------------------------------------------------------
SMTP2GO_API_KEY = os.getenv("SMTP2GO_API_KEY")
SMTP2GO_API_URL = os.getenv("SMTP2GO_API_URL", "https://api.smtp2go.com/v3/email/send")
SMTP_HOST = os.getenv("SMTP_HOST", "mail.smtp2go.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "True") == "True"
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_FROM", "a_nezir@hetic.eu").strip()


def send_email_smtp2go_api(to_email: str, subject: str, html_content: str, text_content: str = ""):
    """Envoie un email via l'API REST SMTP2GO (recommandé - ne nécessite pas de port SMTP)"""
    try:
        logger.info(f"📤 Envoi via API SMTP2GO à {to_email}...")
        
        payload = {
            "api_key": SMTP2GO_API_KEY,
            "to": [to_email],
            "sender": EMAIL_SENDER,
            "subject": subject,
            "text_body": text_content or "Consultez la version HTML de cet email",
            "html_body": html_content
        }
        
        response = requests.post(SMTP2GO_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("data", {}).get("succeeded") == 1:
            logger.info(f"✅ Email envoyé à {to_email} via API SMTP2GO")
            return True
        else:
            logger.error(f"❌ Échec API SMTP2GO: {result}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erreur API SMTP2GO: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Erreur inattendue API SMTP2GO: {e}")
        return False


def send_email_smtp2go(to_email: str, subject: str, html_content: str, text_content: str = ""):
    """
    Envoie un email via SMTP2GO
    Utilise l'API REST (recommandé) ou SMTP en fallback
    """
    # Essayer d'abord l'API REST (pas de problème de firewall)
    if SMTP2GO_API_KEY:
        return send_email_smtp2go_api(to_email, subject, html_content, text_content)
    
    # Fallback SMTP si pas d'API key
    logger.warning("⚠️ Pas d'API key SMTP2GO, utilisation SMTP (peut être bloqué par firewall)")
    return send_email_smtp2go_smtp(to_email, subject, html_content, text_content)


def send_email_smtp2go_smtp(to_email: str, subject: str, html_content: str, text_content: str = ""):
    """Envoie un email via SMTP (peut être bloqué par firewall)"""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        
        if text_content:
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))
        
        logger.info(f"📤 Connexion à {SMTP_HOST}:{SMTP_PORT} (SSL={SMTP_USE_SSL})...")
        
        if SMTP_USE_SSL:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.set_debuglevel(0)
                logger.info(f"🔑 Authentification avec {SMTP_USERNAME}...")
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                logger.info(f"📨 Envoi à {to_email}...")
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.set_debuglevel(0)
                logger.info("🔐 Activation TLS...")
                server.starttls()
                logger.info(f"🔑 Authentification avec {SMTP_USERNAME}...")
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                logger.info(f"📨 Envoi à {to_email}...")
                server.send_message(msg)
        
        logger.info(f"✅ Email envoyé à {to_email} via SMTP")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur SMTP: {e}")
        return False


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

    # 4) Destinataires depuis CSV
    recipients = get_all_emails_from_csv()
    if not recipients:
        logger.warning("❌ Aucun destinataire d'email configuré.")
        return

    # 5) Envoi via SMTP2GO
    subject = "🔥 Flash AI – Top 3 IA"
    for recipient in recipients:
        send_email_smtp2go(
            to_email=recipient,
            subject=subject,
            html_content=html_email,
            text_content=intro
        )
