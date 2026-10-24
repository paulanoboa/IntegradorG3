from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from dashboard import PROVINCE_CENTERS, build_top50, load_data, render_banner, render_language_buttons  # noqa: E402

render_banner()
english = render_language_buttons() == "English"
st.markdown("""
<style>
.stApp{background:#f5f8f6}.block-container{max-width:1760px;padding:1rem 1.1rem 2rem}
.maphero{background:linear-gradient(110deg,#102f29,#28714f);color:white;padding:1.6rem 2rem;border-radius:22px;margin-bottom:1.2rem}
.maphero h1{color:white;margin:0;font-size:2rem}.maphero p{color:#d6e9df;margin:.4rem 0 0}
[data-testid="stMetric"]{background:white;padding:14px;border:1px solid #dce8e1;border-radius:15px}
.risk-summary-card{min-height:154px;padding:16px 18px;background:white;border:1px solid #dce8e1;border-radius:16px;box-shadow:0 4px 14px #17352e0a}
.risk-summary-label{font-size:1rem;color:#252a36}.risk-summary-label--high{color:rgba(212,71,63,1)}
.risk-summary-value{font-size:2.4rem;line-height:1.2;color:#252a36;margin:.25rem 0 .45rem}
.risk-summary-pill{display:inline-flex;align-items:center;gap:.25rem;padding:.25rem .65rem;border-radius:999px;font-size:.95rem}
.risk-summary-pill--high{color:rgba(212,71,63,1);background:rgba(212,71,63,.12)}
.risk-summary-pill--medium{color:rgba(196,139,0,1);background:rgba(229,166,41,.16)}
.risk-summary-pill--low{color:#32875f;background:rgba(56,147,106,.13)}
div[data-testid="stPlotlyChart"]{background:white;border:1px solid #dce8e1;border-radius:18px;padding:.25rem;box-shadow:0 8px 24px #17352e12}
@media(max-width:700px){.block-container{padding:.6rem}.maphero{padding:1.2rem}.maphero h1{font-size:1.55rem}}
</style>
""", unsafe_allow_html=True)
title = "Interactive risk map · Ecuador" if english else "Mapa interactivo de riesgo · Ecuador"
subtitle = "Top 50 cantons by average critical incidents in the dataset’s two most recent years." if english else "50 cantones con mayor promedio de incidentes críticos en los dos años más recientes del dataset."
st.markdown(f'<div class="maphero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)
if st.button("← Back to dashboard" if english else "← Volver al panel"):
    st.switch_page("pages/0_Inicio.py")

try:
    df = load_data()
    top = build_top50(df)
except Exception as exc:
    st.error(f"Could not build the map: {exc}" if english else f"No se pudo construir el mapa: {exc}")
    st.stop()

colors = {"Alto": "#d4473f", "Medio": "#e5a629", "Bajo": "#38936a"}
missing = sorted(set(top["provincia_norm"]) - set(PROVINCE_CENTERS))
if missing:
    st.warning("No hay centro aproximado configurado para estas provincias: " + ", ".join(missing))
top = top[top["provincia_norm"].isin(PROVINCE_CENTERS)].copy()
top["lat"] = top["provincia_norm"].map(lambda p: PROVINCE_CENTERS[p][0])
top["lon"] = top["provincia_norm"].map(lambda p: PROVINCE_CENTERS[p][1])
# Small deterministic offsets only separate cantons that share a province center on screen.
top["_within_province"] = top.groupby("provincia_norm").cumcount()
top["lat"] += top["_within_province"] * .045
top["lon"] += top["_within_province"] * .055

hi, med, low = st.columns(3)

def render_risk_summary(column, label: str, count: int, tag: str, level: str) -> None:
    column.markdown(
        f'<div class="risk-summary-card"><div class="risk-summary-label risk-summary-label--{level}">{label}</div>'
        f'<div class="risk-summary-value">{count}</div><span class="risk-summary-pill risk-summary-pill--{level}">↑ {tag}</span></div>',
        unsafe_allow_html=True,
    )

render_risk_summary(hi, "High risk" if english else "Riesgo alto", int((top["Nivel"] == "Alto").sum()), "Red" if english else "Rojo", "high")
render_risk_summary(med, "Medium risk" if english else "Riesgo medio", int((top["Nivel"] == "Medio").sum()), "Yellow" if english else "Amarillo", "medium")
render_risk_summary(low, "Low risk" if english else "Riesgo bajo", int((top["Nivel"] == "Bajo").sum()), "Green" if english else "Verde", "low")

fig = px.scatter_map(
    top, lat="lat", lon="lon", color="Nivel", size="Incidentes_Criticos_Media",
    size_max=34, opacity=0.84, hover_name="canton_norm",
    hover_data={"provincia_norm": True, "Rango": True, "Incidentes_Criticos_Media": ":.2f", "Meses_Alto_Riesgo": True, "lat": False, "lon": False, "_within_province": False},
    category_orders={"Nivel": ["Alto", "Medio", "Bajo"]},
    color_discrete_map=colors, title="Top 50 cantons · criticality signals" if english else "Top 50 cantones · señales de criticidad",
    map_style="open-street-map", zoom=4.0, center={"lat": -1.5, "lon": -80.5}, height=850,
)
fig.update_layout(
    height=850, margin={"l":0,"r":0,"t":52,"b":0},
    legend_title_text="Risk level" if english else "Nivel de riesgo",
    paper_bgcolor="rgba(0,0,0,0)", map={"bearing":0,"pitch":0},
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Approximate locations: the dataset identifies province and canton but has no coordinates. Markers sit near province centers and are visually offset when they overlap; they are not exact canton locations. Levels follow the ranking (15 high, 20 medium, 15 low), not official categories." if english else "Ubicaciones aproximadas: el dataset solo identifica provincia y cantón, sin latitud/longitud. Los marcadores se colocan cerca del centro provincial y se separan visualmente cuando coinciden; no representan la ubicación exacta del cantón. Los niveles siguen el ranking (15 altos, 20 medios y 15 bajos), no son categorías oficiales.")

st.subheader("Prioritized cantons" if english else "Cantones priorizados")
display = top[["Rango", "canton_norm", "provincia_norm", "Nivel", "Incidentes_Criticos_Media", "Meses_Alto_Riesgo"]].rename(columns={"canton_norm":"Cantón","provincia_norm":"Provincia","Incidentes_Criticos_Media":"Promedio mensual crítico","Meses_Alto_Riesgo":"Meses alto riesgo"})
st.dataframe(display.style.format({"Promedio mensual crítico":"{:.2f}"}), hide_index=True, use_container_width=True)
