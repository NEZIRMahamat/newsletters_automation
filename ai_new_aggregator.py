import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_complete():
    print("=== DIAGNOSTIC COMPLET GROQ ===")
    
    # Test 1: Fichier .env
    api_key = os.getenv('GROQ_API_KEY')
    print(f"1. Clé API: {'✅ Trouvée' if api_key else '❌ Manquante'}")
    if api_key:
        print(f"   - Longueur: {len(api_key)} caractères")
        print(f"   - Début: {api_key[:15]}...")
    
    # Test 2: Connexion Internet
    try:
        response = requests.get("https://api.groq.com", timeout=10)
        print(f"2. Connexion à api.groq.com: ✅ ({response.status_code})")
    except Exception as e:
        print(f"2. Connexion à api.groq.com: ❌ {e}")
        return
    
    # Test 3: Test direct de l'API Groq
    if api_key:
        try:
            # Test avec requests directement
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "messages": [{"role": "user", "content": "Test"}],
                "model": "llama3-8b-8192",
                "max_tokens": 10
            }
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            print(f"3. Test API direct: ✅ ({response.status_code})")
            if response.status_code != 200:
                print(f"   - Erreur: {response.text}")
        except Exception as e:
            print(f"3. Test API direct: ❌ {e}")
    
    # Test 4: Vérifier le package groq
    try:
        from groq import Groq
        print("4. Package groq: ✅")
        
        # Test avec le client Groq
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "Dis bonjour"}],
            model="llama3-8b-8192",
            max_tokens=5,
            timeout=30
        )
        print("5. Client Groq: ✅")
        print(f"   - Réponse: {chat_completion.choices[0].message.content}")
        
    except Exception as e:
        print(f"4/5. Package/Client Groq: ❌ {e}")

if __name__ == "__main__":
    test_complete()