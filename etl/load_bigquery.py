"""
BigQuery Loader - MMM Project
Charge les données MMM dans BigQuery avec gestion d'erreurs et validation.
"""

import os
import pandas as pd
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ID = "rh-etl-project-467521"
DATASET_ID = "MMM_datset"
TABLE_ID = "mmm"

# Chemins
CLEAN_DATA_PATH = os.path.join(BASE_DIR, "data/processed/mmm_clean.csv")
FEATURES_DATA_PATH = os.path.join(BASE_DIR, "data/processed/mmm_with_features.csv")
NORMALIZED_DATA_PATH = os.path.join(BASE_DIR, "data/processed/mmm_normalized.csv")


class BigQueryLoader:
    """Charge les données dans BigQuery"""
    
    def __init__(self, project_id: str, dataset_id: str, table_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.client = bigquery.Client(project=project_id)
        self.table_ref = f"{project_id}.{dataset_id}.{table_id}"
    
    def load_dataframe(self, df: pd.DataFrame, table_suffix: str = "") -> bool:
        """
        Charge un DataFrame dans BigQuery
        
        Args:
            df: DataFrame à charger
            table_suffix: Suffixe pour le nom de la table (e.g. "_clean", "_features")
        
        Returns:
            True si succès, False sinon
        """
        table_id = self.table_id + table_suffix
        table_ref = f"{self.project_id}.{self.dataset_id}.{table_id}"
        
        try:
            print(f"\n📤 Chargement dans BigQuery: {table_ref}")
            print(f"   Dimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
            
            # Configuration du job de chargement
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                autodetect=True,
            )
            
            # Charger
            load_job = self.client.load_table_from_dataframe(
                df, 
                table_ref,
                job_config=job_config
            )
            
            # Attendre la fin
            load_job.result()
            
            print(f"✅ {df.shape[0]} lignes chargées dans {table_id}")
            return True
            
        except GoogleAPIError as e:
            logger.error(f"❌ Erreur BigQuery: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            return False
    
    def load_from_csv(self, csv_path: str, table_suffix: str = "") -> bool:
        """
        Charge un fichier CSV dans BigQuery
        
        Args:
            csv_path: Chemin du fichier CSV
            table_suffix: Suffixe pour le nom de la table
        
        Returns:
            True si succès, False sinon
        """
        try:
            print(f"📂 Lecture du fichier: {csv_path}")
            df = pd.read_csv(csv_path)
            return self.load_dataframe(df, table_suffix)
        
        except FileNotFoundError:
            logger.error(f"❌ Fichier non trouvé: {csv_path}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur de lecture CSV: {e}")
            return False
    
    def create_views(self) -> bool:
        """Crée des vues utiles dans BigQuery"""
        try:
            print("\n📊 Création des vues BigQuery...")
            
            # Vue: agrégation par canal
            view_channel = f"""
            CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.mmm_by_channel` AS
            SELECT
              date_day,
              GOOGLE_TOTAL_SPEND,
              META_TOTAL_SPEND,
              TIKTOK_SPEND,
              revenue,
              GOOGLE_TOTAL_SPEND + META_TOTAL_SPEND + TIKTOK_SPEND as total_spend
            FROM `{self.table_ref}`
            """
            
            # Vue: ROI par jour
            view_roi = f"""
            CREATE OR REPLACE VIEW `{self.project_id}.{self.dataset_id}.mmm_daily_roi` AS
            SELECT
              date_day,
              revenue,
              GOOGLE_TOTAL_SPEND + META_TOTAL_SPEND + TIKTOK_SPEND as total_spend,
              revenue / (GOOGLE_TOTAL_SPEND + META_TOTAL_SPEND + TIKTOK_SPEND + 1) as roi
            FROM `{self.table_ref}`
            WHERE revenue > 0
            """
            
            # Exécuter les requêtes
            self.client.query(view_channel).result()
            self.client.query(view_roi).result()
            
            print("✅ Vues créées avec succès")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erreur création vues: {e}")
            return False


def load_all_data():
    """Charge toutes les étapes de données dans BigQuery"""
    print("="*70)
    print("🚀 CHARGEMENT DES DONNÉES DANS BIGQUERY")
    print("="*70)
    
    loader = BigQueryLoader(PROJECT_ID, DATASET_ID, TABLE_ID)
    
    results = {
        'clean': False,
        'features': False,
        'normalized': False,
        'views': False
    }
    
    # Charger les données nettoyées
    if os.path.exists(CLEAN_DATA_PATH):
        results['clean'] = loader.load_from_csv(CLEAN_DATA_PATH, "_clean")
    else:
        print(f"⚠️  Fichier non trouvé: {CLEAN_DATA_PATH}")
    
    # Charger les données avec features
    if os.path.exists(FEATURES_DATA_PATH):
        results['features'] = loader.load_from_csv(FEATURES_DATA_PATH, "_features")
    else:
        print(f"⚠️  Fichier non trouvé: {FEATURES_DATA_PATH}")
    
    # Charger les données normalisées
    if os.path.exists(NORMALIZED_DATA_PATH):
        results['normalized'] = loader.load_from_csv(NORMALIZED_DATA_PATH)
    else:
        print(f"⚠️  Fichier non trouvé: {NORMALIZED_DATA_PATH}")
    
    # Créer les vues
    results['views'] = loader.create_views()
    
    # Résumé
    print("\n" + "="*70)
    print("📊 RÉSUMÉ")
    print("="*70)
    print(f"Données nettoyées:  {'✅' if results['clean'] else '❌'}")
    print(f"Données avec features: {'✅' if results['features'] else '❌'}")
    print(f"Données normalisées: {'✅' if results['normalized'] else '❌'}")
    print(f"Vues créées:        {'✅' if results['views'] else '❌'}")
    print("="*70 + "\n")
    
    return results


if __name__ == "__main__":
    load_all_data()