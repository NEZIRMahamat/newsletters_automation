# Newsletter IA – Multi-agents

Une application pour générer une newsletter d'actualités IA personnalisée avec enrichissement via Groq.

## 🎯 Caractéristiques

- **📚 Multiples sources RSS** : Flux organisés par domaine (IA générale, ML, NLP, Vision, Robotique, Sécurité, Data Science)
- **⚙️ Configuration flexible** : Choisissez le domaine, nombre d'articles, et fréquence d'envoi
- **✨ Enrichissement IA** : Résumés, tags, classification, et scoring des articles via Groq
- **🎨 Interface HTMX** : UI moderne avec mise à jour dynamique du contenu (pas de rechargement page)
- **🔄 API REST** : Endpoints pour accéder à la config et aux articles

## 🚀 Démarrage rapide

### Prérequis

- Python 3.8+
- Une clé API Groq (obtenir sur [console.groq.com](https://console.groq.com))

### Installation

**Option 1: Avec le script PowerShell (Windows)**

```powershell
# Ouvrir PowerShell à la racine du projet, puis :
.\run-dev.ps1
```

Le script va :
1. Créer un environnement virtuel (venv)
2. Installer les dépendances
3. Créer le fichier `.env`
4. Démarrer le serveur

**Option 2: Installation manuelle**

```powershell
# Créer et activer le venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt

# Configurer la clé Groq
Set-Content -Path .env -Value 'GROQ_API_KEY=ta_clef_groq_ici'

# Démarrer le serveur
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Configuration Groq

Modifiez le fichier `.env` et remplacez `ta_clef_groq_ici` par votre vraie clé :

```env
GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXXXXXXX
```

## 📱 Interfaces

- **Web (HTMX)** : http://127.0.0.1:8000/ui
  - Configuration en temps réel (domaine, nb articles, fréquence)
  - Affichage dynamique des articles enrichis
  - Tags, scores, résumés détaillés

- **API REST** : http://127.0.0.1:8000/docs
  - Endpoints pour RSS bruts et enrichis
  - Gestion de la configuration utilisateur
  - Endpoints HTML/HTMX

## 🔌 Endpoints principaux

### Articles
- `GET /rss-test?domain=ia_generale&limit=10` → Articles bruts (sans enrichissement)
- `GET /rss-enriched-test?domain=ia_generale&limit=5` → Articles enrichis par Groq
- `GET /api/articles` → Articles selon la config utilisateur

### Configuration
- `GET /api/config` → Configuration actuelle
- `POST /api/config?domain=ml&num_articles=15&frequency=weekly` → Mise à jour config
- `GET /api/domains` → Liste des domaines disponibles

### UI
- `GET /ui` → Page principale (HTMX)
- `GET /ui/config` → Formulaire de configuration (HTML)
- `GET /ui/articles` → Liste d'articles (HTML)
- `POST /ui/config` → Mise à jour config via formulaire (HTML)

## 📊 Domaines disponibles

| Domaine | Description |
|---------|------------|
| `ia_generale` | Intelligence artificielle générale |
| `ml` | Machine Learning |
| `nlp` | Traitement du langage naturel |
| `computer_vision` | Vision par ordinateur |
| `robotique` | Robotique |
| `security` | Sécurité informatique |
| `data_science` | Data Science |

## 🎨 Architecture

```
├── main.py                              # Application FastAPI principale
├── agents/
│   ├── rss_reader.py                   # Récupération des flux RSS
│   ├── llm_groq.py                     # Enrichissement via Groq
│   └── newsletter_config_agent.py      # Gestion de la configuration
├── db/
│   └── newsletter_config.py            # Stockage JSON de la config
├── ui/
│   └── templates/
│       └── index.html                  # Interface HTMX
├── config/
│   └── settings.py                     # Paramètres (clé Groq)
├── requirements.txt                     # Dépendances
└── .env                                # Variables d'environnement
```

## 🔧 Configuration avancée

### Ajouter de nouvelles sources RSS

Modifiez `agents/rss_reader.py` et ajoutez des flux dans `RSS_SOURCES_BY_DOMAIN` :

```python
RSS_SOURCES_BY_DOMAIN = {
    "mon_domaine": [
        "https://example.com/rss",
        "https://autre.com/feed",
    ],
    # ...
}
```

### Personnaliser l'enrichissement Groq

Éditez `agents/llm_groq.py` et ajustez le `system_prompt` pour modifier :
- Longueur des résumés
- Types de tags
- Critères de scoring

## 🐛 Dépannage

### Erreur: `ModuleNotFoundError: No module named 'groq'`
```powershell
pip install groq
```

### Erreur: `GROQ_API_KEY not found`
Assurez-vous que le fichier `.env` existe et contient votre clé API Groq.

### Les articles ne s'affichent pas
1. Vérifiez que l'API est en cours d'exécution (`GET http://127.0.0.1:8000/`)
2. Vérifiez que la clé Groq est valide (pour l'enrichissement)
3. Vérifiez la console pour les messages d'erreur

### Timeout lors de l'enrichissement
Les modèles Groq peuvent être lents. Réduisez `num_articles` ou augmentez le timeout.

## 📝 Structure de réponse d'un article enrichi

```json
{
  "source": "Arxiv IA",
  "title": "Titre de l'article",
  "link": "https://...",
  "published_at": "2025-11-25T10:30:00",
  "short_summary": "Résumé très court (3 phrases max)",
  "detailed_summary": "Résumé détaillé (10-15 lignes)",
  "tags": ["tag1", "tag2", ...],
  "type_contenu": "news|recherche|tuto|produit|opinion",
  "audience": "débutant|intermédiaire|expert",
  "score_global": 85,
  "score_details": "Article très pertinent pour... Raison de la note."
}
```

## 📜 Licence

MIT

## 👨‍💻 Auteur

Créé pour HETIC – Projet Multi-agent Newsletter
