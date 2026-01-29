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
