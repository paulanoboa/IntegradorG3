"""Aplicación web local para consultar resultados del pipeline."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from flask import Flask, abort, jsonify, render_template, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
METRICS = RESULTS / "metrics"
REPORTS = RESULTS / "reports"
FIGURES = RESULTS / "figures"
app = Flask(__name__, template_folder="templates", static_folder="static")


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return pd.read_csv(path).replace({float("nan"): None}).to_dict(orient="records")


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/graficos")
def charts():
    images = sorted(path.name for path in FIGURES.glob("*.png")) if FIGURES.exists() else []
    per_file = sorted(path.name for path in (FIGURES / "by_file").glob("*.png")) if (FIGURES / "by_file").exists() else []
    return render_template("charts.html", images=images, per_file=per_file)


@app.get("/mapa")
def map_view():
    return render_template("map.html")


@app.get("/api/resultados")
def api_results():
    metrics = load_csv(METRICS / "global_metrics.csv")
    files = load_csv(METRICS / "per_file_summary.csv")
    locations = load_csv(ROOT / "data" / "processed" / "province_risk.csv")
    forecasts = load_csv(ROOT / "data" / "processed" / "forecast_months.csv")
    report_dir = REPORTS / "source_files"
    reports = ([{"archivo": path.name, "url": f"/reports/{path.name}"}
                for path in sorted(report_dir.glob("*.md"))] if report_dir.exists() else [])
    return jsonify({"metricas": metrics, "archivos": files, "provincias": locations,
                    "pronosticos": forecasts, "reportes": reports})


@app.get("/api/mapa")
def api_map():
    path = FIGURES / "risk_map.json"
    if not path.exists():
        return jsonify([])
    return app.response_class(path.read_text(encoding="utf-8"), mimetype="application/json")


@app.get("/figures/<path:filename>")
def figure(filename: str):
    base = FIGURES.resolve()
    candidate = (base / filename).resolve()
    if base not in candidate.parents or not candidate.is_file():
        abort(404)
    return send_from_directory(candidate.parent, candidate.name)


@app.get("/reports/<path:filename>")
def report(filename: str):
    base = (REPORTS / "source_files").resolve()
    candidate = (base / filename).resolve()
    if base not in candidate.parents or candidate.suffix != ".md" or not candidate.is_file():
        abort(404)
    return send_from_directory(candidate.parent, candidate.name, mimetype="text/markdown")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
