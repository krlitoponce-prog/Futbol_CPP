import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Football Intel Pro v14", layout="wide")

# --- DATA MAESTRA (Verificada: 36 Equipos Champions/Europa) ---
DATA_MASTER = {
    "CHAMPIONS & EUROPE": {
        "Arsenal": {"id": 42, "xG": 2.1, "xGA": 0.8}, "Bayern Munich": {"id": 2672, "xG": 2.1, "xGA": 1.0},
        "Paris Saint-Germain": {"id": 1644, "xG": 2.0, "xGA": 1.1}, "Manchester City": {"id": 17, "xG": 2.4, "xGA": 0.9},
        "Atalanta": {"id": 2686, "xG": 1.7, "xGA": 1.1}, "Internazionale": {"id": 2697, "xG": 1.8, "xGA": 0.9},
        "Real Madrid": {"id": 2829, "xG": 2.2, "xGA": 1.1}, "Atlético Madrid": {"id": 2836, "xG": 1.7, "xGA": 1.1},
        "Liverpool": {"id": 44, "xG": 2.2, "xGA": 1.0}, "Borussia Dortmund": {"id": 2673, "xG": 1.7, "xGA": 1.2},
        "Tottenham Hotspur": {"id": 33, "xG": 1.8, "xGA": 1.5}, "Newcastle United": {"id": 37, "xG": 1.7, "xGA": 1.5},
        "Chelsea": {"id": 38, "xG": 1.9, "xGA": 1.3}, "Sporting CP": {"id": 3001, "xG": 1.8, "xGA": 0.9},
        "Barcelona": {"id": 2817, "xG": 2.1, "xGA": 1.2}, "Marseille": {"id": 1641, "xG": 1.8, "xGA": 1.2},
        "Juventus": {"id": 2687, "xG": 1.6, "xGA": 0.8}, "Galatasaray": {"id": 2901, "xG": 1.8, "xGA": 1.3},
        "AS Mónaco": {"id": 1653, "xG": 1.7, "xGA": 1.3}, "Bayer Leverkusen": {"id": 2681, "xG": 1.9, "xGA": 1.0},
        "PSV Eindhoven": {"id": 2722, "xG": 1.9, "xGA": 1.1}, "FK Qarabag": {"id": 5510, "xG": 1.3, "xGA": 1.6},
        "Napoli": {"id": 2714, "xG": 1.7, "xGA": 1.0}, "F.C. København": {"id": 2699, "xG": 1.4, "xGA": 1.3},
        "Benfica": {"id": 3006, "xG": 1.7, "xGA": 1.0}, "Pafos": {"id": 36173, "xG": 1.1, "xGA": 1.6},
        "Union St.-Gilloise": {"id": 3662, "xG": 1.3, "xGA": 1.4}, "Athletic Club": {"id": 2825, "xG": 1.6, "xGA": 1.2},
        "Olympiacos": {"id": 2616, "xG": 1.6, "xGA": 1.2}, "Eintracht Frankfurt": {"id": 2679, "xG": 1.5, "xGA": 1.4},
        "Club Brujas": {"id": 2634, "xG": 1.4, "xGA": 1.5}, "Bodo/Glimt": {"id": 5444, "xG": 1.4, "xGA": 1.4},
        "Slavia Prague": {"id": 2261, "xG": 1.4, "xGA": 1.3}, "Ajax Amsterdam": {"id": 2692, "xG": 1.6, "xGA": 1.2},
        "Villarreal": {"id": 2819, "xG": 1.7, "xGA": 1.6}, "Kairat Almaty": {"id": 4726, "xG": 1.2, "xGA": 1.5}
    },
    "INGLESA": { "Arsenal": {"id": 42, "xG": 2.1, "xGA": 0.8}, "Man City": {"id": 17, "xG": 2.3, "xGA": 0.9} },
    "ESPAÑOLA": { "Barcelona": {"id": 2817, "xG": 2.2, "xGA": 1.2}, "Real Madrid": {"id": 2829, "xG": 2.3, "xGA": 1.1} },
    "PERUANA": { "Universitario": {"id": 2225, "xG": 1.8, "xGA": 0.7} }
}

def get_logo(team_id):
    return f"https://www.sofascore.com/static/images/team-logo/team_{team_id}.png"

def motor_calculo(l_l, l_v):
    prob_btts = (1 - poisson.pmf(0, l_l)) * (1 - poisson.pmf(0, l_v)) * 100
    marcadores = []
    for gl in range(5):
        for gv in range(5):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            marcadores.append({"m": f"{gl}-{gv}", "p": p * 100})
    return {"btts": prob_btts, "marcadores": sorted(marcadores, key=lambda x: x['p'], reverse=True)[:5]}

# --- INTERFAZ ---
st.title("⚽ Football Intelligence Global: v14 (Radar de Valor)")

liga_sel = st.sidebar.selectbox("Selecciona Torneo", list(DATA_MASTER.keys()))
equipos = list(DATA_MASTER[liga_sel].keys())

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Equipo Local", equipos, key="loc")
    st.image(get_logo(DATA_MASTER[liga_sel][loc]['id']), width=80)
    bajas_l = st.multiselect(f"Bajas: {loc}", ["Goleador", "Medio", "Defensa"], key="bl")

with col2:
    vis = st.selectbox("Equipo Visitante", equipos, key="vis")
    st.image(get_logo(DATA_MASTER[liga_sel][vis]['id']), width=80)
    bajas_v = st.multiselect(f"Bajas: {vis}", ["Goleador", "Medio", "Defensa"], key="bv")

# Simulador de Cuota de Mercado para el Radar
st.sidebar.divider()
bookie_odds = st.sidebar.number_input("Cuota de la Casa (Local)", value=2.0, step=0.1)

if st.button("🚀 GENERAR ANÁLISIS"):
    dl, dv = DATA_MASTER[liga_sel][loc], DATA_MASTER[liga_sel][vis]
    xg_l, xga_l = dl["xG"], dl["xGA"]
    xg_v, xga_v = dv["xG"], dv["xGA"]
    
    # Aplicar impacto de bajas
    for b in bajas_l:
        if b == "Goleador": xg_l *= 0.85
        if b == "Defensa": xga_l *= 1.15
    for b in bajas_v:
        if b == "Goleador": xg_v *= 0.85
        if b == "Defensa": xga_v *= 1.15

    l_l, l_v = (xg_l * xga_v)/1.45, (xg_v * xga_l)/1.45
    res = motor_calculo(l_l, l_v)
    
    # Probabilidades 1X2
    pl, pe, pv = 0, 0, 0
    for gl in range(10):
        for gv in range(10):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            if gl > gv: pl += p
            elif gl == gv: pe += p
            else: pv += p

    # --- ALERTA DE VALOR ---
    fair_odds = 1/pl
    edge = (bookie_odds / fair_odds) - 1
    
    st.subheader("📡 Alerta de Valor (Radar)")
    if edge > 0.10:
        st.success(f"🔥 OPORTUNIDAD DE VALOR: El mercado paga {bookie_odds}, nuestra cuota es {fair_odds:.2f}. Ventaja: {edge*100:.1f}%")
    else:
        st.error(f"⚠️ SIN VALOR: La cuota de la casa ({bookie_odds}) es menor o muy cercana a nuestra cuota justa ({fair_odds:.2f}).")

    # Gráfico y Marcadores
    c_pie, c_met = st.columns([1, 1.5])
    with c_pie:
        fig = go.Figure(data=[go.Pie(labels=['Local', 'Empate', 'Visitante'], values=[pl, pe, pv], hole=.3)])
        st.plotly_chart(fig, use_container_width=True)

    with c_met:
        st.success(f"### {loc} vs {vis}")
        st.metric("Goles Esperados Totales", f"{l_l+l_v:.2f}")
        
    st.subheader("🎯 Top 5 Marcadores Exactos")
    m_cols = st.columns(5)
    for idx, m in enumerate(res['marcadores']):
        with m_cols[idx]:
            st.info(f"**{m['m']}**\n\n{m['p']:.1f}%")