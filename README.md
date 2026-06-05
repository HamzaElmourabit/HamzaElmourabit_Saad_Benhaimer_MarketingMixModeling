# 🎯 Marketing Mix Modeling (MMM) avec attribution multi_touch — Projet Complet

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28.1-FF4B4B)](https://streamlit.io)
[![Scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-F7931E)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Système end-to-end pour analyser l'efficacité des canaux marketing, estimer les contributions des dépenses publicitaires et simuler des scénarios budgétaires.

## 📚 Documentation Complète

Trois niveaux de documentation sont disponibles :

| Document | Contenu | Format | Usage |
|----------|---------|--------|-------|
| **[README.md](README.md)** (ce fichier) | Vue d'ensemble générale | Markdown | Introduction rapide |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Architecture détaillée, flux ETL, pipeline, technologies | Markdown | Compréhension technique complète |
| **[Rapport_Projet18.pdf](Rapport_Projet18.pdf)** | Rapport professionnel ~30 pages avec images réelles | PDF | Reporting executive, publication |

## 🚀 Démarrage Rapide

### Installation (5 minutes)

```bash
# 1. Clone ou télécharger le projet
cd MMM_Project

# 2. Créer environment virtuel
python -m venv venv
source venv/bin/activate  # ou: venv\Scripts\activate (Windows)

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer environnement
cp .env.example .env
# Éditer .env avec vos paramètres (BigQuery, Looker, etc.)
```

### Lancer le Dashboard (2 minutes)

```bash
streamlit run dashboard/app.py
# Accès : http://localhost:8501
```

### Exécuter le Pipeline ETL (15 minutes)

```bash
# Première exécution : données brutes → données prêtes
python run_pipeline.py

# Options :
python run_pipeline.py --validate-only    # Validation uniquement
python run_pipeline.py --clean-only       # Nettoyage uniquement
python run_pipeline.py --bigquery         # + Export BigQuery
```

**Résultat** : `data/processed/mmm_ready.csv` (utilisé par le dashboard)

---

## 🏗️ Architecture Globale

```
┌─────────────────────────────────────────────────────────────────┐
│                    MMM SYSTEM ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Raw Data             ETL Pipeline          Processed Data     │
│  └─ compressed_data   ├─ validation         └─ mmm_ready.csv   │
│     .csv              ├─ cleaning                               │
│                       ├─ event_enrichment                       │
│                       ├─ feature_engineering (adstock, sat)     │
│                       ├─ normalization                          │
│                       └─ export                                 │
│                             ↓                                   │
│                    ┌────────┴────────┐                          │
│                    ↓                 ↓                          │
│              Models              Dashboard                      │
│         (mmm_model.py)      (Streamlit app.py)                 │
│         └─ Ridge Regression  ├─ Dashboard (KPIs)               │
│            · Training         ├─ Channels Analysis              │
│            · Attribution      ├─ Budget Scenarios               │
│            · Prediction       ├─ Attribution                    │
│                                ├─ Looker Embed                  │
│                                └─ Configuration                 │
│                                       ↓                         │
│                    ┌──────────────────┴────────────┐            │
│                    ↓                               ↓            │
│                BigQuery                      PDF Report         │
│           (Analytics DB)                   (MMM_Report.pdf)    │
│         └─ mmm table                    with real images       │
│            (for Looker)                 & technologies         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Pour la **documentation architecture détaillée** → voir [ARCHITECTURE.md](ARCHITECTURE.md)

### Illustrations clés

![Architecture du pipeline](Assets/architecture_mmm.png)  
**Figure 1** : Architecture MMM — Pipeline ETL complet (ingestion → modélisation → dashboard)

![Interface dashboard](Assets/Interface_dashboard.png)  
**Figure 2** : Interface Streamlit — Vue principale du dashboard avec KPIs et tendances

![Attribution multi-touch](Assets/Attribution_multi_touch.png)  
**Figure 3** : Attribution multi-touch — Breakdown des contributions par canal marketing

![Scénarios budgétaires](Assets/Budget_Scenarios_What_if.png)  
**Figure 4** : Simulations budgétaires — What-if analysis avec sliders et prédictions

![ROI global](Assets/ROI_Global.png)  
**Figure 5** : ROI global — Vue synthétique de la performance par canal

![Top 5 canaux dépensiers](Assets/Top_5_canaux_les_plus_dépensiers.png)  
**Figure 6** : Top 5 canaux — Ranking des dépenses marketing par canal

![Dashboard_Looker](Assets/Dashboard_Looker.png)
**Figure 7** : Lokker_Dashboard

### Composants principaux

1. `data/` :
   - `raw/` : sources brutes
   - `processed/` : données prêtes pour MMM
   - `reference/` : fichiers de référence (holidays, events)

2. `etl/` : pipeline Data
   - `config.py` : chemins et paramètres
   - `validation.py` : règles qualité et cohérence
   - `clean.py` : nettoyage, type casting, uniformisation
   - `event_enrichment.py` : ajout de features calendrier et événements
   - `feature_engineering.py` : adstock, lags, saturations, interactions
   - `normalize.py` : normalisation / standardisation
   - `pipeline.py` : orchestrateur de bout en bout
   - `load_bigquery.py` : export vers BigQuery

3. `bigquery/` :
   - `schema.sql` : définition du modèle de données
   - `queries.sql` : requêtes d’analyse exemple

4. `dashboard/` :
   - `app.py` : application Streamlit principale
   - `looker_integration.py` : génération d’embed Looker
   - `pages/looker_dashboards.py` : page Streamlit dédiée à Looker

5. `looker/` :
   - `lookml_models.py` : exemples LookML pour le modèle et le dashboard

6. `run_pipeline.py` : exécution rapide de la pipeline Data
7. `.env.example` : variables de configuration
8. `requirements.txt` : dépendances Python

## 🧠 Architecture détaillée

### Flux de données

1. Les fichiers bruts sont lus depuis `data/raw/`
2. La pipeline ETL vérifie la qualité, nettoie et enrichit les données
3. Le résultat `data/processed/mmm_ready.csv` est créé
4. Le jeu de données peut être chargé dans BigQuery
5. Les dashboards Streamlit et Looker consomment les données transformées

### Orchestrateur ETL

- `etl/pipeline.py` orchestre toutes les étapes
- `run_pipeline.py` déclenche le pipeline de manière simple
- Les modules sont découplés pour faciliter l’ajout de nouvelles transformations ou de tests

### Modélisation MMM

Le projet est prévu pour une modélisation Bayésienne MMM basée sur :
- `pymc` / `arviz`
- des variables marketing transformées (adstock, saturation)
- des termes de saisonnalité et d’événement
- des variables d’output comme le revenu ou les ventes

Une version de démonstration est actuellement implémentée dans `models/mmm_model.py` avec une régression Ridge sur les features adstockées et les contrôles.

### Objectifs de la modélisation

- estimer l’impact de chaque canal marketing sur les ventes
- produire des elasticités de dépense
- simuler des budgets alternatifs et optimiser l’allocation
- fournir une base pour une attribution multi-touch robuste

## 📁 Structure détaillée

- `data/raw/compressed_data.csv` : input brut
- `data/processed/mmm_ready.csv` : output ETL prêt pour modélisation
- `data/reference/holidays.csv` : calendrier d’événements
- `etl/clean.py` : nettoyage et préparation initiale
- `etl/validation.py` : règles métier et qualité des données
- `etl/event_enrichment.py` : features événementielles
- `etl/feature_engineering.py` : calcul des drives marketing
- `etl/normalize.py` : mise à l’échelle et standardisation
- `etl/pipeline.py` : classe `ETLPipeline`
- `etl/load_bigquery.py` : chargement BigQuery
- `bigquery/schema.sql` : schéma table MMM
- `bigquery/queries.sql` : requêtes analytiques utiles
- `dashboard/app.py` : interface Streamlit
- `dashboard/looker_integration.py` : connexion Looker/embed
- `dashboard/pages/looker_dashboards.py` : page Looker
- `looker/lookml_models.py` : templates LookML
- `run_pipeline.py` : exécution unique de la pipeline
- `MMM_Report.tex` : rapport de synthèse en LaTeX
- `.env.example` : configuration
- `requirements.txt` : packages requis

## ⚙️ Installation

1. Installer les dépendances :

```bash
pip install -r requirements.txt
```

2. Copier et configurer les variables d’environnement :

```bash
cp .env.example .env
```

3. Mettre à jour `.env` avec vos paramètres GCP et Looker :

```text
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
GCP_PROJECT_ID=your-gcp-project
BIGQUERY_DATASET_ID=MMM_dataset
BIGQUERY_TABLE_ID=mmm
RAW_DATA_PATH=data/raw/compressed_data.csv
PROCESSED_DATA_PATH=data/processed/
LOOKER_API_HOST=https://looker.company.com
LOOKER_API_KEY=your-looker-api-key
LOOKER_API_SECRET=your-looker-api-secret
LOOKER_DASHBOARD_IDS=mmm_overview,channel_performance,roi_analysis
LOOKER_EMBED_USER_EMAIL=mmm-user@company.com
LOOKER_EMBED_USER_NAME=MMM User
```

## 📊 Exécution de la pipeline Data

```bash
python run_pipeline.py
```

### Résultat

- Fichier transformé : `data/processed/mmm_ready.csv`
- Table BigQuery mise à jour si `etl/load_bigquery.py` est utilisé

## 🧠 Partie modélisation

### Étapes attendues

1. Charger `data/processed/mmm_ready.csv`
2. Sélectionner la cible RH : `revenue`, `first_purchases`, ou autre KPI business
3. Construire le modèle MMM :
   - canaux marketing transformés (`adstock`, `saturation`, `lags`)
   - variables de contrôle (budget, jours fériés, événements)
   - distribution Bayésienne des coefficients
4. Évaluer la qualité du modèle avec `arviz`
5. Utiliser le modèle pour :
   - prédire les ventes
   - simuler des scenarii budgétaires
   - calculer l’attribution de canal

### Exemple de composants à ajouter

- `etl/modeling.py` : préparation du jeu de données pour PyMC
- `models/memory.py` : logique d’adstock et de saturation
- `models/mcmc.py` : définition du modèle PyMC
- `analysis/model_diagnostics.py` : diagnostics de convergence et de fit
- `models/mmm_model.py` : modèle initial de régression MMM utilisé par le dashboard

### Variables clés du modèle

- `date_day` : dimension temporelle
- `google_search_spend`, `google_display_spend`, `meta_facebook_spend`, etc.
- `revenue` : target principal
- `holidays`, `events` : variables de contrôle
- `channel_adstock` : effet différé des investissements
- `channel_saturation` : effet de seuil et retour décroissant

## 📈 Dashboard Streamlit

Lancer localement :

```bash
streamlit run dashboard/app.py
```

### Pages disponibles
- `Dashboard` : KPI, tendances, mix media
- `Analyse Canaux` : profil et ROI par canal
- `Scenarios` : simulation d’allocation budgétaire
- `Attribution` : attribution multi-touch (héritage)
- `Looker` : dashboards Looker embarqués
- `Configuration` : état des données et documentation

## 🔗 Looker Embed

### Fonctionnement

- `dashboard/looker_integration.py` se connecte à l’API Looker
- `dashboard/pages/looker_dashboards.py` affiche les dashboards disponibles et l’iframe embed
- `looker/lookml_models.py` fournit des templates LookML

### Fichiers LookML recommandés

- `model/mmm.model`
- `views/mmm.view`
- `views/mmm_channels.view`
- `dashboards/mmm_overview.dashboard`

### Bonnes pratiques

- Créez un service account Looker avec droits d’accès aux dashboards
- Activez l’embed pour les dashboards / espaces de travail
- Vérifiez que `LOOKER_API_HOST` pointe vers votre instance Looker

## 🧪 Tests

Exécuter :

```bash
pytest
```

## 🔧 Développement futur

- Ajouter `etl/modeling.py` pour l’entrainement MMM
- Intégrer un notebook d’analyse (`notebooks/MMM_model.ipynb`)
- Automatiser la pipeline via Airflow, Prefect ou GitHub Actions
- Ajouter des tests unitaires pour l’ETL, la modélisation et les dashboards
- Déployer le dashboard sur un service Streamlit Cloud ou Azure App Service

## 💡 Notes

- Le modèle Looker et les dashboards sont des exemples de base ; adaptez-les à vos dimensions et métriques métiers.
- Le code est modulable pour ajouter des canaux marketing ou des variables de contrôle supplémentaires.
- La modélisation Bayésienne est le prochain niveau : structurez la préparation des données dans `etl/modeling.py`.

---

### Auteur
Hamza Elmourabit 
Saad Benhaimer
Projet Marketing Mix Modeling : pipeline Data, modèle, dashboard et intégration BI.

---

## ⚡ Exécution Pas à Pas

### 1️⃣ Pré-requis

- Python 3.8+
- Données brutes : `data/raw/compressed_data.csv`
- (Optionnel) Compte GCP pour BigQuery
- (Optionnel) Instance Looker pour dashboards

### 2️⃣ Installation

```bash
pip install -r requirements.txt
cp .env.example .env
# Éditer .env avec credentials
```

### 3️⃣ Pipeline ETL

```bash
python run_pipeline.py
# ✅ Output: data/processed/mmm_ready.csv
```

### 4️⃣ Dashboard Streamlit

```bash
streamlit run dashboard/app.py
# Accès: http://localhost:8501
```

### 5️⃣ Rapport LaTeX (optionnel)

```bash
pdflatex MMM_Report_Final.tex
pdflatex MMM_Report_Final.tex
# ✅ Output: MMM_Report_Final.pdf
```

### 6️⃣ BigQuery (optionnel)

```bash
# Charger dans BigQuery (si configuré dans .env)
python run_pipeline.py --bigquery
```

---

## 📈 Workflow Exemple : Simuler un Budget

1. **Ouvrir le dashboard**
   ```bash
   streamlit run dashboard/app.py
   ```

2. **Aller à la page « Scénarios »**

3. **Ajuster les sliders** pour proposer un nouveau budget par canal

4. **Observer la prédiction de revenu** basée sur le modèle entraîné

5. **Comparer** avec le scénario baseline

6. **Exporter** les résultats

Temps total : **~10 minutes**

---

## ✅ Checklist Mise en Production

- [ ] Données brutes validées
- [ ] Pipeline ETL exécutée avec succès
- [ ] Modèle MMM entraîné et validé
- [ ] Dashboard Streamlit testé localement
- [ ] BigQuery configuré et chargé (optionnel)
- [ ] Looker dashboards créés (optionnel)
- [ ] Rapport PDF généré
- [ ] `.env` configuré avec credentials
- [ ] Tests unitaires passent : `pytest`

---

## 🎯 Navigation Rapide

- 🚀 [Démarrage Rapide](#-démarrage-rapide) — Installation et lancement en 5 minutes
- 🏗️ [Architecture Globale](#-architecture-globale) — Vue d'ensemble du système
- 📂 [Structure des Fichiers](#-structure-des-fichiers) — Organisation du projet
- 🔄 [Pipeline ETL](#-pipeline-etl-expliqué) — Transformation des données
- 🤖 [Modélisation](#-modélisation--ridge-regression) — Approche statistique
- 📊 [Dashboard](#-dashboard-streamlit) — Interface interactive
- 🛠️ [Technologies](#-technologies--stack) — Stack technologique
- 📚 [Documentation](#-documentation-supplémentaire) — Ressources avancées

**Commencer maintenant** : [Démarrage Rapide](#-démarrage-rapide) ⬆️
