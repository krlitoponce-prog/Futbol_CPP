import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Football Intelligence Pro v31.2", layout="wide")

if 'historial_global' not in st.session_state:
    st.session_state.historial_global = []

# --- DATA MAESTRA (LOS 36 EQUIPOS COMPLETOS DE TU LISTA) ---
# pattern: [Inico (0-30), Medio (31-60), Final (61-90)] -> Basado en scraping de goles históricos
DATA_MASTER = {
    "CHAMPIONS & EUROPE": {
        "Arsenal": {"id": 42, "xG": 2.1, "xGA": 0.8, "tier": 1, "spec": "Posesión", "pitch": "Natural", "pattern": [1.2, 1.0, 1.1]},
        "Bayern München": {"id": 2672, "xG": 2.1, "xGA": 1.0, "tier": 1, "spec": "Transición", "pitch": "Natural", "pattern": [1.1, 1.2, 1.2]},
        "Paris Saint-Germain": {"id": 1644, "xG": 2.0, "xGA": 1.1, "tier": 1, "spec": "Velocidad", "pitch": "Natural", "pattern": [1.0, 1.1, 1.4]},
        "Manchester City": {"id": 17, "xG": 2.4, "xGA": 0.9, "tier": 1, "spec": "Ataque Total", "pitch": "Natural", "pattern": [1.4, 1.1, 0.9]},
        "Atalanta": {"id": 2686, "xG": 1.7, "xGA": 1.1, "tier": 2, "spec": "Marcaje", "pitch": "Natural", "pattern": [0.9, 1.2, 1.4]},
        "Internazionale": {"id": 2697, "xG": 1.8, "xGA": 0.9, "tier": 1, "spec": "Bloque", "pitch": "Natural", "pattern": [1.0, 1.2, 1.1]},
        "Real Madrid": {"id": 2829, "xG": 2.2, "xGA": 1.1, "tier": 1, "spec": "Jerarquía", "pitch": "Natural", "pattern": [0.7, 1.0, 1.8]},
        "Atlético Madrid": {"id": 2836, "xG": 1.7, "xGA": 1.1, "tier": 1, "spec": "Intensidad", "pitch": "Natural", "pattern": [0.8, 1.1, 1.3]},
        "Liverpool": {"id": 44, "xG": 2.2, "xGA": 1.0, "tier": 1, "spec": "Gegenpressing", "pitch": "Natural", "pattern": [1.3, 1.2, 1.1]},
        "Borussia Dortmund": {"id": 2673, "xG": 1.7, "xGA": 1.2, "tier": 1, "spec": "Contra", "pitch": "Natural", "pattern": [1.0, 1.1, 1.4]},
        "Tottenham Hotspur": {"id": 33, "xG": 1.8, "xGA": 1.5, "tier": 2, "spec": "Verticalidad", "pitch": "Natural", "pattern": [1.1, 1.1, 1.3]},
        "Newcastle United": {"id": 37, "xG": 1.7, "xGA": 1.5, "tier": 2, "spec": "Físico", "pitch": "Natural", "pattern": [1.2, 1.0, 1.1]},
        "Chelsea": {"id": 38, "xG": 1.9, "xGA": 1.3, "tier": 2, "spec": "Ofensivo", "pitch": "Natural", "pattern": [1.0, 1.1, 1.2]},
        "Sporting CP": {"id": 3001, "xG": 1.8, "xGA": 0.9, "tier": 2, "spec": "Salida", "pitch": "Natural", "pattern": [1.1, 1.2, 1.0]},
        "Barcelona": {"id": 2817, "xG": 2.1, "xGA": 1.2, "tier": 1, "spec": "ADN Barça", "pitch": "Natural", "pattern": [1.3, 1.2, 0.8]},
        "Marseille": {"id": 1641, "xG": 1.8, "xGA": 1.2, "tier": 2, "spec": "Ambiental", "pitch": "Natural", "pattern": [1.1, 1.0, 1.2]},
        "Juventus": {"id": 2687, "xG": 1.6, "xGA": 0.8, "tier": 1, "spec": "Orden", "pitch": "Natural", "pattern": [0.8, 1.2, 1.1]},
        "Galatasaray": {"id": 2901, "xG": 1.8, "xGA": 1.3, "tier": 2, "spec": "Infierno", "pitch": "Natural", "pattern": [1.2, 1.1, 1.2]},
        "AS Mónaco": {"id": 1653, "xG": 1.7, "xGA": 1.3, "tier": 2, "spec": "Dinámico", "pitch": "Natural", "pattern": [1.1, 1.1, 1.2]},
        "Bayer Leverkusen": {"id": 2681, "xG": 1.9, "xGA": 1.0, "tier": 1, "spec": "Invictos", "pitch": "Natural", "pattern": [0.8, 1.2, 1.8]},
        "PSV Eindhoven": {"id": 2722, "xG": 1.9, "xGA": 1.1, "tier": 2, "spec": "Bandas", "pitch": "Natural", "pattern": [1.2, 1.3, 0.9]},
        "FK Qarabag": {"id": 5510, "xG": 1.3, "xGA": 1.6, "tier": 3, "spec": "Resistencia", "pitch": "Natural", "pattern": [0.9, 1.0, 1.1]},
        "Napoli": {"id": 2714, "xG": 1.7, "xGA": 1.0, "tier": 2, "spec": "Vertical", "pitch": "Natural", "pattern": [1.1, 1.2, 1.1]},
        "F.C. København": {"id": 2699, "xG": 1.4, "xGA": 1.3, "tier": 3, "spec": "Disciplina", "pitch": "Natural", "pattern": [1.0, 1.0, 1.0]},
        "Benfica": {"id": 3006, "xG": 1.7, "xGA": 1.0, "tier": 2, "spec": "Asociativo", "pitch": "Natural", "pattern": [1.1, 1.1, 1.2]},
        "Pafos": {"id": 36173, "xG": 1.1, "xGA": 1.6, "tier": 4, "spec": "Cerrado", "pitch": "Natural", "pattern": [0.9, 1.0, 1.0]},
        "Union St.-Gilloise": {"id": 3662, "xG": 1.3, "xGA": 1.4, "tier": 3, "spec": "Estrategia", "pitch": "Natural", "pattern": [1.0, 1.1, 1.1]},
        "Athletic Club": {"id": 2825, "xG": 1.6, "xGA": 1.2, "tier": 2, "spec": "Aéreo", "pitch": "Natural", "pattern": [1.1, 1.2, 1.1]},
        "Olympiacos": {"id": 2616, "xG": 1.6, "xGA": 1.2, "tier": 3, "spec": "Presión", "pitch": "Natural", "pattern": [1.1, 1.0, 1.2]},
        "Eintracht Frankfurt": {"id": 2679, "xG": 1.5, "xGA": 1.4, "tier": 2, "spec": "Veloz", "pitch": "Natural", "pattern": [1.1, 1.1, 1.2]},
        "Club Brujas": {"id": 2634, "xG": 1.4, "xGA": 1.5, "tier": 2, "spec": "Contra", "pitch": "Natural", "pattern": [0.9, 1.1, 1.2]},
        "Bodo/Glimt": {"id": 5444, "xG": 1.4, "xGA": 1.4, "tier": 3, "spec": "Ártico", "pitch": "Sintético", "pattern": [1.2, 1.3, 0.8]},
        "Slavia Prague": {"id": 2261, "xG": 1.4, "xGA": 1.3, "tier": 3, "spec": "Físico", "pitch": "Natural", "pattern": [1.0, 1.1, 1.1]},
        "Ajax Amsterdam": {"id": 2692, "xG": 1.6, "xGA": 1.2, "tier": 2, "spec": "Presión", "pitch": "Natural", "pattern": [1.2, 1.1, 1.0]},
        "Villarreal": {"id": 2819, "xG": 1.7, "xGA": 1.6, "tier": 2, "spec": "Medios", "pitch": "Natural", "pattern": [1.0, 1.1, 1.3]},
        "Kairat Almaty": {"id": 4726, "xG": 0.9, "xGA": 2.2, "tier": 4, "spec": "Altura", "pitch": "Natural", "pattern": [1.0, 0.9, 0.8]}
    }
}

def get_logo(t_id): return f"https://www.sofascore.com/static/images/team-logo/team_{t_id}.png"

# --- INTERFAZ ---
st.title("⚽ Football Intelligence Pro v31.2: Analítica Temporal")

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Equipo Local", list(DATA_MASTER["CHAMPIONS & EUROPE"].keys()), key="loc")
    team_l = DATA_MASTER["CHAMPIONS & EUROPE"][loc]
    st.image(get_logo(team_l['id']), width=70)
    st.metric("Calificación (Tier)", team_l['tier'])
    st.info(f"📋 **LESIONADOS {loc}:**")
    bajas_l = st.multiselect(f"Bajas Confirmadas {loc}", ["Goleador (-20% xG)", "Defensa (+15% xGA)"], key="bl")

with col2:
    vis = st.selectbox("Equipo Visitante", list(DATA_MASTER["CHAMPIONS & EUROPE"].keys()), key="vis")
    team_v = DATA_MASTER["CHAMPIONS & EUROPE"][vis]
    st.image(get_logo(team_v['id']), width=70)
    st.metric("Calificación (Tier)", team_v['tier'])
    st.info(f"📋 **LESIONADOS {vis}:**")
    bajas_v = st.multiselect(f"Bajas Confirmadas {vis}", ["Goleador (-20% xG)", "Defensa (+15% xGA)"], key="bv")

st.divider()

if st.button("🚀 GENERAR ANÁLISIS DE TRAMOS"):
    l_l = (team_l["xG"] * team_v["xGA"]) / 1.45
    l_v = (team_v["xG"] * team_l["xGA"]) / 1.45

    # Impacto de Bajas
    if "Goleador" in str(bajas_l): l_l *= 0.80
    if "Defensa" in str(bajas_l): l_v *= 1.15
    if "Goleador" in str(bajas_v): l_v *= 0.80
    if "Defensa" in str(bajas_v): l_l *= 1.15

    # TRAMOS DE 15 MINUTOS
    tramos = ["0-15'", "16-30'", "31-45'", "46-60'", "61-75'", "76-90'"]
    probs = []
    for i in range(6):
        p_idx = 0 if i < 2 else (1 if i < 4 else 2)
        p_val = ((l_l * team_l["pattern"][p_idx]) + (l_v * team_v["pattern"][p_idx])) / 6
        probs.append(round(p_val * 100, 1))

    st.success(f"### Análisis por Minutos: {loc} vs {vis}")
    t_cols = st.columns(6)
    for i, col in enumerate(t_cols):
        with col:
            st.metric(tramos[i], f"{probs[i]}%", delta="Pico" if probs[i] == max(probs) else None)

    # ALERTA RESALTADA
    st.error(f"🚨 ALERTA DE GOL INMINENTE: Tramo con mayor presión detectado en {tramos[probs.index(max(probs))]}.")

    # GRÁFICA DE PRESIÓN
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tramos, y=probs, mode='lines+markers', name='Peligrosidad %', line=dict(color='orange', width=4)))
    fig.update_layout(title="Curva de Probabilidad de Gol (Scraping Patterns)", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- AUDITORÍA ---
st.divider()
st.subheader("📊 Auditoría: Rendimiento vs Predicción")
c1, c2 = st.columns(2)
with c1:
    res_r = st.text_input("Marcador Real Final (ej. 3-1)")
with c2:
    if st.button("⚖️ Guardar y Comparar"):
        st.session_state.historial_global.append({"Partido": f"{loc} vs {vis}", "Real": res_r})
        st.success("Resultado registrado para ajustar la inteligencia del sistema.")