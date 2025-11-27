# 🤖 Newsletter Automation - Flash AI

## 📋 Description du Projet

Système multi-agents d'automatisation complète de newsletters hebdomadaires sur l'Intelligence Artificielle. Cette plateforme collecte automatiquement des articles d'actualité IA, les analyse, sélectionne les meilleurs contenus, génère une newsletter HTML professionnelle et l'envoie aux abonnés.

---

## 🎯 Fonctionnalités

### ✨ Pipeline Automatisé Multi-Agents

1. **Agent Collecteur** 📰
   - Collecte automatique d'articles depuis plusieurs sources (RSS, NewsAPI)
   - Déduplication intelligente des contenus
   - Stockage structuré des articles bruts

2. **Agent d'Analyse** 🧠
   - Analyse sémantique des articles via LLM (Groq)
   - Extraction des thèmes et sous-thèmes
   - Scoring d'importance et pertinence
   - Génération de résumés enrichis

3. **Agent Curateur** ⭐
   - Sélection intelligente des Top 3 articles
   - Détection des tendances importantes
   - Choix de l'article principal pour podcast audio

4. **Agent Newsletter** 📧
   - Génération de newsletter HTML responsive
   - Design professionnel avec templates personnalisables
   - Adaptation mobile et desktop

5. **Agent Blog** 📝
   - Génération d'une page blog complète
   - Vue détaillée de tous les articles sélectionnés
   - Navigation par thèmes

6. **Agent Audio** 🎧
   - Génération de script audio pour l'article principal
   - Synthèse vocale via Groq TTS
   - Export au format MP3

7. **Agent Email** 📨
   - Envoi automatique via API SMTP2GO
   - Gestion des contacts par CSV
   - Support HTML et texte brut

8. **Agent Site Statique** 🌐
   - Génération d'un site web statique
   - Pages par article et par thème
   - Navigation intuitive

---

## 🏗️ Architecture Technique

```
newsletters_automation/
├── app/
│   ├── agents/           # 7 agents spécialisés
│   │   ├── agent_1_collector.py
│   │   ├── agent_2_analysis.py
│   │   ├── agent_3_curator.py
│   │   ├── agent_4_newsletter.py
│   │   ├── agent_4_blog.py
│   │   ├── agent_5_audio.py
│   │   ├── agent_6_email.py
│   │   └── agent_7_static_site.py
│   └── core/            # Modules partagés
│       ├── config.py
│       ├── llm.py
│       ├── user_config.py
│       └── logging_utils.py
├── data/                # Données générées
├── contacts_newsletters.csv
├── pipeline.py          # Orchestrateur principal
└── ui_streamlit.py      # Interface web
```

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
- 📝 **Collecte** : Visualiser les articles collectés
- 🧠 **Analyse** : Voir les articles enrichis par LLM
- ⭐ **Sélection** : Articles sélectionnés pour la newsletter
- 📰 **Newsletter** : Aperçu de la newsletter HTML
- 📰 **Blog** : Page blog complète
- 🎧 **Audio** : Écouter le podcast généré
- 📧 **Email** : Brouillon de l'email

### Mode CLI (Pipeline Automatique)

```bash
# Exécuter le pipeline complet
venv/bin/python pipeline.py
```

Le pipeline exécute séquentiellement :
1. Collecte des articles
2. Analyse et enrichissement
3. Sélection des meilleurs contenus
4. Génération newsletter + blog
5. Génération audio
6. Envoi par email aux contacts
7. Création du site statique

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

Éditer `app/agents/agent_4_newsletter.py` pour modifier le HTML généré.

### Ajuster les Critères de Sélection

Modifier les prompts dans `app/agents/agent_3_curator.py`.

---

## 🐛 Dépannage

### Problème d'envoi d'emails

**Erreur : Timeout SMTP**
- Solution : Le système utilise l'API REST SMTP2GO qui contourne les blocages de ports SMTP
- Vérifier que `SMTP2GO_API_KEY` est bien configurée dans `.env`

### Erreur LLM (Groq)

**Erreur : Rate limit**
- Groq a des limites de requêtes gratuites
- Attendre quelques minutes entre les générations
- Ou utiliser un autre modèle dans `.env`

### Articles non collectés

- Vérifier `NEWSAPI_KEY` dans `.env`
- Vérifier la connexion internet
- Consulter les logs dans `data/logs.txt`

---

## 📈 Roadmap

- [ ] Support de bases de données (PostgreSQL/MongoDB)
- [ ] Planification automatique (cron jobs)
- [ ] Interface d'administration avancée
- [ ] Multi-langues
- [ ] Intégration avec plus de services d'emailing
- [ ] Système de recommandation personnalisé
- [ ] Analytics et statistiques d'ouverture

---

## 👥 Contributeurs

- **NEZIR Mahamat** - Développement principal
- Projet réalisé dans le cadre de HETIC 2025

---

## 📄 Licence

Ce projet est sous licence MIT.

---

## 🙏 Remerciements

- [Groq](https://groq.com/) pour l'API LLM gratuite
- [SMTP2GO](https://www.smtp2go.com/) pour l'envoi d'emails
- [NewsAPI](https://newsapi.org/) pour les sources d'actualités
- [Streamlit](https://streamlit.io/) pour l'interface web
