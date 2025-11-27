import json
from groq import Groq
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import read_file



def resume_classifier_content_from_rss(client : Groq, prompts_entry: str) -> dict:
    try:
        prompt = read_file("prompts_agents/prompt_agent_1.txt")
        context = read_file("contents_agents/context_agent_1.txt")
        if not prompt and not context:
            return None
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": f"{prompt}\n\nVoici les articles des flux RSS:\n{prompts_entry}"},
            ],
            model="openai/gpt-oss-20b",
            response_format={"type": "json_object"},
            #max_tokens=8000,  # Augmenté pour générer le JSON complet
            temperature=0.2,
        )
        results = json.loads(response.choices[0].message.content.strip())
        
        return results
    
    except Exception as e:
        print(f"Erreur lors de la génération des résumé(s) des article(s) avec Groq: {e}")
        return None






