# Newsletter Automation - All NewsAI

## Description du Projet

Système multi-agents d'automatisation complète de newsletters hebdomadaires sur l'Intelligence Artificielle. Cette plateforme collecte automatiquement des articles d'actualité IA, les analyse, sélectionne les meilleurs contenus, génère une newsletter HTML professionnelle et l'envoie aux abonnés.

---

## Fonctionnalités

### Architecture à 3 Agents Intelligents

#### **Agent 1 : Synthétiseur & Analyseur IA** 
Combine la collecte et l'analyse intelligente des contenus :
- **Collecte multi-sources** : RSS feeds et NewsAPI pour scraper les actualités IA
- **Déduplication** : Élimine les articles en double
- **Analyse LLM (Groq)** : Génère des résumés détaillés, extrait les sous-thèmes (LLM, NLP, robotique, etc.)
- **Scoring d'importance** : Note chaque article de 1 à 5 pour identifier les contenus prioritaires
- **Sélection automatique** : Choisit intelligemment le Top 3 des articles + l'article principal pour l'audio
- **Génération de contenus** : Produit la newsletter HTML, le blog complet et le site statique

#### **Agent 2 : Rédacteur & Expéditeur d'Emails**
Gère la communication avec les abonnés :
- **Rédaction LLM** : Génère un email d'accroche professionnel avec le Top 3 des articles
- **Template HTML** : Newsletter responsive adaptée mobile/desktop
- **Envoi SMTP2GO** : Utilise l'API REST SMTP2GO pour l'envoi d'emails (contourne les blocages firewall)
- **Gestion contacts CSV** : Stockage et gestion des destinataires dans `contacts_newsletters.csv`, utilié en memoire disque (remplacement par une DB pour amélioration)
- **Support multi-format** : Envoie en HTML et texte brut

#### **Agent 3 : Générateur Audio & Intégration UI** 🎧🎙️
Transforme le contenu en audio et enrichit l'interface :
- **Transcription text-to-speech** : Convertit l'article principal en script audio via LLM
- **Synthèse vocale** : Génère un fichier MP3 professionnel (2 min max)
- **Injection dans UI Streamlit** : Intègre l'audio dans l'interface web pour une écoute directe
- **Player intégré** : Lecture audio native dans le navigateur

---


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
│  AGENT 3: Audio & UI                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │
│  │   LLM    │→ │   LLM    │→ │ Streamlit│→ 🌐 Interface.     │
│  │  Script  │  │   TTS    │  │    UI    │                   │
│  └──────────┘  └──────────┘  └──────────┘                   │
│       ↓             ↓              ↓                        │
│   [script]    [capsule.mp3]  [Audio Player]                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    Déploiement Render Cloud
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

## Installation et Configuration

### Prérequis
- Python 3.9+
- Compte SMTP2GO (pour envoi d'emails)
- Clés API : Groq, NewsAPI, ElevenLabs (optionnel)

### Installation

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

### Configuration des Variables d'Environnement

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

### Obtenir les Clés API

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

## Utilisation

### Interface Web (Streamlit)

```bash
# Lancer l'application
venv/bin/streamlit run ui_streamlit.py
```

Accéder à http://localhost:8501

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

## Gestion des Contacts

Les contacts sont stockés dans `contacts_newsletters.csv` :

```csv
```csv
email,nom,date_ajout,user_actif,date_abonnement,date_desabonnement,newsletter_frequency,topics
john.doe@example.com,John Doe,2025-11-27 14:30:00,true,2025-11-27 14:30:00,,weekly,IA;LLM;NLP
jane.smith@example.com,Jane Smith,2025-11-27 15:00:00,true,2025-11-27 15:00:00,,weekly,IA;robotique
```

**Format des colonnes** :
- `email` : Adresse email du contact (obligatoire)
- `nom` : Nom complet du destinataire (obligatoire)
- `date_ajout` : Date et heure d'ajout au format `YYYY-MM-DD HH:MM:SS` (auto-généré)
- `user_actif` : Statut d'activité (`true`/`false`) - indique si le contact reçoit les newsletters
- `date_abonnement` : Date d'abonnement initiale
- `date_desabonnement` : Date de désabonnement (vide si actif)
- `newsletter_frequency` : Fréquence d'envoi (`weekly`, `daily`, `monthly`)
- `topics` : Thématiques d'intérêt séparées par `;` (ex: `IA;LLM;robotique`)
```

---

## Déploiement sur Render Cloud

### Configuration Render

1. **Connecter le repo GitHub** : `@username_github/newsletters_automation`
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

## 👥 Contributeurs : All NewsAI Team

- **NEZIR Mahamat** - Project Manager : Gestion des tâches, intégration SMTP2GO, contacts newsletters, architecture et déploiement
- **Ouassim** - Developer : Développement, UI/UX
- **Akram** - Developer : Architecture backend, tests, développement
- **Samar** - Product Owner : Cahier de charges, présentation, documentation et tests

*Projet réalisé dans le cadre du cours **Création d'agents** - HETIC 2025*

---

## 📄 Licence

Ce projet est sous licence MIT.

---

## 🙏 Remerciements

- Hakim HORAIRY, Michel CADENNES, mes deux super intervenants
- La communauté HETIC MD5
- La communauté open-source pour les outils et bibliothèques utilisés


---

## 📧 Contact

Pour toute question ou suggestion :
- GitHub Issues : [newsletters_automation/issues](https://github.com/NEZIRMahamat/newsletters_automation/issues)
- Email : Voir profil GitHub

---

**Made with ❤️ by the All NewsAI Team**

- [Groq](https://groq.com/) pour l'API LLM gratuite
- [SMTP2GO](https://www.smtp2go.com/) pour l'envoi d'emails
- [NewsAPI](https://newsapi.org/) pour les sources d'actualités
- [Streamlit](https://streamlit.io/) pour l'interface web
