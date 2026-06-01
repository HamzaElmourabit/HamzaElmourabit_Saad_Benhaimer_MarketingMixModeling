
import os
import pandas as pd
import numpy as np
from validation import DataValidator

# ====== CONFIGURATION ======
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_PATH = os.path.join(BASE_DIR, "data/raw/compressed_data.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data/processed/mmm_ready.csv")

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)


class DataCleaner:
    """Nettoie et prépare les données brutes"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
    
    def clean_all(self) -> pd.DataFrame:
        """Pipeline complète de nettoyage"""
        print("🧹 Nettoyage des données en cours...\n")
        
        self.df = self._parse_dates()
        self.df = self._standardize_columns()
        self.df = self._handle_missing_values()
        self.df = self._fix_negative_values()
        self.df = self._remove_duplicates()
        self.df = self._aggregate_channels()
        self.df = self._create_basic_metrics()
        
        print("\n✅ Nettoyage complété")
        return self.df
    
    def _parse_dates(self) -> pd.DataFrame:
        """Parse et valide les dates"""
        print("📅 Parsing des dates...")
        
        try:
            self.df['DATE_DAY'] = pd.to_datetime(
                self.df['DATE_DAY'], 
                format="%d-%m-%Y",
                errors='coerce'
            )
            
            invalid_dates = self.df['DATE_DAY'].isnull().sum()
            if invalid_dates > 0:
                print(f"⚠️  {invalid_dates} dates invalides remplacées")
                self.df = self.df[self.df['DATE_DAY'].notna()].reset_index(drop=True)
        
        except Exception as e:
            print(f"❌ Erreur: {e}")
        
        return self.df
    
    def _standardize_columns(self) -> pd.DataFrame:
        """Standardise les noms et types de colonnes"""
        print("🏷️  Standardisation des colonnes...")
        
        # Convertir en minuscules
        self.df.columns = self.df.columns.str.upper()
        
        # Assurer que les colonnes de dépense sont numériques
        spend_cols = [col for col in self.df.columns if 'SPEND' in col]
        for col in spend_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        # Assurer que les colonnes de métrique sont numériques
        metric_cols = [col for col in self.df.columns 
                      if any(x in col for x in ['PRICE', 'COST', 'CLICKS', 'IMPRESSIONS', 'PURCHASES'])]
        for col in metric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        
        return self.df
    
    def _handle_missing_values(self) -> pd.DataFrame:
        """Traite les valeurs manquantes intelligemment"""
        print("🔍 Traitement des valeurs manquantes...")
        
        # Pour les dépenses: remplir avec 0 (aucune dépense ce jour-là)
        spend_cols = [col for col in self.df.columns if 'SPEND' in col]
        self.df[spend_cols] = self.df[spend_cols].fillna(0)
        
        # Pour les métriques: interpoler ou remplir avec la médiane
        metric_cols = [col for col in self.df.columns 
                      if any(x in col for x in ['PRICE', 'COST', 'CLICKS', 'IMPRESSIONS', 'PURCHASES'])]
        
        for col in metric_cols:
            # Interpoler linéairement
            self.df[col] = self.df[col].interpolate(method='linear', limit_direction='both')
            # Remplir les NaN restants avec la médiane
            self.df[col] = self.df[col].fillna(self.df[col].median())
        
        remaining_na = self.df.isnull().sum().sum()
        print(f"  Valeurs manquantes résiduelles: {remaining_na}")
        
        return self.df
    
    def _fix_negative_values(self) -> pd.DataFrame:
        """Corrige les valeurs négatives invalides"""
        print("🔧 Correction des valeurs négatives...")
        
        # Les dépenses et revenus ne peuvent pas être négatifs
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            negatives = (self.df[col] < 0).sum()
            if negatives > 0:
                # Remplacer par 0 ou la médiane
                self.df.loc[self.df[col] < 0, col] = 0
                print(f"  ⚠️  {col}: {negatives} valeurs négatives corrigées")
        
        return self.df
    
    def _remove_duplicates(self) -> pd.DataFrame:
        """Supprime les lignes dupliquées"""
        print("🔄 Suppression des doublons...")
        
        subset_cols = ['DATE_DAY', 'ORGANISATION_VERTICAL', 'ORGANISATION_SUBVERTICAL']
        duplicates_before = len(self.df)
        
        self.df = self.df.drop_duplicates(subset=subset_cols, keep='first').reset_index(drop=True)
        
        duplicates_removed = duplicates_before - len(self.df)
        if duplicates_removed > 0:
            print(f"  Doublons supprimés: {duplicates_removed}")
        
        return self.df
    
    def _aggregate_channels(self) -> pd.DataFrame:
        """Agrège les dépenses par canal de haut niveau"""
        print("📊 Agrégation des canaux...")
        
        # Créer des colonnes de canal parent si elles n'existent pas
        if 'GOOGLE_SEARCH_SPEND' not in self.df.columns:
            if 'GOOGLE_PAID_SEARCH_SPEND' in self.df.columns:
                self.df['GOOGLE_SEARCH_SPEND'] = self.df['GOOGLE_PAID_SEARCH_SPEND']
        
        if 'GOOGLE_TOTAL_SPEND' not in self.df.columns:
            google_cols = [col for col in self.df.columns 
                          if col.startswith('GOOGLE') and 'SPEND' in col]
            if google_cols:
                self.df['GOOGLE_TOTAL_SPEND'] = self.df[google_cols].sum(axis=1)
        
        if 'META_TOTAL_SPEND' not in self.df.columns:
            meta_cols = [col for col in self.df.columns 
                        if col.startswith('META') and 'SPEND' in col]
            if meta_cols:
                self.df['META_TOTAL_SPEND'] = self.df[meta_cols].sum(axis=1)
        
        return self.df
    
    def _create_basic_metrics(self) -> pd.DataFrame:
        """Crée des métriques de base pour la validation"""
        print("📈 Création des métriques de base...")
        
        # ROI par canal (si données disponibles)
        if 'GOOGLE_PAID_SEARCH_SPEND' in self.df.columns and 'FIRST_PURCHASES_ORIGINAL_PRICE' in self.df.columns:
            self.df['REVENUE_PER_SPEND'] = (
                self.df['FIRST_PURCHASES_ORIGINAL_PRICE'] / 
                (self.df['GOOGLE_PAID_SEARCH_SPEND'] + 1)
            )
        
        # CPA moyen
        if 'GOOGLE_PAID_SEARCH_SPEND' in self.df.columns and 'FIRST_PURCHASES' in self.df.columns:
            self.df['AVG_CPA'] = (
                self.df['GOOGLE_PAID_SEARCH_SPEND'] / 
                (self.df['FIRST_PURCHASES'] + 1)
            )
        
        return self.df


def main():
    """Pipeline principal"""
    print("=" * 60)
    print("🚀 MMM DATA CLEANING PIPELINE")
    print("=" * 60 + "\n")
    
    # Charger les données
    print(f"📂 Chargement: {INPUT_PATH}")
    df_raw = pd.read_csv(INPUT_PATH)
    print(f"   Dimensions: {df_raw.shape[0]} lignes, {df_raw.shape[1]} colonnes\n")
    
    # Valider les données brutes
    validator = DataValidator(df_raw)
    validator.validate_all()
    
    # Nettoyer
    cleaner = DataCleaner(df_raw)
    df_clean = cleaner.clean_all()
    
    # Afficher statistiques
    print("\n" + "=" * 60)
    print("📊 STATISTIQUES APRÈS NETTOYAGE")
    print("=" * 60)
    print(f"Dimensions finales: {df_clean.shape[0]} lignes, {df_clean.shape[1]} colonnes")
    print(f"\nPériode: {df_clean['DATE_DAY'].min()} à {df_clean['DATE_DAY'].max()}")
    print(f"Verticales: {df_clean['ORGANISATION_VERTICAL'].nunique()}")
    
    # Résumé des dépenses et revenus
    spend_cols = [col for col in df_clean.columns if 'SPEND' in col and 'TOTAL' not in col]
    if spend_cols:
        print(f"\nDépenses totales:")
        for col in spend_cols[:5]:  # Afficher les 5 premiers
            total = df_clean[col].sum()
            print(f"  {col}: ${total:,.0f}")
    
    if 'FIRST_PURCHASES_ORIGINAL_PRICE' in df_clean.columns:
        print(f"\nRevenue total: ${df_clean['FIRST_PURCHASES_ORIGINAL_PRICE'].sum():,.0f}")
    
    # Sauvegarder
    print(f"\n💾 Sauvegarde: {OUTPUT_PATH}")
    df_clean.to_csv(OUTPUT_PATH, index=False)
    print("✅ Données nettoyées sauvegardées avec succès!\n")


if __name__ == "__main__":
    main()