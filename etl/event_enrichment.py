"""
Event Enrichment Module - MMM Project
Enrichit les données avec les jours fériés et événements spéciaux.
"""

import pandas as pd
import os
from datetime import datetime


class EventEnricher:
    """Enrichit les données avec les variables d'événement"""
    
    def __init__(self, df: pd.DataFrame, holidays_path: str = None):
        self.df = df.copy()
        
        if holidays_path is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            holidays_path = os.path.join(base_dir, "data/reference/holidays.csv")
        
        self.holidays_df = pd.read_csv(holidays_path)
        self.holidays_df['date'] = pd.to_datetime(self.holidays_df['date'])
    
    def enrich(self) -> pd.DataFrame:
        """Enrichit les données avec les variables d'événement"""
        print("🎉 Enrichissement avec événements...")
        
        # Assurer que DATE_DAY est datetime
        if self.df['DATE_DAY'].dtype == 'object':
            self.df['DATE_DAY'] = pd.to_datetime(self.df['DATE_DAY'], errors='coerce')
        
        # Créer une colonne pour chaque événement
        self.df['IS_HOLIDAY'] = 0
        self.df['IS_MAJOR_EVENT'] = 0
        self.df['EVENT_IMPACT'] = 'NONE'
        self.df['EVENT_NAME'] = None
        
        # Matcher les dates avec les événements
        for idx, row in self.holidays_df.iterrows():
            event_date = row['date']
            mask = self.df['DATE_DAY'].dt.date == event_date.date()
            
            if 'holiday' in row['event_type'].lower():
                self.df.loc[mask, 'IS_HOLIDAY'] = 1
            else:
                self.df.loc[mask, 'IS_MAJOR_EVENT'] = 1
            
            self.df.loc[mask, 'EVENT_IMPACT'] = row['impact_level']
            self.df.loc[mask, 'EVENT_NAME'] = row['event_name']
        
        # Créer des flags numériques pour chaque niveau d'impact
        self.df['IS_CRITICAL_EVENT'] = (self.df['EVENT_IMPACT'] == 'CRITICAL').astype(int)
        self.df['IS_HIGH_IMPACT'] = (self.df['EVENT_IMPACT'].isin(['HIGH', 'CRITICAL'])).astype(int)
        self.df['IS_MEDIUM_IMPACT'] = (self.df['EVENT_IMPACT'] == 'MEDIUM').astype(int)
        
        print("✅ Enrichissement complété")
        return self.df
    
    def get_event_summary(self) -> pd.DataFrame:
        """Retourne un résumé des événements dans la période"""
        return self.holidays_df[self.holidays_df['date'].dt.year >= self.df['DATE_DAY'].dt.year.min()].copy()


def enrich_with_events(df: pd.DataFrame, holidays_path: str = None) -> pd.DataFrame:
    """Fonction wrapper"""
    enricher = EventEnricher(df, holidays_path)
    return enricher.enrich()
