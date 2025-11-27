import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv

# Charger .env
load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS") == "True"

def test_email():
    print("📨 Test d'envoi d'email via Gmail…")

    destinataire = input("👉 Entre un email de test : ").strip()
    if not destinataire:
        print("❌ Aucun destinataire entré.")
        return

    # Construire message
    subject = "Test SMTP – Veille IA"
    body = "Si tu vois cet email, c'est que ton SMTP Gmail fonctionne !"

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = formataddr(("Test SMTP", EMAIL_FROM))
    msg["To"] = destinataire

    try:
        # Connexion SMTP
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        if SMTP_USE_TLS:
            server.starttls()

        # Authentification
        print("🔐 Connexion au serveur Gmail…")
        server.login(EMAIL_FROM, EMAIL_PASSWORD)

        # Envoi
        print("📤 Envoi...")
        server.sendmail(EMAIL_FROM, [destinataire], msg.as_string())
        server.quit()

        print("✅ EMAIL ENVOYÉ AVEC SUCCÈS !")
    except Exception as e:
        print("❌ ERREUR SMTP :", e)


if __name__ == "__main__":
    test_email()
