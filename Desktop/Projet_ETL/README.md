# ETL Data Extraction Interface

Ce dépôt contient un notebook d'extraction et une application Gradio de démonstration.

Déployer sur Hugging Face Spaces (résumé):

1. Créez un repo Space (Python) sur https://huggingface.co/spaces
2. Poussez ce dépôt (ou copiez `app.py` + `requirements.txt`) dans le repo Space
3. Le Space démarrera automatiquement et exposera l'interface publique

Exécuter localement:

```bash
pip install -r requirements.txt
python app.py
```

L'interface sera accessible sur `http://localhost:7860`.

Remarque: L'application `app.py` propose une démo OCR locale.

Intégration Tensorlake:

- Placez votre clé API dans la variable d'environnement `TENSORLAKE_API_KEY` avant d'exécuter l'app localement, par exemple:

```bash
export TENSORLAKE_API_KEY="tl_apiKey_..."   # macOS / Linux
setx TENSORLAKE_API_KEY "tl_apiKey_..."    # Windows (PowerShell may require $env:...)
```

- Sur Hugging Face Spaces, définissez un secret (Settings → Secrets) nommé `TENSORLAKE_API_KEY`.

Lorsque la clé est présente, l'application tentera d'appeler Tensorlake pour obtenir une extraction structurée et affichera le résultat JSON dans l'interface.

Installation de Tesseract et Poppler (Windows)

L'OCR requiert le binaire Tesseract (pytesseract est une interface Python). Installez l'un des paquets suivants, puis ajoutez le dossier `Tesseract-OCR` à votre `PATH`, ou définissez `TESSERACT_CMD` vers l'exécutable.

Via Chocolatey (si installé):

```powershell
choco install tesseract -y
choco install poppler -y
```

Téléchargements manuels:

- Tesseract (Windows installer) — ex. UB Mannheim: https://github.com/UB-Mannheim/tesseract/wiki
- Poppler for Windows (binaries) — par ex. https://github.com/oschwartz10612/poppler-windows/releases

Après installation, ajoutez les répertoires `C:\Program Files\Tesseract-OCR` (ou équivalent) et le `bin` de Poppler à la variable d'environnement `PATH`, ou définissez temporairement pour la session PowerShell:

```powershell
$env:TESSERACT_CMD = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
$env:POPPLER_PATH = "C:\\path\\to\\poppler-xx\\Library\\bin"
```

Alternativement, définissez `TESSERACT_CMD` et/ou `POPPLER_PATH` comme variables d'environnement permanentes via les Paramètres Windows.

Vérifiez l'installation:

```powershell
tesseract --version
pdftoppm -h
```

Si vous préférez ne pas modifier le `PATH`, définissez `TESSERACT_CMD` et `POPPLER_PATH` et relancez `app.py`.
