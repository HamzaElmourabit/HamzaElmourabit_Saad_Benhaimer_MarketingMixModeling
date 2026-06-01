"""
Streamlit App - MMM Pro Dashboard
Architecture multi-page avec Streamlit
"""

import sys
import streamlit as st
import pandas as pd
import numpy as np
import os
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard.pages.looker_dashboards import show_looker_page
from models.mmm_model import (
    train_mmm_model,
    estimate_budget_revenue,
    get_channel_attribution,
)

# ===== CONFIG =====
st.set_page_config(
    page_title="MMM Pro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== STYLE NETFLIX =====
st.markdown("""
    <style>
        /* Dark theme */
        .main {
            background-color: #0e1117;
            color: #e6edf3;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #58a6ff;
            font-weight: 700;
        }
        
        /* Metrics */
        .stMetric {
            background-color: #1a1c24;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #58a6ff;
        }
        
        /* Buttons */
        .stButton > button {
            background-color: #238636;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: 600;
        }
        
        .stButton > button:hover {
            background-color: #2ea043;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab"] {
            color: #58a6ff;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: #1a1c24;
        }

        /* Metrics high contrast */
        [data-testid="metric-container"] {
            background-color: #131722 !important;
            border: 1px solid #2f4f7f !important;
            border-radius: 16px !important;
            padding: 14px !important;
        }

        [data-testid="metric-container"] div {
            color: #e6edf3 !important;
        }

        [data-testid="metric-container"] .stMetricValue, 
        [data-testid="metric-container"] .stMetricDelta, 
        [data-testid="metric-container"] .stMetricLabel {
            color: #e6edf3 !important;
        }

        [data-testid="metric-container"] .stMetricDelta {
            color: #7ee787 !important;
        }
    </style>
""", unsafe_allow_html=True)

# ===== SETUP PATHS =====
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MMDATA_PATH = DATA_DIR / "mmm_ready.csv"

# ===== CACHE DATA LOADING =====
@st.cache_data
def load_mmm_data():
    """Cache le chargement des données"""
    if not MMDATA_PATH.exists():
        return None
    
    df = pd.read_csv(MMDATA_PATH)
    
    # Parse dates
    date_cols = [col for col in df.columns if 'DATE' in col.upper()]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df


def get_spend_cols(df):
    """Detecte les colonnes de dépense pertinentes, y compris les transformations adstock/sat."""
    candidates = [c for c in df.columns if 'SPEND' in c.upper()]
    candidates = [c for c in candidates if 'INTERACTION' not in c.upper() and 'REVENUE_PER_SPEND' not in c.upper()]
    if not candidates:
        return []

    # Prefer clean spend columns without scaling/logs
    preferred = [c for c in candidates if not any(x in c.upper() for x in ['SCALED', 'LOG', 'LAG'])]
    if preferred:
        return preferred

    # Fallback to adstock spend columns
    adstock = [c for c in candidates if 'ADSTOCK' in c.upper() and not any(x in c.upper() for x in ['SCALED', 'LOG', 'LAG'])]
    if adstock:
        return adstock

    return [c for c in candidates if 'LAG' not in c.upper()]


def get_revenue_col(df):
    priorities = ['FIRST_PURCHASES_ORIGINAL_PRICE', 'REVENUE']
    for token in priorities:
        for col in df.columns:
            if token in col.upper():
                return col
    return None


def get_date_col(df):
    date_cols = [c for c in df.columns if 'DATE' in c.upper()]
    return date_cols[0] if date_cols else None


def format_currency(value):
    return f"${value:,.0f}" if pd.notna(value) else "N/A"


def format_percent(value):
    return f"{value*100:.1f}%" if pd.notna(value) else "N/A"


def compute_channel_summary(df, spend_cols):
    spend_total = df[spend_cols].sum()
    total = spend_total.sum()
    summary = pd.DataFrame({
        'Canal': spend_total.index,
        'Dépenses totales': spend_total.values,
        'Part budget': [(x / total if total > 0 else 0) for x in spend_total.values]
    })
    summary['Dépenses totales'] = summary['Dépenses totales'].map(format_currency)
    summary['Part budget'] = summary['Part budget'].map(format_percent)
    return summary.sort_values('Canal')

# ===== MAIN APP =====
def main():
    st.sidebar.title("🎯 Navigation")
    
    # Menu principal
    page = st.sidebar.radio(
        "Sélectionnez une page",
        ["📊 Dashboard", "📈 Analyse Canaux", "🎯 Scenarios", "🎨 Attribution", "🔗 Looker", "⚙️ Configuration"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **MMM Pro Dashboard**\n"
        "Marketing Mix Modeling avec PyMC3\n"
        "Attribution multi-touch et scenarios budgétaires"
    )
    
    # Charger les données
    df = load_mmm_data()
    
    if df is None:
        st.error("❌ Données MMM non trouvées. Lancez d'abord la pipeline ETL.")
        st.code("python run_pipeline.py")
        return
    
    # Router vers les pages
    if page == "📊 Dashboard":
        show_dashboard(df)
    elif page == "📈 Analyse Canaux":
        show_channel_analysis(df)
    elif page == "🎯 Scenarios":
        show_scenarios(df)
    elif page == "🎨 Attribution":
        show_attribution(df)
    elif page == "🔗 Looker":
        show_looker_page()
    elif page == "⚙️ Configuration":
        show_config()


def show_dashboard(df):
    """Page principale - KPIs et trends"""
    st.markdown("# 📊 Dashboard MMM")
    
    # Filtres
    date_col = get_date_col(df)
    if date_col is None:
        st.error("❌ Aucune colonne de date trouvée dans les données. Impossible d'afficher le dashboard.")
        return

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Date début", value=df[date_col].min().date())
    with col2:
        end_date = st.date_input("Date fin", value=df[date_col].max().date())
    
    # Filter data
    df_filtered = df[
        (df[date_col].dt.date >= start_date) & 
        (df[date_col].dt.date <= end_date)
    ].copy()
    
    # ===== KPI SECTION =====
    st.markdown("## 🔥 Key Metrics")
    
    # Identifier les colonnes
    spend_cols = get_spend_cols(df_filtered)
    revenue_col = get_revenue_col(df_filtered)

    if not spend_cols:
        st.warning("⚠️ Aucune colonne de dépense trouvée dans le dataset. Vérifiez `mmm_ready.csv`.")
        return

    if revenue_col is None:
        st.warning("⚠️ Aucune colonne de revenu trouvée dans le dataset. Vérifiez `mmm_ready.csv`.")
        return

    total_spend = df_filtered[spend_cols].sum().sum() if spend_cols else 0
    total_revenue = df_filtered[revenue_col].sum() if revenue_col else 0
    roi = total_revenue / total_spend if total_spend > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Total Spend",
            f"${total_spend:,.0f}",
            delta=f"{(total_spend/len(df_filtered)):,.0f} /day" if len(df_filtered) > 0 else None
        )
    
    with col2:
        st.metric(
            "📈 Total Revenue",
            f"${total_revenue:,.0f}",
            delta=f"{(total_revenue/len(df_filtered)):,.0f} /day" if len(df_filtered) > 0 else None
        )
    
    with col3:
        st.metric(
            "🎯 ROI",
            f"{roi:.2f}x",
            delta=f"Revenue per $ spent"
        )
    
    with col4:
        days = len(df_filtered)
        st.metric(
            "📅 Période",
            f"{days} jours",
            delta=f"{(total_spend/days):,.0f} spend/day" if days > 0 else None
        )
    
    # ===== CHANNEL SUMMARY =====
    st.markdown("## 💼 Spend par canal")
    channel_summary = compute_channel_summary(df_filtered, spend_cols)
    st.dataframe(channel_summary, width='stretch')

    top_channels = channel_summary.sort_values('Dépenses totales', key=lambda x: x.str.replace('[$,]', '', regex=True).astype(float), ascending=False).head(5)
    st.markdown("### 🔥 Top 5 Canaux par Dépense")
    st.table(top_channels.reset_index(drop=True))
    
    # ===== TRENDS =====
    st.markdown("## 📊 Trends")
    
    tab1, tab2, tab3 = st.tabs(["Revenue Trend", "Spend Trend", "ROI Trend"])
    
    with tab1:
        date_col_name = date_col
        revenue_ts = df_filtered.groupby(date_col_name)[revenue_col].sum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=revenue_ts.index,
            y=revenue_ts.values,
            mode='lines',
            name='Revenue',
            line=dict(color='#58a6ff', width=3),
            fill='tozeroy'
        ))
        fig.update_layout(
            template='plotly_dark',
            hovermode='x unified',
            title='Daily Revenue'
        )
        st.plotly_chart(fig, width='stretch')
    
    with tab2:
        spend_ts = df_filtered.groupby(date_col_name)[spend_cols].sum().sum(axis=1)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=spend_ts.index,
            y=spend_ts.values,
            mode='lines',
            name='Spend',
            line=dict(color='#f85149', width=3),
            fill='tozeroy'
        ))
        fig.update_layout(
            template='plotly_dark',
            hovermode='x unified',
            title='Daily Spend'
        )
        st.plotly_chart(fig, width='stretch')
    
    with tab3:
        roi_ts = (df_filtered.groupby(date_col_name)[revenue_col].sum() / 
                 df_filtered.groupby(date_col_name)[spend_cols].sum().sum(axis=1))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=roi_ts.index,
            y=roi_ts.values,
            mode='lines+markers',
            name='ROI',
            line=dict(color='#79c0ff', width=3)
        ))
        fig.update_layout(
            template='plotly_dark',
            hovermode='x unified',
            title='Daily ROI'
        )
        st.plotly_chart(fig, width='stretch')
    
    # ===== CHANNEL MIX =====
    st.markdown("## 💰 Channel Spend Mix")
    
    channel_spend = df_filtered[spend_cols].sum()
    
    fig = go.Figure(data=[go.Pie(
        labels=channel_spend.index,
        values=channel_spend.values,
        hole=.3
    )])
    fig.update_layout(template='plotly_dark', title='Spend Distribution')
    st.plotly_chart(fig, width='stretch')


def show_channel_analysis(df):
    """Analyse détaillée par canal"""
    st.markdown("# 📈 Analyse par Canal")
    
    spend_cols = get_spend_cols(df)
    revenue_col = get_revenue_col(df)

    if not spend_cols:
        st.warning("⚠️ Aucun canal dépense trouvé dans le dataset. Vérifiez `mmm_ready.csv`.")
        return

    if revenue_col is None:
        st.warning("⚠️ Colonne de revenu introuvable (ex: `revenue` ou `FIRST_PURCHASES_ORIGINAL_PRICE`). Impossible d'afficher l'analyse canal.")
        return
    
    # Sélection canal
    selected_channel = st.selectbox("Sélectionnez un canal", spend_cols)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # selected_channel is guaranteed to be one of spend_cols
        st.metric(
            f"Total {selected_channel}",
            f"${df[selected_channel].sum():,.0f}"
        )
    
    with col2:
        spend_sum = df[selected_channel].fillna(0).sum()
        revenue_sum = df[revenue_col].fillna(0).sum()
        roi_channel = revenue_sum / spend_sum if spend_sum > 0 else 0
        spend_share = spend_sum / df[spend_cols].sum().sum() if df[spend_cols].sum().sum() > 0 else 0
        st.metric(
            f"ROI {selected_channel}",
            f"{roi_channel:.2f}x"
        )
    
    st.markdown("### 📌 Résumé canal")
    st.write(f"- **Part du budget canal**: {format_percent(spend_share)}")
    st.write(f"- **Dépense totale canal**: {format_currency(spend_sum)}")
    
    with st.expander("Voir les 5 canaux les plus dépensiers"):
        channel_summary = compute_channel_summary(df, spend_cols)
        top_channels = channel_summary.sort_values('Dépenses totales', key=lambda x: x.str.replace('[$,]', '', regex=True).astype(float), ascending=False).head(5)
        st.table(top_channels)
    
    # Time series & Scatter: Spend vs Revenue
    date_col = get_date_col(df)
    if date_col is None:
        st.warning("⚠️ Aucune colonne de date trouvée — impossible d'afficher les séries temporelles.")
        return
    df_ts = df[[date_col, selected_channel, revenue_col]].copy()
    df_ts[date_col] = pd.to_datetime(df_ts[date_col], errors='coerce')
    df_daily = df_ts.groupby(date_col).agg({
        selected_channel: 'sum',
        revenue_col: 'sum'
    }).reset_index().fillna(0)

    # Time series plot for spend and revenue
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(x=df_daily[date_col], y=df_daily[selected_channel], name='Spend', line=dict(color='#f85149')))
    fig_ts.add_trace(go.Scatter(x=df_daily[date_col], y=df_daily[revenue_col], name='Revenue', line=dict(color='#58a6ff')))
    fig_ts.update_layout(template='plotly_dark', title=f'{selected_channel} - Spend vs Revenue Over Time', hovermode='x unified')
    st.plotly_chart(fig_ts, width='stretch')

    # Scatter with trendline
    fig = px.scatter(
        df_daily,
        x=selected_channel,
        y=revenue_col,
        title=f'{selected_channel} vs Revenue (daily)'
    )
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, width='stretch')


def show_scenarios(df):
    """What-if scenarios budgétaires"""
    st.markdown("# 🎯 Budget Scenarios (What-If Analysis)")
    
    st.info(
        "💡 Simulez différents allocations budgétaires et voyez l'impact prédit par le modèle MMM."
    )
    
    spend_cols = get_spend_cols(df)
    revenue_col = get_revenue_col(df)

    if not spend_cols:
        st.warning("⚠️ Aucun canal de dépense disponible pour la simulation. Vérifiez `mmm_ready.csv`.")
        return

    if revenue_col is None:
        st.warning("⚠️ Colonne de revenu introuvable. La simulation nécessite une colonne `revenue` ou similaire.")
        return

    model_info = train_mmm_model(df, target_col=revenue_col)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("R² du modèle", f"{model_info['r2']:.2f}")
    with col2:
        st.metric("Erreur quadratique moyenne", f"{model_info['mse']:,.0f}")

    # Budget actuel
    current_budget = df[spend_cols].sum().sum()
    
    st.markdown("## 💰 Budget Actuel")
    st.metric("Total Budget", f"${current_budget:,.0f}")
    
    # Sliders pour ajuster le budget par canal
    st.markdown("## 🎚️ Ajustez l'allocation budgétaire")
    
    allocation_pct = {}
    cols = st.columns(len(spend_cols))
    
    for idx, (col_name, col) in enumerate(zip(spend_cols, cols)):
        current_pct = (df[col_name].sum() / current_budget) * 100 if current_budget > 0 else 0
        with col:
            allocation_pct[col_name] = st.slider(
                f"{col_name.replace('_SPEND', '')}",
                min_value=0,
                max_value=100,
                value=int(current_pct),
                step=5
            )
    
    # Vérifier que la somme = 100%
    total_pct = sum(allocation_pct.values())
    
    if abs(total_pct - 100) > 1:
        st.warning(f"⚠️ Total = {total_pct}%. Doit être 100%")
    else:
        st.success("✅ Allocation valide")
        
        # Calculer le budget proposé
        st.markdown("## 📊 Budget Proposé")
        
        proposed_budget = {
            channel: (current_budget * pct) / 100
            for channel, pct in allocation_pct.items()
        }
        
        proposed_df = pd.DataFrame({
            'Channel': list(proposed_budget.keys()),
            'Current': [df[c].sum() for c in proposed_budget.keys()],
            'Proposed': list(proposed_budget.values()),
        })
        proposed_df['Change'] = proposed_df['Proposed'] - proposed_df['Current']
        proposed_df['Change %'] = (proposed_df['Change'] / proposed_df['Current'] * 100).replace([np.inf, -np.inf], 0).round(1)
        proposed_df['Current'] = proposed_df['Current'].map(format_currency)
        proposed_df['Proposed'] = proposed_df['Proposed'].map(format_currency)
        proposed_df['Change'] = proposed_df['Change'].map(format_currency)
        proposed_df['Change %'] = proposed_df['Change %'].map(lambda x: f"{x:.1f}%")
        
        st.dataframe(proposed_df, width='stretch')

        current_prediction = estimate_budget_revenue(
            model_info,
            df,
            {channel: df[channel].sum() for channel in spend_cols}
        )
        proposed_prediction = estimate_budget_revenue(model_info, df, proposed_budget)
        delta_prediction = proposed_prediction - current_prediction

        st.markdown("### 📈 Scénario Modélisé")
        st.write(f"- **Prévision actuelle**: {format_currency(current_prediction)}")
        st.write(f"- **Prévision scénario**: {format_currency(proposed_prediction)}")
        st.write(f"- **Delta attendu**: {format_currency(delta_prediction)}")
        st.write(f"- **ROI modèle**: {format_percent(delta_prediction / current_prediction) if current_prediction != 0 else 'N/A'}")

        st.markdown("### 📌 Notes")
        st.write(
            "Ce scénario utilise un modèle de régression MMM entraîné sur les colonnes `ADSTOCK_SAT` et les interactions."
        )


def show_attribution(df):
    """Attribution multi-touch (Shapley)"""
    st.markdown("# 🎨 Attribution Multi-Touch")
    
    st.info(
        "💡 Attribution via Shapley Values\n"
        "Attribue le crédit à chaque canal de manière équitable"
    )
    
    spend_cols = get_spend_cols(df)
    revenue_col = get_revenue_col(df)

    if not spend_cols:
        st.warning("⚠️ Aucun canal dépense trouvé — impossible de calculer l'attribution.")
        return

    if revenue_col is None:
        st.warning("⚠️ Colonne de revenu introuvable — impossible de calculer l'attribution.")
        return
    
    st.markdown("## 📊 Attribution Model")
    
    attribution_model = st.radio(
        "Modèle d'attribution",
        ["Model-based", "Linear", "Shapley Value (Proxy)"]
    )
    
    if attribution_model == "Model-based":
        model_info = train_mmm_model(df, target_col=revenue_col)
        attribution_df = get_channel_attribution(model_info, df)
        attribution_df['Attributed Revenue'] = attribution_df['Contribution'].map(format_currency)
        attribution_df['Contribution Share'] = attribution_df['Contribution Share'].map(format_percent)
        title = "Revenue Attribution basées sur le modèle MMM"
    elif attribution_model == "Linear":
        total_revenue = df[revenue_col].sum()
        attribution_df = pd.DataFrame({
            'Channel': spend_cols,
            'Attributed Revenue': [total_revenue / len(spend_cols)] * len(spend_cols)
        })
        attribution_df['Contribution Share'] = 1.0 / len(spend_cols)
        title = "Revenue Attribution linéaire"
    else:
        total_revenue = df[revenue_col].sum()
        spend_total = df[spend_cols].sum().sum()
        attribution_df = pd.DataFrame({
            'Channel': spend_cols,
            'Attributed Revenue': [
                total_revenue * (df[channel].sum() / spend_total if spend_total > 0 else 0)
                for channel in spend_cols
            ]
        })
        attribution_df['Contribution Share'] = attribution_df['Attributed Revenue'].abs() / attribution_df['Attributed Revenue'].abs().sum()
        title = "Revenue Attribution proxy Shapley"

    display_df = attribution_df.copy()
    display_df['Attributed Revenue'] = display_df['Attributed Revenue'].map(format_currency)
    display_df['Contribution Share'] = display_df['Contribution Share'].map(format_percent)
    
    fig = px.bar(
        attribution_df,
        x='Channel',
        y='Attributed Revenue',
        title=title
    )
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, width='stretch')
    st.markdown("### Attribution par canal")
    st.table(display_df)


def show_config():
    """Configuration et docs"""
    st.markdown("# ⚙️ Configuration")
    
    tab1, tab2, tab3 = st.tabs(["📊 Data Status", "🔧 MMM Config", "📚 Documentation"])
    
    with tab1:
        st.markdown("## Data Files")
        
        if MMDATA_PATH.exists():
            df = load_mmm_data()
            st.success(f"✅ mmm_ready.csv loaded")
            st.metric("Rows", len(df))
            st.metric("Columns", len(df.columns))
            
            st.markdown("### Column Info")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': [str(df[col].dtype) for col in df.columns],
                'Non-Null': [df[col].notna().sum() for col in df.columns]
            })
            st.dataframe(col_info, width='stretch')
        else:
            st.error(f"❌ mmm_ready.csv not found at {MMDATA_PATH}")
    
    with tab2:
        st.markdown("## Channel Configuration")
        
        config_info = {
            'Channel': [
                'Google Search', 'Google Shopping', 'Google Display',
                'Google PMax', 'Google Video', 'Meta Facebook',
                'Meta Instagram', 'TikTok'
            ],
            'Decay': [0.5, 0.4, 0.7, 0.6, 0.65, 0.6, 0.65, 0.7],
            'Saturation': [1.5, 1.5, 1.2, 1.5, 1.3, 1.4, 1.3, 1.2]
        }
        
        config_df = pd.DataFrame(config_info)
        st.dataframe(config_df, width='stretch')
    
    with tab3:
        st.markdown("## Documentation")
        
        st.markdown("""
        ### 📖 Guides Disponibles
        
        - **DATA_PIPELINE.md** - Pipeline ETL complète
        - **DATA_IMPROVEMENTS.md** - Améliorations apportées
        - **MMM_VARIABLES_REFERENCE.md** - Référence des variables
        
        ### 🚀 Quick Start
        
        ```bash
        # Lancer la pipeline Data
        python run_pipeline.py
        
        # Lancer le dashboard
        streamlit run dashboard/app.py
        ```
        
        ### 📞 Support
        
        Pour des questions sur la modélisation MMM, consultez la documentation dans le dossier racine.
        """)


if __name__ == "__main__":
    main()