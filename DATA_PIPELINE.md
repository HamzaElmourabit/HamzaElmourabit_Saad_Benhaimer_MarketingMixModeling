# 📊 Marketing Mix Modeling (MMM) - Data Pipeline

Ce projet implement une pipeline **Data complète** pour la modélisation marketing mix avec attribution multi-touch.

## 🏗️ Architecture de la Pipeline

```
data/raw/
├── compressed_data.csv          # Données brutes
└── reference/
    └── holidays.csv             # Jours spéciaux et événements

↓ [ÉTAPE 1: Validation]
↓ [ÉTAPE 2: Nettoyage]
↓ [ÉTAPE 3: Feature Engineering]
↓ [ÉTAPE 4: Normalisation]
↓ [ÉTAPE 5: Préparation pour Modélisation]

data/processed/
├── mmm_clean.csv               # Données nettoyées
├── mmm_with_features.csv       # Avec features transformées
├── mmm_normalized.csv          # Données normalisées
├── mmm_ready.csv               # Prêt pour modélisation
├── adstock_params.pkl          # Paramètres pour production
└── normalization_params.pkl    # Paramètres pour dénormalisation

↓ [Chargement BigQuery]

BigQuery:
├── mmm (table principale)
├── mmm_clean (version nettoyée)
├── mmm_features (avec features)
└── Views analytiques
```

## 🔧 Modules ETL

### 1. **validation.py** - Validation des données
Vérifie la qualité des données brutes:
- ✅ Valeurs manquantes
- ✅ Format des dates
- ✅ Plages numériques valides
- ✅ Doublons
- ✅ Cohérence spend/revenue

**Usage:**
```python
from validation import DataValidator

df = pd.read_csv('data/raw/compressed_data.csv')
validator = DataValidator(df)
validator.validate_all()
```

### 2. **clean.py** - Nettoyage des données
Prépare les données brutes pour la modélisation:
- 🧹 Parse les dates
- 🧹 Standardise les colonnes
- 🧹 Traite les valeurs manquantes intelligemment
- 🧹 Corrige les valeurs négatives
- 🧹 Supprime les doublons
- 🧹 Agrège les canaux

**Usage:**
```bash
python etl/clean.py
```

### 3. **feature_engineering.py** - Transformations MMM
Crée les variables essentielles pour la modélisation:

#### 📍 **Adstock (Réduction de Dimension)**
Modélise le délai de réaction du marketing:
```
adstocked_spend(t) = spend(t) + λ*spend(t-1) + λ²*spend(t-2) + ...
```
- Decay parameters par canal (0.4-0.7)
- Normalisation pour préserver l'effet total

#### 📉 **Saturation (Hill Transformation)**
Modélise les rendements décroissants:
```
saturated = x^s / (k^s + x^s)
```
- Saturation coefficient s = 1.2-1.5
- Midpoint k = 0.5

#### ⏱️ **Lags (Effets Retardés)**
Capture l'effet du marketing passé:
- Lags: 1 jour, 2 jours, 4 jours
- Appliqué à chaque canal

#### 🔗 **Interactions**
Capture les synergies entre canaux:
- Google + Meta (synergie digitale)
- Search + Display (brand building)

**Configuration par canal:**
```python
CHANNEL_CONFIG = {
    'GOOGLE_PAID_SEARCH_SPEND': {'decay': 0.5, 'saturation_s': 1.5},
    'META_FACEBOOK_SPEND': {'decay': 0.6, 'saturation_s': 1.4},
    'TIKTOK_SPEND': {'decay': 0.7, 'saturation_s': 1.2},
}
```

### 4. **normalize.py** - Normalisation
Prépare les données pour la modélisation bayésienne (PyMC3):
- ✅ Standardisation z-score (mean=0, std=1)
- ✅ Log-transformation des dépenses
- ✅ Gestion des NaN
- ✅ Sauvegarde des paramètres pour dénormalisation

**Variables sauvegardées:**
```python
{
    'feature_means': {...},      # Pour dénormalisation
    'feature_stds': {...},       # Pour dénormalisation
    'scalers': {...}
}
```

### 5. **event_enrichment.py** - Enrichissement avec événements
Ajoute les jours spéciaux:
- 🎉 Jours fériés
- 🛍️ Événements commerciaux (Black Friday, Cyber Monday)
- 📊 Flags d'impact (CRITICAL, HIGH, MEDIUM, LOW)
- 🔢 Variables numériques pour modélisation

### 6. **load_bigquery.py** - Chargement BigQuery
Charge les données dans BigQuery avec:
- 📤 Support multi-tables
- 🛡️ Gestion d'erreurs
- 📊 Création de vues analytiques
- ✅ Validation de chargement

## 🚀 Exécution de la Pipeline

### **Option 1: Pipeline Complète (Recommandée)**
```bash
cd etl
python pipeline.py
```

**Sortie:**
```
🚀 MARKETING MIX MODELING - ETL PIPELINE COMPLÈTE

[1/5] VALIDATION DES DONNÉES BRUTES
✅ Validation complétée

[2/5] NETTOYAGE DES DONNÉES
✅ Nettoyage complété: 1000 lignes restantes

[3/5] FEATURE ENGINEERING
📍 Application de l'Adstock...
📍 Application des Lags...
📍 Application de la Saturation...
📍 Création des Interactions...
✅ Features créées: 45 nouvelles colonnes

[4/5] NORMALISATION DES DONNÉES
✅ Normalisation complétée

[5/5] PRÉPARATION POUR MODÉLISATION
✅ Dataset de modélisation: 950 lignes, 52 colonnes
```

### **Option 2: Modules Individuels**

```bash
# Nettoyage seul
python clean.py

# Chargement BigQuery
python load_bigquery.py
```

## 📊 Variables Disponibles pour MMM

### **Variable Dépendante**
- `revenue` ou `FIRST_PURCHASES_ORIGINAL_PRICE`

### **Variables Indépendantes (Canaux)**
```
Dépenses brutes (non-transformées):
- google_search_spend
- google_shopping_spend
- google_display_spend
- google_pmax_spend
- google_video_spend
- meta_facebook_spend
- meta_instagram_spend
- tiktok_spend

Après Adstock (réduction de dimension):
- google_search_spend_adstock
- meta_facebook_spend_adstock
- tiktok_spend_adstock
- ... (pour tous les canaux)

Après Saturation (Hill):
- google_search_spend_adstock_sat
- meta_facebook_spend_adstock_sat
- tiktok_spend_adstock_sat
- ... (pour tous les canaux)

Lags (effets retardés):
- google_search_spend_lag1, lag2, lag4
- meta_facebook_spend_lag1, lag2, lag4
- tiktok_spend_lag1, lag2

Interactions:
- google_meta_interaction (Search + Social)
- search_display_interaction (Brand building)
```

### **Variables de Contrôle**
```
Temporalité:
- weekday (0=lundi, 6=dimanche)
- month (1-12)
- quarter (1-4)
- trend (nombre de jours depuis le début)

Cyclicité (sin/cos encoding):
- month_sin
- month_cos

Événements:
- is_holiday
- is_major_event
- is_critical_event
- is_high_impact
- is_medium_impact
- event_name
```

## 📈 Statistiques de Sortie

Après exécution complète:
```
✅ Données brutes:       5000 lignes × 15 colonnes
✅ Après nettoyage:     4900 lignes × 20 colonnes
✅ Avec features:       4900 lignes × 65 colonnes
✅ Après normalisation: 4900 lignes × 65 colonnes
✅ Prêt pour modeling:  4700 lignes × 52 colonnes

📉 Réduction de données: 6% lignes supprimées (revenus zéro)
📈 Expansion de features: 37 nouvelles colonnes
```

## 💾 Artefacts de Production

La pipeline crée deux fichiers de paramètres pour **reproduire exactement** les transformations:

### **adstock_params.pkl**
```python
{
    'google_search_spend': 0.5,
    'meta_facebook_spend': 0.6,
    'tiktok_spend': 0.7,
    ...
}
```

### **normalization_params.pkl**
```python
{
    'feature_means': {...},
    'feature_stds': {...},
    'scalers': {...}
}
```

**Usage:** Charger pour dénormaliser les prédictions
```python
import pickle

with open('normalization_params.pkl', 'rb') as f:
    params = pickle.load(f)

# Dénormaliser les prédictions du modèle
pred_denorm = params['feature_stds']['revenue'] * pred_scaled + params['feature_means']['revenue']
```

## 🔍 Validation et Qualité

### **Checks Automatiques**
- ✅ Pas de NaN résiduels
- ✅ Toutes les dépenses >= 0
- ✅ Revenue >= 0
- ✅ Dates valides
- ✅ Pas de doublons
- ✅ Coherence spend/revenue ratio

### **Sortie de Validation**
```
⚠️  {n} valeurs manquantes détectées
⚠️  {n} dates invalides détectées
⚠️  {col}: {n} valeurs négatives

💰 Dépenses totales: $1,234,567
💰 Revenus totales: $2,345,678
📈 Ratio revenue/spend: 1.90
```

## 🏁 Prochaines Étapes

Après cette pipeline, les données sont prêtes pour:

1. **Modélisation MMM (PyMC3)**
   - Ridge Regression
   - Bayesian MMM
   - Incremental Testing (Geo Experiments)

2. **Attribution Multi-Touch**
   - Shapley Value
   - Data-driven attribution

3. **Dashboard Streamlit**
   - Scenario budgétaires
   - What-if analysis
   - ROI par canal

4. **Looker Embedding**
   - Visualisations interactives
   - KPIs en temps réel

## ⚙️ Configuration

### **Credentials BigQuery**
```bash
# Linux/Mac
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Windows PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account-key.json"
```

### **Paramètres Adstock par Canal**
Modifier dans `feature_engineering.py`:
```python
CHANNEL_CONFIG = {
    'VOTRE_CANAL': {'decay': 0.5, 'saturation_s': 1.5},
    ...
}
```

Valeurs typiques:
- **decay**: 0.3-0.7 (plus bas = effet plus court)
- **saturation_s**: 1.0-2.0 (plus haut = saturation plus rapide)

## 📝 Logs et Debugging

Les logs sont affichés dans le terminal:
```
🔍 Validation des données en cours...
🧹 Nettoyage des données en cours...
🔧 Feature Engineering en cours...
🔄 Normalisation des données en cours...
```

Pour plus de détails:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎓 Concepts Clés

### **Adstock**
- Modélise comment le marketing d'hier affecte les ventes d'aujourd'hui
- Paramètre decay [0, 1]: 0.5 = 50% de l'effet le jour suivant

### **Saturation**
- Les dépenses supplémentaires ont un effet décroissant
- Hill curve avec saturation coefficient s

### **Lag**
- Capture les effets non-immédiats
- 1j = effet immédiat, 4j = effet court-moyen terme

### **Interactions**
- Modélise les synergies entre canaux
- Google + Meta = effet multiplicatif

## 📞 Support

Pour des questions sur:
- **Adstock**: Voir `feature_engineering.py` - classe `AdstockTransform`
- **Normalisation**: Voir `normalize.py` - classe `DataNormalizer`
- **Validation**: Voir `validation.py` - classe `DataValidator`

---

**Status:** ✅ Pipeline complète et prête pour production
