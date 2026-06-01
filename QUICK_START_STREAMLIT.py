"""
Quick Start Guide - Streamlit Dashboard
Lancez le dashboard en 30 secondes!
"""

# ===== COMMANDES =====

"""
1. PRÉPARATION (one-time setup)
================================

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et remplir les valeurs

# Créer les données (si pas déjà fait)
python run_pipeline.py


2. LANCER LE DASHBOARD
======================

# Option A: Lancement simple
streamlit run dashboard/app.py

# Option B: Avec debug
streamlit run dashboard/app.py --logger.level=debug

# Option C: Sur un port spécifique
streamlit run dashboard/app.py --server.port=8502

# Accéder: http://localhost:8501


3. ARRÊTER
==========

# Ctrl+C dans le terminal


4. DÉVELOPPEMENT
================

# Streamlit rechargera automatiquement les changements
# Juste éditer le fichier et F5 dans le navigateur
"""

# ===== STRUCTURE DES PAGES =====

PAGES = {
    "📊 Dashboard": {
        "description": "Vue d'ensemble KPIs",
        "features": [
            "💰 Total Spend",
            "📈 Total Revenue", 
            "🎯 ROI",
            "📊 3 trends (Revenue, Spend, ROI)",
            "🥧 Channel mix pie chart",
            "📅 Date filtering"
        ],
        "use_when": "Vous voulez un aperçu rapide du jour"
    },
    
    "📈 Analyse Canaux": {
        "description": "Performance détaillée par canal",
        "features": [
            "🎯 Sélecteur de canal",
            "💰 Total spend par canal",
            "📈 ROI par canal",
            "📊 Scatter plot: Spend vs Revenue"
        ],
        "use_when": "Vous analysez la performance d'un canal spécifique"
    },
    
    "🎯 Scenarios": {
        "description": "What-if budget analysis",
        "features": [
            "💰 Budget actuel affiché",
            "🎚️ Sliders pour ajuster l'allocation %",
            "✅ Validation du budget",
            "📊 Tableau: Current vs Proposed"
        ],
        "use_when": "Vous testez différentes stratégies budgétaires"
    },
    
    "🎨 Attribution": {
        "description": "Multi-touch attribution",
        "features": [
            "📊 5 modèles d'attribution",
            "🎯 First Touch, Last Touch, Linear, Time Decay, Shapley",
            "📈 Bar chart: Revenue par canal"
        ],
        "use_when": "Vous voulez comprendre la vraie contribution de chaque canal"
    },
    
    "⚙️ Configuration": {
        "description": "Settings et documentation",
        "features": [
            "📊 Data status (rows, cols)",
            "🔧 Channel config (decay, saturation)",
            "📚 Links vers la documentation"
        ],
        "use_when": "Vous avez besoin de vérifier la configuration"
    }
}

# ===== DÉPENDANCES =====

"""
Streamlit & Visualization:
- streamlit              ← App framework
- streamlit-plotly-events  ← Interactions Plotly
- plotly                ← Graphs interactives

Data & Science:
- pandas                ← Data manipulation
- numpy                 ← Numerical computing
- scikit-learn          ← ML utilities

BigQuery & Cloud:
- google-cloud-bigquery ← BigQuery client
- google-cloud-bigquery-storage ← Optimized transfers

Analytics & Attribution:
- shap                  ← Shapley values
- pymc                  ← Bayesian modeling (future)

Utils:
- requests              ← HTTP (for Looker API)
- python-dotenv         ← .env support
"""

# ===== FICHIERS KEY =====

"""
dashboard/
├── app.py                      ← Main app (5 pages)
├── looker_integration.py       ← Looker embeddings
└── pages/
    └── looker_dashboards.py    ← Looker page

data/processed/
├── mmm_ready.csv               ← Main data file (loaded by app)
├── mmm_clean.csv
├── mmm_with_features.csv
├── mmm_normalized.csv
├── adstock_params.pkl
└── normalization_params.pkl

looker/
├── lookml_models.py            ← LookML definitions
└── credentials.json            ← (Ne pas commiter!)

.env                            ← Configuration (Ne pas commiter!)
requirements.txt                ← Python dependencies
.env.example                    ← Template pour .env
"""

# ===== EXAMPLE WORKFLOWS =====

WORKFLOWS = {
    "Vérifier le health du marketing aujourd'hui": """
    1. streamlit run dashboard/app.py
    2. Aller à: 📊 Dashboard
    3. Voir: KPIs du jour (Spend, Revenue, ROI)
    4. Vérifier: Les trends ne sont pas anormales
    """,
    
    "Analyser la performance de Google Search": """
    1. Aller à: 📈 Analyse Canaux
    2. Sélectionner: GOOGLE_PAID_SEARCH_SPEND
    3. Voir: Total spend, ROI
    4. Analyser: Le scatter plot (tendance?)
    """,
    
    "Tester une nouvelle allocation budgétaire": """
    1. Aller à: 🎯 Scenarios
    2. Ajuster: Les sliders pour les canaux
    3. Vérifier: Que l'allocation = 100%
    4. Voir: Proposed budget vs Current
    5. Note: Nécessite un modèle PyMC3 pour les prédictions
    """,
    
    "Comprendre la vraie contribution de chaque canal": """
    1. Aller à: 🎨 Attribution
    2. Comparer: Linear vs Shapley Value
    3. Voir: Comment le revenue est attribué
    4. Action: Ajuster la stratégie en conséquence
    """,
    
    "Vérifier les données": """
    1. Aller à: ⚙️ Configuration
    2. Onglet: 📊 Data Status
    3. Voir: Combien de rows, colonnes
    4. Vérifier: mmm_ready.csv existe
    """,
}

# ===== TROUBLESHOOTING =====

ERRORS = {
    "ModuleNotFoundError: No module named 'streamlit'": """
    Solution:
    pip install streamlit
    """,
    
    "FileNotFoundError: data/processed/mmm_ready.csv": """
    Solution:
    1. Lancez la pipeline:
       python run_pipeline.py
    2. Vérifiez que le fichier existe:
       data/processed/mmm_ready.csv
    """,
    
    "Streamlit keeps reloading": """
    Solution:
    Appuyez sur 'R' dans l'app Streamlit pour réinitialiser
    ou Ctrl+C pour arrêter et relancer
    """,
    
    "Credentials not found for LOOKER": """
    Solution:
    1. Configurez .env:
       cp .env.example .env
    2. Remplissez les variables:
       LOOKER_API_HOST=...
       LOOKER_API_KEY=...
       LOOKER_API_SECRET=...
    3. Source .env ou définissez les env vars:
       export LOOKER_API_HOST=...
    """,
}

# ===== PERFORMANCE TIPS =====

TIPS = {
    "Streamlit est lent": """
    1. Utiliser @st.cache_data:
       @st.cache_data
       def load_data():
           return pd.read_csv('data.csv')
    
    2. Réduire la taille des données:
       df_filtered = df[df.date > '2024-01-01']
    
    3. Utiliser LazyDataFrame ou DuckDB pour big data
    """,
    
    "Les graphs sont lents": """
    1. Utiliser Plotly express au lieu de ggplot
    2. Limiter le nombre de points:
       df_sampled = df.sample(min(1000, len(df)))
    3. Désactiver les transitions:
       fig.update_layout(transition=dict(duration=0))
    """,
    
    "Looker embed est lent": """
    1. Vérifier les permissions Looker
    2. Utiliser les filtres (pour activer le cache)
    3. Contacter l'admin Looker pour optimiser
    """,
}

# ===== NEXT STEPS =====

NEXT = """
✅ Étape 1: ETL Pipeline (FAIT)
✅ Étape 2: Streamlit Dashboard (FAIT)
⏳ Étape 3: PyMC3 Modeling
   - Entraîner le modèle MMM
   - Estimer les coefficients par canal
   - Prédire le ROI pour les scenarios

⏳ Étape 4: Attribution Shapley
   - Calculer la contribution réelle de chaque canal
   - Comparer avec les autres modèles d'attribution

⏳ Étape 5: Looker Integration
   - Créer les modèles LookML
   - Créer les dashboards Looker
   - Configurer les credentials
   - Intégrer dans Streamlit

⏳ Étape 6: Production Deployment
   - Déployer sur Cloud Run / App Engine
   - Configurer les secrets
   - Mettre en place les monitoring/alertes
"""

if __name__ == "__main__":
    print("🎨 Streamlit Dashboard Quick Start")
    print("=" * 60)
    print("\n🚀 LANCER:")
    print("streamlit run dashboard/app.py")
    print("\n📖 PAGES DISPONIBLES:")
    for page, info in PAGES.items():
        print(f"\n{page}")
        print(f"  {info['description']}")
        print(f"  Quand: {info['use_when']}")
    print("\n" + "=" * 60)
