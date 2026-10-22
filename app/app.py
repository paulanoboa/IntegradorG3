from __future__ import annotations

import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dashboard import (  # noqa: E402
    FEATURES, HYPERPARAMS, METRICS, RESULTS_PATH, build_top10, fairness_summary,
    get_cluster_quality, get_clusters, load_data, model_metrics_display, predict_risk, render_header,
)

st.set_page_config(page_title="Riesgo Ecuador | Inteligencia territorial", page_icon="🇪🇨", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--forest:#123c32;--leaf:#2d7656;--mint:#e6f1eb;--ink:#17352e;--muted:#668078;--paper:#f5f8f6}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;color:var(--ink)}
.stApp{background:var(--paper)} .block-container{max-width:1320px;padding-top:1.4rem}
.hero{background:linear-gradient(110deg,#102f29 0%,#1f5c45 65%,#34795a 100%);padding:2rem 2.4rem;border-radius:24px;color:white;margin-bottom:1rem;box-shadow:0 15px 36px #153e3022}
.hero .eyebrow{font-size:.68rem;letter-spacing:.18em;font-weight:700;color:#c2e6d2}.hero h1{font-family:Manrope,sans-serif;font-size:2.35rem;margin:.45rem 0;color:white}.hero p{margin:0;color:#d3e6dc}
.section-label{color:#318061;font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin:.5rem 0}
.soft-card{border:1px solid #dce8e1;background:white;border-radius:18px;padding:1rem 1.2rem;height:100%}
[data-testid="stMetric"]{background:white;padding:16px 18px;border:1px solid #e0ebe5;border-radius:16px;box-shadow:0 4px 14px #17352e0a}
[data-testid="stMetricValue"]{color:#174b39;font-family:Manrope,sans-serif}
.stButton>button{border-radius:12px;border:1px solid #c9dbd1;background:white;color:#174b39;font-weight:700;padding:.62rem 1rem}
.stButton>button:hover{border-color:#3d8b67;background:#eaf4ee;color:#123c32}
div[data-testid="stForm"]{background:white;border:1px solid #dce8e1;padding:1rem 1.2rem;border-radius:18px}
.stTabs [data-baseweb="tab"]{font-weight:700}.stTabs [aria-selected="true"]{color:#21674a}
.foot{color:#7c928a;font-size:.76rem;border-top:1px solid #dce8e1;padding-top:1rem;margin-top:2rem}
@media(max-width:700px){.hero{padding:1.4rem;border-radius:18px}.hero h1{font-size:1.7rem}.block-container{padding-left:1rem;padding-right:1rem}}
</style>
""", unsafe_allow_html=True)

lang = st.sidebar.selectbox("Idioma / Language", ["Español", "English"], index=0, key="language")
english = lang == "English"
T = {
    "consult": "Consult" if english else "Consultar", "metrics": "View charts" if english else "Ver gráficos",
    "map": "View map" if english else "Ver mapa", "about": "About the model" if english else "Acerca del modelo",
    "input": "Enter scenario" if english else "Ingresa un escenario", "result": "Prediction result" if english else "Resultado de la predicción",
    "history": "Session history" if english else "Historial de la sesión", "comparison": "Compare predictions" if english else "Comparar predicciones",
    "download": "Download results" if english else "Descargar resultados", "high": "High risk" if english else "Riesgo alto",
    "months": "Critical months" if english else "Meses críticos", "records": "Monthly records" if english else "Registros mensuales",
    "cantons": "Cantons" if english else "Cantones", "loading": "Running prediction…" if english else "Ejecutando predicción…",
    "map_link": "Open interactive map ↗" if english else "Abrir mapa interactivo ↗",
}

try:
    df = load_data()
    clusters = get_clusters(df)
except Exception as exc:
    st.error(f"No se pudo cargar la información del proyecto: {exc}")
    st.stop()

render_header(lang)
max_year = int(df["Anio"].max())
latest = df[df["Anio"] == max_year]
c1, c2, c3, c4 = st.columns(4)
c1.metric(T["cantons"], f"{df['canton_norm'].nunique():,}")
c2.metric(T["records"], f"{len(df):,}")
c3.metric(T["high"], f"{df['Mes_Alto_Riesgo'].mean():.1%}")
c4.metric(T["months"], f"{int(latest['Mes_Alto_Riesgo'].sum()):,}", f"{max_year}")

b1, b2, b3 = st.columns([1, 1, 1])
if b1.button(f"⌕  {T['consult']}", use_container_width=True): st.session_state["section"] = "consult"
if b2.button(f"▥  {T['metrics']}", use_container_width=True): st.session_state["section"] = "metrics"
if b3.button(f"⌖  {T['map']}", use_container_width=True): st.switch_page("pages/1_Mapa_interactivo.py")
section = st.session_state.get("section", "consult")

if section == "consult":
    st.markdown(f'<div class="section-label">{T["input"]}</div>', unsafe_allow_html=True)
    cantons = df[["provincia_norm", "canton_norm"]].drop_duplicates().sort_values(["provincia_norm", "canton_norm"])
    with st.form("risk_form"):
        left, right = st.columns(2)
        provinces = sorted(cantons["provincia_norm"].dropna().unique())
        province = left.selectbox("Provincia" if not english else "Province", provinces)
        options = sorted(cantons.loc[cantons["provincia_norm"] == province, "canton_norm"].dropna().unique())
        canton = right.selectbox("Cantón" if not english else "Canton", options)
        a, b, c = st.columns(3)
        month = a.selectbox("Mes" if not english else "Month", list(range(1, 13)), format_func=lambda m: ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][m-1] if not english else datetime(2024,m,1).strftime("%B"))
        total = b.number_input("Incidentes totales recientes" if not english else "Recent total incidents", min_value=0, max_value=100000, value=100, step=10)
        security = c.number_input("Incidentes de seguridad" if not english else "Security incidents", min_value=0, max_value=100000, value=60, step=5)
        d, e, f = st.columns(3)
        critical = d.number_input("Incidentes críticos recientes" if not english else "Recent critical incidents", min_value=0, max_value=100000, value=10, step=1)
        lag1 = e.number_input("Críticos mes anterior" if not english else "Critical incidents last month", min_value=0, max_value=100000, value=8, step=1)
        lag2 = f.number_input("Críticos hace 2 meses" if not english else "Critical incidents 2 months ago", min_value=0, max_value=100000, value=7, step=1)
        submitted = st.form_submit_button(T["consult"], type="primary", use_container_width=True)

    if submitted:
        st.session_state.pop("latest_prediction", None)
        st.session_state["prediction_error"] = None
        if security > total:
            st.error("Los incidentes de seguridad no pueden superar el total.")
        elif critical > total or critical > security:
            st.error("Los incidentes críticos no pueden superar los incidentes de seguridad ni el total.")
        else:
            with st.spinner(T["loading"]):
                season = int(month in [1, 2, 7, 8, 12])
                row = {
                    "canton_norm": canton, "Mes": month, "Trimestre": (month-1)//3+1,
                    "Semestre": 1 if month <= 6 else 2, "Es_Temporada_Alta": season,
                    "Total_Incidentes": total, "Incidentes_Seguridad": security,
                    "Proporcion_Delitos": critical / total if total else 0.0,
                    "Delitos_Lag_1": lag1, "Delitos_Lag_2": lag2,
                    "Media_Movil_3M": (critical+lag1+lag2)/3,
                    "Tendencia_Inercial": critical-lag1,
                }
                try:
                    pred, probability, model_name = predict_risk(row, df, clusters)
                    record = {"Provincia": province, "Cantón": canton, "Mes": month, "Año": max_year + 1, "Riesgo": "Alto" if pred else "Bajo", "Probabilidad": probability, "Modelo": model_name}
                    st.session_state.setdefault("predictions", []).append(record)
                    st.session_state["latest_prediction"] = record
                    st.session_state["prediction_error"] = None
                except Exception as exc:
                    st.session_state["prediction_error"] = str(exc)
    if st.session_state.get("prediction_error"):
        st.error(st.session_state["prediction_error"])
        st.caption("Revisa que las dependencias de `requirements.txt` estén instaladas y que el artefacto .joblib use las 12 variables definidas.")
    record = st.session_state.get("latest_prediction")
    if record:
        st.markdown(f'<div class="section-label">{T["result"]}</div>', unsafe_allow_html=True)
        result_col, prob_col = st.columns([1, 2])
        result_col.metric("Nivel de riesgo" if not english else "Risk level", record["Riesgo"], record["Cantón"])
        prob_col.metric("Probabilidad estimada" if not english else "Estimated probability", f"{record['Probabilidad']:.1%}", record["Modelo"])
        st.progress(record["Probabilidad"], text="Probabilidad del modelo; no equivale a certeza ni a riesgo oficial.")

    if st.session_state.get("predictions"):
        history = pd.DataFrame(st.session_state["predictions"])
        st.subheader(T["history"])
        st.dataframe(history, hide_index=True, use_container_width=True)
        if len(history) > 1:
            st.subheader(T["comparison"])
            chosen = st.multiselect("Selecciona predicciones para comparar", options=list(range(len(history))), default=list(range(min(5, len(history)))), format_func=lambda i: f"{history.iloc[i]['Cantón']} · {history.iloc[i]['Mes']}/{history.iloc[i]['Año']}")
            if chosen:
                fig = px.bar(history.iloc[chosen], x="Cantón", y="Probabilidad", color="Riesgo", color_discrete_map={"Alto":"#ce514c","Bajo":"#3a986c"}, hover_data=["Provincia","Mes","Modelo"], title="Probabilidad por escenario")
                st.plotly_chart(fig, use_container_width=True)
        st.download_button("Descargar CSV", history.to_csv(index=False).encode("utf-8-sig"), "predicciones_riesgo.csv", "text/csv")
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            pdf_buffer = BytesIO()
            pdf = canvas.Canvas(pdf_buffer, pagesize=letter)
            pdf.setTitle("Reporte de predicciones de riesgo")
            pdf.drawString(54, 750, "Ecuador | Reporte de escenarios de riesgo")
            pdf.drawString(54, 728, "Estimaciones del modelo; no constituyen una alerta oficial.")
            y = 690
            for _, r in history.tail(18).iterrows():
                pdf.drawString(54, y, f"{r['Provincia']} / {r['Cantón']} · mes {r['Mes']}/{r['Año']} · {r['Riesgo']} · {r['Probabilidad']:.1%}")
                y -= 20
            pdf.save()
            st.download_button("Descargar PDF", pdf_buffer.getvalue(), "predicciones_riesgo.pdf", "application/pdf")
        except ImportError:
            st.info("Instala reportlab para habilitar la descarga en PDF.")

elif section == "metrics":
    st.subheader("Rendimiento en el conjunto de prueba 2025–2026" if not english else "Test set performance, 2025–2026")
    st.caption("Valores supervisados transcritos de la tabla comparativa guardada en notebooks/optimizacion_modelo.ipynb. Las métricas de K-Means se calculan por separado porque es un método no supervisado.")
    try:
        cluster_stats = get_cluster_quality(df)
        st.markdown("#### K-Means · agrupamiento cantonal (TRAIN)")
        kc1, kc2, kc3, kc4 = st.columns(4)
        kc1.metric("Cantones", f"{cluster_stats['cantons']:,}")
        kc2.metric("Grupos (k)", cluster_stats["clusters"])
        kc3.metric("Silhouette ↑", f"{cluster_stats['silhouette']:.3f}")
        kc4.metric("Davies–Bouldin ↓", f"{cluster_stats['davies_bouldin']:.3f}")
        st.caption(f"Inercia: {cluster_stats['inertia']:.1f} · Recalculada con perfiles cantonales del conjunto TRAIN. Silhouette mayor y Davies–Bouldin menor indican mejor separación relativa; no son métricas de predicción.")
    except Exception as exc:
        st.warning(f"No se pudieron calcular métricas de K-Means: {exc}")
    m1, m2, m3 = st.columns(3)
    for col, (_, r) in zip((m1,m2,m3), METRICS.iterrows()):
        col.metric(r["Modelo"], f"Recall {r['Recall']:.1%}", f"F1 {r['F1']:.3f} · AUC {r['ROC-AUC']:.3f}")
    st.dataframe(model_metrics_display(), hide_index=True, use_container_width=True)
    fig = px.bar(METRICS.melt(id_vars="Modelo", value_vars=["Precision","Recall","F1","ROC-AUC","PR-AUC"], var_name="Métrica", value_name="Valor"), x="Métrica", y="Valor", color="Modelo", barmode="group", color_discrete_sequence=["#4b8b70","#85aa67","#173f34"], title="Comparación de métricas (prueba)")
    st.plotly_chart(fig, use_container_width=True)
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Hiperparámetros XGBoost")
        st.dataframe(HYPERPARAMS, hide_index=True, use_container_width=True)
    with c2:
        st.subheader("Auditoría de fairness por macro región")
        fairness = fairness_summary(df)
        st.dataframe(fairness, hide_index=True, use_container_width=True)
        st.caption("Disparate Impact Ratio (DI): referencia habitual cercana a 1; este resumen describe el indicador incluido en el dataset y no certifica ausencia de sesgo.")
    about, limits = st.columns(2)
    with about:
        st.subheader(T["about"])
        st.write("K-Means agrupa perfiles cantonales históricos; Random Forest y XGBoost estiman meses de alta incidencia. El flujo usa variables mensuales agregadas y una partición temporal documentada en los notebooks.")
    with limits:
        st.subheader("Limitaciones y advertencias")
        st.write("La predicción depende de los datos ingresados, no representa causalidad ni riesgo oficial. Los datos no incluyen coordenadas de cantón. El rendimiento histórico puede cambiar por cobertura, subregistro o cambios temporales.")
    st.image(str(RESULTS_PATH / "models_generacion_dataset_model_pry_v1_1" / "07_paridad_demografica_disparate_impact_ratio_por_macro_region.png"), caption="Indicador de disparate impact por macro región (artefacto del notebook)", use_container_width=True)

st.markdown(f'<div class="foot">Fuente: dataset mensual de incidentes del proyecto y notebooks de modelado. {"Indicative analysis, not an official safety alert." if english else "Análisis indicativo; no constituye una alerta oficial."} · <a href="pages/1_Mapa_interactivo.py">{T["map_link"]}</a></div>', unsafe_allow_html=True)
