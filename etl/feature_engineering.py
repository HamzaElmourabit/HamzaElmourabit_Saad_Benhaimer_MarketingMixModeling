

import pandas as pd
import numpy as np
from typing import Dict, List
import pickle


class AdstockTransform:
    """
    Adstock transforme les dépenses passées pour tenir compte du délai de réaction
    Formule: adstocked_spend(t) = spend(t) + λ*spend(t-1) + λ²*spend(t-2) + ...
    où λ (lambda) est le decay parameter [0, 1]
    """
    
    @staticmethod
    def geometric_adstock(spend: np.ndarray, decay: float = 0.5, window: int = 13) -> np.ndarray:
        """
        Adstock géométrique (forme standard)
        
        Args:
            spend: array de dépenses
            decay: paramètre de décroissance (0.1-0.9)
            window: nombre de périodes antérieures à considérer
        
        Returns:
            array avec adstock appliqué
        """
        adstocked = np.zeros_like(spend, dtype=float)
        
        for i in range(len(spend)):
            # Somme des périodes passées avec décroissance exponentielle
            for j in range(window):
                if i >= j:
                    weight = decay ** j
                    adstocked[i] += spend[i - j] * weight
        
        return adstocked
    
    @staticmethod
    def adstock_with_normalize(spend: np.ndarray, decay: float = 0.5, window: int = 13) -> np.ndarray:
        """Adstock normalisé pour préserver l'effet total"""
        adstocked = AdstockTransform.geometric_adstock(spend, decay, window)
        # Normalisation pour que la somme soit conservée
        normalization_factor = 1 + decay + decay**2 + decay**3
        return adstocked / normalization_factor


class SaturationTransform:
    """
    Transformation Hill pour modéliser la saturation
    Formule: saturated = x^s / (k^s + x^s)
    où s = saturation coeff, k = midpoint
    """
    
    @staticmethod
    def hill_transform(spend: np.ndarray, s: float = 1.5, k: float = 0.5) -> np.ndarray:
        """
        Transformation Hill (saturation)
        
        Args:
            spend: dépenses (normalisées 0-1)
            s: saturation coefficient (0.5-2.0, défaut 1.5)
            k: midpoint (0.1-1.0, défaut 0.5)
        
        Returns:
            spend transformé avec saturation
        """
        return (spend ** s) / (k ** s + spend ** s)
    
    @staticmethod
    def logistic_saturation(spend: np.ndarray, midpoint: float = 0.5) -> np.ndarray:
        """Alternative: transformation logistique"""
        return 1 / (1 + np.exp(-10 * (spend - midpoint)))


class FeatureEngineer:
    """Pipeline de feature engineering pour MMM"""
    
    # Configuration par défaut pour chaque canal
    CHANNEL_CONFIG = {
        'GOOGLE_PAID_SEARCH_SPEND': {'decay': 0.5, 'saturation_s': 1.5},
        'GOOGLE_SHOPPING_SPEND': {'decay': 0.4, 'saturation_s': 1.5},
        'GOOGLE_DISPLAY_SPEND': {'decay': 0.7, 'saturation_s': 1.2},
        'GOOGLE_PMAX_SPEND': {'decay': 0.6, 'saturation_s': 1.5},
        'GOOGLE_VIDEO_SPEND': {'decay': 0.65, 'saturation_s': 1.3},
        'META_FACEBOOK_SPEND': {'decay': 0.6, 'saturation_s': 1.4},
        'META_INSTAGRAM_SPEND': {'decay': 0.65, 'saturation_s': 1.3},
        'TIKTOK_SPEND': {'decay': 0.7, 'saturation_s': 1.2},
    }
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.adstock_params = {}
        self.normalization_params = {}
    
    def create_features(self) -> pd.DataFrame:
        """Pipeline complète de feature engineering"""
        print("🔧 Feature Engineering en cours...")
        
        # 1. Adstock (réduction de dimension)
        self.df = self._apply_adstock()
        
        # 2. Lags
        self.df = self._apply_lags()
        
        # 3. Saturation
        self.df = self._apply_saturation()
        
        # 4. Interactions
        self.df = self._create_interactions()
        
        # 5. Variables de contrôle
        self.df = self._create_control_variables()
        
        print("✅ Feature Engineering complété")
        return self.df
    
    def _apply_adstock(self) -> pd.DataFrame:
        """Applique l'adstock à tous les canaux"""
        print("  📍 Application de l'Adstock...")
        
        spend_cols = [col for col in self.df.columns if 'SPEND' in col]
        
        for col in spend_cols:
            # Grouper par organisation et appliquer adstock
            for org in self.df['ORGANISATION_VERTICAL'].unique():
                mask = self.df['ORGANISATION_VERTICAL'] == org
                spend_values = self.df.loc[mask, col].values
                
                decay = self.CHANNEL_CONFIG.get(col, {}).get('decay', 0.5)
                adstocked = AdstockTransform.adstock_with_normalize(spend_values, decay=decay)
                
                self.df.loc[mask, f'{col}_ADSTOCK'] = adstocked
                self.adstock_params[col] = decay
        
        return self.df
    
    def _apply_lags(self) -> pd.DataFrame:
        """Crée des lags pour les dépenses (effet du marketing passé)"""
        print("  📍 Application des Lags...")
        
        spend_cols = [col for col in self.df.columns if 'SPEND' in col and 'ADSTOCK' not in col]
        
        for col in spend_cols:
            for lag in [1, 2, 4]:  # 1 jour, 2 jours, 4 jours
                for org in self.df['ORGANISATION_VERTICAL'].unique():
                    mask = self.df['ORGANISATION_VERTICAL'] == org
                    self.df.loc[mask, f'{col}_LAG{lag}'] = \
                        self.df.loc[mask, col].shift(lag).fillna(0)
        
        return self.df
    
    def _apply_saturation(self) -> pd.DataFrame:
        """Applique la transformation Hill (saturation) aux adstock"""
        print("  📍 Application de la Saturation...")
        
        adstock_cols = [col for col in self.df.columns if 'ADSTOCK' in col]
        
        for col in adstock_cols:
            # Normaliser en 0-1
            col_min = self.df[col].min()
            col_max = self.df[col].max()
            col_normalized = (self.df[col] - col_min) / (col_max - col_min + 1e-10)
            
            # Appliquer saturation
            original_col = col.replace('_ADSTOCK', '')
            s = self.CHANNEL_CONFIG.get(original_col, {}).get('saturation_s', 1.5)
            
            self.df[f'{col}_SAT'] = SaturationTransform.hill_transform(
                col_normalized.values, 
                s=s, 
                k=0.5
            )
            
            # Rescaler à l'amplitude originale
            self.df[f'{col}_SAT'] = self.df[f'{col}_SAT'] * (col_max - col_min) + col_min
        
        return self.df
    
    def _create_interactions(self) -> pd.DataFrame:
        """Crée les interactions entre canaux"""
        print("  📍 Création des Interactions...")
        
        # Interactions entre Google et Meta (synergy)
        google_cols = [col for col in self.df.columns 
                      if 'GOOGLE' in col and 'ADSTOCK_SAT' in col]
        meta_cols = [col for col in self.df.columns 
                    if 'META' in col and 'ADSTOCK_SAT' in col]
        
        if google_cols and meta_cols:
            google_mean = self.df[google_cols].mean(axis=1)
            meta_mean = self.df[meta_cols].mean(axis=1)
            self.df['GOOGLE_META_INTERACTION'] = google_mean * meta_mean
        
        # Interactions Google Search + Display (brand building)
        if 'GOOGLE_PAID_SEARCH_SPEND_ADSTOCK_SAT' in self.df.columns and \
           'GOOGLE_DISPLAY_SPEND_ADSTOCK_SAT' in self.df.columns:
            self.df['SEARCH_DISPLAY_INTERACTION'] = \
                self.df['GOOGLE_PAID_SEARCH_SPEND_ADSTOCK_SAT'] * \
                self.df['GOOGLE_DISPLAY_SPEND_ADSTOCK_SAT']
        
        return self.df
    
    def _create_control_variables(self) -> pd.DataFrame:
        """Crée des variables de contrôle"""
        print("  📍 Création des Variables de Contrôle...")
        
        # Day of week effect
        self.df['DATE_DAY'] = pd.to_datetime(self.df['DATE_DAY'], format="%d-%m-%Y", errors='coerce')
        self.df['WEEKDAY'] = self.df['DATE_DAY'].dt.dayofweek
        self.df['MONTH'] = self.df['DATE_DAY'].dt.month
        self.df['QUARTER'] = self.df['DATE_DAY'].dt.quarter
        
        # Trend (nombre de jours depuis le début)
        self.df['TREND'] = (self.df['DATE_DAY'] - self.df['DATE_DAY'].min()).dt.days
        
        # Cycliques (sin/cos encoding)
        self.df['MONTH_SIN'] = np.sin(2 * np.pi * self.df['MONTH'] / 12)
        self.df['MONTH_COS'] = np.cos(2 * np.pi * self.df['MONTH'] / 12)
        
        return self.df
    
    def save_params(self, path: str):
        """Sauvegarde les paramètres pour reproduction"""
        params = {
            'adstock_params': self.adstock_params,
            'normalization_params': self.normalization_params
        }
        with open(path, 'wb') as f:
            pickle.dump(params, f)
        print(f"✅ Paramètres sauvegardés: {path}")


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Fonction wrapper simple"""
    engineer = FeatureEngineer(df)
    return engineer.create_features()
