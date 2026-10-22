"""Shared data and presentation helpers for the Ecuador risk dashboard."""
from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "data_limpia_fairness.csv"
RESULTS_PATH = ROOT / "results" / "results"
MODEL_PATH = ROOT / "models"

FEATURES = [
    "Mes", "Trimestre", "Semestre", "Es_Temporada_Alta",
    "Total_Incidentes", "Incidentes_Seguridad", "Proporcion_Delitos",
    "Delitos_Lag_1", "Delitos_Lag_2", "Media_Movil_3M",
    "Tendencia_Inercial", "Cluster_Riesgo",
]

METRICS = pd.DataFrame([
    ["Random Forest (Baseline)", .840766, .656989, .611612, .633489, .887104, .690795, .114289],
    ["XGBoost (preoptimización)", .830405, .596698, .759760, .668428, .894794, .710315, .117882],
    ["XGBoost optimizado", .812387, .556157, .822823, .663706, .898111, .717359, .127808],
], columns=["Modelo", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "PR-AUC", "Brier"])

HYPERPARAMS = pd.DataFrame([
    ["n_estimators", "300", "160"], ["max_depth", "6", "5"],
    ["learning_rate", "0.0447", "0.05"], ["subsample", "0.70", "0.85"],
    ["colsample_bytree", "0.90", "0.85"], ["min_child_weight", "3", "1"],
    ["scale_pos_weight", "2.2", "1.5"], ["reg_alpha", "0.3298", "0.10"],
    ["reg_lambda", "4.0918", "1.20"], ["gamma", "0.5", "0"],
], columns=["Hiperparámetro", "Optimizado", "Base"])

# Approximate province centers for a national overview. The source data has no canton coordinates.
PROVINCE_CENTERS = {
    "ESMERALDAS": (-0.9, -79.6), "CARCHI": (0.8, -77.9), "IMBABURA": (0.4, -78.2),
    "SUCUMBIOS": (0.1, -76.7), "PICHINCHA": (-0.1, -78.5), "SANTO DOMINGO DE LOS TSACHILAS": (-0.3, -79.3),
    "MANABI": (-0.8, -80.2), "NAPO": (-0.8, -77.8), "COTOPAXI": (-0.9, -78.6),
    "ORELLANA": (-0.7, -76.7), "LOS RIOS": (-1.4, -79.5), "TUNGURAHUA": (-1.3, -78.6),
    "BOLIVAR": (-1.6, -79.0), "PASTAZA": (-1.5, -77.9), "GUAYAS": (-2.2, -79.9),
    "CHIMBORAZO": (-1.7, -78.7), "SANTA ELENA": (-2.2, -80.8), "CAÑAR": (-2.6, -78.9),
    "MORONA SANTIAGO": (-2.3, -78.1), "AZUAY": (-2.9, -79.0), "EL ORO": (-3.5, -79.9),
    "ZAMORA CHINCHIPE": (-4.1, -78.9), "LOJA": (-4.0, -79.2), "GALAPAGOS": (-0.7, -90.3),
}


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"No se encontró el dataset: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH, low_memory=False)
    needed = {"provincia_norm", "canton_norm", "Region", "Anio", "Mes", "Total_Incidentes", "Incidentes_Seguridad", "Delitos_Criticos", "Proporcion_Delitos", "Delitos_Lag_1", "Delitos_Lag_2", "Media_Movil_3M", "Tendencia_Inercial", "Es_Temporada_Alta", "Mes_Alto_Riesgo", "Disparate_Impact_Region"}
    missing = needed.difference(df.columns)
    if missing:
        raise ValueError("Faltan columnas requeridas en el dataset: " + ", ".join(sorted(missing)))
    return df


def get_clusters(df: pd.DataFrame) -> dict[str, int]:
    """Rebuild train-only canton clusters following the optimization notebook."""
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    train = df[df.get("Split_Particion_Temporal", "TRAIN") == "TRAIN"].copy()
    if train.empty:
        train = df.copy()
    group = train.groupby(["provincia_norm", "canton_norm", "Region"], dropna=False)
    profile = group.agg(
        Media_Delitos=("Delitos_Criticos", "mean"),
        Max_Delitos=("Delitos_Criticos", "max"),
        Tasa_Delitos=("Proporcion_Delitos", "mean"),
        Media_Total_Incidentes=("Total_Incidentes", "mean"),
        Tasa_Alto_Riesgo=("Mes_Alto_Riesgo", "mean"),
    ).reset_index()
    high_season = train[train["Es_Temporada_Alta"] == 1].groupby("canton_norm")["Delitos_Criticos"].mean()
    profile["Delitos_Temporada_Alta"] = profile["canton_norm"].map(high_season).fillna(0)
    cols = ["Media_Delitos", "Max_Delitos", "Tasa_Delitos", "Media_Total_Incidentes", "Tasa_Alto_Riesgo", "Delitos_Temporada_Alta"]
    scaled = StandardScaler().fit_transform(profile[cols].fillna(0))
    raw = KMeans(n_clusters=3, init="k-means++", n_init=15, random_state=42).fit_predict(scaled)
    means = profile.assign(_cluster=raw).groupby("_cluster")["Media_Delitos"].mean().sort_values()
    levels = {cluster: level for level, cluster in enumerate(means.index)}
    profile["Cluster_Riesgo"] = [levels[c] for c in raw]
    return profile.drop_duplicates("canton_norm").set_index("canton_norm")["Cluster_Riesgo"].astype(int).to_dict()


@st.cache_data(show_spinner=False)
def get_cluster_quality(df: pd.DataFrame) -> dict:
    """Recompute unsupervised diagnostics on train-only canton profiles."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import davies_bouldin_score, silhouette_score
    from sklearn.preprocessing import StandardScaler

    train = df[df["Split_Particion_Temporal"] == "TRAIN"].copy()
    profile = train.groupby(["provincia_norm", "canton_norm", "Region"], dropna=False).agg(
        Media_Delitos=("Delitos_Criticos", "mean"), Max_Delitos=("Delitos_Criticos", "max"),
        Tasa_Delitos=("Proporcion_Delitos", "mean"), Media_Total_Incidentes=("Total_Incidentes", "mean"),
        Tasa_Alto_Riesgo=("Mes_Alto_Riesgo", "mean"),
    ).reset_index()
    high = train[train["Es_Temporada_Alta"] == 1].groupby("canton_norm")["Delitos_Criticos"].mean()
    profile["Delitos_Temporada_Alta"] = profile["canton_norm"].map(high).fillna(0)
    columns = ["Media_Delitos", "Max_Delitos", "Tasa_Delitos", "Media_Total_Incidentes", "Tasa_Alto_Riesgo", "Delitos_Temporada_Alta"]
    scaled = StandardScaler().fit_transform(profile[columns].fillna(0))
    model = KMeans(n_clusters=3, init="k-means++", n_init=15, random_state=42).fit(scaled)
    return {
        "clusters": int(model.n_clusters), "silhouette": float(silhouette_score(scaled, model.labels_)),
        "davies_bouldin": float(davies_bouldin_score(scaled, model.labels_)),
        "inertia": float(model.inertia_), "cantons": int(len(profile)),
    }


def build_top10(df: pd.DataFrame) -> pd.DataFrame:
    recent_years = sorted(df["Anio"].dropna().unique())[-2:]
    recent = df[df["Anio"].isin(recent_years)]
    top = recent.groupby(["provincia_norm", "canton_norm"], as_index=False).agg(
        Incidentes_Criticos_Media=("Delitos_Criticos", "mean"),
        Meses_Alto_Riesgo=("Mes_Alto_Riesgo", "sum"),
        Incidentes_Total_Media=("Total_Incidentes", "mean"),
    ).sort_values(["Incidentes_Criticos_Media", "Meses_Alto_Riesgo"], ascending=False).head(10).reset_index(drop=True)
    top["Nivel"] = ["Alto"] * min(3, len(top)) + ["Medio"] * max(0, min(4, len(top) - 3)) + ["Bajo"] * max(0, len(top) - 7)
    top["Rango"] = range(1, len(top) + 1)
    return top


def predict_risk(input_row: dict, df: pd.DataFrame, clusters: dict[str, int]) -> tuple[int, float, str]:
    """Use a compatible serialized classifier or fit the documented XGBoost model."""
    row = dict(input_row)
    row["Cluster_Riesgo"] = clusters.get(row["canton_norm"], 0)
    frame = pd.DataFrame([{key: row[key] for key in FEATURES}], columns=FEATURES)
    errors = []
    for name in ("xgboost_monthly.joblib", "random_forest.joblib"):
        path = MODEL_PATH / name
        if not path.exists():
            continue
        try:
            import joblib
            model = joblib.load(path)
            expected = getattr(model, "n_features_in_", len(FEATURES))
            if expected != len(FEATURES):
                errors.append(f"{name}: el artefacto espera {expected} variables, la aplicación tiene {len(FEATURES)}")
                continue
            if hasattr(model, "feature_names_in_"):
                frame = frame.reindex(columns=list(model.feature_names_in_))
            probability = float(model.predict_proba(frame)[0][1])
            return int(probability >= 0.5), probability, name
        except Exception as exc:  # display actionable dependency or artifact errors in the UI
            errors.append(f"{name}: {exc}")
    try:
        model = _fit_project_xgboost(tuple(sorted(clusters.items())), DATA_PATH.stat().st_mtime_ns)
        probability = float(model.predict_proba(frame[FEATURES])[0][1])
        return int(probability >= 0.5), probability, "XGBoost optimizado (ajustado desde TRAIN)"
    except Exception as exc:
        detail = " | ".join(errors)
        if detail:
            detail += " | "
        raise RuntimeError("No se pudo generar una predicción. " + detail + f"Ajuste del XGBoost optimizado: {exc}") from exc


@st.cache_resource(show_spinner=False)
def _fit_project_xgboost(cluster_items: tuple[tuple[str, int], ...], data_mtime: int):
    """Fit the notebook's production configuration on the documented TRAIN rows."""
    from xgboost import XGBClassifier

    df = load_data().copy()
    cluster_map = dict(cluster_items)
    df["Cluster_Riesgo"] = df["canton_norm"].map(cluster_map).fillna(0).astype(int)
    train_mask = df["Split_Particion_Temporal"].eq("TRAIN")
    model = XGBClassifier(
        n_estimators=300, max_depth=6, learning_rate=0.0447, subsample=0.70,
        colsample_bytree=0.90, min_child_weight=3, scale_pos_weight=2.2,
        reg_alpha=0.3298, reg_lambda=4.0918, gamma=0.5,
        eval_metric="logloss", random_state=42, n_jobs=-1,
    )
    model.fit(
        df.loc[train_mask, FEATURES].astype(float),
        df.loc[train_mask, "Mes_Alto_Riesgo"].astype(int),
        sample_weight=df.loc[train_mask, "Peso_Muestra_Fairness"].astype(float),
    )
    return model


def fairness_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Region", dropna=False).agg(
        Disparate_Impact_Medio=("Disparate_Impact_Region", "mean"),
        Peso_Fairness_Medio=("Peso_Muestra_Fairness", "mean") if "Peso_Muestra_Fairness" in df else ("Disparate_Impact_Region", "size"),
        Cantones=("canton_norm", "nunique"),
    ).reset_index().sort_values("Region")


def render_header(lang: str = "Español") -> None:
    title = "Ecuador · Riesgo y alertas" if lang == "Español" else "Ecuador · Risk and alerts"
    st.markdown(f'<div class="hero"><div class="eyebrow">INTELIGENCIA TERRITORIAL · ECUADOR</div><h1>{title}</h1><p>Modelos de riesgo mensual · K-Means · Random Forest · XGBoost</p></div>', unsafe_allow_html=True)


def model_metrics_display() -> pd.DataFrame:
    formatted = METRICS.copy()
    for col in formatted.columns[1:]:
        formatted[col] = formatted[col].map(lambda x: f"{x:.3f}")
    return formatted

