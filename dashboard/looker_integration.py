"""
Looker Integration Module - MMM Project
Intègre les dashboards Looker dans Streamlit
"""

import streamlit as st
import requests
from typing import Optional
import os


class LookerEmbedManager:
    """Gère l'intégration des dashboards Looker"""
    
    def __init__(self, api_host: str, api_key: str, api_secret: str):
        self.api_host = api_host.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.token = None
        self.api_version = '4.0'
    
    def authenticate(self) -> bool:
        """Authentifie avec l'API Looker"""
        try:
            auth_url = f"{self.api_host}/api/{self.api_version}/login"
            response = requests.post(
                auth_url,
                json={
                    'client_id': self.api_key,
                    'client_secret': self.api_secret
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.token = response.json().get('access_token')
                return True
            st.error(f"❌ Looker auth failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
            return False
    
    def get_embed_url(self, dashboard_id: str, user_email: str, user_name: str) -> Optional[str]:
        """Génère l'URL d'embedding sécurisée pour un dashboard"""
        if not self.token and not self.authenticate():
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            embed_payload = {
                'user_id': user_email,
                'external_user_id': user_email,
                'external_group_ids': [],
                'group_ids': [],
                'models': ['mmm'],
                'permissions': ['see_user_dashboards', 'see_looks', 'see_user_dashboards'],
                'access_filters': {},
                'first_name': user_name,
                'session_length': 3600,
                'force_logout_login': True
            }
            
            sso_url = f"{self.api_host}/api/{self.api_version}/login/embed/{dashboard_id}"
            response = requests.post(
                sso_url,
                headers=headers,
                json=embed_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                embed_url = response.json().get('url')
                if embed_url.startswith('http'):
                    return embed_url
                return f"{self.api_host}{embed_url}"
            st.error(f"❌ Looker embed failed: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            st.error(f"❌ Error generating embed URL: {e}")
            return None
    
    def list_dashboards(self) -> dict:
        """Liste les dashboards Looker disponibles"""
        if not self.token and not self.authenticate():
            return {}
        
        try:
            headers = {'Authorization': f'Bearer {self.token}'}
            response = requests.get(
                f"{self.api_host}/api/{self.api_version}/dashboards",
                headers=headers,
                params={'limit': 100},
                timeout=10
            )
            
            if response.status_code == 200:
                dashboards = {}
                for dash in response.json():
                    dashboards[str(dash['id'])] = {
                        'title': dash['title'],
                        'description': dash.get('description', ''),
                        'id': str(dash['id'])
                    }
                return dashboards
            st.error(f"❌ Looker list dashboards failed: {response.status_code} - {response.text}")
            return {}
        except Exception as e:
            st.error(f"❌ Error listing dashboards: {e}")
            return {}


def show_looker_dashboard(dashboard_id: str, api_host: str, api_key: str, api_secret: str):
    """
    Affiche un dashboard Looker dans Streamlit
    
    Args:
        dashboard_id: ID du dashboard Looker
        api_host: Host Looker
        api_key: API key
        api_secret: API secret
    """
    manager = LookerEmbedManager(api_host, api_key, api_secret)
    
    # Obtenir les infos utilisateur
    user_email = "mmm-user@company.com"  # À remplacer par session user
    user_name = "MMM User"
    
    # Générer l'URL d'embedding
    embed_url = manager.get_embed_url(dashboard_id, user_email, user_name)
    
    if embed_url:
        st.markdown(f'<iframe src="{embed_url}" width="100%" height="800"></iframe>', 
                   unsafe_allow_html=True)
    else:
        st.error("❌ Impossible de charger le dashboard Looker")


@st.cache_data
def get_looker_credentials() -> dict:
    """Charge les credentials Looker depuis les variables d'environnement"""
    return {
        'api_host': os.getenv('LOOKER_API_HOST', ''),
        'api_key': os.getenv('LOOKER_API_KEY', ''),
        'api_secret': os.getenv('LOOKER_API_SECRET', '')
    }


def looker_section_available() -> bool:
    """Vérifie si les credentials Looker sont configurés"""
    creds = get_looker_credentials()
    return all([creds['api_host'], creds['api_key'], creds['api_secret']])
