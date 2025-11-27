import json
import streamlit as st

from pipeline import pipeline_hebdomadaire
from app.core.config import (
    RAW_PATH,
    ENRICHED_PATH,
    SELECTION_PATH,
    NEWSLETTER_HTML_PATH,
    AUDIO_PATH,
    BLOG_HTML_PATH,
    EMAIL_DRAFT_PATH,
)
from app.core.user_config import load_user_config, save_user_config
from app.core.theme_detector import detect_themes
from app.core.logging_utils import LOG_FILE

# Pas d'import send_email → il n'existe plus
# Tout est fait via Gmail API dans agent_6_email.py


st.set_page_config(
    page_title="Veille IA – Multi Agents",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Plateforme de Veille IA – Multi-Agents")

config = load_user_config()

# ---------------------------------------------------------------------
# SIDEBAR CONFIG
# ---------------------------------------------------------------------
st.sidebar.title("⚙️ Configuration")


# --------------------------------------
# 📅 Fréquence
# --------------------------------------
st.sidebar.subheader("📅 Fréquence de génération")
frequences = ["quotidien", "tous les 3 jours", "hebdomadaire"]

freq_value = config.get("frequence_generation", "hebdomadaire")
if freq_value not in frequences:
    freq_value = "hebdomadaire"

freq = st.sidebar.selectbox("Fréquence", frequences, index=frequences.index(freq_value))

config["frequence_generation"] = freq

heure = st.sidebar.time_input("Heure de génération", key="hour_input")
config["heure_generation"] = f"{heure.hour:02d}:{heure.minute:02d}"


# --------------------------------------
# 📧 Emails destinataires
# --------------------------------------
st.sidebar.subheader("📧 Destinataires des emails")

new_mail = st.sidebar.text_input("Ajouter un email")
if st.sidebar.button("➕ Ajouter email"):
    if new_mail and new_mail not in config["emails_destinataires"]:
        config["emails_destinataires"].append(new_mail)

# Liste emails
for mail in list(config["emails_destinataires"]):
    col1, col2 = st.sidebar.columns([4, 1])
    col1.write(mail)
    if col2.button("❌", key=f"del_{mail}"):
        config["emails_destinataires"].remove(mail)


# --------------------------------------
# 📨 TEST EMAIL VIA GMAIL API
# --------------------------------------
st.sidebar.subheader("📬 Tester l’envoi d’un email")

test_mail = st.sidebar.text_input("Email de test")

if st.sidebar.button("📨 Envoyer email test"):
    if not test_mail:
        st.sidebar.error("Saisis un email valide.")
    else:
        try:
            # Construction message test
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from app.agents.agent_6_email import gmail_service, EMAIL_SENDER
            import base64

            msg = MIMEMultipart("alternative")
            msg["to"] = test_mail
            msg["from"] = EMAIL_SENDER
            msg["subject"] = "Test Gmail API – Flash AI"
            msg.attach(MIMEText("Ceci est un test via Gmail API.", "plain", "utf-8"))

            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

            gmail_service().users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()

            st.sidebar.success("✅ Email envoyé via Gmail API !")

        except Exception as e:
            st.sidebar.error(f"❌ Erreur Gmail API : {e}")


# --------------------------------------
# 🧠 Détection thème IA
# --------------------------------------
st.sidebar.subheader("🧠 Détection automatique des thèmes")

txt = st.sidebar.text_area("Décris ta veille IA", placeholder="Ex : veille IA, LLM, ML…")

if st.sidebar.button("🔍 Détecter"):
    if txt.strip():
        det = detect_themes(txt)
        if det:
            config["themes_actifs"] = det
            st.sidebar.success(f"Thèmes détectés : {det}")
        else:
            st.sidebar.error("Impossible de détecter un thème.")
    else:
        st.sidebar.error("Écris quelque chose.")

if not config.get("themes_actifs"):
    config["themes_actifs"] = ["intelligence artificielle"]

st.sidebar.write("**Thèmes actifs :**")
st.sidebar.write(", ".join(config["themes_actifs"]))


save_user_config(config)


# --------------------------------------
# 🚀 Génération immédiate
# --------------------------------------
st.sidebar.subheader("🚀 Générer la veille maintenant")

if st.sidebar.button("Générer maintenant"):
    LOG_FILE.write_text("", encoding="utf-8")
    st.success("⏳ Génération en cours…")
    pipeline_hebdomadaire()
    st.success("✨ Veille générée !")


# ---------------------------------------------------------------------
# TABS
# ---------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📝 Collecte",
    "🧠 Analyse",
    "⭐ Sélection",
    "📰 Newsletter",
    "📰 Blog",
    "🎧 Audio",
    "📧 Email",
])


# ------------------ TAB COLLECTE ------------------
with tab1:
    st.header("📝 Articles collectés")
    if RAW_PATH.exists():
        data = json.loads(RAW_PATH.read_text(encoding="utf-8"))
        st.write(f"**{len(data)} articles collectés**")
        st.dataframe(data)
    else:
        st.info("Aucun article collecté.")

# ------------------ TAB ANALYSE ------------------
with tab2:
    st.header("🧠 Analyse LLM")
    if ENRICHED_PATH.exists():
        data = json.loads(ENRICHED_PATH.read_text(encoding="utf-8"))
        st.write(f"**{len(data)} articles enrichis**")
        st.dataframe(data)
    else:
        st.info("Analyse non disponible.")

# ------------------ TAB SÉLECTION ------------------
with tab3:
    st.header("⭐ Sélection IA")
    if SELECTION_PATH.exists():
        sel = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
        data = json.loads(ENRICHED_PATH.read_text(encoding="utf-8"))

        st.subheader("📌 Articles sélectionnés")
        for idx in sel["indices_selection"]:
            if idx < len(data):
                st.write(f"- **{data[idx]['titre']}** ({data[idx].get('sous_theme','')})")

        st.subheader("🎧 Article principal (audio)")
        idx = sel["index_audio"]
        if idx < len(data):
            st.success(data[idx]["titre"])

    else:
        st.info("Sélection non disponible.")

# ------------------ TAB NEWSLETTER ------------------
with tab4:
    st.header("📰 Newsletter HTML")
    if NEWSLETTER_HTML_PATH.exists():
        html = NEWSLETTER_HTML_PATH.read_text(encoding="utf-8")
        st.components.v1.html(html, height=900, scrolling=True)
    else:
        st.info("Newsletter non générée.")

# ------------------ TAB BLOG ------------------
with tab5:
    st.header("📰 Blog complet")
    if BLOG_HTML_PATH.exists():
        html = BLOG_HTML_PATH.read_text(encoding="utf-8")
        st.components.v1.html(html, height=900, scrolling=True)
    else:
        st.info("Blog non généré.")

# ------------------ TAB AUDIO ------------------
with tab6:
    st.header("🎧 Capsule audio")
    if AUDIO_PATH.exists():
        st.audio(str(AUDIO_PATH))
    else:
        st.info("Pas d'audio.")

# ------------------ TAB EMAIL ------------------
with tab7:
    st.header("📧 Email généré")
    if EMAIL_DRAFT_PATH.exists():
        content = EMAIL_DRAFT_PATH.read_text(encoding="utf-8")
        st.text_area("Email (texte brut)", content, height=200)
    else:
        st.info("Aucun email généré.")
