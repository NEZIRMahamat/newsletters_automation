import json
import csv
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path("config_user.json")
CONTACTS_CSV = Path("contacts_newsletters.csv")

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

# ---------------------------------------------------------------------
# Gestion des contacts via CSV
# ---------------------------------------------------------------------
def load_contacts_from_csv():
    """Charge tous les contacts depuis le fichier CSV"""
    if not CONTACTS_CSV.exists():
        CONTACTS_CSV.write_text("email,nom,date_ajout\n", encoding="utf-8")
        return []
    
    contacts = []
    with open(CONTACTS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append(row)
    return contacts

def add_contact_to_csv(email: str, nom: str = ""):
    """Ajoute un contact au fichier CSV s'il n'existe pas déjà"""
    contacts = load_contacts_from_csv()
    
    # Vérifier si l'email existe déjà
    for contact in contacts:
        if contact['email'] == email:
            return False  # Email déjà existant
    
    # Ajouter le nouveau contact
    with open(CONTACTS_CSV, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([email, nom, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    
    return True

def remove_contact_from_csv(email: str):
    """Supprime un contact du fichier CSV"""
    contacts = load_contacts_from_csv()
    contacts = [c for c in contacts if c['email'] != email]
    
    with open(CONTACTS_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['email', 'nom', 'date_ajout'])
        writer.writeheader()
        writer.writerows(contacts)
    
    return True

def get_all_emails_from_csv():
    """Retourne la liste de tous les emails du CSV"""
    contacts = load_contacts_from_csv()
    return [c['email'] for c in contacts if c['email']]
