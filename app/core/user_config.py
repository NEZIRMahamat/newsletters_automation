import json
from pathlib import Path

CONFIG_FILE = Path("config_user.json")

DEFAULT_CONFIG = {
    "frequence_generation": "hebdomadaire",
    "emails_destinataires": [],
    "themes_actifs": [],
    "heure_generation": "09:00",
}

def load_user_config():
    if not CONFIG_FILE.exists():
        save_user_config(DEFAULT_CONFIG)
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))

def save_user_config(config: dict):
    CONFIG_FILE.write_text(
        json.dumps(config, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
