# 📊 Référence Variables MMM

## 🎯 Variables Dépendantes (Y)

### **revenue** ou **FIRST_PURCHASES_ORIGINAL_PRICE**
- 💰 Prix total des premières achats
- 📏 Unité: Currency ($, €, etc.)
- 📊 Distribution: Asymétrique (log-scale)
- ✅ Target pour la modélisation

---

## 📍 Variables Indépendantes (X) - Les Canaux

### **Données Brutes (Pas transformées)**
```
GOOGLE_PAID_SEARCH_SPEND      → 'google_search_spend'
GOOGLE_SHOPPING_SPEND         → 'google_shopping_spend'
GOOGLE_PMAX_SPEND            → 'google_pmax_spend'
GOOGLE_DISPLAY_SPEND         → 'google_display_spend'
GOOGLE_VIDEO_SPEND           → 'google_video_spend'

META_FACEBOOK_SPEND          → 'meta_facebook_spend'
META_INSTAGRAM_SPEND         → 'meta_instagram_spend'
META_OTHER_SPEND             → 'meta_other_spend'

TIKTOK_SPEND                 → 'tiktok_spend'
```

### **Adstock (Niveau 1: Réduction de Dimension)**

**Concept:** Modélise que les ventes dépendent du marketing passé

```python
adstocked_spend(t) = spend(t) + λ*spend(t-1) + λ²*spend(t-2) + ...
```

**Paramètres de decay par canal:**
```
GOOGLE_PAID_SEARCH:   decay = 0.5  (50% effect persists next day)
GOOGLE_SHOPPING:      decay = 0.4  (immediate, short-term)
GOOGLE_PMAX:          decay = 0.6  (medium-term)
GOOGLE_DISPLAY:       decay = 0.7  (long-term, awareness)
GOOGLE_VIDEO:         decay = 0.65 (awareness-building)

META_FACEBOOK:        decay = 0.6  (engagement medium-term)
META_INSTAGRAM:       decay = 0.65 (visual storytelling)
META_OTHER:           decay = 0.55

TIKTOK:               decay = 0.7  (viral, long reach)
```

**Colonnes créées:** `*_ADSTOCK` (9 colonnes)

**Interprétation:**
- decay=0.5 → Half-life ~1.3 jours (Search, intent-driven)
- decay=0.7 → Half-life ~2.3 jours (Display/TikTok, awareness)

### **Saturation (Niveau 2: Rendements Décroissants)**

**Concept:** Les dépenses élevées ont effet diminué (courbe en S)

```python
saturated = x^s / (k^s + x^s)
```

**Paramètres par canal:**
```
GOOGLE_PAID_SEARCH:   s = 1.5, k = 0.5  (moderate saturation)
GOOGLE_SHOPPING:      s = 1.5, k = 0.5  (moderate saturation)
GOOGLE_PMAX:          s = 1.5, k = 0.5  (moderate saturation)
GOOGLE_DISPLAY:       s = 1.2, k = 0.5  (mild saturation)
GOOGLE_VIDEO:         s = 1.3, k = 0.5  (mild-moderate)

META_FACEBOOK:        s = 1.4, k = 0.5  (moderate)
META_INSTAGRAM:       s = 1.3, k = 0.5  (mild-moderate)
META_OTHER:           s = 1.4, k = 0.5  (moderate)

TIKTOK:               s = 1.2, k = 0.5  (mild saturation)
```

**Colonnes créées:** `*_ADSTOCK_SAT` (9 colonnes)

**Interprétation:**
- s=1.0 → Pas de saturation (linéaire)
- s=1.5 → Saturation modérée (courbe en S classique)
- s=2.0 → Saturation forte (effet plateau rapide)

### **Lags (Niveau 3: Effets Retardés)**

**Concept:** Le marketing d'hier/avant-hier affecte les ventes d'aujourd'hui

```
LAG 1: spend(t-1)    → Effet 1 jour avant
LAG 2: spend(t-2)    → Effet 2 jours avant  
LAG 4: spend(t-4)    → Effet 4 jours avant
```

**Colonnes créées:** `*_LAG1, *_LAG2, *_LAG4` (3 lags × 9 canaux = 27 colonnes)

**Exemple d'interprétation:**
```
Si GOOGLE_SEARCH_LAG1 a coefficient élevé:
→ Les recherches Google d'hier génèrent plus de ventes qu'aujourd'hui
```

---

## 🔗 Interactions (Synergies entre Canaux)

### **GOOGLE_META_INTERACTION**
```python
GOOGLE_META_INTERACTION = GOOGLE_ADSTOCK_SAT × META_ADSTOCK_SAT
```

**Concept:** Synergie digitale
- Si utilisateur voir pub Google ET pub Meta
- L'effet combiné > somme des effets individuels

**Interprétation coefficient:**
- Positif → Les canaux se renforcent (multiplicateur)
- Négatif → Les canaux se cannibalisent

### **SEARCH_DISPLAY_INTERACTION**
```python
SEARCH_DISPLAY_INTERACTION = SEARCH_ADSTOCK_SAT × DISPLAY_ADSTOCK_SAT
```

**Concept:** Brand building
- Display crée l'awareness
- Search convertit l'awareness en ventes
- Effet combiné est plus fort que individuel

---

## 🕐 Variables de Contrôle (Temporalité)

### **Catégoriques**
```
weekday:    0=Monday, 1=Tuesday, ..., 6=Sunday
month:      1=January, 2=February, ..., 12=December
quarter:    1, 2, 3, 4
```

**Utilité:** Capturer l'effet jour de la semaine/saison

### **Continues**
```
trend:      0, 1, 2, 3, ... (nombre de jours depuis le début)
month_sin:  sin(2π × month / 12)  → Cyclicité saisonnière (sine)
month_cos:  cos(2π × month / 12)  → Cyclicité saisonnière (cosine)
```

**Utilité:**
- trend: Croissance/décroissance long-terme
- month_sin/cos: Captures la saisonnalité (e.g., pic Noël)

**Exemple:**
```
Si on a 12 mois de données:
month_sin oscille: 0 → 1 → 0 → -1 → 0
(pattern saisonnier complet)
```

---

## 🎉 Variables d'Événement

### **Flags Binaires**
```
is_holiday:          1 si jour férié (Noël, Thanksgiving, etc.)
is_major_event:      1 si événement commercial (Black Friday, etc.)
is_critical_event:   1 si ultra-important (Black Friday, Cyber Monday)
is_high_impact:      1 si HIGH ou CRITICAL
is_medium_impact:    1 si MEDIUM impact
```

### **Texte Événement**
```
event_name:          "Black Friday", "Christmas", "Valentine's Day", etc.
event_impact:        "CRITICAL" / "HIGH" / "MEDIUM" / "LOW" / "NONE"
```

**Utilité:**
- Corriger les anomalies (e.g., revenue pic sur Black Friday)
- Le modèle peut apprendre un coefficient pour chaque niveau d'impact
- Améliore les prédictions en jours normaux

---

## 📊 Métriques Calculées

### **revenue_per_spend**
```python
revenue_per_spend = revenue / (google_search_spend + 1)
```
**Interprétation:** Simple ROI pour un seul canal

### **avg_cpa**
```python
avg_cpa = google_search_spend / (first_purchases + 1)
```
**Interprétation:** Coût par acquisition moyen

---

## ✅ Variables Prêtes pour PyMC3

### **À Utiliser pour Modélisation:**

**Variables Continues Normalisées (Z-score):**
```python
# Adstock + Saturation (le cœur de MMM)
google_search_spend_adstock_sat_SCALED
meta_facebook_spend_adstock_sat_SCALED
tiktok_spend_adstock_sat_SCALED
... (9 canaux)

# Lags
google_search_spend_lag1_SCALED
google_search_spend_lag2_SCALED
google_search_spend_lag4_SCALED
... (27 lags)

# Interactions
GOOGLE_META_INTERACTION_SCALED
SEARCH_DISPLAY_INTERACTION_SCALED

# Contrôle temporel
trend_SCALED
month_sin
month_cos

# Événements
is_critical_event
is_high_impact
is_medium_impact

# Target
revenue_SCALED (= Y)
```

**Nombre total:** ~52 variables

---

## 🎯 Modèle MMM Typique

```python
import pymc as pm
import numpy as np

with pm.Model() as mmm_model:
    # Intercept
    intercept = pm.Normal('intercept', mu=0, sigma=2)
    
    # Coefficients pour les 9 canaux adstock+sat
    channel_coefs = pm.Normal('channel_coefs', mu=0, sigma=1, shape=9)
    
    # Coefficients pour les 27 lags
    lag_coefs = pm.Normal('lag_coefs', mu=0, sigma=1, shape=27)
    
    # Interactions
    interaction_coefs = pm.Normal('interaction_coefs', mu=0, sigma=1, shape=2)
    
    # Saisonnalité
    season_coef = pm.Normal('season_coef', mu=0, sigma=1)
    
    # Événements
    event_coef = pm.Normal('event_coef', mu=0, sigma=1)
    
    # Trend
    trend_coef = pm.Normal('trend_coef', mu=0, sigma=1)
    
    # Likelihood
    mu = (intercept + 
          pm.math.dot(channel_coefs, df[channel_adstock_sat_cols].T) +
          pm.math.dot(lag_coefs, df[lag_cols].T) +
          pm.math.dot(interaction_coefs, df[interaction_cols].T) +
          season_coef * (df['month_sin'] + df['month_cos']) +
          event_coef * df['is_critical_event'] +
          trend_coef * df['trend'])
    
    sigma = pm.HalfNormal('sigma', sigma=1)
    likelihood = pm.Normal('likelihood', mu=mu, sigma=sigma, observed=df['revenue'])
    
    # Sample
    trace = pm.sample(2000, tune=1000, cores=4)
```

**Résultat:** Vous avez les coefficients par canal!
```
channel_coefs:
  google_search:    0.45  → 45% contribution
  google_display:   0.15  → 15% contribution
  meta_facebook:    0.22  → 22% contribution
  tiktok:           0.18  → 18% contribution
```

---

## 🚀 Pipeline Résumé

```
Données Brutes (9 colonnes de spend)
        ↓
    ADSTOCK (9 colonnes)
        ↓
    SATURATION (9 colonnes)
        ↓
    LAGS (27 colonnes)
        ↓
    INTERACTIONS (2 colonnes)
        ↓
    CONTRÔLE + ÉVÉNEMENTS (10+ colonnes)
        ↓
    NORMALISATION (z-score)
        ↓
    52 colonnes prêtes pour PyMC3 ✅
```

---

## 💡 Conseils Pratiques

### **Choix des Lags**
```
LAG 1: Toujours inclure (effet immédiat)
LAG 2: Pour les canaux medium-terme
LAG 4: Pour les canaux awareness/long-terme
```

### **Choix de Decay par Canal**
```
Recherche (Search):    decay=0.4-0.5  (rapide, intent)
Shopping:              decay=0.3-0.4  (très rapide, e-commerce)
Display/Video:         decay=0.6-0.7  (lent, awareness)
Social (Meta/TikTok):  decay=0.6-0.7  (lent, engagement)
```

### **Validation du Modèle**
```
1. Vérifier que coefficients ont des signes sensés
   (dépenses → revenue positive)
2. Vérifier que adstock decay estimés ≈ nos priors
3. Vérifier que interactions sont positives
4. Vérifier que R² > 0.6 pour bon fit
5. Vérifier que prédictions hors-sample ≈ réelles
```

---

**Vous avez maintenant une référence complète pour interpréter les variables MMM! 🎯**
