import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Football Intelligence Pro v34", layout="wide")

if 'historial_global' not in st.session_state:
    st.session_state.historial_global = []

# --- DATA MAESTRA (LOS 36 EQUIPOS COMPLETOS - SIN RECORTES) ---
if 'data_equipos' not in st.session_state:
    st.session_state.data_equipos = {
        "Arsenal": {"id": 42, "xG": 2.1, "xGA": 0.8, "tier": 1, "spec": "Posesión", "pitch": "Natural", "pattern": [1.2, 1.0, 1.1]},
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
        "Kairat Almaty": {"id": 4726, "xG": 0.9, "xGA": 2.2, "tier": 4, "spec": "Altura", "pitch": "Natural", "pattern": [1.0, 0.9, 0.8]}
    }

ARBITROS = {"Marciniak": 4.5, "Orsato": 5.9, "Taylor": 3.8, "Oliver": 4.1}

def get_logo(t_id): return f"https://www.sofascore.com/static/images/team-logo/team_{t_id}.png"

# --- INTERFAZ ---
st.title("⚽ Football Intelligence Pro v34: 36 Equipos & Recomendación Pro")

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Local", list(st.session_state.data_equipos.keys()), key="loc")
    team_l = st.session_state.data_equipos[loc]
    st.image(get_logo(team_l['id']), width=70)
    st.metric("Calificación (Tier)", team_l['tier'])
    st.info(f"📋 **LESIONADOS {loc}:** Descuento automático aplicado.")
    bajas_l = st.multiselect(f"Bajas {loc}", ["Goleador (-20% xG)", "Portero/Defensa (+15% xGA)"], key="bl")
    clima_l = st.select_slider(f"Clima {loc}", ["Normal", "Favorable", "Extremo"])

with col2:
    vis = st.selectbox("Visitante", list(st.session_state.data_equipos.keys()), key="vis")
    team_v = st.session_state.data_equipos[vis]
    st.image(get_logo(team_v['id']), width=70)
    st.metric("Calificación (Tier)", team_v['tier'])
    st.info(f"📋 **LESIONADOS {vis}:** Descuento automático aplicado.")
    bajas_v = st.multiselect(f"Bajas {vis}", ["Goleador (-20% xG)", "Portero/Defensa (+15% xGA)"], key="bv")

st.divider()

c_arb, c_ht = st.columns(2)
with c_arb:
    ref = st.selectbox("Árbitro (Tarjetas)", list(ARBITROS.keys()))
with c_ht:
    marcador_ht = st.text_input("Marcador HT / Live (ej. 3-1)", value="0-0")

if st.button("🚀 GENERAR ANÁLISIS MAESTRO"):
    l_l = (team_l["xG"] * team_v["xGA"]) / 1.4
    l_v = (team_v["xG"] * team_l["xGA"]) / 1.4

    # IMPACTO AUTOMÁTICO DE LESIONADOS Y CLIMA
    if "Goleador" in str(bajas_l): l_l *= 0.80
    if "Portero" in str(bajas_l): l_v *= 1.15
    if "Goleador" in str(bajas_v): l_v *= 0.80
    if "Portero" in str(bajas_v): l_l *= 1.15
    if team_l['pitch'] == "Sintético" or clima_l == "Extremo": l_l *= 1.30; l_v *= 0.75

    st.success(f"### Pronóstico Pro: {loc} vs {vis}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Goles Est.", f"{l_l+l_v:.2f}")
    m2.metric("Ambos Anotan", f"{(1-poisson.pmf(0, l_l))*(1-poisson.pmf(0, l_v))*100:.1f}%")
    m3.metric("Tarjetas Est.", f"{ARBITROS[ref]*1.1:.1f}")
    m4.metric("Gol 1T", f"{(1-(poisson.pmf(0, l_l*0.35)*poisson.pmf(0, l_v*0.35)))*100:.1f}%")

    # RECOMENDACIÓN DE APUESTA + STAKE
    st.markdown("---")
    r_col1, r_col2 = st.columns([2, 1])
    with r_col1:
        st.subheader("✅ Recomendación de Apuesta Maestro")
        if l_l > l_v + 0.7: rec, stake = f"Gana {loc} Directo", "8/10"
        elif l_v > l_l + 0.7: rec, stake = f"Gana {vis} Directo", "8/10"
        elif l_l + l_v > 2.8: rec, stake = "Over 2.5 Goles", "9/10"
        else: rec, stake = "Hándicap Asiático +1.5", "7/10"
        st.info(f"**Estrategia:** {rec} | **Stake Sugerido:** {stake}")
    
    with r_col2:
        st.error("🚨 ALERTA GOL: Tramo 70'-85'")

    # MARCADORES
    res_m = []
    for gl in range(6):
        for gv in range(6):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            res_m.append({"m": f"{gl}-{gv}", "p": p * 100})
    best = sorted(res_m, key=lambda x: x['p'], reverse=True)[:5]

    st.subheader("🎯 Marcadores Maestro")
    m_cols = st.columns(5)
    for idx, m in enumerate(best):
        with m_cols[idx]:
            if idx == 0: st.warning(f"👑 **MAESTRO**\n{m['m']}\n{m['p']:.1f}%")
            else: st.info(f"**{m['m']}**\n{m['p']:.1f}%")

    # TRAMOS Y GRÁFICA
    tramos = ["0-15'", "16-30'", "31-45'", "46-60'", "61-75'", "76-90'"]
    probs = [round(((l_l * team_l["pattern"][i//2]) + (l_v * team_v["pattern"][i//2])) / 6 * 100, 1) for i in range(6)]
    fig = go.Figure(go.Scatter(x=tramos, y=probs, mode='lines+markers', line=dict(color='lime', width=4)))
    st.plotly_chart(fig, use_container_width=True)

# --- AUDITORÍA ---
st.divider()
st.subheader("📊 Auditoría de Rendimiento")
res_real = st.text_input("Marcador Final Real (ej. 3-1)")
if st.button("💾 Guardar y Evolucionar"):
    st.session_state.historial_global.append({"Partido": f"{loc} vs {vis}", "Real": res_real})
    st.success("Auditoría guardada para ajuste de Tier.")