from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from dashboard import PROVINCE_CENTERS, build_top10, load_data  # noqa: E402

st.set_page_config(page_title="Mapa de riesgo | Ecuador", page_icon="🗺️", layout="wide")
english = st.sidebar.selectbox("Idioma / Language", ["Español", "English"], index=0, key="language") == "English"
st.markdown("""
<style>
.stApp{background:#f5f8f6}.block-container{max-width:1320px;padding-top:1.5rem}
.maphero{background:linear-gradient(110deg,#102f29,#28714f);color:white;padding:1.6rem 2rem;border-radius:22px;margin-bottom:1.2rem}
.maphero h1{color:white;margin:0;font-size:2rem}.maphero p{color:#d6e9df;margin:.4rem 0 0}
[data-testid="stMetric"]{background:white;padding:14px;border:1px solid #dce8e1;border-radius:15px}
</style>
""", unsafe_allow_html=True)
title = "Interactive risk map · Ecuador" if english else "Mapa interactivo de riesgo · Ecuador"
subtitle = "Top 10 cantons by average critical incidents in the dataset’s two most recent years." if english else "Top 10 cantones según promedio de incidentes críticos en los dos años más recientes del dataset."
st.markdown(f'<div class="maphero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)
if st.button("← Back to dashboard" if english else "← Volver al panel"):
    st.switch_page("app.py")

try:
    df = load_data()
    top = build_top10(df)
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
hi.metric("High risk" if english else "Riesgo alto", int((top["Nivel"] == "Alto").sum()), "Red" if english else "Rojo")
med.metric("Medium risk" if english else "Riesgo medio", int((top["Nivel"] == "Medio").sum()), "Yellow" if english else "Amarillo")
low.metric("Low risk" if english else "Riesgo bajo", int((top["Nivel"] == "Bajo").sum()), "Green" if english else "Verde")

fig = px.scatter_geo(
    top, lat="lat", lon="lon", color="Nivel", size="Incidentes_Criticos_Media",
    size_max=30, hover_name="canton_norm",
    hover_data={"provincia_norm": True, "Rango": True, "Incidentes_Criticos_Media": ":.2f", "Meses_Alto_Riesgo": True, "lat": False, "lon": False, "_within_province": False},
    category_orders={"Nivel": ["Alto", "Medio", "Bajo"]},
    color_discrete_map=colors, title="Top 10 cantons · criticality signals" if english else "Top 10 cantones · señales de criticidad",
)
fig.update_geos(
    scope="south america", projection_type="mercator", showcountries=True,
    countrycolor="#aebfb5", showland=True, landcolor="#e8eee9",
    showocean=True, oceancolor="#eaf2f4", showcoastlines=True,
    coastlinecolor="#aebfb5", lataxis_range=[-5.3, 1.7], lonaxis_range=[-92.5, -74.5],
    center={"lat": -1.5, "lon": -79.5},
)
fig.update_layout(height=650, margin={"l":0,"r":0,"t":55,"b":0}, legend_title_text="Risk level" if english else "Nivel de riesgo", paper_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)
st.caption("Approximate locations: the dataset identifies province and canton but has no coordinates. Markers sit near province centers and are visually offset when they overlap; they are not exact canton locations. Levels follow the top-10 ranking (3 high, 4 medium, 3 low), not official categories." if english else "Ubicaciones aproximadas: el dataset solo identifica provincia y cantón, sin latitud/longitud. Los marcadores se colocan cerca del centro provincial y se separan visualmente cuando coinciden; no representan la ubicación exacta del cantón. Los niveles se asignan por orden del top 10 (3 altos, 4 medios y 3 bajos), no son categorías oficiales.")

st.subheader("Prioritized cantons" if english else "Cantones priorizados")
display = top[["Rango", "canton_norm", "provincia_norm", "Nivel", "Incidentes_Criticos_Media", "Meses_Alto_Riesgo"]].rename(columns={"canton_norm":"Cantón","provincia_norm":"Provincia","Incidentes_Criticos_Media":"Promedio mensual crítico","Meses_Alto_Riesgo":"Meses alto riesgo"})
st.dataframe(display.style.format({"Promedio mensual crítico":"{:.2f}"}), hide_index=True, use_container_width=True)
