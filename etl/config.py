"""
Configuration et Constantes - MMM Project
Centralise tous les paramètres de configuration.
"""

import os
from pathlib import Path

# ===== CHEMINS DE BASE =====
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REFERENCE_DIR = DATA_DIR / "reference"
ETL_DIR = PROJECT_ROOT / "etl"

# Créer les répertoires s'ils n'existent pas
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REFERENCE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ===== FICHIERS DE DONNÉES =====
RAW_DATA_PATH = RAW_DATA_DIR / "compressed_data.csv"
HOLIDAYS_PATH = REFERENCE_DIR / "holidays.csv"

# Fichiers intermédiaires
CLEAN_DATA_PATH = PROCESSED_DATA_DIR / "mmm_clean.csv"
FEATURES_DATA_PATH = PROCESSED_DATA_DIR / "mmm_with_features.csv"
NORMALIZED_DATA_PATH = PROCESSED_DATA_DIR / "mmm_normalized.csv"
READY_DATA_PATH = PROCESSED_DATA_DIR / "mmm_ready.csv"

# Paramètres sauvegardés
ADSTOCK_PARAMS_PATH = PROCESSED_DATA_DIR / "adstock_params.pkl"
NORMALIZATION_PARAMS_PATH = PROCESSED_DATA_DIR / "normalization_params.pkl"

# ===== CONFIGURATION BIGQUERY =====
BIGQUERY_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "rh-etl-project-467521")
BIGQUERY_DATASET_ID = "MMM_datset"
BIGQUERY_TABLE_ID = "mmm"

# ===== PARAMÈTRES MMM PAR CANAL =====
# Adstock decay rate et saturation coefficient
CHANNEL_CONFIG = {
    'GOOGLE_PAID_SEARCH_SPEND': {
        'decay': 0.5,
        'saturation_s': 1.5,
        'description': 'Search intent-driven, shorter decay'
    },
    'GOOGLE_SHOPPING_SPEND': {
        'decay': 0.4,
        'saturation_s': 1.5,
        'description': 'Product-focused, immediate effect'
    },
    'GOOGLE_DISPLAY_SPEND': {
        'decay': 0.7,
        'saturation_s': 1.2,
        'description': 'Awareness-building, longer decay'
    },
    'GOOGLE_PMAX_SPEND': {
        'decay': 0.6,
        'saturation_s': 1.5,
        'description': 'Automated bidding, medium decay'
    },
    'GOOGLE_VIDEO_SPEND': {
        'decay': 0.65,
        'saturation_s': 1.3,
        'description': 'Brand awareness, medium-long decay'
    },
    'META_FACEBOOK_SPEND': {
        'decay': 0.6,
        'saturation_s': 1.4,
        'description': 'Awareness and engagement'
    },
    'META_INSTAGRAM_SPEND': {
        'decay': 0.65,
        'saturation_s': 1.3,
        'description': 'Visual storytelling, medium decay'
    },
    'META_OTHER_SPEND': {
        'decay': 0.55,
        'saturation_s': 1.4,
        'description': 'Meta other channels'
    },
    'TIKTOK_SPEND': {
        'decay': 0.7,
        'saturation_s': 1.2,
        'description': 'Viral content, longer reach'
    }
}

# ===== PARAMÈTRES DE NETTOYAGE =====
# Seuil pour supprimer les revenus zéro
MIN_REVENUE_THRESHOLD = 0

# Nombre de jours minimum de données
MIN_DAYS_REQUIRED = 30

# ===== PARAMÈTRES DE FEATURE ENGINEERING =====
# Fenêtre adstock (nombre de périodes antérieures)
ADSTOCK_WINDOW = 13

# Lags à créer (en jours)
LAGS_TO_CREATE = [1, 2, 4]

# ===== PARAMÈTRES DE NORMALISATION =====
# Moyenne et std pour une distribution normale standard
NORMALIZE_TARGET_MEAN = 0.0
NORMALIZE_TARGET_STD = 1.0

# ===== CONFIGURATION LOGGING =====
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ===== COLONNES CRITIQUES =====
REQUIRED_SPEND_COLUMNS = [
    'GOOGLE_PAID_SEARCH_SPEND',
    'META_FACEBOOK_SPEND',
    'TIKTOK_SPEND'
]

REQUIRED_METRIC_COLUMNS = [
    'FIRST_PURCHASES_ORIGINAL_PRICE',  # Revenue
    'DATE_DAY',
    'ORGANISATION_VERTICAL'
]

# ===== COLONNES DE DIMENSIOIN =====
DIMENSION_COLUMNS = [
    'DATE_DAY',
    'ORGANISATION_VERTICAL',
    'ORGANISATION_SUBVERTICAL',
    'ORGANISATION_PRIMARY_TERRITORY_NAME'
]

# ===== MAPPAGE DES COLONNES =====
COLUMN_MAPPING = {
    'FIRST_PURCHASES_ORIGINAL_PRICE': 'revenue',
    'GOOGLE_PAID_SEARCH_SPEND': 'google_search_spend',
    'GOOGLE_SHOPPING_SPEND': 'google_shopping_spend',
    'GOOGLE_PMAX_SPEND': 'google_pmax_spend',
    'GOOGLE_DISPLAY_SPEND': 'google_display_spend',
    'GOOGLE_VIDEO_SPEND': 'google_video_spend',
    'META_FACEBOOK_SPEND': 'meta_facebook_spend',
    'META_INSTAGRAM_SPEND': 'meta_instagram_spend',
    'META_OTHER_SPEND': 'meta_other_spend',
    'TIKTOK_SPEND': 'tiktok_spend',
}

# ===== FONCTIONS UTILITAIRES =====
def get_channel_config(channel_name: str) -> dict:
    """Retourne la configuration pour un canal"""
    return CHANNEL_CONFIG.get(channel_name, {
        'decay': 0.5,
        'saturation_s': 1.5
    })

def get_data_paths() -> dict:
    """Retourne tous les chemins de données"""
    return {
        'raw': str(RAW_DATA_PATH),
        'clean': str(CLEAN_DATA_PATH),
        'features': str(FEATURES_DATA_PATH),
        'normalized': str(NORMALIZED_DATA_PATH),
        'ready': str(READY_DATA_PATH),
        'holidays': str(HOLIDAYS_PATH),
        'adstock_params': str(ADSTOCK_PARAMS_PATH),
        'normalization_params': str(NORMALIZATION_PARAMS_PATH),
    }

def get_spend_columns() -> list:
    """Retourne la liste des colonnes de dépense"""
    return [col for col in CHANNEL_CONFIG.keys()]

def get_all_channels() -> list:
    """Retourne la liste de tous les canaux"""
    return list(CHANNEL_CONFIG.keys())

# ===== VALIDATION =====
if __name__ == "__main__":
    print("📋 MMM Configuration")
    print("=" * 60)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"BigQuery Project: {BIGQUERY_PROJECT_ID}")
    print(f"Number of channels: {len(CHANNEL_CONFIG)}")
    print("\n✅ Configuration validée")
