
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import pickle
from typing import Dict, Tuple


class DataNormalizer:
    """Normalise les données pour la modélisation"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.scalers = {}
        self.feature_means = {}
        self.feature_stds = {}
    
    def normalize_all(self) -> Tuple[pd.DataFrame, Dict]:
        """Pipeline complète de normalisation"""
        print("🔄 Normalisation des données en cours...")
        
        # Identifier les types de colonnes
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        
        # Standardiser les variables numériques (0 mean, 1 std)
        self._standardize_numeric(numeric_cols)
        
        # Log-transform les dépenses (souvent très asymétriques)
        self._log_transform_spend()
        
        # Gérer les NaN résiduels
        self._handle_remaining_nans()
        
        print("✅ Normalisation complétée")
        return self.df, self.scalers
    
    def _standardize_numeric(self, numeric_cols):
        """Standardise les colonnes numériques"""
        print("  📍 Standardisation (z-score)...")
        
        for col in numeric_cols:
            if col in ['DATE_DAY', 'WEEKDAY', 'MONTH', 'QUARTER', 'TREND']:
                continue  # Ne pas standardiser les variables catégoriques
            
            # Calculer mean et std
            mean = self.df[col].mean()
            std = self.df[col].std()
            
            if std > 0:
                self.df[f'{col}_SCALED'] = (self.df[col] - mean) / std
                self.feature_means[col] = mean
                self.feature_stds[col] = std
            else:
                self.df[f'{col}_SCALED'] = self.df[col]
    
    def _log_transform_spend(self):
        """Log-transform les dépenses (pour réduire l'asymétrie)"""
        print("  📍 Log-transformation des dépenses...")
        
        spend_cols = [col for col in self.df.columns if 'SPEND' in col and 'SCALED' not in col]
        
        for col in spend_cols:
            # Log(1 + x) pour gérer les zéros
            self.df[f'{col}_LOG'] = np.log1p(self.df[col])
    
    def _handle_remaining_nans(self):
        """Remplace les NaN résiduels"""
        print("  📍 Gestion des valeurs manquantes...")
        
        # Forward fill puis backward fill
        self.df = self.df.fillna(method='ffill').fillna(method='bfill')
        
        # Remplacer les NaN restants par 0 (pour Bayesian)
        self.df = self.df.fillna(0)
        
        nan_count = self.df.isnull().sum().sum()
        print(f"    Valeurs manquantes résiduelles: {nan_count}")
    
    def get_normalization_params(self) -> Dict:
        """Retourne les paramètres de normalisation pour reproduction"""
        return {
            'feature_means': self.feature_means,
            'feature_stds': self.feature_stds,
            'scalers': self.scalers
        }
    
    def save_params(self, path: str):
        """Sauvegarde les paramètres de normalisation"""
        params = self.get_normalization_params()
        with open(path, 'wb') as f:
            pickle.dump(params, f)
        print(f"✅ Paramètres de normalisation sauvegardés: {path}")
    
    @staticmethod
    def denormalize(scaled_values: np.ndarray, mean: float, std: float) -> np.ndarray:
        """Dénormalise les prédictions (pour retourner à l'échelle originale)"""
        return scaled_values * std + mean


def normalize_dataset(df: pd.DataFrame, save_params_path: str = None) -> Tuple[pd.DataFrame, Dict]:
    """Fonction wrapper"""
    normalizer = DataNormalizer(df)
    df_normalized, scalers = normalizer.normalize_all()
    
    if save_params_path:
        normalizer.save_params(save_params_path)
    
    return df_normalized, scalers


def prepare_for_modeling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare le dataframe pour la modélisation:
    - Sélectionne les colonnes appropriées
    - Supprime les valeurs invalides
    - Assure la cohérence des données
    """
    print("🎯 Préparation pour la modélisation...")
    
    # Colonnes essentielles pour MMM
    feature_cols = {
        'date': 'DATE_DAY',
        'revenue': 'FIRST_PURCHASES_ORIGINAL_PRICE',
        'vertical': 'ORGANISATION_VERTICAL',
    }
    
    # Ajouter toutes les colonnes adstock+sat
    adstock_sat_cols = [col for col in df.columns if 'ADSTOCK_SAT' in col]
    
    # Créer le dataframe de modélisation
    model_df = df[['DATE_DAY', 'ORGANISATION_VERTICAL', 'FIRST_PURCHASES_ORIGINAL_PRICE'] + 
                  adstock_sat_cols + 
                  [col for col in df.columns if 'INTERACTION' in col]].copy()
    
    # Supprimer les lignes avec revenue zéro ou NaN
    model_df = model_df[model_df['FIRST_PURCHASES_ORIGINAL_PRICE'] > 0].reset_index(drop=True)
    
    # Standardiser la revenue
    normalizer = DataNormalizer(model_df)
    model_df, _ = normalizer.normalize_all()
    
    print(f"✅ Dataset de modélisation: {model_df.shape[0]} lignes, {model_df.shape[1]} colonnes")
    
    return model_df
