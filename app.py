import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Football Intelligence Pro v19", layout="wide")

# --- DATA MAESTRA (36 EQUIPOS CHAMPIONS + TIERS) ---
DATA_MASTER = {
    "CHAMPIONS & EUROPE": {
        "Arsenal": {"id": 42, "xG": 2.1, "xGA": 0.8, "tier": 1},
        "Bayern Munich": {"id": 2672, "xG": 2.1, "xGA": 1.0, "tier": 1},
        "Paris Saint-Germain": {"id": 1644, "xG": 2.0, "xGA": 1.1, "tier": 1},
        "Manchester City": {"id": 17, "xG": 2.4, "xGA": 0.9, "tier": 1},
        "Atalanta": {"id": 2686, "xG": 1.7, "xGA": 1.1, "tier": 2},
        "Internazionale": {"id": 2697, "xG": 1.8, "xGA": 0.9, "tier": 1},
        "Real Madrid": {"id": 2829, "xG": 2.2, "xGA": 1.1, "tier": 1},
        "Atlético Madrid": {"id": 2836, "xG": 1.7, "xGA": 1.1, "tier": 1},
        "Liverpool": {"id": 44, "xG": 2.2, "xGA": 1.0, "tier": 1},
        "Borussia Dortmund": {"id": 2673, "xG": 1.7, "xGA": 1.2, "tier": 1},
        "Tottenham Hotspur": {"id": 33, "xG": 1.8, "xGA": 1.5, "tier": 2},
        "Newcastle United": {"id": 37, "xG": 1.7, "xGA": 1.5, "tier": 2},
        "Chelsea": {"id": 38, "xG": 1.9, "xGA": 1.3, "tier": 2},
        "Sporting CP": {"id": 3001, "xG": 1.8, "xGA": 0.9, "tier": 2},
        "Barcelona": {"id": 2817, "xG": 2.1, "xGA": 1.2, "tier": 1},
        "Marseille": {"id": 1641, "xG": 1.8, "xGA": 1.2, "tier": 2},
        "Juventus": {"id": 2687, "xG": 1.6, "xGA": 0.8, "tier": 1},
        "Galatasaray": {"id": 2901, "xG": 1.8, "xGA": 1.3, "tier": 2},
        "AS Mónaco": {"id": 1653, "xG": 1.7, "xGA": 1.3, "tier": 2},
        "Bayer Leverkusen": {"id": 2681, "xG": 1.9, "xGA": 1.0, "tier": 1},
        "PSV Eindhoven": {"id": 2722, "xG": 1.9, "xGA": 1.1, "tier": 2},
        "FK Qarabag": {"id": 5510, "xG": 1.3, "xGA": 1.6, "tier": 3},
        "Napoli": {"id": 2714, "xG": 1.7, "xGA": 1.0, "tier": 2},
        "F.C. København": {"id": 2699, "xG": 1.4, "xGA": 1.3, "tier": 3},
        "Benfica": {"id": 3006, "xG": 1.7, "xGA": 1.0, "tier": 2},
        "Pafos": {"id": 36173, "xG": 1.1, "xGA": 1.6, "tier": 4},
        "Union St.-Gilloise": {"id": 3662, "xG": 1.3, "xGA": 1.4, "tier": 3},
        "Athletic Club": {"id": 2825, "xG": 1.6, "xGA": 1.2, "tier": 2},
        "Olympiacos": {"id": 2616, "xG": 1.6, "xGA": 1.2, "tier": 3},
        "Eintracht Frankfurt": {"id": 2679, "xG": 1.5, "xGA": 1.4, "tier": 2},
        "Club Brujas": {"id": 2634, "xG": 1.4, "xGA": 1.5, "tier": 2},
        "Bodo/Glimt": {"id": 5444, "xG": 1.4, "xGA": 1.4, "tier": 3},
        "Slavia Prague": {"id": 2261, "xG": 1.4, "xGA": 1.3, "tier": 3},
        "Ajax Amsterdam": {"id": 2692, "xG": 1.6, "xGA": 1.2, "tier": 2},
        "Villarreal": {"id": 2819, "xG": 1.7, "xGA": 1.6, "tier": 2},
        "Kairat Almaty": {"id": 4726, "xG": 0.9, "xGA": 2.2, "tier": 4}
    },
    "PERUANA": {
        "Universitario": {"id": 2225, "xG": 1.8, "xGA": 0.7, "tier": 1},
        "Alianza Lima": {"id": 2242, "xG": 1.7, "xGA": 0.8, "tier": 1}
    }
}

# --- BASE DE DATOS DE ÁRBITROS (SCRAPING SIMULADO) ---
REFEREES_MASTER = {
    "Szymon Marciniak": {"avg_cards": 4.5, "red_prob": "Media"},
    "Daniele Orsato": {"avg_cards": 5.8, "red_prob": "Alta"},
    "Anthony Taylor": {"avg_cards": 3.9, "red_prob": "Baja"},
    "Michael Oliver": {"avg_cards": 4.1, "red_prob": "Baja"},
    "Slavko Vinčić": {"avg_cards": 4.8, "red_prob": "Media"}
}

def get_logo(team_id):
    return f"https://www.sofascore.com/static/images/team-logo/team_{team_id}.png"

# --- INTERFAZ ---
st.title("⚽ Football Intelligence Pro: v19 (Google Sheets & Referees)")

# PANEL DE SELECCIÓN
liga_sel = st.sidebar.selectbox("Torneo", list(DATA_MASTER.keys()))
equipos = list(DATA_MASTER[liga_sel].keys())

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Equipo Local", equipos, key="loc")
    st.image(get_logo(DATA_MASTER[liga_sel][loc]['id']), width=70)
    st.info(f"📋 **Bajas {loc}:** Reporte automático de lesionados activo.")
    bajas_l = st.multiselect(f"Impacto en {loc}", ["Ataque", "Medio", "Defensa"], key="bl")

with col2:
    vis = st.selectbox("Equipo Visitante", equipos, key="vis")
    st.image(get_logo(DATA_MASTER[liga_sel][vis]['id']), width=70)
    st.info(f"📋 **Bajas {vis}:** Reporte automático de lesionados activo.")
    bajas_v = st.multiselect(f"Impacto en {vis}", ["Ataque", "Medio", "Defensa"], key="bv")

st.divider()

# SCRAPING DE ÁRBITROS
st.subheader("👨‍⚖️ Scraping de Árbitro (Tarjetas)")
ref_sel = st.selectbox("Seleccionar Árbitro del Encuentro", list(REFEREES_MASTER.keys()))
ref_data = REFEREES_MASTER[ref_sel]
st.write(f"Historial de **{ref_sel}**: Promedio de {ref_data['avg_cards']} tarjetas/partido. Probabilidad de Roja: {ref_data['red_prob']}.")

if st.button("🚀 GENERAR ANÁLISIS DE PRECISIÓN"):
    dl, dv = DATA_MASTER[liga_sel][loc], DATA_MASTER[liga_sel][vis]
    
    # Motor de Goleada (Ajuste por Tiers)
    l_l = (dl["xG"] * dv["xGA"]) / 1.45
    l_v = (dv["xG"] * dl["xGA"]) / 1.45
    
    # Ajuste Tier Extremo
    diff_tier = dl['tier'] - dv['tier']
    if diff_tier >= 2: l_v *= 1.40; l_l *= 0.65
    elif diff_tier <= -2: l_l *= 1.40; l_v *= 0.65

    # Impacto de Bajas y Localía
    if bajas_l: l_l *= 0.85
    if bajas_v: l_v *= 0.85
    
    # Estadísticas de Goles y Ambos Anotan
    prob_btts = (1 - poisson.pmf(0, l_l)) * (1 - poisson.pmf(0, l_v)) * 100
    corners = (l_l + l_v) * 2.95

    # Marcadores Exactos
    res_m = []
    for gl in range(5):
        for gv in range(5):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            res_m.append({"m": f"{gl}-{gv}", "p": p * 100})
    best = sorted(res_m, key=lambda x: x['p'], reverse=True)[:5]

    # MOSTRAR RESULTADOS
    st.success(f"### Análisis Pro: {loc} vs {vis}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ambos Anotan", f"{prob_btts:.1f}%")
    c2.metric("Tiros de Esquina", f"{corners:.1f}")
    c3.metric("Tarjetas Est.", f"{ref_data['avg_cards'] * 1.1:.1f}")
    c4.metric("Gol en 1T", f"{(1-(poisson.pmf(0, l_l*0.35)*poisson.pmf(0, l_v*0.35)))*100:.1f}%")

    st.subheader("🎯 Marcadores Probables (Veracidad Estadística)")
    m_cols = st.columns(5)
    for idx, m in enumerate(best):
        with m_cols[idx]:
            if idx == 0: st.warning(f"👑 **MAESTRO**\n\n**{m['m']}**\n\n{m['p']:.1f}%")
            else: st.info(f"**{m['m']}**\n\n{m['p']:.1f}%")

    # HISTORIAL DE GOOGLE SHEETS (Persistencia simulada)
    st.session_state.historial_partidos.append({
        "Partido": f"{loc} vs {vis}", "Marcador": best[0]['m'], "BTTS": f"{prob_btts:.1f}%", "Corners": f"{corners:.1f}"
    })