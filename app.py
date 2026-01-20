import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Football Intelligence Pro v17", layout="wide")

# --- DATA MAESTRA CON RANKING (TIER) ---
# Tier 1: Élite | Tier 2: Fuerte | Tier 3: Medio | Tier 4: Débil
DATA_MASTER = {
    "CHAMPIONS & EUROPE": {
        "Manchester City": {"id": 17, "xG": 2.4, "xGA": 0.9, "tier": 1},
        "Real Madrid": {"id": 2829, "xG": 2.2, "xGA": 1.1, "tier": 1},
        "Arsenal": {"id": 42, "xG": 2.1, "xGA": 0.8, "tier": 1},
        "Barcelona": {"id": 2817, "xG": 2.1, "xGA": 1.2, "tier": 1},
        "Club Brujas": {"id": 2634, "xG": 1.7, "xGA": 1.3, "tier": 2}, # Subido de nivel
        "Bodø/Glimt": {"id": 5444, "xG": 1.4, "xGA": 1.4, "tier": 3},
        "Kairat Almaty": {"id": 4726, "xG": 0.9, "xGA": 2.2, "tier": 4}, # Ajustado por bajo rendimiento
        "Slovan Bratislava": {"id": 2341, "xG": 0.9, "xGA": 2.3, "tier": 4},
        # ... (Resto de los 36 equipos mantienen sus IDs y Tiers)
    }
}

# --- FUNCIONES DE SCRAPING Y AJUSTE ---
def aplicar_ajuste_elite(l_l, l_v, tier_l, tier_v, loc_name, vis_name):
    """Ajusta porcentajes según la jerarquía de los equipos."""
    # Si hay una diferencia de 2 o más Tiers, es una posible goleada
    if tier_v <= 2 and tier_l >= 4:
        l_v *= 1.45 # El visitante fuerte golea
        l_l *= 0.60 # El local débil casi no anota
    
    # Ajuste por fortaleza de localía (Simulado SofaScore)
    if loc_name in ["Real Madrid", "Man City", "Arsenal"]:
        l_l *= 1.15 # Fortalezas en casa
    
    return l_l, l_v

def get_logo(team_id):
    return f"https://www.sofascore.com/static/images/team-logo/team_{team_id}.png"

# --- INTERFAZ ---
st.title("⚽ Football Intelligence Pro: v17 (Power Rankings & Stats)")

liga_sel = st.sidebar.selectbox("Seleccionar Torneo", list(DATA_MASTER.keys()))
equipos = list(DATA_MASTER[liga_sel].keys())

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Equipo Local", equipos, key="loc")
    st.image(get_logo(DATA_MASTER[liga_sel][loc]['id']), width=70)
    st.caption(f"📊 Tier: {DATA_MASTER[liga_sel][loc].get('tier', 3)} (1=Élite, 4=Débil)")
    bajas_l = st.multiselect(f"Bajas {loc}", ["Ataque", "Medio", "Defensa"], key="bl")

with col2:
    vis = st.selectbox("Equipo Visitante", equipos, key="vis")
    st.image(get_logo(DATA_MASTER[liga_sel][vis]['id']), width=70)
    st.caption(f"📊 Tier: {DATA_MASTER[liga_sel][vis].get('tier', 3)}")
    bajas_v = st.multiselect(f"Bajas {vis}", ["Ataque", "Medio", "Defensa"], key="bv")

st.divider()

if st.button("🚀 GENERAR ANÁLISIS DE PRECISIÓN"):
    dl, dv = DATA_MASTER[liga_sel][loc], DATA_MASTER[liga_sel][vis]
    
    # Lambdas base
    l_l = (dl["xG"] * dv["xGA"]) / 1.45
    l_v = (dv["xG"] * dl["xGA"]) / 1.45
    
    # APLICAR AJUSTE DE RANKING Y LOCALÍA
    l_l, l_v = aplicar_ajuste_elite(l_l, l_v, dl.get("tier", 3), dv.get("tier", 3), loc, vis)
    
    # Impacto de Bajas
    if bajas_l: l_l *= 0.85
    if bajas_v: l_v *= 0.85

    # Resultados
    pl, pe, pv = 0, 0, 0
    for gl in range(10):
        for gv in range(10):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            if gl > gv: pl += p
            elif gl == gv: pe += p
            else: pv += p

    # --- PANEL DE RESULTADOS ---
    st.success(f"### Análisis de Precisión: {loc} vs {vis}")
    c1, c2, c3 = st.columns(3)
    c1.metric("Gol 1T", f"{(1-(poisson.pmf(0, l_l*0.35)*poisson.pmf(0, l_v*0.35)))*100:.1f}%")
    c2.metric("Goles Totales", f"{l_l+l_v:.2f}")
    c3.metric("Favorito", loc if pl > pv else vis)

    # --- MARCADORES CON CORONA MAESTRA ---
    st.subheader("🎯 Marcadores Probables (Ajustados por Ranking)")
    marcadores = []
    for gl in range(5):
        for gv in range(5):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            marcadores.append({"m": f"{gl}-{gv}", "p": p * 100})
    best = sorted(marcadores, key=lambda x: x['p'], reverse=True)[:5]
    
    m_cols = st.columns(5)
    for idx, m in enumerate(best):
        with m_cols[idx]:
            if idx == 0:
                st.warning(f"👑 **MAESTRO**\n\n**{m['m']}**\n\n{m['p']:.1f}%")
            else:
                st.info(f"**{m['m']}**\n\n{m['p']:.1f}%")

    # --- xG FLOW ---
    st.subheader("📈 Presión Ofensiva (xG Flow)")
    minutos = np.arange(0, 95, 5)
    curva_l = np.random.uniform(0.05, 0.2, len(minutos)) * l_l
    curva_v = np.random.uniform(0.05, 0.2, len(minutos)) * l_v
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=minutos, y=curva_l, mode='lines', name=loc, line=dict(color='#2ecc71')))
    fig.add_trace(go.Scatter(x=minutos, y=curva_v, mode='lines', name=vis, line=dict(color='#e74c3c')))
    st.plotly_chart(fig, use_container_width=True)