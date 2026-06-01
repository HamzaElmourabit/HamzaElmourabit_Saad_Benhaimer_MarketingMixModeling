"""
Page Looker Dashboards - Streamlit App
Affiche les dashboards Looker intégrés dans Streamlit
"""

import os
import streamlit as st
from dashboard.looker_integration import LookerEmbedManager, get_looker_credentials, looker_section_available


def show_looker_page():
    """Affiche la page Looker"""
    st.markdown("# 🎨 Looker Dashboards (Embedded)")
    
    if not looker_section_available():
        st.warning(
            "⚠️ Credentials Looker non configurées\n\n"
            "Pour intégrer Looker, configurez:\n"
            "- `LOOKER_API_HOST`\n"
            "- `LOOKER_API_KEY`\n"
            "- `LOOKER_API_SECRET`"
        )
        
        with st.expander("📖 Configuration Looker"):
            st.markdown("""
            ### Variables d'environnement requises
            
            ```bash
            export LOOKER_API_HOST=https://looker.company.com
            export LOOKER_API_KEY=your-api-key
            export LOOKER_API_SECRET=your-api-secret
            ```
            
            ### Étapes d'intégration
            
            1. **Créer une Service Account dans Looker**
               - Admin → Users → Service Accounts
               - Générer une API key/secret
            
            2. **Créer les dashboards dans Looker**
               - Explore → MMM model
               - Créer des visualisations
               - Sauvegarder comme dashboards
            
            3. **Configurer les permissions**
               - Service Account doit avoir accès aux dashboards
               - Activer les paramètres d'embed pour le compte
            
            4. **Configurer la liste des dashboards**
               - Utiliser `LOOKER_DASHBOARD_IDS` dans `.env`
            
            ### Dashboards recommandés
            
            - **mmm_overview** - Vue d'ensemble MMM
            - **channel_performance** - Performance par canal
            - **roi_analysis** - Analyse ROI
            - **trends** - Tendances long-terme
            """)
        
        return
    
    creds = get_looker_credentials()
    manager = LookerEmbedManager(creds['api_host'], creds['api_key'], creds['api_secret'])
    configured_ids = [dash.strip() for dash in os.getenv('LOOKER_DASHBOARD_IDS', '').split(',') if dash.strip()]
    dashboards = manager.list_dashboards()

    st.markdown("## 📊 Tableau de bord Looker")
    if configured_ids:
        st.info(f"Dashboards configurés via `LOOKER_DASHBOARD_IDS`: {', '.join(configured_ids)}")
    
    if dashboards:
        dashboard_options = []
        if configured_ids:
            dashboard_options = [dash_id for dash_id in configured_ids if dash_id in dashboards]
            if not dashboard_options:
                dashboard_options = list(dashboards.keys())
        else:
            dashboard_options = list(dashboards.keys())

        selected_dash_id = st.selectbox(
            "Sélectionnez un dashboard Looker",
            dashboard_options,
            format_func=lambda x: dashboards[x]['title'] if x in dashboards else x
        )

        st.markdown(f"### {dashboards[selected_dash_id]['title']}" if selected_dash_id in dashboards else "### Dashboard sélectionné")
        if selected_dash_id in dashboards and dashboards[selected_dash_id]['description']:
            st.info(dashboards[selected_dash_id]['description'])

        user_email = os.getenv('LOOKER_EMBED_USER_EMAIL', 'mmm-user@company.com')
        user_name = os.getenv('LOOKER_EMBED_USER_NAME', 'MMM User')
        embed_url = manager.get_embed_url(selected_dash_id, user_email, user_name)

        if embed_url:
            st.markdown(f'<iframe src="{embed_url}" width="100%" height="900" frameborder="0"></iframe>', unsafe_allow_html=True)
        else:
            st.error("❌ Impossible de charger le dashboard Looker. Vérifiez les permissions et l'URL Looker.")
    else:
        st.info("📭 Aucun dashboard trouvé dans Looker")
        st.markdown("""
        ### Créer les dashboards dans Looker
        1. Ouvrir Looker
        2. Aller sur "Explore" → "MMM" model
        3. Créer des visualisations
        4. Sauvegarder comme dashboard
        """)

    with st.expander("📄 Snippets LookML pour le modèle MMM"):
        st.markdown("""
        ### Exemple LookML pour `mmm.view`
        ```lookml
        view: mmm {
          sql_table_name: `{{ project_id }}.{{ dataset_id }}.{{ table_id }}` ;;
          dimension_group: date_day {
            type: date
            sql: ${TABLE}.date_day ;;
          }
          dimension: channel {
            type: string
            sql: ${TABLE}.channel ;;
          }
          measure: total_revenue {
            type: sum
            sql: ${TABLE}.revenue ;;
          }
          measure: total_spend {
            type: sum
            sql: ${TABLE}.google_search_spend + ${TABLE}.google_display_spend + ${TABLE}.meta_facebook_spend + ${TABLE}.meta_instagram_spend + ${TABLE}.tiktok_spend ;;
          }
          measure: roi {
            type: number
            sql: ${total_revenue} / NULLIF(${total_spend}, 0) ;;
            value_format: "0.00x"
          }
        }
        ```

        ### Exemple LookML pour `mmm_overview.dashboard`
        ```lookml
        dashboard: mmm_overview {
          title: "MMM Overview"
          layout: newspaper
          element: {
            title: "Total Revenue"
            type: single_value
            query: {
              fields: [mmm.total_revenue]
            }
          }
          element: {
            title: "Total Spend"
            type: single_value
            query: {
              fields: [mmm.total_spend]
            }
          }
          element: {
            title: "Revenue Trend"
            type: line
            query: {
              fields: [mmm.date_day, mmm.total_revenue]
            }
          }
        }
        ```
        """)


def looker_dashboard_snippets() -> dict:
    """
    Fournit les snippets LookML pour les dashboards MMM
    À ajouter dans Looker
    """
    return {
        'mmm_overview': """
        - title: "MMM Overview"
          description: "Vue d'ensemble MMM"
          layout: newspaper
          tiles:
            - title: "Total Spend"
              query: mmm_daily
              dimensions: [date_day]
              measures: [total_spend]
              type: metric
              
            - title: "Total Revenue"
              query: mmm_daily
              dimensions: [date_day]
              measures: [total_revenue]
              type: metric
              
            - title: "Revenue vs Spend"
              query: mmm_daily
              dimensions: [date_day]
              measures: [total_revenue, total_spend]
              type: line
              
            - title: "Channel Mix"
              query: mmm_channel
              dimensions: [channel]
              measures: [spend]
              type: donut
        """,
        
        'channel_performance': """
        - title: "Channel Performance"
          description: "Performance détaillée par canal"
          layout: newspaper
          tiles:
            - title: "Spend by Channel"
              query: mmm_channel
              dimensions: [channel]
              measures: [spend]
              type: bar
              
            - title: "Revenue by Channel"
              query: mmm_channel
              dimensions: [channel]
              measures: [revenue]
              type: bar
              
            - title: "ROI by Channel"
              query: mmm_channel
              dimensions: [channel]
              measures: [roi]
              type: table
        """,
        
        'roi_analysis': """
        - title: "ROI Analysis"
          description: "Analyse détaillée du ROI"
          layout: newspaper
          tiles:
            - title: "Daily ROI"
              query: mmm_daily
              dimensions: [date_day]
              measures: [roi]
              type: line
              
            - title: "ROI Distribution"
              query: mmm_daily
              dimensions: [roi_bucket]
              measures: [count]
              type: bar
        """
    }


if __name__ == "__main__":
    show_looker_page()
