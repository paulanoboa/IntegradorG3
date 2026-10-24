import streamlit as st

st.set_page_config(
    page_title="Riesgo Ecuador | Inteligencia territorial",
    page_icon="🇪🇨",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = [
    st.Page("pages/0_Inicio.py", title="Inicio", icon="🏠", default=True),
    st.Page("pages/1_Mapa_interactivo.py", title="Mapa interactivo", icon="🗺️"),
]
page = st.navigation(pages)
page.run()
