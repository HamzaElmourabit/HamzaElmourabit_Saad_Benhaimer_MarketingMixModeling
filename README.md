# MMM Project - Marketing Mix Modeling (MMM)

## 🚀 Overview

Ce projet implémente une solution complète de Marketing Mix Modeling (MMM) avec attribution multi-touch, modélisation Bayésienne et visualisation analytique.

Le pipeline couvre :
- ingestion et nettoyage des données marketing et commerciales
- enrichissement calendrier et événements
- ingénierie des features MMM (adstock, lags, saturations, interactions)
- normalisation des variables pour amélioration de la modélisation
- chargement de la table transformée dans BigQuery
- dashboard Streamlit pour le reporting
- intégration de dashboards Looker embarqués

## 🏛️ Architecture du projet

```text
[Data Source] --> [ETL Pipeline] --> [Processed CSV + BigQuery] --> [Visualization]
                                              |                     |
                                              v                     v
                                          [Bayesian MMM]       [Streamlit App]
                                                                 [Looker Embed]
```

### Illustrations clés

![Architecture du pipeline](Assets/architecture_mmm.png)

![Interface dashboard](Assets/Interface_dashboard.png)

![Attribution multi-touch](Assets/Attribution_multi_touch.png)

![Scénarios budgétaires](Assets/Budget_Scenarios_What_if.png)

![ROI global](Assets/ROI_Global.png)

![Top 5 canaux dépensiers](Assets/Top_5_canaux_les_plus_dépensiers.png)

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
