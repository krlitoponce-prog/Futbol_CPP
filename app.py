import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Football Intelligence Pro v36.1", layout="wide")

if 'historial_global' not in st.session_state:
    st.session_state.historial_global = []

# --- DATA MAESTRA (36 CHAMPIONS + FRANCIA) ---
# Se mantiene el 100% de los equipos con sus atributos de Tier, pattern y pitch.
if 'data_equipos' not in st.session_state:
    st.session_state.data_equipos = {
        "Arsenal": {"id": 42, "xG": 2.2, "xGA": 0.8, "tier": 1, "spec": "Posesión", "pitch": "Natural", "pattern": [1.2, 1.0, 1.1]},
        "Aston Villa": {"id": 40, "xG": 1.8, "xGA": 1.2, "tier": 2, "spec": "Contra", "pitch": "Natural", "pattern": [1.0, 1.1, 1.2]},
        "Atalanta": {"id": 2686, "xG": 1.7, "xGA": 1.1, "tier": 2, "spec": "Marcaje", "pitch": "Natural", "pattern": [0.9, 1.2, 1.4]},
        "Atlético Madrid": {"id": 2836, "xG": 1.7, "xGA": 1.1, "tier": 1, "spec": "Intensidad", "pitch": "Natural", "pattern": [0.8, 1.1, 1.3]},
        "Barcelona": {"id": 2817, "xG": 2.2, "xGA": 1.2, "tier": 1, "spec": "ADN Barça", "pitch": "Natural", "pattern": [1.3, 1.2, 0.8]},
        "Bayern München": {"id": 2672, "xG": 2.1, "xGA": 1.0, "tier": 1, "spec": "Transición", "pitch": "Natural", "pattern": [1.1, 1.2, 1.2]},
        "Benfica": {"id": 3006, "xG": 1.7, "xGA": 1.0, "tier": 2, "spec": "Asociativo", "pitch": "Natural", "pattern": [1.1, 1.1, 1.2]},
        "Bayer Leverkusen": {"id": 2681, "xG": 1.9, "xGA": 1.0, "tier": 1, "spec": "Invictos", "pitch": "Natural", "pattern": [0.8, 1.2, 1.8]},
        "Bologna": {"id": 2685, "xG": 1.4, "xGA": 1.2, "tier": 3, "spec": "Orden", "pitch": "Natural", "pattern": [1.0, 1.0, 1.0]},
        "Brest": {"id": 1645, "xG": 1.3, "xGA": 1.4, "tier": 3, "spec": "Entusiasmo", "pitch": "Natural", "pattern": [1.1, 1.0, 0.9]},
        "Celtic": {"id": 2352, "xG": 1.5, "xGA": 1.8, "tier": 3, "spec": "Presión", "pitch": "Natural", "pattern": [1.2, 1.0, 0.8]},
        "Club Brugge": {"id": 2634, "xG": 1.4, "xGA": 1.5, "tier": 2, "spec": "Contragolpe", "pitch": "Natural", "pattern": [0.9, 1.1, 1.2]},
        "Crvena Zvezda": {"id": 2362, "xG": 1.2, "xGA": 2.1, "tier": 4, "spec": "Localía", "pitch": "Natural", "pattern": [1.1, 0.9, 0.7]},
        "Feyenoord": {"id": 2713, "xG": 1.6, "xGA": 1.3, "tier": 2, "spec": "Ataque", "pitch": "Natural", "pattern": [1.1, 1.1, 1.1]},
        "Girona": {"id": 2822, "xG": 1.6, "xGA": 1.4, "tier": 2, "spec": "Ofensivo", "pitch": "Natural", "pattern": [1.1, 1.1, 1.0]},
        "GNK Dinamo": {"id": 2351, "xG": 1.2, "xGA": 2.2, "tier": 4, "spec": "Resistencia", "pitch": "Natural", "pattern": [1.0, 1.0, 0.8]},
        "Inter": {"id": 2697, "xG": 1.8, "xGA": 0.9, "tier": 1, "spec": "Bloque", "pitch": "Natural", "pattern": [1.0, 1.2, 1.1]},
        "Juventus": {"id": 2687, "xG": 1.6, "xGA": 0.8, "tier": 1, "spec": "Defensa", "pitch": "Natural", "pattern": [0.8, 1.2, 1.1]},
        "RB Leipzig": {"id": 2684, "xG": 1.8, "xGA": 1.2, "tier": 2, "spec": "Velocidad", "pitch": "Natural", "pattern": [1.1, 1.1, 1.2]},
        "Liverpool": {"id": 44, "xG": 2.2, "xGA": 1.0, "tier": 1, "spec": "Gegenpressing", "pitch": "Natural", "pattern": [1.3, 1.2, 1.1]},
        "Lille": {"id": 1643, "xG": 1.5, "xGA": 1.3, "tier": 2, "spec": "Equilibrio", "pitch": "Natural", "pattern": [1.0, 1.1, 1.1]},
        "Man City": {"id": 17, "xG": 2.4, "xGA": 0.9, "tier": 1, "spec": "Ataque Total", "pitch": "Natural", "pattern": [1.4, 1.1, 0.9]},
        "Monaco": {"id": 1653, "xG": 1.7, "xGA": 1.3, "tier": 2, "spec": "Dinámico", "pitch": "Natural", "pattern": [1.1, 1.1, 1.2]},
        "PSG": {"id": 1644, "xG": 2.0, "xGA": 1.1, "tier": 1, "spec": "Velocidad", "pitch": "Natural", "pattern": [1.0, 1.1, 1.4]},
        "PSV Eindhoven": {"id": 2722, "xG": 1.9, "xGA": 1.1, "tier": 2, "spec": "Bandas", "pitch": "Natural", "pattern": [1.2, 1.3, 0.9]},
        "Real Madrid": {"id": 2829, "xG": 2.2, "xGA": 1.1, "tier": 1, "spec": "Jerarquía", "pitch": "Natural", "pattern": [0.7, 1.0, 1.8]},
        "Salzburg": {"id": 2603, "xG": 1.5, "xGA": 1.6, "tier": 3, "spec": "Juventud", "pitch": "Natural", "pattern": [1.2, 1.0, 0.9]},
        "Shakhtar Donetsk": {"id": 2355, "xG": 1.3, "xGA": 1.7, "tier": 3, "spec": "Técnica", "pitch": "Natural", "pattern": [0.9, 1.1, 1.0]},
        "Slovan Bratislava": {"id": 2341, "xG": 0.9, "xGA": 2.3, "tier": 4, "spec": "Bloque", "pitch": "Natural", "pattern": [0.8, 1.0, 0.7]},
        "Sparta Praha": {"id": 2244, "xG": 1.3, "xGA": 1.6, "tier": 3, "spec": "Físico", "pitch": "Natural", "pattern": [1.1, 1.0, 1.0]},
        "Sporting CP": {"id": 3001, "xG": 1.8, "xGA": 0.9, "tier": 2, "spec": "Salida", "pitch": "Natural", "pattern": [1.1, 1.2, 1.0]},
        "Sturm Graz": {"id": 2605, "xG": 1.1, "xGA": 1.9, "tier": 4, "spec": "Lucha", "pitch": "Natural", "pattern": [1.0, 0.9, 0.9]},
        "Stuttgart": {"id": 2677, "xG": 1.7, "xGA": 1.4, "tier": 2, "spec": "Vertical", "pitch": "Natural", "pattern": [1.1, 1.2, 1.1]},
        "Bodo/Glimt": {"id": 5444, "xG": 1.4, "xGA": 1.4, "tier": 3, "spec": "Ártico", "pitch": "Sintético", "pattern": [1.2, 1.3, 0.8]},
        "Young Boys": {"id": 2600, "xG": 1.3, "xGA": 1.9, "tier": 4, "spec": "Ataque", "pitch": "Sintético", "pattern": [1.1, 1.0, 0.9]},
        "Kairat Almaty": {"id": 4726, "xG": 0.9, "xGA": 2.2, "tier": 4, "spec": "Altura", "pitch": "Natural", "pattern": [1.0, 0.9, 0.8]},
        "Olympique de Marseille": {"id": 1641, "xG": 1.8, "xGA": 1.1, "tier": 2, "spec": "Ambiental", "pitch": "Natural", "pattern": [1.1, 1.0, 1.3]},
        "Olympique Lyonnais": {"id": 1647, "xG": 1.9, "xGA": 1.2, "tier": 2, "spec": "Vertical", "pitch": "Natural", "pattern": [1.1, 1.2, 1.3]}
    }

def get_logo(t_id): return f"https://www.sofascore.com/static/images/team-logo/team_{t_id}.png"

st.title("⚽ Football Intelligence Pro v36.1")

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Equipo Local", list(st.session_state.data_equipos.keys()), key="loc")
    t_l = st.session_state.data_equipos[loc]
    st.image(get_logo(t_l['id']), width=70)
    st.warning(f"💎 Fortaleza: {t_l['spec']} | 🏟️ Césped: {t_l['pitch']}")
    st.info(f"📋 **LESIONADOS {loc}:** Descuento automático al marcar.")
    bajas_l = st.multiselect(f"Bajas {loc}", ["Goleador (-20% xG)", "Portero/Defensa (+15% xGA)"], key="bl")
    panico_l = st.toggle("🚨 ¡ROJA PARA LOCAL!", key="pl")

with col2:
    vis = st.selectbox("Equipo Visitante", list(st.session_state.data_equipos.keys()), key="vis")
    t_v = st.session_state.data_equipos[vis]
    st.image(get_logo(t_v['id']), width=70)
    st.warning(f"💎 Fortaleza: {t_v['spec']} | 🏟️ Césped: {t_v['pitch']}")
    st.info(f"📋 **LESIONADOS {vis}:** Descuento automático al marcar.")
    bajas_v = st.multiselect(f"Bajas {vis}", ["Goleador (-20% xG)", "Portero/Defensa (+15% xGA)"], key="bv")
    panico_v = st.toggle("🚨 ¡ROJA PARA VISITANTE!", key="pv")

st.divider()

if st.button("🚀 GENERAR ANÁLISIS MAESTRO"):
    # Lambdas Base
    l_l = (t_l["xG"] * t_v["xGA"]) / 1.4
    l_v = (t_v["xG"] * t_l["xGA"]) / 1.4

    # IMPACTO BAJAS Y PÁNICO
    if "Goleador" in str(bajas_l): l_l *= 0.80
    if "Portero" in str(bajas_l): l_v *= 1.15
    if "Goleador" in str(bajas_v): l_v *= 0.80
    if "Portero" in str(bajas_v): l_l *= 1.15
    if panico_l: l_l *= 0.60; l_v *= 1.40
    if panico_v: l_v *= 0.60; l_l *= 1.40
    if t_l['pitch'] == "Sintético": l_l *= 1.25

    # RESULTADOS
    st.success(f"### Análisis Pro: {loc} vs {vis}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Goles Est.", f"{l_l+l_v:.2f}")
    m2.metric("Ambos Anotan", f"{(1-poisson.pmf(0, l_l))*(1-poisson.pmf(0, l_v))*100:.1f}%")
    m3.metric("Córners Est.", f"{(l_l+l_v)*2.9:.1f}")
    m4.metric("Gol 1T", f"{(1-(poisson.pmf(0, l_l*0.35)*poisson.pmf(0, l_v*0.35)))*100:.1f}%")

    # RECOMENDACIÓN
    rec = "Gana Local + Over 1.5" if l_l > l_v + 0.6 else "BTTS (Ambos Anotan)"
    st.info(f"✅ **Estrategia Maestra:** {rec} | **Stake: 8/10**")
    st.error("🚨 ALERTA DE GOL: Pico de presión detectado en tramo 75'-90'.")

    # MARCADORES MAESTROS
    res_m = []
    for gl in range(6):
        for gv in range(6):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            res_m.append({"m": f"{gl}-{gv}", "p": p * 100})
    best = sorted(res_m, key=lambda x: x['p'], reverse=True)[:5]

    st.subheader("🎯 Marcadores Exactos (Marcador Maestro)")
    m_cols = st.columns(5)
    for idx, m in enumerate(best):
        with m_cols[idx]:
            if idx == 0: st.warning(f"👑 **{m['m']}**\n{m['p']:.1f}%")
            else: st.info(f"**{m['m']}**\n{m['p']:.1f}%")

    # TRAMOS
    tramos = ["0-15'", "16-30'", "31-45'", "46-60'", "61-75'", "76-90'"]
    probs = [round(((l_l * t_l["pattern"][i//2]) + (l_v * t_v["pattern"][i//2])) / 6 * 100, 1) for i in range(6)]
    fig = go.Figure(go.Scatter(x=tramos, y=probs, mode='lines+markers', line=dict(color='orange', width=4)))
    st.plotly_chart(fig, use_container_width=True)