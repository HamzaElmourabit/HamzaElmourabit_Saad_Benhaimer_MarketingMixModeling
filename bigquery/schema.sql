-- =========================
-- MMM COMPREHENSIVE SCHEMA
-- =========================
-- Cette table contient tous les niveaux de données MMM:
-- 1. Données brutes (spend, revenue)
-- 2. Features transformées (adstock, lags)
-- 3. Variables calculées (saturation, interactions)

CREATE TABLE IF NOT EXISTS `rh-etl-project-467521.MMM_datset.mmm` (
  -- ===== IDENTIFIANTS =====
  date_day DATE,
  organisation_vertical STRING,
  organisation_subvertical STRING,
  territory STRING,
  
  -- ===== VARIABLES DÉPENDANTES =====
  revenue FLOAT64,  -- Variable cible pour MMM
  
  -- ===== DÉPENSES PAR CANAL (Données Brutes) =====
  -- Google
  google_search_spend FLOAT64,
  google_shopping_spend FLOAT64,
  google_pmax_spend FLOAT64,
  google_display_spend FLOAT64,
  google_video_spend FLOAT64,
  google_total_spend FLOAT64,  -- Agrégation
  
  -- Meta
  meta_facebook_spend FLOAT64,
  meta_instagram_spend FLOAT64,
  meta_other_spend FLOAT64,
  meta_total_spend FLOAT64,  -- Agrégation
  
  -- TikTok
  tiktok_spend FLOAT64,
  
  -- ===== ADSTOCK (Réduction de Dimension) =====
  -- Adstock géométrique avec decay parameter
  google_search_spend_adstock FLOAT64,
  google_shopping_spend_adstock FLOAT64,
  google_pmax_spend_adstock FLOAT64,
  google_display_spend_adstock FLOAT64,
  google_video_spend_adstock FLOAT64,
  
  meta_facebook_spend_adstock FLOAT64,
  meta_instagram_spend_adstock FLOAT64,
  meta_other_spend_adstock FLOAT64,
  tiktok_spend_adstock FLOAT64,
  
  -- ===== SATURATION (Hill Transformation) =====
  -- Modélise les rendements décroissants
  google_search_spend_adstock_sat FLOAT64,
  google_shopping_spend_adstock_sat FLOAT64,
  google_pmax_spend_adstock_sat FLOAT64,
  google_display_spend_adstock_sat FLOAT64,
  google_video_spend_adstock_sat FLOAT64,
  
  meta_facebook_spend_adstock_sat FLOAT64,
  meta_instagram_spend_adstock_sat FLOAT64,
  meta_other_spend_adstock_sat FLOAT64,
  tiktok_spend_adstock_sat FLOAT64,
  
  -- ===== LAGS (Effets Retardés) =====
  -- Capture l'effet du marketing des périodes précédentes
  google_search_spend_lag1 FLOAT64,
  google_search_spend_lag2 FLOAT64,
  google_search_spend_lag4 FLOAT64,
  
  meta_facebook_spend_lag1 FLOAT64,
  meta_facebook_spend_lag2 FLOAT64,
  meta_facebook_spend_lag4 FLOAT64,
  
  tiktok_spend_lag1 FLOAT64,
  tiktok_spend_lag2 FLOAT64,
  
  -- ===== INTERACTIONS (Synergies entre Canaux) =====
  google_meta_interaction FLOAT64,  -- Synergie: Search + Social
  search_display_interaction FLOAT64,  -- Brand building
  
  -- ===== VARIABLES DE CONTRÔLE =====
  weekday INT64,  -- 0=lundi, 6=dimanche
  month INT64,    -- 1-12
  quarter INT64,  -- 1-4
  trend INT64,    -- Nombre de jours depuis le début
  
  -- Cyclicité (sin/cos encoding)
  month_sin FLOAT64,
  month_cos FLOAT64,
  
  -- ===== MÉTRIQUES D'EFFICACITÉ =====
  clicks INT64,
  impressions INT64,
  revenue_per_spend FLOAT64,  -- ROI simple
  avg_cpa FLOAT64,  -- Coût par acquisition
  
  -- ===== PARTITIONNEMENT ET INDEXATION =====
  CONSTRAINT valid_date CHECK (date_day IS NOT NULL),
  CONSTRAINT valid_revenue CHECK (revenue >= 0),
  CONSTRAINT valid_spend CHECK (
    google_search_spend >= 0 AND
    meta_facebook_spend >= 0 AND
    tiktok_spend >= 0
  )
)
PARTITION BY date_day;

-- ===== INDEX POUR PERFORMANCE =====
CREATE INDEX idx_vertical_date
ON `rh-etl-project-467521.MMM_datset.mmm`(organisation_vertical, date_day);

-- ===== VUES ANALYTIQUES =====

-- Vue 1: Agrégation par canal
CREATE OR REPLACE VIEW `rh-etl-project-467521.MMM_datset.mmm_by_channel` AS
SELECT
  date_day,
  google_total_spend,
  meta_total_spend,
  tiktok_spend,
  google_total_spend + meta_total_spend + tiktok_spend as total_spend,
  revenue
FROM `rh-etl-project-467521.MMM_datset.mmm`
WHERE revenue > 0;

-- Vue 2: ROI quotidien
CREATE OR REPLACE VIEW `rh-etl-project-467521.MMM_datset.mmm_daily_roi` AS
SELECT
  date_day,
  revenue,
  google_total_spend + meta_total_spend + tiktok_spend as total_spend,
  revenue / (google_total_spend + meta_total_spend + tiktok_spend + 1) as roi,
  organisation_vertical
FROM `rh-etl-project-467521.MMM_datset.mmm`
WHERE revenue > 0;

-- Vue 3: Métriques par vertical
CREATE OR REPLACE VIEW `rh-etl-project-467521.MMM_datset.mmm_by_vertical` AS
SELECT
  organisation_vertical,
  DATE_TRUNC(date_day, WEEK) as week,
  SUM(google_total_spend) as google_spend,
  SUM(meta_total_spend) as meta_spend,
  SUM(tiktok_spend) as tiktok_spend,
  SUM(revenue) as total_revenue,
  SUM(revenue) / (SUM(google_total_spend) + SUM(meta_total_spend) + SUM(tiktok_spend) + 1) as week_roi
FROM `rh-etl-project-467521.MMM_datset.mmm`
GROUP BY organisation_vertical, week;