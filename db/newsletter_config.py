"""
Gestion de la configuration de la newsletter utilisateur.
Stockage en JSON simple (peut être remplacé par SQLAlchemy + DB si nécessaire).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Fichier de stockage des configurations
CONFIG_FILE = Path(__file__).parent / "newsletter_config.json"

# Configuration par défaut
DEFAULT_CONFIG = {
    "domain": "ia_generale",
    "num_articles": 10,
    "frequency": "weekly",  # "daily", "weekly", "monthly"
    "last_sent": None,
    "use_llm": False,
}


def load_config(user_id: str = "default") -> Dict[str, Any]:
    """Charge la configuration d'un utilisateur."""
    if not CONFIG_FILE.exists():
        return DEFAULT_CONFIG.copy()
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            all_configs = json.load(f)
        return all_configs.get(user_id, DEFAULT_CONFIG.copy())
    except Exception as e:
        print(f"Erreur lors de la lecture de config: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any], user_id: str = "default") -> None:
    """Sauvegarde la configuration d'un utilisateur."""
    try:
        # Charger les configs existantes
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                all_configs = json.load(f)
        else:
            all_configs = {}
        
        # Mettre à jour la config de cet utilisateur
        all_configs[user_id] = config
        
        # Sauvegarder
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(all_configs, f, indent=2)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de config: {e}")


def update_config(updates: Dict[str, Any], user_id: str = "default") -> Dict[str, Any]:
    """Met à jour partiellement la configuration et retourne la config finale."""
    config = load_config(user_id)
    config.update(updates)
    save_config(config, user_id)
    return config


def update_last_sent(user_id: str = "default") -> None:
    """Met à jour la date de dernier envoi."""
    config = load_config(user_id)
    config["last_sent"] = datetime.now().isoformat()
    save_config(config, user_id)
