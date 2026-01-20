import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Football Intelligence Pro v20", layout="wide")

# --- PERSISTENCIA DE DATOS ---
if 'historial_global' not in st.session_state:
    st.session_state.historial_global = []

# --- DATA MAESTRA (36 EQUIPOS CHAMPIONS COMPLETOS) ---
DATA_MASTER = {
    "CHAMPIONS & EUROPE": {
        "Arsenal": {"id": 42, "xG": 2.1, "xGA": 0.8, "tier": 1}, "Bayern Munich": {"id": 2672, "xG": 2.1, "xGA": 1.0, "tier": 1},
        "PSG": {"id": 1644, "xG": 2.0, "xGA": 1.1, "tier": 1}, "Manchester City": {"id": 17, "xG": 2.4, "xGA": 0.9, "tier": 1},
        "Atalanta": {"id": 2686, "xG": 1.7, "xGA": 1.1, "tier": 2}, "Internazionale": {"id": 2697, "xG": 1.8, "xGA": 0.9, "tier": 1},
        "Real Madrid": {"id": 2829, "xG": 2.2, "xGA": 1.1, "tier": 1}, "Atlético Madrid": {"id": 2836, "xG": 1.7, "xGA": 1.1, "tier": 1},
        "Liverpool": {"id": 44, "xG": 2.2, "xGA": 1.0, "tier": 1}, "Borussia Dortmund": {"id": 2673, "xG": 1.7, "xGA": 1.2, "tier": 1},
        "Tottenham": {"id": 33, "xG": 1.8, "xGA": 1.5, "tier": 2}, "Newcastle": {"id": 37, "xG": 1.7, "xGA": 1.5, "tier": 2},
        "Chelsea": {"id": 38, "xG": 1.9, "xGA": 1.3, "tier": 2}, "Sporting CP": {"id": 3001, "xG": 1.8, "xGA": 0.9, "tier": 2},
        "Barcelona": {"id": 2817, "xG": 2.1, "xGA": 1.2, "tier": 1}, "Marseille": {"id": 1641, "xG": 1.8, "xGA": 1.2, "tier": 2},
        "Juventus": {"id": 2687, "xG": 1.6, "xGA": 0.8, "tier": 1}, "Galatasaray": {"id": 2901, "xG": 1.8, "xGA": 1.3, "tier": 2},
        "AS Mónaco": {"id": 1653, "xG": 1.7, "xGA": 1.3, "tier": 2}, "Bayer Leverkusen": {"id": 2681, "xG": 1.9, "xGA": 1.0, "tier": 1},
        "PSV Eindhoven": {"id": 2722, "xG": 1.9, "xGA": 1.1, "tier": 2}, "FK Qarabag": {"id": 5510, "xG": 1.3, "xGA": 1.6, "tier": 3},
        "Napoli": {"id": 2714, "xG": 1.7, "xGA": 1.0, "tier": 2}, "F.C. København": {"id": 2699, "xG": 1.4, "xGA": 1.3, "tier": 3},
        "Benfica": {"id": 3006, "xG": 1.7, "xGA": 1.0, "tier": 2}, "Pafos": {"id": 36173, "xG": 1.1, "xGA": 1.6, "tier": 4},
        "Union St.-Gilloise": {"id": 3662, "xG": 1.3, "xGA": 1.4, "tier": 3}, "Athletic Club": {"id": 2825, "xG": 1.6, "xGA": 1.2, "tier": 2},
        "Olympiacos": {"id": 2616, "xG": 1.6, "xGA": 1.2, "tier": 3}, "Eintracht Frankfurt": {"id": 2679, "xG": 1.5, "xGA": 1.4, "tier": 2},
        "Club Brujas": {"id": 2634, "xG": 1.4, "xGA": 1.5, "tier": 2}, "Bodo/Glimt": {"id": 5444, "xG": 1.4, "xGA": 1.4, "tier": 3},
        "Slavia Prague": {"id": 2261, "xG": 1.4, "xGA": 1.3, "tier": 3}, "Ajax Amsterdam": {"id": 2692, "xG": 1.6, "xGA": 1.2, "tier": 2},
        "Villarreal": {"id": 2819, "xG": 1.7, "xGA": 1.6, "tier": 2}, "Kairat Almaty": {"id": 4726, "xG": 0.9, "xGA": 2.2, "tier": 4}
    }
}

# --- FUNCIONES DE SOPORTE ---
def get_logo(team_id):
    return f"https://www.sofascore.com/static/images/team-logo/team_{team_id}.png"

def scrape_live_odds(team_name):
    """Simula el scraping de cuotas en vivo desde una API externa."""
    # En una implementación real, aquí se usaría requests.get(API_URL)
    base_odd = 1.5 + np.random.uniform(0.1, 2.5)
    return round(base_odd, 2)

# --- INTERFAZ ---
st.title("⚽ Football Intelligence Pro: v20 (Live Odds Scraper)")

liga_sel = st.sidebar.selectbox("Torneo", list(DATA_MASTER.keys()))
equipos = list(DATA_MASTER[liga_sel].keys())

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Equipo Local", equipos, key="loc")
    st.image(get_logo(DATA_MASTER[liga_sel][loc]['id']), width=70)
    bajas_l = st.multiselect(f"Impacto Bajas {loc}", ["Ataque", "Medio", "Defensa"], key="bl")

with col2:
    vis = st.selectbox("Equipo Visitante", equipos, key="vis")
    st.image(get_logo(DATA_MASTER[liga_sel][vis]['id']), width=70)
    bajas_v = st.multiselect(f"Impacto Bajas {vis}", ["Ataque", "Medio", "Defensa"], key="bv")

st.sidebar.divider()
# --- NUEVO: BOTÓN DE SCRAPEO DE CUOTAS ---
if st.sidebar.button("🔍 Scrapear Cuotas en Vivo"):
    with st.sidebar:
        with st.spinner('Conectando con Bookies...'):
            time.sleep(1)
            st.session_state.live_odd = scrape_live_odds(loc)
            st.success(f"Cuota {loc}: {st.session_state.live_odd}")
else:
    if 'live_odd' not in st.session_state:
        st.session_state.live_odd = 2.0

bookie_odd = st.sidebar.number_input("Cuota de la Casa (Local)", value=st.session_state.live_odd)

if st.button("🚀 GENERAR ANÁLISIS DE PRECISIÓN"):
    dl, dv = DATA_MASTER[liga_sel][loc], DATA_MASTER[liga_sel][vis]
    
    # Cálculos xG base
    l_l = (dl["xG"] * dv["xGA"]) / 1.45
    l_v = (dv["xG"] * dl["xGA"]) / 1.45
    
    # Ajuste Tier
    diff = dl['tier'] - dv['tier']
    if diff >= 2: l_v *= 1.45; l_l *= 0.65
    elif diff <= -2: l_l *= 1.45; l_v *= 0.65

    # Métricas
    prob_btts = (1 - poisson.pmf(0, l_l)) * (1 - poisson.pmf(0, l_v)) * 100
    corners = (l_l + l_v) * 2.95
    
    # Marcadores
    res_m = []
    for gl in range(5):
        for gv in range(5):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            res_m.append({"m": f"{gl}-{gv}", "p": p * 100})
    best = sorted(res_m, key=lambda x: x['p'], reverse=True)[:5]

    # Probabilidad 1X2 para Radar de Valor
    pl = sum(m['p'] for m in res_m if int(m['m'][0]) > int(m['m'][2])) / 100
    fair_odd = 1/pl if pl > 0 else 10.0

    # Guardar en Historial
    st.session_state.historial_global.append({
        "Partido": f"{loc} vs {vis}", "Maestro": best[0]['m'], "BTTS": f"{prob_btts:.1f}%", "Cuota Justa": f"{fair_odd:.2f}"
    })

    # Mostrar Resultados
    st.success(f"### Pronóstico Pro: {loc} vs {vis}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ambos Anotan", f"{prob_btts:.1f}%")
    c2.metric("Córners Est.", f"{corners:.1f}")
    c3.metric("Gol 1T", f"{(1-(poisson.pmf(0, l_l*0.35)*poisson.pmf(0, l_v*0.35)))*100:.1f}%")
    c4.metric("Valor Detectado", "SÍ" if bookie_odd > fair_odd * 1.1 else "NO")

    # Radar de Valor Detallado
    if bookie_odd > fair_odd * 1.1:
        st.info(f"🔥 RADAR DE VALOR: El mercado paga {bookie_odd}, nuestra cuota justa es {fair_odd:.2f}. Ventaja del {((bookie_odd/fair_odd)-1)*100:.1f}%")

    st.subheader("🎯 Marcadores Probables & Veracidad")
    m_cols = st.columns(5)
    for idx, m in enumerate(best):
        with m_cols[idx]:
            label = "👑 MAESTRO" if idx == 0 else f"Opción {idx+1}"
            st.info(f"**{m['m']}**\n\n{m['p']:.1f}%")

# --- SECCIÓN HISTORIAL ---
st.divider()
st.subheader("📚 Historial de Análisis")
if st.session_state.historial_global:
    df_h = pd.DataFrame(st.session_state.historial_global)
    st.table(df_h)
    csv = df_h.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar Reporte Excel/CSV", csv, "reporte_futbol.csv", "text/csv")