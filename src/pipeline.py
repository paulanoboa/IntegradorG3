"""Pipeline reproducible para análisis de incidentes de Ecuador.

Ejecutar desde cualquier directorio: python src/pipeline.py --stage all
Los CSV originales no se modifican. Las salidas son agregadas/anonimizadas a nivel
territorial y de mes; no hay coordenadas puntuales de los incidentes en la fuente.
"""
from __future__ import annotations

import argparse
import itertools
import json
import logging
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, auc, confusion_matrix, f1_score, precision_score,
    recall_score, roc_auc_score, roc_curve, silhouette_score,
)
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
METRICS = ROOT / "results" / "metrics"
REPORTS = ROOT / "results" / "reports"
FIGURES = ROOT / "results" / "figures"
MODELS = ROOT / "models"
CHUNK_SIZE = 200_000
SEED = 42

PROVINCE_CENTERS = {
    "AZUAY": (-2.90, -79.00), "BOLIVAR": (-1.59, -79.00),
    "CAÑAR": (-2.56, -78.94), "CARCHI": (0.81, -77.72),
    "CHIMBORAZO": (-1.67, -78.65), "COTOPAXI": (-0.93, -78.61),
    "EL ORO": (-3.26, -79.96), "ESMERALDAS": (0.96, -79.65),
    "GALAPAGOS": (-0.90, -89.60), "GUAYAS": (-2.20, -79.89),
    "IMBABURA": (0.35, -78.13), "LOJA": (-3.99, -79.20),
    "LOS RIOS": (-1.02, -79.46), "MANABI": (-0.95, -80.73),
    "MORONA SANTIAGO": (-2.31, -78.12), "NAPO": (-0.99, -77.81),
    "ORELLANA": (-0.47, -76.99), "PASTAZA": (-1.49, -78.00),
    "PICHINCHA": (-0.18, -78.47), "SANTA ELENA": (-2.23, -80.86),
    "SANTO DOMINGO DE LOS TSACHILAS": (-0.25, -79.17),
    "SANTO DOMINGO DE LOS TSACHILAS ": (-0.25, -79.17),
    "SUCUMBIOS": (0.09, -76.88), "TUNGURAHUA": (-1.24, -78.62),
    "ZAMORA CHINCHIPE": (-4.07, -78.96),
}
MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
CANONICAL = {
    "fecha": ("fecha", "date"),
    "provincia": ("provincia", "province"),
    "canton": ("canton", "cantón", "county"),
    "cod_parroquia": ("codparroquia", "codigo parroquia", "parishcode"),
    "parroquia": ("parroquia", "parish"),
    "servicio": ("servicio", "service"),
    "subtipo": ("subtipo", "tipo", "subcategory"),
}


def setup_logging() -> logging.Logger:
    (ROOT / "results").mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ecuador_pipeline")
    logger.setLevel(logging.INFO)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(ROOT / "results" / "processing_log.txt", encoding="utf-8")
    file_handler.setFormatter(formatter)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console)
    return logger


def normalized_header(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value).strip().lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]", "", text)


def locate_raw() -> Path:
    if RAW.is_dir():
        return RAW
    raise FileNotFoundError(f"No se encontró la carpeta de entrada: {RAW}")


def read_chunks(path: Path):
    # Estos datasets son delimitados principalmente por ';'; probar coma como respaldo.
    encodings = ("utf-8-sig", "cp1252", "latin-1")
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            reader = pd.read_csv(path, sep=";", encoding=encoding, dtype=str,
                                 chunksize=CHUNK_SIZE, on_bad_lines="skip",
                                 low_memory=False)
            first = next(reader, None)
            if first is None:
                return
            # Si el archivo no era ';', volver a abrir usando autodetección en una lectura acotada.
            if len(first.columns) <= 1:
                reader = pd.read_csv(path, sep=None, engine="python", encoding=encoding,
                                     dtype=str, chunksize=CHUNK_SIZE, on_bad_lines="skip")
                yield from reader
            else:
                yield from itertools.chain((first,), reader)
            return
        except (UnicodeDecodeError, pd.errors.ParserError, OSError) as exc:
            last_error = exc
    raise ValueError(f"No se pudo leer {path}: {last_error}")


def canonicalize(chunk: pd.DataFrame, source: Path) -> pd.DataFrame:
    renames: dict[Any, str] = {}
    aliases = {normalized_header(alias): field for field, names in CANONICAL.items() for alias in names}
    for column in chunk.columns:
        key = normalized_header(column)
        if key in aliases:
            renames[column] = aliases[key]
    chunk = chunk.rename(columns=renames)
    chunk = chunk.loc[:, [c for c in chunk.columns if not normalized_header(c).startswith("unnamed")]]
    missing = [key for key in ("fecha", "provincia", "canton", "parroquia", "servicio", "subtipo")
               if key not in chunk.columns]
    if missing:
        raise ValueError(f"{source.name}: no se encontraron columnas requeridas {missing}; disponibles={list(chunk.columns)}")
    if "cod_parroquia" not in chunk:
        chunk["cod_parroquia"] = ""
    chunk = chunk[list(CANONICAL)].copy()
    chunk["fecha"] = pd.to_datetime(chunk["fecha"], dayfirst=True, errors="coerce", format="mixed")
    chunk = chunk.loc[chunk["fecha"].notna()].copy()
    for col in ("provincia", "canton", "parroquia", "servicio", "subtipo"):
        chunk[col] = (chunk[col].fillna("").astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
                      .replace({"": "SIN DATO", "nan": "SIN DATO", "None": "SIN DATO"}).str.upper())
    chunk["cod_parroquia"] = (chunk["cod_parroquia"].fillna("").astype(str)
                                .str.replace(r"\.0$", "", regex=True).str.strip())
    chunk["cod_parroquia"] = chunk["cod_parroquia"].replace({"": "SIN DATO", "nan": "SIN DATO"})
    chunk["anio"] = chunk["fecha"].dt.year.astype("int16")
    chunk["mes"] = chunk["fecha"].dt.month.astype("int8")
    chunk["fuente"] = source.name
    return chunk


def safe_slug(value: str) -> str:
    slug = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", slug).strip("_")[:120] or "archivo"


def save_source_report(source: Path, n_read: int, n_clean: int, invalid_dates: int,
                       aggregates: pd.DataFrame, top_provinces: dict[str, int],
                       top_types: dict[str, int]) -> None:
    slug = safe_slug(source.stem)
    REPORTS.joinpath("source_files").mkdir(parents=True, exist_ok=True)
    FIGURES.joinpath("by_file").mkdir(parents=True, exist_ok=True)
    report = REPORTS / "source_files" / f"{slug}.md"
    dates = aggregates[["anio", "mes"]].drop_duplicates().sort_values(["anio", "mes"])
    period = ", ".join(f"{int(r.anio)}-{int(r.mes):02d}" for r in dates.itertuples()) or "sin fechas válidas"
    report.write_text(
        f"# Informe de {source.name}\n\n"
        f"- Filas leídas: {n_read:,}\n- Filas válidas: {n_clean:,}\n"
        f"- Fechas inválidas/eliminadas: {invalid_dates:,}\n"
        f"- Periodo detectado: {period}\n- Provincias distintas: {aggregates['provincia'].nunique() if not aggregates.empty else 0}\n\n"
        "## Provincias con más registros\n\n" +
        (pd.Series(top_provinces).sort_values(ascending=False).head(10).to_frame("registros").to_markdown() if top_provinces else "Sin datos") +
        "\n\n## Servicios/subtipos más frecuentes\n\n" +
        (pd.Series(top_types).sort_values(ascending=False).head(10).to_frame("registros").to_markdown() if top_types else "Sin datos") +
        "\n\n> El mapa y las categorías de riesgo describen volúmenes observados; no representan una tasa poblacional ni garantizan seguridad.\n",
        encoding="utf-8")
    if top_provinces:
        series = pd.Series(top_provinces).sort_values().tail(12)
        fig, ax = plt.subplots(figsize=(10, max(4, len(series) * .32)))
        series.plot.barh(ax=ax, color="#d95f59")
        ax.set(title=f"Registros por provincia · {source.name}", xlabel="Registros", ylabel="")
        fig.tight_layout()
        fig.savefig(FIGURES / "by_file" / f"{slug}_provincias.png", dpi=140)
        plt.close(fig)


def preprocess(logger: logging.Logger) -> pd.DataFrame:
    raw_root = locate_raw()
    files = sorted(p for p in raw_root.rglob("*.csv") if p.is_file())
    if not files:
        raise FileNotFoundError(f"No se hallaron CSV en {raw_root}")
    PROCESSED.mkdir(parents=True, exist_ok=True)
    METRICS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "source_files").mkdir(parents=True, exist_ok=True)
    (FIGURES / "by_file").mkdir(parents=True, exist_ok=True)
    file_rollups: list[pd.DataFrame] = []
    manifest: list[dict[str, Any]] = []
    for index, source in enumerate(files, 1):
        slug = safe_slug(source.stem)
        cleaned_path = PROCESSED / f"{slug}_limpio.csv.gz"
        aggregate_path = PROCESSED / f"{slug}_agregado.csv"
        if cleaned_path.exists():
            cleaned_path.unlink()
        n_read = n_clean = 0
        group_parts: list[pd.DataFrame] = []
        province_totals: defaultdict[str, int] = defaultdict(int)
        subtype_totals: defaultdict[str, int] = defaultdict(int)
        with __import__("gzip").open(cleaned_path, "wt", encoding="utf-8", newline="") as handle:
            first_write = True
            for chunk in read_chunks(source):
                n_read += len(chunk)
                clean = canonicalize(chunk, source)
                n_clean += len(clean)
                if clean.empty:
                    continue
                clean.to_csv(handle, index=False, header=first_write, date_format="%Y-%m-%d")
                first_write = False
                for key, val in clean["provincia"].value_counts().items():
                    province_totals[str(key)] += int(val)
                for key, val in clean["subtipo"].value_counts().head(30).items():
                    subtype_totals[str(key)] += int(val)
                clean["es_seguridad"] = clean["servicio"].str.contains("SEGURIDAD CIUDADANA", regex=False).astype("int32")
                grouped = (clean.groupby(["provincia", "canton", "cod_parroquia", "parroquia", "anio", "mes"],
                                         as_index=False, observed=True)
                           .agg(registros=("fecha", "size"), seguridad=("es_seguridad", "sum")))
                group_parts.append(grouped)
        if group_parts:
            rollup = (pd.concat(group_parts, ignore_index=True)
                      .groupby(["provincia", "canton", "cod_parroquia", "parroquia", "anio", "mes"],
                               as_index=False, observed=True)
                      .agg(registros=("registros", "sum"), seguridad=("seguridad", "sum")))
        else:
            rollup = pd.DataFrame(columns=["provincia", "canton", "cod_parroquia", "parroquia", "anio", "mes", "registros", "seguridad"])
        rollup["fuente"] = source.name
        rollup.to_csv(aggregate_path, index=False, encoding="utf-8")
        file_rollups.append(rollup)
        manifest.append({"archivo": source.relative_to(raw_root).as_posix(), "filas_leidas": n_read,
                         "filas_validas": n_clean, "filas_invalidas": n_read - n_clean,
                         "parroquias_mensuales": len(rollup), "salida_limpia": cleaned_path.name})
        save_source_report(source, n_read, n_clean, n_read - n_clean, rollup, dict(province_totals), dict(subtype_totals))
        logger.info("[%d/%d] %s: %s de %s filas válidas", index, len(files), source.name, f"{n_clean:,}", f"{n_read:,}")
    if not file_rollups:
        raise RuntimeError("No hubo archivos procesables")
    all_rollups = pd.concat(file_rollups, ignore_index=True)
    monthly = (all_rollups.groupby(["provincia", "canton", "cod_parroquia", "parroquia", "anio", "mes"],
                                   as_index=False, observed=True)
               .agg(registros=("registros", "sum"), seguridad=("seguridad", "sum")))
    monthly["fecha_mes"] = pd.to_datetime(monthly["anio"].astype(str) + "-" + monthly["mes"].astype(str).str.zfill(2) + "-01")
    monthly.to_csv(PROCESSED / "monthly_location_counts.csv", index=False, encoding="utf-8")
    pd.DataFrame(manifest).to_csv(METRICS / "per_file_summary.csv", index=False, encoding="utf-8")
    (PROCESSED / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Preprocesamiento terminado: %d CSV, %s filas limpias", len(files), f"{sum(r['filas_validas'] for r in manifest):,}")
    return monthly


def load_monthly() -> pd.DataFrame:
    path = PROCESSED / "monthly_location_counts.csv"
    if not path.exists():
        raise FileNotFoundError("Ejecute primero --stage preprocess para crear los agregados.")
    return pd.read_csv(path, parse_dates=["fecha_mes"], dtype={"cod_parroquia": str})


def make_panel(monthly: pd.DataFrame) -> pd.DataFrame:
    # Predicción territorial por provincia/mes: la fuente no aporta latitud/longitud.
    data = monthly.groupby(["provincia", "anio", "mes", "fecha_mes"], as_index=False)["registros"].sum()
    months = pd.date_range(data.fecha_mes.min(), data.fecha_mes.max(), freq="MS")
    provinces = sorted(data.provincia.dropna().unique())
    complete = pd.MultiIndex.from_product([provinces, months], names=["provincia", "fecha_mes"]).to_frame(index=False)
    complete["anio"] = complete.fecha_mes.dt.year
    complete["mes"] = complete.fecha_mes.dt.month
    data = complete.merge(data[["provincia", "fecha_mes", "registros"]], on=["provincia", "fecha_mes"], how="left")
    data["registros"] = data.registros.fillna(0).astype(float)
    data["lag_1"] = data.groupby("provincia").registros.shift(1)
    data["lag_2"] = data.groupby("provincia").registros.shift(2)
    data["lag_3"] = data.groupby("provincia").registros.shift(3)
    data["media_3"] = data.groupby("provincia").registros.transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    data["mes_sin"] = np.sin(2 * np.pi * data.mes / 12)
    data["mes_cos"] = np.cos(2 * np.pi * data.mes / 12)
    data["provincia"] = data.provincia.astype(str)
    return data.dropna(subset=["lag_1", "lag_2", "lag_3"]).reset_index(drop=True)


def add_province_features(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    categorical = pd.get_dummies(data["provincia"], prefix="prov", dtype=int)
    features = pd.concat([data[["anio", "mes_sin", "mes_cos", "lag_1", "lag_2", "lag_3", "media_3"]].reset_index(drop=True),
                          categorical.reset_index(drop=True)], axis=1)
    return features, list(features.columns)


def binary_metrics(y_true: np.ndarray, y_pred: np.ndarray, probabilities: np.ndarray, model: str) -> dict[str, Any]:
    auc_value = float("nan")
    if len(np.unique(y_true)) > 1:
        auc_value = float(roc_auc_score(y_true, probabilities))
    return {"modelo": model, "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, zero_division=0)), "auc_roc": auc_value,
            "silhouette_score": float("nan"), "n_test": int(len(y_true))}


def cluster_provinces(monthly: pd.DataFrame, logger: logging.Logger) -> pd.DataFrame:
    totals = monthly.groupby("provincia", as_index=False)["registros"].sum()
    totals["latitud"] = totals.provincia.map(lambda p: PROVINCE_CENTERS.get(p, (np.nan, np.nan))[0])
    totals["longitud"] = totals.provincia.map(lambda p: PROVINCE_CENTERS.get(p, (np.nan, np.nan))[1])
    totals = totals.dropna(subset=["latitud", "longitud"]).copy()
    if len(totals) < 3:
        raise ValueError("Se requieren al menos 3 provincias georreferenciadas para K-Means.")
    totals["log_registros"] = np.log1p(totals.registros)
    # El componente de frecuencia detecta niveles relativos de riesgo y las coordenadas conservan geografía.
    scaled = StandardScaler().fit_transform(totals[["latitud", "longitud", "log_registros"]])
    estimator = KMeans(n_clusters=3, random_state=SEED, n_init=20)
    totals["cluster_id"] = estimator.fit_predict(scaled)
    means = totals.groupby("cluster_id").registros.mean().sort_values()
    label_map = {int(cluster): label for cluster, label in zip(means.index, ["BAJO", "MEDIO", "ALTO"])}
    totals["nivel_riesgo"] = totals.cluster_id.map(label_map)
    score = float(silhouette_score(scaled, totals.cluster_id)) if totals.cluster_id.nunique() > 1 and len(totals) > 3 else float("nan")
    totals["silhouette_score"] = score
    totals["centro_latitud"] = totals.latitud
    totals["centro_longitud"] = totals.longitud
    totals.to_csv(PROCESSED / "province_risk.csv", index=False, encoding="utf-8")
    logger.info("K-Means: %d provincias; Silhouette=%.4f", len(totals), score)
    return totals


def write_model(model: Any, filename: str) -> None:
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError("Instale joblib para guardar los modelos.") from exc
    MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODELS / filename)


def train_rf(monthly: pd.DataFrame, logger: logging.Logger) -> tuple[dict[str, Any] | None, pd.DataFrame | None]:
    panel = make_panel(monthly)
    if len(panel) < 40:
        logger.warning("Datos insuficientes para entrenar Random Forest (%d filas).", len(panel))
        return None, None
    split_date = panel.fecha_mes.quantile(.8)
    train = panel[panel.fecha_mes < split_date].copy()
    test = panel[panel.fecha_mes >= split_date].copy()
    thresholds = train.groupby("provincia").registros.quantile(.75)
    train["umbral_provincia"] = train.provincia.map(thresholds)
    test["umbral_provincia"] = test.provincia.map(thresholds)
    train["riesgo_alto"] = (train.registros > train.umbral_provincia).astype(int)
    test["riesgo_alto"] = (test.registros > test.umbral_provincia).astype(int)
    if train.riesgo_alto.nunique() < 2 or test.riesgo_alto.nunique() < 2:
        logger.warning("RF omitido: la variable objetivo no tiene ambas clases en train/test.")
        return None, None
    x_train, feature_cols = add_province_features(train)
    x_test, _ = add_province_features(test)
    x_test = x_test.reindex(columns=feature_cols, fill_value=0)
    model = RandomForestClassifier(n_estimators=350, min_samples_leaf=2, class_weight="balanced_subsample",
                                   max_features="sqrt", n_jobs=-1, random_state=SEED)
    model.fit(x_train, train.riesgo_alto)
    prob = model.predict_proba(x_test)[:, 1]
    pred = (prob >= .5).astype(int)
    metrics = binary_metrics(test.riesgo_alto.to_numpy(), pred, prob, "Random Forest")
    metrics["umbral_registros_alto_promedio"] = float(thresholds.mean())
    predictions = test[["provincia", "fecha_mes", "registros", "riesgo_alto"]].copy()
    predictions["prediccion"] = pred
    predictions["probabilidad_alto"] = prob
    predictions.to_csv(PROCESSED / "predictions_random_forest.csv", index=False)
    write_model({"estimator": model, "features": feature_cols,
                 "threshold_by_province": thresholds.to_dict()}, "random_forest.joblib")
    logger.info("Random Forest: F1=%.3f, AUC=%.3f", metrics["f1"], metrics["auc_roc"])
    return metrics, predictions


def train_xgb(monthly: pd.DataFrame, logger: logging.Logger) -> tuple[dict[str, Any] | None, pd.DataFrame | None, pd.DataFrame | None]:
    try:
        from xgboost import XGBClassifier
    except ImportError as exc:
        raise RuntimeError("XGBoost no está instalado. Ejecute: pip install -r requirements.txt") from exc
    panel = make_panel(monthly)
    if len(panel) < 40:
        logger.warning("Datos insuficientes para entrenar XGBoost (%d filas).", len(panel))
        return None, None, None
    split_date = panel.fecha_mes.quantile(.8)
    train = panel[panel.fecha_mes < split_date].copy()
    test = panel[panel.fecha_mes >= split_date].copy()
    thresholds = train.groupby("provincia").registros.quantile(.75)
    train["umbral_provincia"] = train.provincia.map(thresholds)
    test["umbral_provincia"] = test.provincia.map(thresholds)
    train["riesgo_alto"] = (train.registros > train.umbral_provincia).astype(int)
    test["riesgo_alto"] = (test.registros > test.umbral_provincia).astype(int)
    if train.riesgo_alto.nunique() < 2 or test.riesgo_alto.nunique() < 2:
        logger.warning("XGBoost omitido: no hay ambas clases en train/test.")
        return None, None, None
    validation_date = train.fecha_mes.quantile(.8)
    fit_frame = train[train.fecha_mes < validation_date].copy()
    validation = train[train.fecha_mes >= validation_date].copy()
    if fit_frame.riesgo_alto.nunique() < 2 or validation.riesgo_alto.nunique() < 2:
        fit_frame, validation = train, train
    x_fit, feature_cols = add_province_features(fit_frame)
    x_validation, _ = add_province_features(validation)
    x_validation = x_validation.reindex(columns=feature_cols, fill_value=0)
    positives = max(1, int(train.riesgo_alto.sum()))
    negatives = max(1, len(train) - positives)
    parameters = dict(n_estimators=280, max_depth=3, learning_rate=.04, subsample=.85,
                      colsample_bytree=.85, reg_lambda=2, objective="binary:logistic",
                      eval_metric="logloss", scale_pos_weight=negatives / positives,
                      random_state=SEED, n_jobs=-1)
    calibration_model = XGBClassifier(**parameters)
    calibration_model.fit(x_fit, fit_frame.riesgo_alto)
    validation_prob = calibration_model.predict_proba(x_validation)[:, 1]
    # El corte se ajusta solo en meses de calibración anteriores al periodo final de prueba.
    candidates = np.linspace(.2, .8, 31)
    tuned_threshold = max(candidates, key=lambda cut: f1_score(validation.riesgo_alto, validation_prob >= cut, zero_division=0))
    x_train, _ = add_province_features(train)
    x_train = x_train.reindex(columns=feature_cols, fill_value=0)
    x_test, _ = add_province_features(test)
    x_test = x_test.reindex(columns=feature_cols, fill_value=0)
    model = XGBClassifier(**parameters)
    model.fit(x_train, train.riesgo_alto)
    prob = model.predict_proba(x_test)[:, 1]
    pred = (prob >= tuned_threshold).astype(int)
    metrics = binary_metrics(test.riesgo_alto.to_numpy(), pred, prob, "XGBoost")
    metrics["umbral_registros_alto_promedio"] = float(thresholds.mean())
    metrics["umbral_probabilidad"] = float(tuned_threshold)
    predictions = test[["provincia", "fecha_mes", "registros", "riesgo_alto"]].copy()
    predictions["prediccion"] = pred
    predictions["probabilidad_alto"] = prob
    predictions.to_csv(PROCESSED / "predictions_xgboost.csv", index=False)
    forecast = make_forecast(panel, model, feature_cols, tuned_threshold)
    forecast.to_csv(PROCESSED / "forecast_months.csv", index=False)
    write_model({"estimator": model, "features": feature_cols, "threshold": float(tuned_threshold),
                 "count_threshold_by_province": thresholds.to_dict()}, "xgboost_monthly.joblib")
    logger.info("XGBoost: F1=%.3f, AUC=%.3f; corte=%.2f", metrics["f1"], metrics["auc_roc"], tuned_threshold)
    return metrics, predictions, forecast


def make_forecast(panel: pd.DataFrame, model: Any, feature_cols: list[str], threshold: float) -> pd.DataFrame:
    future_months = pd.date_range(panel.fecha_mes.max() + pd.offsets.MonthBegin(1), periods=3, freq="MS")
    rows = []
    for province in sorted(panel.provincia.unique()):
        history = panel.loc[panel.provincia.eq(province)].sort_values("fecha_mes").registros.tail(3).tolist()
        if not history:
            continue
        history = ([0.0] * (3 - len(history))) + [float(v) for v in history]
        for date in future_months:
            rows.append({"provincia": province, "fecha_mes": date, "anio": date.year, "mes": date.month,
                         "lag_1": history[-1], "lag_2": history[-2], "lag_3": history[-3],
                         "media_3": float(np.mean(history[-3:])), "mes_sin": np.sin(2 * np.pi * date.month / 12),
                         "mes_cos": np.cos(2 * np.pi * date.month / 12)})
            # A forecast is categorical risk, not a point estimate of a future event count.
            # Preserve observed history for each of the three horizons to avoid invented counts.
    future = pd.DataFrame(rows)
    X, _ = add_province_features(future)
    X = X.reindex(columns=feature_cols, fill_value=0)
    future["probabilidad_riesgo_alto"] = model.predict_proba(X)[:, 1]
    future["prediccion_riesgo"] = np.where(future.probabilidad_riesgo_alto >= threshold, "ALTO", "BAJO")
    future["nota"] = "Pronóstico categórico por provincia; no es una tasa ni un conteo de incidentes."
    return future[["provincia", "fecha_mes", "prediccion_riesgo", "probabilidad_riesgo_alto", "nota"]]


def plot_evaluation(predictions: pd.DataFrame, model: str) -> None:
    if predictions is None or predictions.empty:
        return
    stem = safe_slug(model.lower().replace(" ", "_"))
    y = predictions.riesgo_alto.astype(int).to_numpy()
    p = predictions.prediccion.astype(int).to_numpy()
    scores = predictions.probabilidad_alto.astype(float).to_numpy()
    cm = confusion_matrix(y, p, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    image = ax.imshow(cm, cmap="Reds")
    for (i, j), value in np.ndenumerate(cm):
        ax.text(j, i, str(value), ha="center", va="center", fontsize=13)
    ax.set(xticks=[0, 1], yticks=[0, 1], xticklabels=["Bajo", "Alto"], yticklabels=["Bajo", "Alto"],
           xlabel="Predicción", ylabel="Real", title=f"Matriz de confusión · {model}")
    fig.colorbar(image, ax=ax, shrink=.8)
    fig.tight_layout(); fig.savefig(FIGURES / f"confusion_{stem}.png", dpi=150); plt.close(fig)
    if len(np.unique(y)) > 1:
        fpr, tpr, _ = roc_curve(y, scores)
        fig, ax = plt.subplots(figsize=(6, 4.5))
        ax.plot(fpr, tpr, lw=2, label=f"AUC = {roc_auc_score(y, scores):.3f}")
        ax.plot([0, 1], [0, 1], "--", color="gray")
        ax.set(xlabel="Tasa de falsos positivos", ylabel="Tasa de verdaderos positivos", title=f"Curva ROC · {model}")
        ax.legend(loc="lower right"); fig.tight_layout(); fig.savefig(FIGURES / f"roc_{stem}.png", dpi=150); plt.close(fig)


def save_evaluation_artifacts(model_metrics: list[dict[str, Any]], cluster_data: pd.DataFrame,
                              predictions: dict[str, pd.DataFrame], logger: logging.Logger) -> None:
    METRICS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    rows = list(model_metrics)
    cluster_score = float(cluster_data.silhouette_score.iloc[0]) if not cluster_data.empty else float("nan")
    rows.append({"modelo": "K-Means (provincias)", "accuracy": np.nan, "precision": np.nan,
                 "recall": np.nan, "f1": np.nan, "auc_roc": np.nan,
                 "silhouette_score": cluster_score, "n_test": len(cluster_data)})
    metrics = pd.DataFrame(rows)
    metrics.to_csv(METRICS / "global_metrics.csv", index=False, encoding="utf-8")
    metrics.to_csv(METRICS / "model_metrics.csv", index=False, encoding="utf-8")
    for name, frame in predictions.items():
        plot_evaluation(frame, name)
    # Model metric plots requested: accuracy, precision, recall and F1.
    classifier = metrics[metrics.modelo.isin(["Random Forest", "XGBoost"])].set_index("modelo")
    for metric in ("accuracy", "precision", "recall", "f1"):
        if not classifier.empty:
            fig, ax = plt.subplots(figsize=(6, 4))
            classifier[metric].plot.bar(ax=ax, color=["#237a78", "#e9984a"][:len(classifier)], ylim=(0, 1))
            ax.set(title=f"{metric.replace('_', ' ').title()} por modelo", ylabel=metric.title(), xlabel="")
            ax.tick_params(axis="x", rotation=0); fig.tight_layout()
            fig.savefig(FIGURES / f"{metric}_comparison.png", dpi=150); plt.close(fig)
    if cluster_data.cluster_id.nunique() > 1:
        fig, ax = plt.subplots(figsize=(8, 6))
        colors = {"BAJO": "#38a169", "MEDIO": "#e6ad35", "ALTO": "#dc4545"}
        for level, subset in cluster_data.groupby("nivel_riesgo"):
            ax.scatter(subset.longitud, subset.latitud, c=colors[level], s=40 + 120 * np.sqrt(subset.registros / max(1, cluster_data.registros.max())),
                       label=level.title(), alpha=.82, edgecolor="white", linewidth=.5)
            for row in subset.itertuples():
                ax.annotate(row.provincia.title(), (row.longitud, row.latitud), xytext=(3, 3), textcoords="offset points", fontsize=7)
        ax.set(title=f"Riesgo relativo por provincia · Silhouette {cluster_score:.3f}", xlabel="Longitud", ylabel="Latitud")
        ax.legend(title="Nivel relativo"); fig.tight_layout(); fig.savefig(FIGURES / "silhouette_risk_clusters.png", dpi=160); plt.close(fig)
    summary = ("# Resumen global de métricas\n\n" + metrics.to_markdown(index=False, floatfmt=".4f") +
               "\n\nEl mapa usa centroides provinciales aproximados y los grupos reflejan volumen observado, no riesgo individual ni tasa ajustada por población. "
               "La evaluación supervisada es temporal (entrenamiento en meses anteriores y prueba en el tramo final).\n")
    (REPORTS / "global_summary.md").write_text(summary, encoding="utf-8")
    make_map_data(cluster_data)
    logger.info("Métricas, reportes, figuras y datos del mapa escritos en results/.")


def make_map_data(cluster_data: pd.DataFrame) -> None:
    columns = ["provincia", "latitud", "longitud", "registros", "nivel_riesgo", "cluster_id"]
    cluster_data[columns].to_json(FIGURES / "risk_map.json", orient="records", force_ascii=False)


def run_stage(stage: str) -> None:
    logger = setup_logging()
    if stage in ("preprocess", "all"):
        monthly = preprocess(logger)
    else:
        monthly = load_monthly()
    cluster_path = PROCESSED / "province_risk.csv"
    if stage in ("model", "all") or not cluster_path.exists():
        cluster = cluster_provinces(monthly, logger)
    else:
        cluster = pd.read_csv(cluster_path)
    rf_path = PROCESSED / "predictions_random_forest.csv"
    rf_metric_path = METRICS / "random_forest_metrics.json"
    rf_metrics = None
    rf_predictions = pd.read_csv(rf_path, parse_dates=["fecha_mes"]) if rf_path.exists() else None
    if stage in ("model", "all") or rf_predictions is None:
        rf_metrics, rf_predictions = train_rf(monthly, logger)
        if rf_metrics:
            METRICS.mkdir(parents=True, exist_ok=True)
            (METRICS / "random_forest_metrics.json").write_text(json.dumps(rf_metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    elif rf_metric_path.exists():
        rf_metrics = json.loads(rf_metric_path.read_text(encoding="utf-8"))
    xgb_metrics = None
    xgb_path = PROCESSED / "predictions_xgboost.csv"
    xgb_metric_path = METRICS / "xgboost_metrics.json"
    xgb_predictions = pd.read_csv(xgb_path, parse_dates=["fecha_mes"]) if xgb_path.exists() else None
    if stage in ("optimize", "all"):
        xgb_metrics, xgb_predictions, forecast = train_xgb(monthly, logger)
        if xgb_metrics:
            METRICS.mkdir(parents=True, exist_ok=True)
            (METRICS / "xgboost_metrics.json").write_text(json.dumps(xgb_metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    elif xgb_metric_path.exists():
        xgb_metrics = json.loads(xgb_metric_path.read_text(encoding="utf-8"))
    elif stage in ("model", "evaluate"):
        logger.info("No existe salida XGBoost; ejecute --stage optimize antes de evaluar.")
    if stage in ("evaluate", "all"):
        model_metrics = []
        for item in (rf_metrics, xgb_metrics):
            if item:
                model_metrics.append(item)
        predictions = {}
        if rf_predictions is not None:
            predictions["Random Forest"] = rf_predictions
        if xgb_predictions is not None:
            predictions["XGBoost"] = xgb_predictions
        save_evaluation_artifacts(model_metrics, cluster, predictions, logger)
    elif stage in ("model", "optimize"):
        # Keep risk map up to date even when notebooks are executed stepwise.
        make_map_data(cluster)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline de análisis y predicción de incidentes de Ecuador")
    parser.add_argument("--stage", choices=["preprocess", "model", "optimize", "evaluate", "all"], default="all",
                        help="Etapa a ejecutar (all ejecuta el flujo completo).")
    args = parser.parse_args()
    run_stage(args.stage)


if __name__ == "__main__":
    main()
