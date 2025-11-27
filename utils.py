
import os
from time import time
from groq import Groq
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

"""
    Module des fonctions utilitaires.
    pour la lecture de fichiers, etc.

"""

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Fonction pour lire le contenu d'un fichier
def read_file(file_path: str) -> str | None:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        return None

# Fonction pour initialiser le client Groq
def get_groq_client() -> Groq | None:
    try:
        client = Groq()
        return client
    except Exception as e:
        print(f"Erreur lors de la création du client Groq: {e}")
        return None
    
def get_elevenlabs_client() -> ElevenLabs | None:
    """
    Initialise et retourne le client ElevenLabs.
    Utilise la clé API depuis la variable d'environnement ELEVEN_API_KEY.
    """
    try:
        client = ElevenLabs(api_key=os.getenv("ELEVEN_API_KEY"))
        return client
    except Exception as e:
        print(f"Erreur lors de la création du client ElevenLabs: {e}")
        return None

def text_to_speech_elevenlabs(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb", 
                              output_dir: str = "data") -> tuple[str, bool] | None:
    """
    Convertit du texte en audio avec ElevenLabs et renvoie le fichier audio.
    
    Args:
        text: Le texte à convertir en audio
        voice_id: ID de la voix à utiliser (par défaut: Rachel)
        output_path: Chemin où sauvegarder le fichier audio
    
    Returns:
        Tuple (Chemin du fichier audio + True) si la conversion a réussi, sinon (None, False).
    """
    random_three_chars = ''.join(os.urandom(3).hex())
    file_name = f"output_audio_{int(time.time())}_{random_three_chars}.mp3"
    output_file_path = os.path.join(output_dir, file_name)
    try:
        client = get_elevenlabs_client()
        if not client:
            return None, False
        
        # Générer l'audio avec la méthode correcte
        audio = client.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_44100_128",
            text=text,
            model_id="eleven_multilingual_v2"
        )
        
        # Sauvegarder l'audio dans un fichier
        with open(output_file_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
        
        print(f"Audio généré avec succès : {output_file_path}")
        return output_file_path, True
        
    except Exception as e:
        print(f"Erreur lors de la génération audio: {e}")
        return None, False