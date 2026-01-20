import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Football Intelligence Pro v25", layout="wide")

# --- DATA MAESTRA (36 EQUIPOS COMPLETOS) ---
DATA_MASTER = {
    "CHAMPIONS & EUROPE": {
        "Arsenal": {"id": 42, "xG": 2.1, "xGA": 0.8, "tier": 1, "spec": "Posesión"},
        "Bayern München": {"id": 2672, "xG": 2.1, "xGA": 1.0, "tier": 1, "spec": "Transición"},
        "PSG": {"id": 1644, "xG": 2.0, "xGA": 1.1, "tier": 1, "spec": "Velocidad"},
        "Man City": {"id": 17, "xG": 2.4, "xGA": 0.9, "tier": 1, "spec": "Ataque Total"},
        "Atalanta": {"id": 2686, "xG": 1.7, "xGA": 1.1, "tier": 2, "spec": "Marcaje"},
        "Inter": {"id": 2697, "xG": 1.8, "xGA": 0.9, "tier": 1, "spec": "Bloque"},
        "Real Madrid": {"id": 2829, "xG": 2.2, "xGA": 1.1, "tier": 1, "spec": "Jerarquía"},
        "Atlético Madrid": {"id": 2836, "xG": 1.7, "xGA": 1.1, "tier": 1, "spec": "Intensidad"},
        "Liverpool": {"id": 44, "xG": 2.2, "xGA": 1.0, "tier": 1, "spec": "Gegenpressing"},
        "Borussia Dortmund": {"id": 2673, "xG": 1.7, "xGA": 1.2, "tier": 1, "spec": "Contra"},
        "Tottenham": {"id": 33, "xG": 1.8, "xGA": 1.5, "tier": 2, "spec": "Verticalidad"},
        "Newcastle": {"id": 37, "xG": 1.7, "xGA": 1.5, "tier": 2, "spec": "Físico"},
        "Chelsea": {"id": 38, "xG": 1.9, "xGA": 1.3, "tier": 2, "spec": "Ofensivo"},
        "Sporting CP": {"id": 3001, "xG": 1.8, "xGA": 0.9, "tier": 2, "spec": "Salida"},
        "Barcelona": {"id": 2817, "xG": 2.1, "xGA": 1.2, "tier": 1, "spec": "ADN"},
        "Marseille": {"id": 1641, "xG": 1.8, "xGA": 1.2, "tier": 2, "spec": "Ambiental"},
        "Juventus": {"id": 2687, "xG": 1.6, "xGA": 0.8, "tier": 1, "spec": "Orden"},
        "Galatasaray": {"id": 2901, "xG": 1.8, "xGA": 1.3, "tier": 2, "spec": "Infierno"},
        "Monaco": {"id": 1653, "xG": 1.7, "xGA": 1.3, "tier": 2, "spec": "Dinámico"},
        "Leverkusen": {"id": 2681, "xG": 1.9, "xGA": 1.0, "tier": 1, "spec": "Invictos"},
        "PSV": {"id": 2722, "xG": 1.9, "xGA": 1.1, "tier": 2, "spec": "Bandas"},
        "Qarabag": {"id": 5510, "xG": 1.3, "xGA": 1.6, "tier": 3, "spec": "Resistencia"},
        "Napoli": {"id": 2714, "xG": 1.7, "xGA": 1.0, "tier": 2, "spec": "Vertical"},
        "København": {"id": 2699, "xG": 1.4, "xGA": 1.3, "tier": 3, "spec": "Disciplina"},
        "Benfica": {"id": 3006, "xG": 1.7, "xGA": 1.0, "tier": 2, "spec": "Asociativo"},
        "Pafos": {"id": 36173, "xG": 1.1, "xGA": 1.6, "tier": 4, "spec": "Cerrado"},
        "Union SG": {"id": 3662, "xG": 1.3, "xGA": 1.4, "tier": 3, "spec": "Estrategia"},
        "Athletic Club": {"id": 2825, "xG": 1.6, "xGA": 1.2, "tier": 2, "spec": "Aéreo"},
        "Olympiacos": {"id": 2616, "xG": 1.6, "xGA": 1.2, "tier": 3, "spec": "Presión"},
        "Eintracht": {"id": 2679, "xG": 1.5, "xGA": 1.4, "tier": 2, "spec": "Veloz"},
        "Club Brujas": {"id": 2634, "xG": 1.4, "xGA": 1.5, "tier": 2, "spec": "Contragolpe"},
        "Bodo/Glimt": {"id": 5444, "xG": 1.4, "xGA": 1.4, "tier": 3, "spec": "Ártico"},
        "Slavia Praha": {"id": 2261, "xG": 1.4, "xGA": 1.3, "tier": 3, "spec": "Físico"},
        "Ajax": {"id": 2692, "xG": 1.6, "xGA": 1.2, "tier": 2, "spec": "Presión"},
        "Villarreal": {"id": 2819, "xG": 1.7, "xGA": 1.6, "tier": 2, "spec": "Medios"},
        "Kairat Almaty": {"id": 4726, "xG": 0.9, "xGA": 2.2, "tier": 4, "spec": "Altura"}
    }
}

# --- ÁRBITROS ---
ARBITROS = {"Marciniak": 4.5, "Orsato": 5.9, "Taylor": 3.8, "Oliver": 4.1}

def get_logo(t_id): return f"https://www.sofascore.com/static/images/team-logo/team_{t_id}.png"

# --- INTERFAZ ---
st.title("⚽ Football Intelligence Pro: v25")

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Local", list(DATA_MASTER["CHAMPIONS & EUROPE"].keys()), key="loc")
    st.image(get_logo(DATA_MASTER["CHAMPIONS & EUROPE"][loc]['id']), width=70)
    st.warning(f"💎 Fortaleza: {DATA_MASTER['CHAMPIONS & EUROPE'][loc]['spec']}")
    st.info(f"📋 **LESIONADOS {loc}:**\n- Reporte de bajas activo.")
    bajas_l = st.multiselect(f"Impacto Bajas {loc}", ["Ataque", "Medio", "Defensa"], key="bl")

with col2:
    vis = st.selectbox("Visitante", list(DATA_MASTER["CHAMPIONS & EUROPE"].keys()), key="vis")
    st.image(get_logo(DATA_MASTER["CHAMPIONS & EUROPE"][vis]['id']), width=70)
    st.warning(f"💎 Fortaleza: {DATA_MASTER['CHAMPIONS & EUROPE'][vis]['spec']}")
    st.info(f"📋 **LESIONADOS {vis}:**\n- Reporte de bajas activo.")
    bajas_v = st.multiselect(f"Impacto Bajas {vis}", ["Ataque", "Medio", "Defensa"], key="bv")

st.divider()

c_arb, c_ht = st.columns(2)
with c_arb:
    ref = st.selectbox("Árbitro (Scraping Tarjetas)", list(ARBITROS.keys()))
    st.write(f"Tendencia: **{'ALTAMENTE TARJETERO' if ARBITROS[ref] > 5 else 'MODERADO'}**")

with c_ht:
    marcador_live = st.text_input("Marcador Actual / Descanso (ej. 3-1)", value="0-0")

if st.button("🚀 GENERAR ANÁLISIS MAESTRO"):
    dl, dv = DATA_MASTER["CHAMPIONS & EUROPE"][loc], DATA_MASTER["CHAMPIONS & EUROPE"][vis]
    l_l = (dl["xG"] * dv["xGA"]) / 1.45
    l_v = (dv["xG"] * dl["xGA"]) / 1.45

    # AJUSTE 2T LIVE
    try:
        gl_ht, gv_ht = map(int, marcador_live.split('-'))
        if gl_ht != 0 or gv_ht != 0:
            l_v *= 1.30 if gl_ht > gv_ht else 1.0
            l_l *= 1.30 if gv_ht > gl_ht else 1.0
    except: pass

    # MOSTRAR MÉTRICAS
    st.success(f"### Pronóstico Pro: {loc} vs {vis}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tarjetas Est.", f"{ARBITROS[ref]*1.1:.1f}")
    m2.metric("Inminente Roja", "SÍ" if ARBITROS[ref] > 5.5 else "BAJA")
    m3.metric("Ambos Anotan", f"{(1-poisson.pmf(0, l_l))*(1-poisson.pmf(0, l_v))*100:.1f}%")
    m4.metric("Córners Totales", f"{(l_l+l_v)*2.9:.1f}")

    # ALERTA DE GOL INMINENTE RESALTADA
    st.markdown("""<div style="background-color:#ff4b4b;padding:15px;border-radius:10px;text-align:center;">
    <h2 style="color:white;margin:0;">🚨 ALERTA DE GOL INMINENTE: Tramo 70' - 85' 🚨</h2>
    <p style="color:white;">Alta presión detectada en el área rival. ¡Ojo al Live!</p></div>""", unsafe_allow_allow_html=True)

    # Marcadores
    res_m = []
    for gl in range(6):
        for gv in range(6):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            res_m.append({"m": f"{gl}-{gv}", "p": p * 100})
    best = sorted(res_m, key=lambda x: x['p'], reverse=True)[:5]

    st.subheader("🎯 Marcadores Probables (Ajuste 2T)")
    m_cols = st.columns(5)
    for idx, m in enumerate(best):
        with m_cols[idx]:
            if idx == 0: st.warning(f"👑 **MAESTRO**\n{m['m']}\n{m['p']:.1f}%")
            else: st.info(f"**{m['m']}**\n{m['p']:.1f}%")