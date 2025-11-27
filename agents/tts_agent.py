"""
Agent TTS pour générer des résumés audio des articles via gTTS (Google Text-to-Speech).
"""
import os
from typing import Optional
from gtts import gTTS


def generate_article_audio(summary_text: str, output_path: str = "audio_output.mp3") -> Optional[str]:
    """
    Génère un fichier audio MP3 à partir d'un résumé d'article en utilisant gTTS (gratuit).
    
    Args:
        summary_text: Le texte du résumé à convertir en audio
        output_path: Chemin du fichier audio de sortie
    
    Returns:
        Le chemin du fichier audio généré, ou None en cas d'erreur
    """
    try:
        # Générer l'audio avec gTTS (Google Text-to-Speech)
        tts = gTTS(text=summary_text, lang='fr', slow=False)
        tts.save(output_path)
        
        print(f"✅ Audio généré avec gTTS : {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Erreur génération audio avec Groq TTS : {e}")
        return None


def generate_newsletter_audio_summary(articles, newsletter_hash: str) -> Optional[str]:
    """
    Génère un résumé audio global de toutes les news (3-5 minutes).
    
    Args:
        articles: Liste d'articles enrichis
        newsletter_hash: Hash unique de la newsletter
    
    Returns:
        Chemin du fichier audio ou None
    """
    if not articles:
        return None
    
    # Créer un dossier pour les audios si nécessaire
    os.makedirs("audio_cache", exist_ok=True)
    
    # Construire le script audio
    intro = "Bonjour et bienvenue dans votre résumé d'actualités. Voici les principales informations du jour.\n\n"
    
    articles_text = []
    for i, art in enumerate(articles[:10], 1):  # Limiter à 10 articles max
        title = art.title if hasattr(art, 'title') else "Article sans titre"
        summary = art.short_summary if hasattr(art, 'short_summary') else (art.summary if hasattr(art, 'summary') else "Pas de résumé")
        articles_text.append(f"Article {i}: {title}. {summary}")
    
    outro = "\n\nC'est tout pour ce résumé d'actualités. Merci de votre écoute."
    
    # Assembler le texte complet
    full_text = intro + " ".join(articles_text) + outro
    
    # Limiter à environ 3-5 minutes (environ 1800-3000 caractères)
    max_chars = 2500
    if len(full_text) > max_chars:
        full_text = full_text[:max_chars] + "... et bien d'autres actualités encore."
    
    # Générer le fichier audio
    output_path = f"audio_cache/newsletter_{newsletter_hash}.mp3"
    return generate_article_audio(full_text, output_path)
