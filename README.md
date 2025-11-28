# 🤖 Newsletter Automation - Flash AI

## 📋 Description du Projet

Système multi-agents d'automatisation complète de newsletters hebdomadaires sur l'Intelligence Artificielle. Cette plateforme collecte automatiquement des articles d'actualité IA, les analyse, sélectionne les meilleurs contenus, génère une newsletter HTML professionnelle et l'envoie aux abonnés.

---

## 🎯 Fonctionnalités

### ✨ Architecture à 3 Agents Intelligents

#### **Agent 1 : Synthétiseur & Analyseur IA** 📰🧠
Combine la collecte et l'analyse intelligente des contenus :
- **Collecte multi-sources** : RSS feeds et NewsAPI pour scraper les actualités IA
- **Déduplication** : Élimine les articles en double
- **Analyse LLM (Groq)** : Génère des résumés détaillés, extrait les sous-thèmes (LLM, NLP, robotique, etc.)
- **Scoring d'importance** : Note chaque article de 1 à 5 pour identifier les contenus prioritaires
- **Sélection automatique** : Choisit intelligemment le Top 3 des articles + l'article principal pour l'audio
- **Génération de contenus** : Produit la newsletter HTML, le blog complet et le site statique

#### **Agent 2 : Rédacteur & Expéditeur d'Emails** 📧✉️
Gère la communication avec les abonnés :
- **Rédaction LLM** : Génère un email d'accroche professionnel avec le Top 3 des articles
- **Template HTML** : Newsletter responsive adaptée mobile/desktop
- **Envoi SMTP2GO** : Utilise l'API REST SMTP2GO pour l'envoi d'emails (contourne les blocages firewall)
- **Gestion contacts CSV** : Stockage et gestion des destinataires dans `contacts_newsletters.csv`
- **Support multi-format** : Envoie en HTML et texte brut

#### **Agent 3 : Générateur Audio & Intégration UI** 🎧🎙️
Transforme le contenu en audio et enrichit l'interface :
- **Transcription text-to-speech** : Convertit l'article principal en script audio via LLM
- **Synthèse vocale Groq TTS** : Génère un fichier MP3 professionnel (2 min max)
- **Injection dans UI Streamlit** : Intègre l'audio dans l'interface web pour une écoute directe
- **Player intégré** : Lecture audio native dans le navigateur

---

## 🏗️ Architecture Technique

### Structure du Projet

```
newsletters_automation/
├── app/
│   ├── agents/                    # 3 agents intelligents
│   │   ├── agent_1_collector.py   # Agent 1: Collecte RSS/API
│   │   ├── agent_2_analysis.py    # Agent 1: Analyse LLM
│   │   ├── agent_3_curator.py     # Agent 1: Sélection IA
│   │   ├── agent_4_newsletter.py  # Agent 1: Génération newsletter
│   │   ├── agent_4_blog.py        # Agent 1: Génération blog
│   │   ├── agent_5_audio.py       # Agent 3: Audio TTS
│   │   ├── agent_6_email.py       # Agent 2: Email & SMTP
│   │   └── agent_7_static_site.py # Agent 1: Site statique
│   └── core/                      # Modules partagés
│       ├── config.py              # Configuration générale
│       ├── llm.py                 # Client Groq LLM
│       ├── user_config.py         # Config utilisateur & CSV
│       └── logging_utils.py       # Logs
├── data/                          # Données générées
│   ├── raw_articles.json          # Articles bruts collectés
│   ├── articles_enrichis.json     # Articles analysés par LLM
│   ├── selection.json             # Top articles sélectionnés
│   ├── newsletter.html            # Newsletter HTML
│   ├── blog.html                  # Blog complet
│   ├── capsule.mp3                # Audio généré
│   └── site/                      # Site statique
├── contacts_newsletters.csv       # Base contacts emails
├── allnewsai_logo.jpg            # Logo de l'application
├── pipeline.py                    # Orchestrateur principal
├── ui_streamlit.py                # Interface web Streamlit
└── requirements.txt               # Dépendances Python
```

### Flux de Traitement

```
┌─────────────────────────────────────────────────────────────┐
│  AGENT 1: Synthétiseur & Analyseur IA                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   RSS    │→ │ NewsAPI  │→ │ LLM      │→ │ Sélection│   │
│  │  Feeds   │  │   API    │  │ Analyse  │  │   Top 3  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│       ↓             ↓              ↓             ↓          │
│  [raw_articles] [enrichis] [newsletter.html] [blog.html]   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  AGENT 2: Rédacteur & Expéditeur                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   LLM    │→ │  Email   │→ │ SMTP2GO  │→ 📧 Abonnés     │
│  │ Rédaction│  │  HTML    │  │   API    │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│                                    ↑                         │
│                        [contacts_newsletters.csv]           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  AGENT 3: Audio & UI                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   LLM    │→ │  Groq    │→ │ Streamlit│→ 🌐 Interface   │
│  │  Script  │  │   TTS    │  │    UI    │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
│       ↓             ↓              ↓                         │
│   [script]    [capsule.mp3]  [Audio Player]                │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    🚀 Déploiement Render Cloud
```

### Technologies Utilisées

- **Backend** : Python 3.9+
- **LLM** : Groq API (analyse, rédaction, TTS)
- **Collecte** : RSS (feedparser), NewsAPI
- **Email** : SMTP2GO REST API
- **UI** : Streamlit (interface web)
- **Audio** : Groq Text-to-Speech
- **Stockage** : JSON + CSV
- **Déploiement** : Render Cloud + GitHub

---

## 🚀 Installation et Configuration

### Prérequis
- Python 3.9+
- Compte SMTP2GO (pour envoi d'emails)
- Clés API : Groq, NewsAPI, ElevenLabs (optionnel)

### 1️⃣ Installation

```bash
# Cloner le projet
git clone https://github.com/NEZIRMahamat/newsletters_automation.git
cd newsletters_automation

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2️⃣ Configuration des Variables d'Environnement

Créer un fichier `.env` à la racine :

```env
# API LLM
GROQ_API_KEY=votre_cle_groq
GROQ_MODEL=openai/gpt-oss-120b

# API News
NEWSAPI_KEY=votre_cle_newsapi

# API Audio (optionnel)
ELEVENLABS_API_KEY=votre_cle_elevenlabs

# Email Configuration (SMTP2GO)
EMAIL_FROM=votre_email@domaine.com
SMTP2GO_API_KEY=votre_cle_api_smtp2go
SMTP2GO_API_URL=https://api.smtp2go.com/v3/email/send

# URL publique du blog (optionnel)
BLOG_PUBLIC_URL=http://localhost:8501/blog
```

### 3️⃣ Obtenir les Clés API

#### Groq (LLM - Gratuit)
1. Aller sur https://console.groq.com/
2. Créer un compte
3. Générer une clé API dans "API Keys"

#### NewsAPI (Sources d'actualités - Gratuit)
1. Aller sur https://newsapi.org/
2. S'inscrire pour obtenir une clé gratuite

#### SMTP2GO (Envoi d'emails)
1. Créer un compte sur https://www.smtp2go.com/
2. Aller dans Settings → API Keys
3. Créer une nouvelle clé API

#### ElevenLabs (Audio - Optionnel)
1. Aller sur https://elevenlabs.io/
2. Créer un compte et générer une clé API

---

## 💻 Utilisation

### Interface Web (Streamlit)

```bash
# Lancer l'application
venv/bin/streamlit run ui_streamlit.py
```

Accéder à http://localhost:8501

#### Fonctionnalités de l'Interface :

**Sidebar (Configuration)** :
- 📅 Paramétrer la fréquence de génération
- 📧 Gérer les contacts destinataires (ajout/suppression)
- 📬 Envoyer la newsletter à un contact spécifique
- 🧠 Détecter automatiquement les thèmes d'intérêt
- 🚀 Générer la veille immédiatement

**Onglets Principaux** :
- 📝 **Collecte** : Visualiser les articles bruts collectés (RSS + NewsAPI)
- 🧠 **Analyse** : Articles enrichis par LLM avec résumés, thèmes et scores
- ⭐ **Sélection** : Affichage HTML stylisé du Top 3 + article audio sélectionnés
- 📰 **Newsletter** : Aperçu de la newsletter HTML responsive
- 📰 **Blog** : Page blog complète avec audio intégré

### Mode CLI (Pipeline Automatique)

```bash
# Exécuter le pipeline complet des 3 agents
venv/bin/python pipeline.py
```

Le pipeline exécute séquentiellement les 3 agents :

**Agent 1 - Synthétiseur & Analyseur** :
1. Collecte des articles (RSS + NewsAPI)
2. Analyse et enrichissement LLM
3. Sélection IA des meilleurs contenus
4. Génération newsletter + blog + site statique

**Agent 2 - Rédacteur & Expéditeur** :
5. Rédaction email d'accroche LLM
6. Envoi SMTP2GO aux contacts CSV

**Agent 3 - Audio & UI** :
7. Génération script audio LLM
8. Synthèse vocale TTS (MP3)
9. Intégration dans l'interface Streamlit

---

## 📊 Gestion des Contacts

Les contacts sont stockés dans `contacts_newsletters.csv` :

```csv
email,nom,date_ajout
john.doe@example.com,John Doe,2025-11-27 14:30:00
jane.smith@example.com,Jane Smith,2025-11-27 15:00:00
```

**Ajout via l'interface** :
1. Aller dans la sidebar
2. Section "📧 Destinataires des emails"
3. Remplir Email + Nom
4. Cliquer sur "➕ Ajouter contact"

**Suppression** : Cliquer sur ❌ à côté du contact

---

## 🔧 Personnalisation

### Modifier les Sources d'Actualités

Éditer `app/agents/agent_1_collector.py` :

```python
RSS_SOURCES = [
    "https://votre-source-rss.com/feed",
    # Ajouter vos sources RSS
]
```

### Personnaliser le Template Newsletter

## 🔧 Personnalisation

### Modifier les Sources d'Actualités

Éditer `app/agents/agent_1_collector.py` :

```python
RSS_SOURCES = [
    "https://votre-source-rss.com/feed",
    # Ajouter vos sources RSS
]
```

### Personnaliser les Prompts LLM

- **Analyse** : Modifier `SYSTEM` dans `app/agents/agent_2_analysis.py`
- **Sélection** : Ajuster les critères dans `app/agents/agent_3_curator.py`
- **Email d'accroche** : Personnaliser dans `app/agents/agent_6_email.py`
- **Script audio** : Modifier `SYSTEM` dans `app/agents/agent_5_audio.py`

### Personnaliser le Template Newsletter

Éditer le template HTML dans `app/agents/agent_4_newsletter.py`.

---

## 🐛 Dépannage

### Problème d'envoi d'emails

**Erreur : Timeout SMTP**
- ✅ **Solution** : Le système utilise l'API REST SMTP2GO (port HTTPS 443) qui contourne les blocages de ports SMTP (25, 587, 465)
- Vérifier que `SMTP2GO_API_KEY` et `SMTP2GO_API_URL` sont bien configurées dans `.env`
- Tester avec `venv/bin/python -c "from app.agents.agent_6_email import send_email_smtp2go_api; send_email_smtp2go_api('test@example.com', 'Test', '<h1>Test</h1>', 'Test')"`

### Erreur LLM (Groq)

**Erreur : Rate limit exceeded**
- Groq a des limites de requêtes gratuites (environ 30 requêtes/minute)
- Attendre quelques minutes entre les générations
- Réduire `max_par_flux` dans le pipeline
- Ou utiliser un autre modèle dans `.env` : `GROQ_MODEL=llama-3.1-70b-versatile`

### Articles non collectés

- Vérifier `NEWSAPI_KEY` dans `.env` (clé valide et active)
- Vérifier la connexion internet
- Consulter les logs détaillés dans `data/logs.txt`
- Tester manuellement : `venv/bin/python -c "from app.agents.agent_1_collector import collecter_news; print(collecter_news(['IA'], 5))"`

### Déploiement Render échoue

**Erreur : Invalid version ou pyobjc***
- ✅ Le `requirements.txt` a été simplifié pour enlever les dépendances macOS
- Vérifier que le fichier contient uniquement les 8 dépendances essentielles
- Build Command : `pip install -r requirements.txt`
- Start Command : `streamlit run ui_streamlit.py --server.port=$PORT --server.address=0.0.0.0`

---

## 🚀 Déploiement sur Render Cloud

### Configuration Render

1. **Connecter le repo GitHub** : `NEZIRMahamat/newsletters_automation`
2. **Type de service** : Web Service
3. **Branch** : `main`
4. **Build Command** : 
   ```bash
   pip install -r requirements.txt
   ```
5. **Start Command** :
   ```bash
   streamlit run ui_streamlit.py --server.port=$PORT --server.address=0.0.0.0
   ```

### Variables d'environnement Render

Ajouter dans le dashboard Render :
```
GROQ_API_KEY=votre_cle_groq
NEWSAPI_KEY=votre_cle_newsapi
SMTP2GO_API_KEY=votre_cle_smtp2go
SMTP2GO_API_URL=https://api.smtp2go.com/v3/email/send
EMAIL_FROM=votre_email@domaine.com
BLOG_PUBLIC_URL=https://votre-app.onrender.com
```

### Notes de déploiement

- ✅ Render détecte automatiquement Python 3.13
- ✅ Le port est géré automatiquement via `$PORT`
- ✅ SMTP2GO fonctionne en HTTPS (pas de blocage firewall)
- ⚠️ Les fichiers dans `data/` sont éphémères (utiliser un volume ou S3 pour la persistence)

---

## 📈 Roadmap

- [ ] Persistence des données avec PostgreSQL/MongoDB
- [ ] Planification automatique avec cron jobs (génération hebdomadaire)
- [ ] Webhooks pour notifications (Discord, Slack)
- [ ] Multi-langues (anglais, espagnol)
- [ ] Intégration avec plus de services d'emailing (SendGrid, Mailgun)
- [ ] Système de recommandation personnalisé par utilisateur
- [ ] Analytics et statistiques d'ouverture/clics
- [ ] Mode offline avec stockage local
- [ ] Export PDF des newsletters

---

## 👥 Contributeurs

- **NEZIR Mahamat** - Architecture & Développement principal
- **Ouassim** - Intégration SMTP2GO & CSV
- Projet réalisé dans le cadre de **HETIC 2025** - Semestre 1

---

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

---

## 🙏 Remerciements

- [Groq](https://groq.com/) pour l'API LLM gratuite et ultra-rapide
- [SMTP2GO](https://www.smtp2go.com/) pour l'API REST d'envoi d'emails
- [NewsAPI](https://newsapi.org/) pour l'accès aux sources d'actualités
- [Streamlit](https://streamlit.io/) pour le framework d'interface web
- [Render](https://render.com/) pour l'hébergement cloud gratuit
- La communauté open-source pour les outils et bibliothèques utilisés

---

## 📧 Contact

Pour toute question ou suggestion :
- GitHub Issues : [newsletters_automation/issues](https://github.com/NEZIRMahamat/newsletters_automation/issues)
- Email : Voir profil GitHub

---

**Made with ❤️ by HETIC Students | Powered by AI 🤖**

- [Groq](https://groq.com/) pour l'API LLM gratuite
- [SMTP2GO](https://www.smtp2go.com/) pour l'envoi d'emails
- [NewsAPI](https://newsapi.org/) pour les sources d'actualités
- [Streamlit](https://streamlit.io/) pour l'interface web
