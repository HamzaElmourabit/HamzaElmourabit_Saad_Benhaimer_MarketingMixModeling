"""
Data Validation Module - MMM Project
Valide la qualité et l'intégrité des données brutes avant transformation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class DataValidator:
    """Valide les données pour le MMM"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.validation_report = {}
    
    def validate_all(self) -> Dict:
        """Lance toutes les validations"""
        print("🔍 Validation des données en cours...")
        
        self.check_missing_values()
        self.check_date_format()
        self.check_numeric_ranges()
        self.check_duplicates()
        self.check_data_types()
        self.check_spend_revenue_consistency()
        
        self.print_report()
        return self.validation_report
    
    def check_missing_values(self):
        """Détecte les valeurs manquantes"""
        missing = self.df.isnull().sum()
        missing_pct = (missing / len(self.df)) * 100
        
        self.validation_report['missing_values'] = {
            'count': missing[missing > 0].to_dict(),
            'percentage': missing_pct[missing_pct > 0].to_dict()
        }
        
        if missing.sum() > 0:
            print(f"⚠️  {missing.sum()} valeurs manquantes détectées")
            print(missing[missing > 0])
    
    def check_date_format(self):
        """Valide le format des dates"""
        try:
            # Tenter conversion
            dates = pd.to_datetime(self.df['DATE_DAY'], format="%d-%m-%Y", errors='coerce')
            invalid_dates = dates.isnull().sum()
            
            self.validation_report['date_validity'] = {
                'valid_count': len(dates) - invalid_dates,
                'invalid_count': invalid_dates
            }
            
            if invalid_dates > 0:
                print(f"⚠️  {invalid_dates} dates invalides détectées")
        except Exception as e:
            print(f"❌ Erreur format date: {e}")
    
    def check_numeric_ranges(self):
        """Vérifie que les colonnes numériques ont des valeurs raisonnables"""
        spend_cols = [col for col in self.df.columns if 'SPEND' in col or 'COST' in col]
        revenue_cols = [col for col in self.df.columns if 'PRICE' in col or 'REVENUE' in col]
        
        ranges_report = {}
        
        # Vérifier que les dépenses sont positives
        for col in spend_cols:
            if col in self.df.columns:
                negatives = (self.df[col] < 0).sum()
                if negatives > 0:
                    print(f"⚠️  {col}: {negatives} valeurs négatives")
                    ranges_report[col] = f"{negatives} négatives"
        
        # Vérifier que les revenus sont positifs
        for col in revenue_cols:
            if col in self.df.columns:
                negatives = (self.df[col] < 0).sum()
                if negatives > 0:
                    print(f"⚠️  {col}: {negatives} valeurs négatives")
                    ranges_report[col] = f"{negatives} négatives"
        
        self.validation_report['ranges'] = ranges_report
    
    def check_duplicates(self):
        """Détecte les lignes dupliquées"""
        duplicates = self.df.duplicated(
            subset=['DATE_DAY', 'ORGANISATION_VERTICAL', 'ORGANISATION_SUBVERTICAL'],
            keep=False
        ).sum()
        
        self.validation_report['duplicates'] = duplicates
        
        if duplicates > 0:
            print(f"⚠️  {duplicates} lignes potentiellement dupliquées")
    
    def check_data_types(self):
        """Vérifie les types de données"""
        print("\n📊 Types de données:")
        print(self.df.dtypes)
        self.validation_report['dtypes'] = self.df.dtypes.to_dict()
    
    def check_spend_revenue_consistency(self):
        """Vérifie la cohérence entre les dépenses et les revenus"""
        spend_cols = [col for col in self.df.columns if 'SPEND' in col]
        total_spend = self.df[spend_cols].sum().sum()
        total_revenue = self.df['FIRST_PURCHASES_ORIGINAL_PRICE'].sum()
        
        self.validation_report['spend_revenue'] = {
            'total_spend': float(total_spend),
            'total_revenue': float(total_revenue),
            'ratio': float(total_revenue / total_spend) if total_spend > 0 else 0
        }
        
        print(f"\n💰 Dépenses totales: ${total_spend:,.0f}")
        print(f"💰 Revenus totales: ${total_revenue:,.0f}")
        print(f"📈 Ratio revenue/spend: {total_revenue/total_spend if total_spend > 0 else 0:.2f}")
    
    def print_report(self):
        """Affiche le rapport de validation"""
        print("\n" + "="*50)
        print("✅ RAPPORT DE VALIDATION COMPLÉTÉ")
        print("="*50)


def validate_dataset(input_path: str) -> pd.DataFrame:
    """Charge et valide un dataset"""
    df = pd.read_csv(input_path)
    validator = DataValidator(df)
    validator.validate_all()
    return df
