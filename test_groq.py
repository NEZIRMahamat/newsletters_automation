# test_groq.py
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API'))

try:
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "Test de connexion"}],
        model="llama3-8b-8192",
    )
    print("✅ Connexion Groq réussie!")
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"❌ Erreur Groq: {e}")