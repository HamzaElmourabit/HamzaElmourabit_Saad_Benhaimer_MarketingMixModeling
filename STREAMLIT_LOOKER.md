# 🎨 Streamlit & Looker - Documentation Complète

## 📊 Vue d'Ensemble

Votre projet MMM a deux couches de visualisation:

```
┌─────────────────────────────────────────────────────────┐
│                    DASHBOARD LAYER                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │   STREAMLIT      │      │    LOOKER        │       │
│  │  (Python)        │      │   (BI Tool)      │       │
│  │                  │      │                  │       │
│  │ • Quick & Easy   │      │ • Professional   │       │
│  │ • Code-based     │      │ • Embedded       │       │
│  │ • What-if        │      │ • Shared         │       │
│  │ • Attribution    │      │ • Analytics      │       │
│  └──────────────────┘      └──────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────┐
│                   DATA LAYER (BigQuery)                 │
│  mmm_ready.csv, mmm_clean, mmm_features, etc.          │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 STREAMLIT - Dashboard Rapide

### **Structure Actuelle**

```
dashboard/
├── app.py                    ← Main app (5 pages)
├── looker_integration.py     ← Module d'intégration Looker
└── pages/
    └── looker_dashboards.py  ← Page Looker
```

### **Pages Streamlit Disponibles**

#### **1️⃣ Dashboard (📊)**
```
- KPIs: Total Spend, Revenue, ROI
- 3 Trends: Revenue, Spend, ROI (via Plotly)
- Channel Mix: Distribution pie chart
- Date filters: Date début/fin
```

**Quand l'utiliser:**
- Vue rapide des KPIs quotidiens
- Exploring les trends
- Vérifier le health du marketing

#### **2️⃣ Analyse Canaux (📈)**
```
- Selector de canal
- Metrics: Total spend, ROI
- Scatter plot: Spend vs Revenue (avec trendline)
```

**Quand l'utiliser:**
- Analyser la performance d'un seul canal
- Identifier les optimisations possibles

#### **3️⃣ Scenarios (🎯) - What-If Analysis**
```
- Budget actuel affiché
- Sliders: Ajuster l'allocation % par canal
- Validation: Vérifier que total = 100%
- Tableau: Current vs Proposed budget
```

**Quand l'utiliser:**
- Simuler différentes allocations
- Répondre: "Que se passe-t-il si on augmente Google Search de 10%?"
- Planifier le budget de l'année prochaine

**⚠️ Note:** La page montre les budgets proposés, mais les prédictions nécessitent un modèle PyMC3 entraîné

#### **4️⃣ Attribution (🎨) - Multi-Touch**
```
- Radio buttons: Modèles d'attribution
  • First Touch (premier canal crédité)
  • Last Touch (dernier canal)
  • Linear (crédit égal)
  • Time Decay (plus récent = plus de crédit)
  • Shapley Value (optimal - nécessite PyMC3)
  
- Bar chart: Revenue attribué par canal
```

**Quand l'utiliser:**
- Comprendre la contribution réelle de chaque canal
- Comparer les modèles d'attribution

**⚠️ Note:** Actuellement simulations. Nécessite Shapley values (package `shap`)

#### **5️⃣ Configuration (⚙️)**

3 onglets:
- **Data Status**: Infos sur mmm_ready.csv (rows, cols, types)
- **MMM Config**: Paramètres de chaque canal (decay, saturation)
- **Documentation**: Liens vers les guides

---

## 🎨 LOOKER - Dashboard Professionnel

### **Qu'est-ce que Looker?**

Looker est une **plateforme BI** qui se connecte directement à BigQuery et crée des dashboards interactifs.

**Avantages:**
- ✅ Partageable en 1 clic
- ✅ Performances optimisées (cache BigQuery)
- ✅ Filtres interactifs avancés
- ✅ Exports automatiques
- ✅ Alertes sur les seuils
- ✅ Intégration mobile

### **Architecture Looker**

```
┌──────────────────┐
│   BigQuery       │  ← Données MMM
│  (mmm table)     │
└────────┬─────────┘
         │
┌────────▼─────────┐
│   Looker Model   │  ← LookML definitions
│  (views.lkml)    │
└────────┬─────────┘
         │
┌────────▼─────────────────┐
│   Looker Dashboard       │  ← Visualisations
│  (dashboard.lookml)      │
└──────────────────────────┘
         │
┌────────▼─────────────────────┐
│   Streamlit (Embedded)        │  ← Dans cette app
│  (looker_integration.py)      │
└───────────────────────────────┘
```

### **Comment Fonctionner avec Looker**

#### **Étape 1: Créer la Service Account**
```
1. Looker Admin → Users → Service Accounts
2. Create Account:
   - Name: "mmm-streamlit"
   - Email: "mmm-streamlit@company.com"
3. Generate API Credentials:
   - API Key: xyz123
   - API Secret: abc456
4. Copier les credentials
```

#### **Étape 2: Créer les Modèles LookML**

**Fichier 1: views/mmm.view.lkml**
```lookml
view: mmm {
  sql_table_name: `project.dataset.mmm` ;;
  
  dimension: date_day { type: date }
  dimension: organisation_vertical { type: string }
  
  # Channels
  dimension: google_search_spend { type: number }
  dimension: meta_facebook_spend { type: number }
  dimension: revenue { type: number }
  
  # Measures
  measure: total_revenue { type: sum; sql: ${revenue} ;; }
  measure: total_spend { type: sum; ... }
  measure: roi { type: number; sql: ${total_revenue} / ${total_spend} ;; }
}
```

**Fichier 2: dashboards/mmm_overview.dashboard.lookml**
```lookml
- dashboard: mmm_overview
  title: "MMM Overview"
  elements:
    - title: "Daily Revenue"
      query: mmm_daily
      type: looker_line
      dimensions: [mmm.date_day]
      measures: [mmm.total_revenue]
```

Les fichiers LookML complets sont dans:
👉 [looker/lookml_models.py](looker/lookml_models.py)

#### **Étape 3: Déployer dans Looker**

```
1. Ouvrir Looker → Développement
2. Créer/ouvrir le project "mmm"
3. Créer les fichiers:
   - views/mmm.view.lkml (copier le contenu)
   - views/mmm_channels.view.lkml
   - dashboards/mmm_overview.dashboard.lookml
4. Commiter les changements
5. Deploy vers production
```

#### **Étape 4: Intégrer dans Streamlit**

Configurer les variables d'environnement:

```bash
# .env
LOOKER_API_HOST=https://looker.company.com
LOOKER_API_KEY=your-api-key-here
LOOKER_API_SECRET=your-api-secret-here
```

Ou via export:
```bash
export LOOKER_API_HOST=https://looker.company.com
export LOOKER_API_KEY=...
export LOOKER_API_SECRET=...
```

**Puis:** La page "Looker Dashboards" dans Streamlit affichera automatiquement les dashboards!

---

## 🚀 Comment Exécuter

### **Lancer le Dashboard Streamlit**

```bash
# Installation des dépendances (si besoin)
pip install -r requirements.txt

# Lancer l'app
streamlit run dashboard/app.py

# Or, avec options
streamlit run dashboard/app.py --logger.level=debug
```

**Accès:**
```
http://localhost:8501
```

### **Navigation**

Sidebar gauche:
```
🎯 Navigation
├─ 📊 Dashboard          ← KPIs & trends
├─ 📈 Analyse Canaux     ← Performance par canal
├─ 🎯 Scenarios          ← What-if analysis
├─ 🎨 Attribution        ← Multi-touch
└─ ⚙️ Configuration       ← Settings & docs
```

---

## 📊 Utilisations Concrètes

### **Scénario 1: Augmenter le ROI**

```
1. Ouvrir: Dashboard → Date filter (derniers 30 jours)
2. Voir: Total ROI, Channel Mix
3. Aller à: Analyse Canaux
4. Analyser: Quel canal a le meilleur ROAS?
5. Aller à: Scenarios
6. Tester: Augmenter le meilleur canal de +10%
7. Voir: Résultat estimé (si modèle PyMC3 available)
```

### **Scénario 2: Attribution**

```
1. Ouvrir: Attribution
2. Comparer: Linear vs Shapley Value
3. Question: Quelle est la vraie contribution de Meta?
4. Action: Ajuster la stratégie Meta en conséquence
```

### **Scénario 3: Reporting**

```
1. Ouvrir: Looker Dashboards
2. Sélectionner: Dashboard "MMM Overview"
3. Filter: Date range, Vertical
4. Export: PDF ou PNG
5. Envoyer: Au management
```

---

## 🔧 Configuration Avancée

### **Caching Streamlit**

```python
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')
```

Streamlit cache les données pour plus de rapidité. Clear le cache:
```
Ctrl+C → S (dans l'app)
```

### **Performance Looker**

```
- Utiliser les filtres (ils utilisent le cache Looker)
- Éviter les queries sans filtres de date
- Préférer les materialized tables pour les agrégations
```

---

## 📝 Dépannage

### **"Données MMM non trouvées"**

```
❌ Erreur: Données MMM non trouvées

✅ Solution:
1. Lancer la pipeline ETL:
   python run_pipeline.py
   
2. Vérifier le chemin:
   data/processed/mmm_ready.csv
   
3. Relancer Streamlit:
   Ctrl+C puis streamlit run dashboard/app.py
```

### **"Credentials Looker non configurées"**

```
⚠️ Avertissement: Credentials Looker non configurées

✅ Solution:
1. Créer Service Account dans Looker Admin
2. Exporter les credentials:
   export LOOKER_API_HOST=...
   export LOOKER_API_KEY=...
   export LOOKER_API_SECRET=...
3. Relancer Streamlit
```

### **Embeddings Looker ne s'affichent pas**

```
❌ Problème: iFrame vide

✅ Vérifications:
1. Dashboard ID correct?
2. Service Account a les permissions?
3. Looker "Embed dashboards" activé?
4. Vérifier les logs:
   streamlit run app.py --logger.level=debug
```

---

## 🎯 Prochaines Étapes

### **Avant de Mettre en Production**

```
1. ✅ Tester l'ETL (data/processed/mmm_ready.csv)
2. ✅ Lancer Streamlit localement
3. ✅ Vérifier tous les KPIs
4. ⏳ Entraîner le modèle PyMC3 (pour Scenarios/Attribution)
5. ⏳ Créer les Looker Models & Dashboards
6. ⏳ Configurer les Looker credentials
7. ⏳ Deployer en production (Cloud Run, etc.)
```

### **Ajouter des Features**

```python
# Dans dashboard/app.py, ajouter une fonction:

def show_new_feature():
    st.markdown("# 🆕 New Feature")
    # ... votre code
    
# Puis ajouter à la navigation:
page = st.sidebar.radio(
    "Select page",
    [..., "🆕 New Feature"]
)

if page == "🆕 New Feature":
    show_new_feature()
```

---

## 📚 Fichiers Clés

| Fichier | Rôle |
|---------|------|
| `dashboard/app.py` | App principal Streamlit |
| `dashboard/looker_integration.py` | Module d'intégration Looker |
| `looker/lookml_models.py` | Modèles LookML |
| `requirements.txt` | Dépendances Python |

---

## 🔗 Ressources

- [Streamlit Docs](https://docs.streamlit.io/)
- [Looker Embed API](https://cloud.google.com/looker/docs/r/api/embed)
- [Plotly Documentation](https://plotly.com/python/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)

---

**Dashboard Streamlit + Looker = Vue complète de votre MMM! 🎉**
