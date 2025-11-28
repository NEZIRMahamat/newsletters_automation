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
from app.core.user_config import (
    load_user_config, 
    save_user_config,
    load_contacts_from_csv,
    add_contact_to_csv,
    remove_contact_from_csv,
    get_all_emails_from_csv
)
from app.core.theme_detector import detect_themes
from app.core.logging_utils import LOG_FILE

# Pas d'import send_email → il n'existe plus
# Tout est fait via Gmail API dans agent_6_email.py


st.set_page_config(
    page_title="All NewsAI - Plateforme de veille unifiée",
    layout="wide"
)

# Affichage du logo
col1, col2 = st.columns([1, 5])
with col1:
    st.image("allnewsai_logo.jpg", width=180)
with col2:
    st.markdown("<h1 style='margin-top: 40px;'>Plateforme de veille automatique</h1>", unsafe_allow_html=True)

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
# 📧 Emails destinataires (CSV)
# --------------------------------------
st.sidebar.subheader("📧 Destinataires des emails")

col_email, col_nom = st.sidebar.columns([3, 2])
new_mail = col_email.text_input("Email", key="new_email")
new_nom = col_nom.text_input("Nom", key="new_nom")

if st.sidebar.button("➕ Ajouter contact"):
    if new_mail:
        if add_contact_to_csv(new_mail, new_nom):
            st.sidebar.success(f"✅ {new_mail} ajouté !")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Email déjà existant")
    else:
        st.sidebar.error("❌ Email requis")

# Liste des contacts
contacts = load_contacts_from_csv()
if contacts:
    st.sidebar.write(f"**{len(contacts)} contact(s) :**")
    for contact in contacts:
        col1, col2 = st.sidebar.columns([4, 1])
        display = f"{contact['email']} ({contact['nom']})" if contact['nom'] else contact['email']
        col1.write(display)
        if col2.button("❌", key=f"del_{contact['email']}"):
            remove_contact_from_csv(contact['email'])
            st.rerun()
else:
    st.sidebar.info("Aucun contact ajouté")


# --------------------------------------
# 📬 ENVOYER NEWSLETTER À UN CONTACT
# --------------------------------------
st.sidebar.subheader("📬 Envoyer la Newsletter")

# Liste déroulante des contacts
emails_list = get_all_emails_from_csv()

if emails_list:
    selected_email = st.sidebar.selectbox(
        "Choisir un destinataire",
        options=emails_list,
        key="selected_email_newsletter"
    )
    
    if st.sidebar.button("📨 Envoyer Newsletter"):
        # Vérifier que la newsletter existe
        if not NEWSLETTER_HTML_PATH.exists():
            st.sidebar.error("❌ Newsletter non générée. Génère d'abord la veille.")
        else:
            try:
                from app.agents.agent_6_email import send_email_smtp2go
                
                # Charger le contenu HTML de la newsletter
                newsletter_html = NEWSLETTER_HTML_PATH.read_text(encoding="utf-8")
                
                # Envoyer via SMTP2GO
                success = send_email_smtp2go(
                    to_email=selected_email,
                    subject="🔥 Flash AI – Top 3 IA de la semaine",
                    html_content=newsletter_html,
                    text_content="Newsletter Flash AI - Consultez votre email en HTML"
                )
                
                if success:
                    st.sidebar.success(f"✅ Newsletter envoyée à {selected_email}")
                else:
                    st.sidebar.error("❌ Erreur lors de l'envoi")
                    
            except Exception as e:
                st.sidebar.error(f"❌ Erreur : {e}")
else:
    st.sidebar.info("Ajoute d'abord des contacts pour envoyer la newsletter")


# --------------------------------------
# 🧠 Détection thème IA
# --------------------------------------
st.sidebar.subheader("🧠 Détection automatique des thèmes")
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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Collecte",
    "🧠 Analyse",
    "⭐ Sélection",
    "📰 Newsletters",
    "📰 Blog",
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

        # Génération du HTML stylisé
        html_content = """
        <style>
            .selection-container {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
            }
            .article-card {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                color: white;
                transition: transform 0.3s ease;
            }
            .article-card:hover {
                transform: translateY(-5px);
            }
            .article-title {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
                color: #fff;
            }
            .article-theme {
                display: inline-block;
                background: rgba(255,255,255,0.2);
                padding: 5px 15px;
                border-radius: 20px;
                font-size: 14px;
                margin-bottom: 15px;
            }
            .article-summary {
                font-size: 16px;
                line-height: 1.6;
                margin-top: 10px;
            }
            .article-url {
                margin-top: 15px;
            }
            .article-url a {
                color: #fff;
                text-decoration: none;
                border-bottom: 2px solid #fff;
                padding-bottom: 2px;
            }
            .article-url a:hover {
                opacity: 0.8;
            }
            .audio-badge {
                background: #ff6b6b;
                color: white;
                padding: 8px 16px;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
                display: inline-block;
                margin-bottom: 10px;
            }
            .section-title {
                font-size: 28px;
                font-weight: bold;
                color: #333;
                margin: 30px 0 20px 0;
                padding-bottom: 10px;
                border-bottom: 3px solid #667eea;
            }
        </style>
        <div class="selection-container">
        """
        
        # Articles sélectionnés
        html_content += '<div class="section-title">📌 Articles Sélectionnés</div>'
        for idx in sel["indices_selection"]:
            if idx < len(data):
                article = data[idx]
                html_content += f"""
                <div class="article-card">
                    <div class="article-theme">{article.get('sous_theme', 'Non classé')}</div>
                    <div class="article-title">{article['titre']}</div>
                    <div class="article-summary">{article.get('resume', 'Pas de résumé disponible')}</div>
                    <div class="article-url"><a href="{article.get('url', '#')}" target="_blank">🔗 Lire l'article complet</a></div>
                </div>
                """
        
        # Article principal (audio)
        html_content += '<div class="section-title">🎧 Article Principal (Audio)</div>'
        idx = sel["index_audio"]
        if idx < len(data):
            article = data[idx]
            html_content += f"""
            <div class="article-card">
                <div class="audio-badge">🎙️ VERSION AUDIO DISPONIBLE</div>
                <div class="article-theme">{article.get('sous_theme', 'Non classé')}</div>
                <div class="article-title">{article['titre']}</div>
                <div class="article-summary">{article.get('resume', 'Pas de résumé disponible')}</div>
                <div class="article-url"><a href="{article.get('url', '#')}" target="_blank">🔗 Lire l'article complet</a></div>
            </div>
            """
        
        html_content += "</div>"
        
        st.components.v1.html(html_content, height=800, scrolling=True)

    else:
        st.info("Sélection non disponible.")

# ------------------ TAB NEWSLETTER ------------------
with tab4:
    st.header("📰 Newsletters de la semaine")
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
