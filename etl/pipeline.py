"""
ETL Pipeline Orchestrator - MMM Project
Enchaîne tous les processus de nettoyage, feature engineering, et normalisation.
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Ajouter le répertoire au path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'etl'))

from clean import DataCleaner
from validation import DataValidator
from feature_engineering import FeatureEngineer
from normalize import DataNormalizer, prepare_for_modeling


class ETLPipeline:
    """Orchestration complète du pipeline ETL pour MMM"""
    
    def __init__(self, raw_data_path: str, output_dir: str = None):
        self.raw_data_path = raw_data_path
        self.output_dir = output_dir or os.path.join(BASE_DIR, "data/processed")
        
        os.makedirs(self.output_dir, exist_ok=True)
        self.metadata = {}
    
    def run(self) -> pd.DataFrame:
        """Exécute la pipeline complète"""
        print("\n" + "="*70)
        print("🚀 MARKETING MIX MODELING - ETL PIPELINE COMPLÈTE")
        print("="*70 + "\n")
        
        # ÉTAPE 1: VALIDATION
        print("\n[1/5] VALIDATION DES DONNÉES BRUTES")
        print("-" * 70)
        df_raw = self._load_data()
        self._validate_data(df_raw)
        
        # ÉTAPE 2: NETTOYAGE
        print("\n[2/5] NETTOYAGE DES DONNÉES")
        print("-" * 70)
        df_clean = self._clean_data(df_raw)
        self._save_intermediate("mmm_clean.csv", df_clean)
        
        # ÉTAPE 3: FEATURE ENGINEERING
        print("\n[3/5] FEATURE ENGINEERING")
        print("-" * 70)
        df_features = self._engineer_features(df_clean)
        self._save_intermediate("mmm_with_features.csv", df_features)
        
        # ÉTAPE 4: NORMALISATION
        print("\n[4/5] NORMALISATION DES DONNÉES")
        print("-" * 70)
        df_normalized = self._normalize_data(df_features)
        self._save_intermediate("mmm_normalized.csv", df_normalized)
        
        # ÉTAPE 5: PRÉPARATION POUR MODÉLISATION
        print("\n[5/5] PRÉPARATION POUR MODÉLISATION")
        print("-" * 70)
        df_model = self._prepare_for_modeling(df_normalized)
        self._save_final(df_model)
        
        # RÉSUMÉ
        self._print_summary(df_raw, df_clean, df_features, df_normalized, df_model)
        
        return df_model
    
    def _load_data(self) -> pd.DataFrame:
        """Charge les données brutes"""
        print(f"📂 Chargement: {self.raw_data_path}")
        
        if not os.path.exists(self.raw_data_path):
            raise FileNotFoundError(f"Fichier non trouvé: {self.raw_data_path}")
        
        df = pd.read_csv(self.raw_data_path)
        print(f"✅ {df.shape[0]} lignes, {df.shape[1]} colonnes chargées")
        
        self.metadata['raw_rows'] = df.shape[0]
        self.metadata['raw_cols'] = df.shape[1]
        
        return df
    
    def _validate_data(self, df: pd.DataFrame):
        """Valide les données brutes"""
        validator = DataValidator(df)
        validator.validate_all()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nettoie les données"""
        cleaner = DataCleaner(df)
        df_clean = cleaner.clean_all()
        
        self.metadata['clean_rows'] = df_clean.shape[0]
        self.metadata['rows_removed_cleaning'] = self.metadata['raw_rows'] - df_clean.shape[0]
        
        print(f"\n✅ Nettoyage complété: {df_clean.shape[0]} lignes restantes")
        
        return df_clean
    
    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Effectue le feature engineering"""
        engineer = FeatureEngineer(df)
        df_features = engineer.create_features()
        
        self.metadata['feature_cols'] = df_features.shape[1]
        self.metadata['new_features'] = df_features.shape[1] - df.shape[1]
        
        # Sauvegarder les paramètres
        params_path = os.path.join(self.output_dir, "adstock_params.pkl")
        engineer.save_params(params_path)
        
        print(f"\n✅ Features créées: {self.metadata['new_features']} nouvelles colonnes")
        
        return df_features
    
    def _normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalise les données"""
        normalizer = DataNormalizer(df)
        df_normalized, scalers = normalizer.normalize_all()
        
        # Sauvegarder les paramètres de normalisation
        params_path = os.path.join(self.output_dir, "normalization_params.pkl")
        normalizer.save_params(params_path)
        
        print(f"\n✅ Normalisation complétée")
        
        return df_normalized
    
    def _prepare_for_modeling(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prépare les données pour la modélisation"""
        df_model = prepare_for_modeling(df)
        
        self.metadata['model_rows'] = df_model.shape[0]
        self.metadata['model_cols'] = df_model.shape[1]
        
        return df_model
    
    def _save_intermediate(self, filename: str, df: pd.DataFrame):
        """Sauvegarde un fichier intermédiaire"""
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"  💾 Intermédiaire sauvegardé: {filename}")
    
    def _save_final(self, df: pd.DataFrame):
        """Sauvegarde le fichier final"""
        filepath = os.path.join(self.output_dir, "mmm_ready.csv")
        df.to_csv(filepath, index=False)
        print(f"\n✅ Fichier final sauvegardé: mmm_ready.csv")
        print(f"   Chemin: {filepath}")
    
    def _print_summary(self, df_raw, df_clean, df_features, df_normalized, df_model):
        """Affiche un résumé complet"""
        print("\n" + "="*70)
        print("📊 RÉSUMÉ DE LA PIPELINE")
        print("="*70)
        
        print(f"""
✅ Données brutes:       {df_raw.shape[0]:>6} lignes × {df_raw.shape[1]:>3} colonnes
✅ Après nettoyage:     {df_clean.shape[0]:>6} lignes × {df_clean.shape[1]:>3} colonnes
✅ Avec features:       {df_features.shape[0]:>6} lignes × {df_features.shape[1]:>3} colonnes
✅ Après normalisation: {df_normalized.shape[0]:>6} lignes × {df_normalized.shape[1]:>3} colonnes
✅ Prêt pour modeling:  {df_model.shape[0]:>6} lignes × {df_model.shape[1]:>3} colonnes

📉 Réduction de données: {100 * (1 - df_model.shape[0]/df_raw.shape[0]):.1f}% lignes supprimées
📈 Expansion de features: {df_model.shape[1] - df_raw.shape[1]:>3} nouvelles colonnes
        """)
        
        # Résumé des variables pour MMM
        print("\n📋 VARIABLES DISPONIBLES POUR MMM:")
        print("-" * 70)
        
        revenue_cols = [col for col in df_model.columns if 'REVENUE' in col or 'PRICE' in col]
        spend_cols = [col for col in df_model.columns if 'SPEND' in col]
        adstock_cols = [col for col in df_model.columns if 'ADSTOCK' in col]
        interaction_cols = [col for col in df_model.columns if 'INTERACTION' in col]
        
        print(f"  📊 Revenue: {len(revenue_cols)} variable(s)")
        print(f"  💰 Dépenses: {len(spend_cols)} variable(s)")
        print(f"  📍 Adstock: {len(adstock_cols)} variable(s) (réduction de dimension)")
        print(f"  🔗 Interactions: {len(interaction_cols)} variable(s)")
        
        print("\n🎯 Pipeline complétée avec succès!")
        print("="*70 + "\n")


def main():
    """Point d'entrée principal"""
    # Configuration
    raw_data_path = os.path.join(BASE_DIR, "data/raw/compressed_data.csv")
    output_dir = os.path.join(BASE_DIR, "data/processed")
    
    # Exécuter la pipeline
    pipeline = ETLPipeline(raw_data_path, output_dir)
    df_ready = pipeline.run()
    
    return df_ready


if __name__ == "__main__":
    main()
