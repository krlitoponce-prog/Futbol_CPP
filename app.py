import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Football Intelligence Pro v32", layout="wide")

if 'historial_global' not in st.session_state:
    st.session_state.historial_global = []

# --- DATA MAESTRA (LOS 36 EQUIPOS COMPLETOS) ---
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
st.title("⚽ Football Intelligence Pro v32 (Análisis Integral)")

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Equipo Local", list(DATA_MASTER["CHAMPIONS & EUROPE"].keys()), key="loc")
    team_l = DATA_MASTER["CHAMPIONS & EUROPE"][loc]
    st.image(get_logo(team_l['id']), width=70)
    st.metric("Calificación (Tier)", team_l['tier'])
    st.warning(f"💎 Fortaleza: {team_l['spec']} | 🏟️ Césped: {team_l['pitch']}")
    # LESIONADOS CON IMPACTO DIRECTO
    st.info(f"📋 **LESIONADOS {loc}:** Selecciona para aplicar descuento.")
    bajas_l = st.multiselect(f"Bajas Confirmadas {loc}", ["Portero (xGA +15%)", "Defensa (xGA +10%)", "Ataque (xG -20%)"], key="bl")
    clima_l = st.select_slider(f"Estado Clima {loc}", ["Normal", "Favorable", "Extremo"], key="cl")

with col2:
    vis = st.selectbox("Equipo Visitante", list(DATA_MASTER["CHAMPIONS & EUROPE"].keys()), key="vis")
    team_v = DATA_MASTER["CHAMPIONS & EUROPE"][vis]
    st.image(get_logo(team_v['id']), width=70)
    st.metric("Calificación (Tier)", team_v['tier'])
    st.warning(f"💎 Fortaleza: {team_v['spec']} | 🏟️ Césped: {team_v['pitch']}")
    st.info(f"📋 **LESIONADOS {vis}:** Selecciona para aplicar descuento.")
    bajas_v = st.multiselect(f"Bajas Confirmadas {vis}", ["Portero (xGA +15%)", "Defensa (xGA +10%)", "Ataque (xG -20%)"], key="bv")

st.divider()

if st.button("🚀 GENERAR ANÁLISIS MAESTRO"):
    # Lambdas base
    l_l = (team_l["xG"] * team_v["xGA"]) / 1.45
    l_v = (team_v["xG"] * team_l["xGA"]) / 1.45

    # APLICACIÓN DE BAJAS AUTOMÁTICAS
    for b in bajas_l:
        if "Portero" in b: l_v *= 1.15
        if "Defensa" in b: l_v *= 1.10
        if "Ataque" in b: l_l *= 0.80
    for b in bajas_v:
        if "Portero" in b: l_l *= 1.15
        if "Defensa" in b: l_l *= 1.10
        if "Ataque" in b: l_v *= 0.80

    # FACTOR CANCHA Y CLIMA
    if team_l['pitch'] == "Sintético" or clima_l == "Extremo":
        l_l *= 1.30; l_v *= 0.75

    # MÉTRICAS GENERALES
    st.success(f"### Pronóstico Pro: {loc} vs {vis}")
    m1, m2, m3, m4 = st.columns(4)
    total_exp = l_l + l_v
    m1.metric("Goles Totales Est.", f"{total_exp:.2f}")
    m2.metric("Córners Est.", f"{(total_exp)*2.9:.1f}")
    m3.metric("Ambos Anotan", f"{(1-poisson.pmf(0, l_l))*(1-poisson.pmf(0, l_v))*100:.1f}%")
    m4.metric("Gol 1T", f"{(1-(poisson.pmf(0, l_l*0.35)*poisson.pmf(0, l_v*0.35)))*100:.1f}%")

    # MARCADOR MAESTRO (EXACTO)
    res_m = []
    for gl in range(6):
        for gv in range(6):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            res_m.append({"m": f"{gl}-{gv}", "p": p * 100})
    best = sorted(res_m, key=lambda x: x['p'], reverse=True)[:5]

    st.subheader("🎯 Marcadores Más Probables (Marcador Maestro)")
    m_cols = st.columns(5)
    for idx, m in enumerate(best):
        with m_cols[idx]:
            if idx == 0: st.warning(f"👑 **MAESTRO**\n{m['m']}\n{m['p']:.1f}%")
            else: st.info(f"**{m['m']}**\n{m['p']:.1f}%")

    # ANÁLISIS POR TRAMOS
    st.subheader("⏱️ Probabilidad de Gol por Tramo (Cada 15 min)")
    tramos = ["0-15'", "16-30'", "31-45'", "46-60'", "61-75'", "76-90'"]
    probs = []
    for i in range(6):
        idx_p = 0 if i < 2 else (1 if i < 4 else 2)
        p_val = ((l_l * team_l["pattern"][idx_p]) + (l_v * team_v["pattern"][idx_p])) / 6
        probs.append(round(p_val * 100, 1))
    
    t_cols = st.columns(6)
    for i, col in enumerate(t_cols):
        col.metric(tramos[i], f"{probs[i]}%")

    # ALERTA DE GOL INMINENTE (RESALTADA)
    st.error(f"🚨 ALERTA DE GOL INMINENTE: Máxima presión detectada en el tramo {tramos[probs.index(max(probs))]}.")

    # GRÁFICA DE PRESIÓN
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tramos, y=probs, mode='lines+markers', name='xG Flow', line=dict(color='orange', width=4)))
    st.plotly_chart(fig, use_container_width=True)

# --- AUDITORÍA ---
st.divider()
st.subheader("📊 Auditoría de Rendimiento vs Predicción")
c_aud1, c_aud2 = st.columns(2)
with c_aud1:
    res_real = st.text_input("Ingresar Resultado Real Final (ej. 3-1)")
with c_aud2:
    if st.button("⚖️ Guardar y Auditar"):
        st.session_state.historial_global.append({"Partido": f"{loc} vs {vis}", "Real": res_real})
        st.success("Resultado guardado para calibrar la inteligencia del Tier.")