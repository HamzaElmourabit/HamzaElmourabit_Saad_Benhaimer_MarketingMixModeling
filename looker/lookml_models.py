"""
Looker LookML Models - MMM Project
Modèles LookML pour les dashboards Looker
"""

# ==========================
# MMM MODEL - Connexion BigQuery
# ==========================

MODEL_FILE = """
connection: "bigquery"
include: "/views/*.view"

explore: mmm {
  label: "MMM"
  description: "Explore des métriques Marketing Mix Modeling"
  join: mmm_channels {
    sql_on: ${mmm.channel} = ${mmm_channels.channel_name} ;;
    relationship: many_to_one
  }
}
"""

MMM_VIEW = """
view: mmm {
  sql_table_name: `rh-etl-project-467521.MMM_dataset.mmm` ;;

  dimension_group: date_day {
    type: date
    sql: ${TABLE}.date_day ;;
    timeframes: [raw, date, week, month, quarter, year]
  }

  dimension: organisation_vertical {
    type: string
    sql: ${TABLE}.organisation_vertical ;;
  }

  dimension: territory {
    type: string
    sql: ${TABLE}.territory ;;
  }

  dimension: google_search_spend {
    type: number
    sql: ${TABLE}.google_search_spend ;;
  }

  dimension: google_display_spend {
    type: number
    sql: ${TABLE}.google_display_spend ;;
  }

  dimension: meta_facebook_spend {
    type: number
    sql: ${TABLE}.meta_facebook_spend ;;
  }

  dimension: meta_instagram_spend {
    type: number
    sql: ${TABLE}.meta_instagram_spend ;;
  }

  dimension: tiktok_spend {
    type: number
    sql: ${TABLE}.tiktok_spend ;;
  }

  dimension: revenue {
    type: number
    sql: ${TABLE}.revenue ;;
  }

  measure: total_revenue {
    type: sum
    sql: ${revenue} ;;
  }

  measure: total_google_search_spend {
    type: sum
    sql: ${google_search_spend} ;;
  }

  measure: total_google_display_spend {
    type: sum
    sql: ${google_display_spend} ;;
  }

  measure: total_meta_facebook_spend {
    type: sum
    sql: ${meta_facebook_spend} ;;
  }

  measure: total_meta_instagram_spend {
    type: sum
    sql: ${meta_instagram_spend} ;;
  }

  measure: total_tiktok_spend {
    type: sum
    sql: ${tiktok_spend} ;;
  }

  measure: total_spend {
    type: number
    sql: ${total_google_search_spend} + ${total_google_display_spend} + ${total_meta_facebook_spend} + ${total_meta_instagram_spend} + ${total_tiktok_spend} ;;
  }

  measure: roi {
    type: number
    sql: ${total_revenue} / NULLIF(${total_spend}, 0) ;;
    value_format: "0.00x"
  }

  measure: revenue_per_spend {
    type: number
    sql: ${total_revenue} / NULLIF(${total_spend}, 0) ;;
    value_format: "$#,##0.00"
  }
}
"""

# ==========================
# CHANNEL COMPARISON VIEW
# ==========================

CHANNEL_VIEW = """
view: mmm_channels {
  derived_table: {
    sql: SELECT
      CASE
        WHEN google_search_spend > 0 THEN 'Google Search'
        WHEN google_display_spend > 0 THEN 'Google Display'
        WHEN meta_facebook_spend > 0 THEN 'Meta Facebook'
        WHEN meta_instagram_spend > 0 THEN 'Meta Instagram'
        WHEN tiktok_spend > 0 THEN 'TikTok'
        ELSE 'Other'
      END AS channel_name,
      google_search_spend,
      google_display_spend,
      meta_facebook_spend,
      meta_instagram_spend,
      tiktok_spend,
      revenue
    FROM `rh-etl-project-467521.MMM_dataset.mmm` ;;
  }

  dimension: channel_name {
    type: string
    sql: ${TABLE}.channel_name ;;
  }

  measure: total_spend {
    type: sum
    sql: ${TABLE}.google_search_spend + ${TABLE}.google_display_spend + ${TABLE}.meta_facebook_spend + ${TABLE}.meta_instagram_spend + ${TABLE}.tiktok_spend ;;
  }

  measure: total_revenue {
    type: sum
    sql: ${TABLE}.revenue ;;
  }

  measure: roi {
    type: number
    sql: ${total_revenue} / NULLIF(${total_spend}, 0) ;;
    value_format: "0.00x"
  }
}
"""

# ==========================
# DASHBOARD LookML
# ==========================

MMM_DASHBOARD = """
dashboard: mmm_overview {
  title: "MMM Overview"
  description: "Vue d'ensemble du Marketing Mix Modeling"

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
      sorts: [mmm.date_day]
    }
  }

  element: {
    title: "Spend by Channel"
    type: pie
    query: {
      fields: [mmm_channels.channel_name, mmm_channels.total_spend]
    }
  }

  element: {
    title: "ROI by Channel"
    type: table
    query: {
      fields: [mmm_channels.channel_name, mmm_channels.total_spend, mmm_channels.total_revenue, mmm_channels.roi]
    }
  }
}
"""

# ==========================
# LOOKML VIEWS DICTIONARY
# ==========================

LOOKML_FILES = {
    'model/mmm.model': MODEL_FILE,
    'views/mmm.view': MMM_VIEW,
    'views/mmm_channels.view': CHANNEL_VIEW,
    'dashboards/mmm_overview.dashboard': MMM_DASHBOARD,
}


def get_lookml_export() -> dict:
    """Exporte les fichiers LookML"""
    return LOOKML_FILES


def install_lookml_files():
    """
    Instructions pour installer les fichiers LookML dans Looker
    
    À faire manuellement:
    1. Ouvrir Looker Dev Mode
    2. Créer les fichiers dans le dossier project
    3. Copier le contenu des fichiers
    4. Commiter les changements
    """
    
    print("""
    📋 INSTALLATION DES FICHIERS LOOKML
    ===================================
    
    1. Ouvrir Looker (https://looker.company.com)
    2. Développement → Manage Projects
    3. Créer ou ouvrir le project "mmm"
    4. Dev Mode → Créer les fichiers:
    
       ├── views/
       │   ├── mmm.view.lkml
       │   └── mmm_channels.view.lkml
       │
       └── dashboards/
           └── mmm_overview.dashboard.lookml
    
    5. Coller le contenu de chaque fichier
    6. Commiter les changements
    7. Deploy vers production
    
    📚 Fichiers disponibles:
    - views/mmm.view (vue principale)
    - views/mmm_channels.view (analyse canaux)
    - dashboards/mmm_overview.dashboard (dashboard)
    """)


if __name__ == "__main__":
    install_lookml_files()
