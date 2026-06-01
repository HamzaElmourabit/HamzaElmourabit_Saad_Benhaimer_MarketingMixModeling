"""
Quick Start Script - MMM Project
Lance la pipeline complète en une seule commande.

Usage:
    python run_pipeline.py
    python run_pipeline.py --validate-only
    python run_pipeline.py --clean-only
"""

import sys
import os
import argparse
from pathlib import Path

# Ajouter le répertoire ETL au path
BASE_DIR = Path(__file__).parent
ETL_DIR = BASE_DIR / "etl"
sys.path.insert(0, str(ETL_DIR))

def print_banner():
    """Affiche la bannière de démarrage"""
    print("\n" + "=" * 70)
    print("🚀 MARKETING MIX MODELING - DATA PIPELINE")
    print("=" * 70 + "\n")

def run_pipeline():
    """Lance la pipeline complète"""
    from pipeline import ETLPipeline
    
    raw_data_path = BASE_DIR / "data/raw/compressed_data.csv"
    output_dir = BASE_DIR / "data/processed"
    
    pipeline = ETLPipeline(str(raw_data_path), str(output_dir))
    return pipeline.run()

def run_validation_only():
    """Lance uniquement la validation"""
    from validation import validate_dataset
    
    raw_data_path = BASE_DIR / "data/raw/compressed_data.csv"
    
    print("🔍 Mode: Validation uniquement\n")
    return validate_dataset(str(raw_data_path))

def run_cleaning_only():
    """Lance uniquement le nettoyage"""
    from clean import main as clean_main
    
    print("🧹 Mode: Nettoyage uniquement\n")
    return clean_main()

def load_to_bigquery():
    """Charge les données dans BigQuery"""
    from load_bigquery import load_all_data
    
    print("\n" + "=" * 70)
    print("📤 Chargement dans BigQuery")
    print("=" * 70 + "\n")
    
    return load_all_data()

def show_config():
    """Affiche la configuration"""
    from config import get_data_paths, CHANNEL_CONFIG, BIGQUERY_PROJECT_ID
    
    print("\n📋 CONFIGURATION")
    print("=" * 70)
    print(f"BigQuery Project: {BIGQUERY_PROJECT_ID}")
    print(f"Number of channels: {len(CHANNEL_CONFIG)}")
    
    print("\n📊 Paths:")
    paths = get_data_paths()
    for name, path in paths.items():
        exists = "✅" if os.path.exists(path) else "⚠️"
        print(f"  {exists} {name}: {path}")
    
    print("\n🎯 Channels:")
    for channel, config in list(CHANNEL_CONFIG.items())[:3]:
        print(f"  - {channel}")
        print(f"    decay={config['decay']}, saturation_s={config['saturation_s']}")
    print(f"  ... and {len(CHANNEL_CONFIG) - 3} more")

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description="MMM Data Pipeline")
    parser.add_argument("--validate-only", action="store_true", 
                       help="Validate data only")
    parser.add_argument("--clean-only", action="store_true", 
                       help="Clean data only")
    parser.add_argument("--config", action="store_true", 
                       help="Show configuration")
    parser.add_argument("--bigquery", action="store_true", 
                       help="Load to BigQuery after pipeline")
    
    args = parser.parse_args()
    
    print_banner()
    
    try:
        if args.config:
            show_config()
            return
        
        if args.validate_only:
            run_validation_only()
        elif args.clean_only:
            run_cleaning_only()
        else:
            # Pipeline complète
            df_ready = run_pipeline()
            
            if args.bigquery:
                load_to_bigquery()
        
        print("\n" + "=" * 70)
        print("✅ SUCCÈS - Pipeline complétée!")
        print("=" * 70 + "\n")
        
        return 0
    
    except FileNotFoundError as e:
        print(f"\n❌ ERREUR: Fichier non trouvé")
        print(f"   {e}")
        print(f"\n💡 Assurez-vous que les données brutes sont dans: data/raw/compressed_data.csv")
        return 1
    
    except Exception as e:
        print(f"\n❌ ERREUR INATTENDUE")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
