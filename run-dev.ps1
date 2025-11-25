# Script de lancement du projet Multi-agent Newsletter

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Multi-agent IA Newsletter" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si venv existe
if (!(Test-Path ".\.venv")) {
    Write-Host "[1/4] Création de l'environnement virtuel..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur: Impossible de créer le venv" -ForegroundColor Red
        exit 1
    }
}

# Activer venv
Write-Host "[2/4] Activation du venv..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur: Impossible d'activer le venv" -ForegroundColor Red
    exit 1
}

# Installer les dépendances
Write-Host "[3/4] Installation des dépendances..." -ForegroundColor Yellow
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur: Impossible d'installer les dépendances" -ForegroundColor Red
    exit 1
}

# Vérifier/créer le fichier .env
if (!(Test-Path ".env")) {
    Write-Host "[4/4] Création du fichier .env..." -ForegroundColor Yellow
    # On crée un fichier .env avec placeholder
    @"
# Clé API Groq (à obtenir sur https://console.groq.com)
GROQ_API_KEY=ta_clef_groq_ici
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "⚠️  Veuillez éditer le fichier .env et y insérer votre clé Groq" -ForegroundColor Yellow
} else {
    Write-Host "[4/4] Fichier .env trouvé ✓" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "Démarrage du serveur FastAPI" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "L'API est disponible à: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "La documentation: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "L'interface web: http://127.0.0.1:8000/ui" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur" -ForegroundColor Yellow
Write-Host ""

# Démarrer le serveur
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
