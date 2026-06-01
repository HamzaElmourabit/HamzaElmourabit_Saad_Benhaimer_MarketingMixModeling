import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional

DEFAULT_TARGET_CANDIDATES = [
    'FIRST_PURCHASES_ORIGINAL_PRICE',
    'REVENUE',
    'FIRST_PURCHASES'
]

CONTROL_FEATURES = ['WEEKDAY', 'MONTH_SIN', 'MONTH_COS', 'TREND']


def _is_base_adstock_feature(col: str) -> bool:
    return (
        col.endswith('_SPEND_ADSTOCK_SAT')
        and 'TOTAL' not in col
        and 'REVENUE_PER_SPEND' not in col
        and 'SCALED' not in col
        and 'LOG' not in col
    )


def get_revenue_col(df: pd.DataFrame) -> Optional[str]:
    for candidate in DEFAULT_TARGET_CANDIDATES:
        for col in df.columns:
            if candidate in col.upper():
                return col
    return None


def get_channel_feature_cols(df: pd.DataFrame, include_controls: bool = True) -> List[str]:
    feature_cols = [c for c in df.columns if _is_base_adstock_feature(c)]
    feature_cols += [c for c in df.columns if 'INTERACTION' in c and 'SCALED' not in c and 'LOG' not in c]

    if include_controls:
        feature_cols += [c for c in CONTROL_FEATURES if c in df.columns]

    return [c for c in feature_cols if c in df.columns]


def prepare_model_data(df: pd.DataFrame, target_col: Optional[str] = None, include_controls: bool = True):
    target_col = target_col or get_revenue_col(df)
    if target_col is None:
        raise ValueError('Aucune colonne cible de revenu trouvée dans le dataset.')

    feature_cols = get_channel_feature_cols(df, include_controls=include_controls)
    if not feature_cols:
        raise ValueError('Aucune colonne de feature marketing trouvée pour le modèle MMM.')

    df_model = df.copy()
    df_model = df_model[feature_cols + [target_col]].fillna(0)

    X = df_model[feature_cols].astype(float)
    y = df_model[target_col].astype(float)
    return X, y, feature_cols


def train_mmm_model(df: pd.DataFrame, target_col: Optional[str] = None, include_controls: bool = True, alpha: float = 1.0):
    X, y, feature_cols = prepare_model_data(df, target_col=target_col, include_controls=include_controls)

    model = Pipeline([
        ('scaler', StandardScaler()),
        ('ridge', Ridge(alpha=alpha, random_state=42))
    ])
    model.fit(X, y)

    y_pred = model.predict(X)
    metrics = {
        'r2': float(r2_score(y, y_pred)),
        'mse': float(mean_squared_error(y, y_pred)),
        'target_col': target_col,
        'feature_cols': feature_cols,
        'baseline_pred': float(np.mean(y_pred)),
        'feature_means': X.mean(axis=0).to_dict(),
        'channel_feature_names': [c for c in feature_cols if 'ADSTOCK_SAT' in c or 'INTERACTION' in c],
        'control_feature_names': [c for c in feature_cols if c in CONTROL_FEATURES]
    }

    return {
        'model': model,
        'X': X,
        'y': y,
        'y_pred': y_pred,
        **metrics
    }


def _map_spend_to_feature(df: pd.DataFrame, spend_col: str) -> Optional[str]:
    candidates = [
        c for c in df.columns
        if c.startswith(spend_col) and c.endswith('_ADSTOCK_SAT')
    ]
    return candidates[0] if candidates else None


def _recompute_interactions(feature_values: Dict[str, float]) -> Dict[str, float]:
    feature_values = feature_values.copy()

    if 'SEARCH_DISPLAY_INTERACTION' in feature_values:
        search = feature_values.get('GOOGLE_PAID_SEARCH_SPEND_ADSTOCK_SAT', 0.0)
        display = feature_values.get('GOOGLE_DISPLAY_SPEND_ADSTOCK_SAT', 0.0)
        feature_values['SEARCH_DISPLAY_INTERACTION'] = search * display

    google_cols = [k for k in feature_values if k.startswith('GOOGLE') and 'ADSTOCK_SAT' in k]
    meta_cols = [k for k in feature_values if k.startswith('META') and 'ADSTOCK_SAT' in k]

    if 'GOOGLE_META_INTERACTION' in feature_values and google_cols and meta_cols:
        google_mean = np.mean([feature_values.get(col, 0.0) for col in google_cols])
        meta_mean = np.mean([feature_values.get(col, 0.0) for col in meta_cols])
        feature_values['GOOGLE_META_INTERACTION'] = google_mean * meta_mean

    return feature_values


def estimate_budget_revenue(model_info: Dict, df: pd.DataFrame, proposed_budget: Dict[str, float]) -> float:
    feature_cols = model_info['feature_cols']
    feature_means = {k: float(v) for k, v in model_info['feature_means'].items()}

    adjusted_features = feature_means.copy()

    for spend_col, budget in proposed_budget.items():
        feature_name = _map_spend_to_feature(df, spend_col)
        if feature_name and spend_col in df.columns:
            current_spend = float(df[spend_col].sum())
            ratio = float(budget / current_spend) if current_spend > 0 else 1.0
            adjusted_features[feature_name] = adjusted_features.get(feature_name, 0.0) * ratio

    adjusted_features = _recompute_interactions(adjusted_features)
    row = pd.DataFrame([adjusted_features], columns=feature_cols)

    prediction = float(model_info['model'].predict(row)[0])
    return prediction


def get_channel_attribution(model_info: Dict, df: pd.DataFrame) -> pd.DataFrame:
    coef = model_info['model'].named_steps['ridge'].coef_
    feature_cols = model_info['feature_cols']
    feature_means = {k: float(v) for k, v in model_info['feature_means'].items()}

    contributions = []
    for name, weight in zip(feature_cols, coef):
        if 'ADSTOCK_SAT' not in name and 'INTERACTION' not in name:
            continue

        contribution = weight * feature_means.get(name, 0.0)
        contributions.append({
            'Channel': name,
            'Coefficient': float(weight),
            'Average Feature': float(feature_means.get(name, 0.0)),
            'Contribution': float(contribution)
        })

    attribution_df = pd.DataFrame(contributions)
    if attribution_df.empty:
        return pd.DataFrame(columns=['Channel', 'Coefficient', 'Average Feature', 'Contribution', 'Contribution Share'])

    total_contribution = attribution_df['Contribution'].abs().sum()
    if total_contribution == 0:
        attribution_df['Contribution Share'] = 0.0
    else:
        attribution_df['Contribution Share'] = attribution_df['Contribution'].abs() / total_contribution

    attribution_df = attribution_df.sort_values(by='Contribution', key=lambda x: x.abs(), ascending=False)
    return attribution_df
