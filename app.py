import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Football Intel Pro v29", layout="wide")

if 'historial_global' not in st.session_state:
    st.session_state.historial_global = []

# --- DATA MAESTRA (LOS 36 EQUIPOS COMPLETOS) ---
if 'data_equipos' not in st.session_state:
    st.session_state.data_equipos = {
        "Arsenal": {"id": 42, "xG": 2.1, "xGA": 0.8, "tier": 1, "spec": "Posesión", "pitch": "Natural"},
        "Bayern München": {"id": 2672, "xG": 2.1, "xGA": 1.0, "tier": 1, "spec": "Transición", "pitch": "Natural"},
        "PSG": {"id": 1644, "xG": 2.0, "xGA": 1.1, "tier": 1, "spec": "Velocidad", "pitch": "Natural"},
        "Man City": {"id": 17, "xG": 2.4, "xGA": 0.9, "tier": 1, "spec": "Ataque Total", "pitch": "Natural"},
        "Atalanta": {"id": 2686, "xG": 1.7, "xGA": 1.1, "tier": 2, "spec": "Marcaje", "pitch": "Natural"},
        "Inter": {"id": 2697, "xG": 1.8, "xGA": 0.9, "tier": 1, "spec": "Bloque", "pitch": "Natural"},
        "Real Madrid": {"id": 2829, "xG": 2.2, "xGA": 1.1, "tier": 1, "spec": "Jerarquía", "pitch": "Natural"},
        "Atlético Madrid": {"id": 2836, "xG": 1.7, "xGA": 1.1, "tier": 1, "spec": "Intensidad", "pitch": "Natural"},
        "Liverpool": {"id": 44, "xG": 2.2, "xGA": 1.0, "tier": 1, "spec": "Gegenpressing", "pitch": "Natural"},
        "Borussia Dortmund": {"id": 2673, "xG": 1.7, "xGA": 1.2, "tier": 1, "spec": "Contra", "pitch": "Natural"},
        "Tottenham": {"id": 33, "xG": 1.8, "xGA": 1.5, "tier": 2, "spec": "Verticalidad", "pitch": "Natural"},
        "Newcastle": {"id": 37, "xG": 1.7, "xGA": 1.5, "tier": 2, "spec": "Físico", "pitch": "Natural"},
        "Chelsea": {"id": 38, "xG": 1.9, "xGA": 1.3, "tier": 2, "spec": "Ofensivo", "pitch": "Natural"},
        "Sporting CP": {"id": 3001, "xG": 1.8, "xGA": 0.9, "tier": 2, "spec": "Salida", "pitch": "Natural"},
        "Barcelona": {"id": 2817, "xG": 2.1, "xGA": 1.2, "tier": 1, "spec": "ADN Barça", "pitch": "Natural"},
        "Marseille": {"id": 1641, "xG": 1.8, "xGA": 1.2, "tier": 2, "spec": "Ambiental", "pitch": "Natural"},
        "Juventus": {"id": 2687, "xG": 1.6, "xGA": 0.8, "tier": 1, "spec": "Orden", "pitch": "Natural"},
        "Galatasaray": {"id": 2901, "xG": 1.8, "xGA": 1.3, "tier": 2, "spec": "Infierno Turco", "pitch": "Natural"},
        "Monaco": {"id": 1653, "xG": 1.7, "xGA": 1.3, "tier": 2, "spec": "Dinámico", "pitch": "Natural"},
        "Leverkusen": {"id": 2681, "xG": 1.9, "xGA": 1.0, "tier": 1, "spec": "Invictos", "pitch": "Natural"},
        "PSV": {"id": 2722, "xG": 1.9, "xGA": 1.1, "tier": 2, "spec": "Bandas", "pitch": "Natural"},
        "Qarabag": {"id": 5510, "xG": 1.3, "xGA": 1.6, "tier": 3, "spec": "Resistencia", "pitch": "Mixto"},
        "Napoli": {"id": 2714, "xG": 1.7, "xGA": 1.0, "tier": 2, "spec": "Vertical", "pitch": "Natural"},
        "København": {"id": 2699, "xG": 1.4, "xGA": 1.3, "tier": 3, "spec": "Disciplina", "pitch": "Natural"},
        "Benfica": {"id": 3006, "xG": 1.7, "xGA": 1.0, "tier": 2, "spec": "Asociativo", "pitch": "Natural"},
        "Pafos": {"id": 36173, "xG": 1.1, "xGA": 1.6, "tier": 4, "spec": "Cerrado", "pitch": "Natural"},
        "Union SG": {"id": 3662, "xG": 1.3, "xGA": 1.4, "tier": 3, "spec": "Estrategia", "pitch": "Natural"},
        "Athletic Club": {"id": 2825, "xG": 1.6, "xGA": 1.2, "tier": 2, "spec": "Aéreo", "pitch": "Natural"},
        "Olympiacos": {"id": 2616, "xG": 1.6, "xGA": 1.2, "tier": 3, "spec": "Presión", "pitch": "Natural"},
        "Eintracht": {"id": 2679, "xG": 1.5, "xGA": 1.4, "tier": 2, "spec": "Veloz", "pitch": "Natural"},
        "Club Brujas": {"id": 2634, "xG": 1.4, "xGA": 1.5, "tier": 2, "spec": "Contragolpe", "pitch": "Natural"},
        "Bodo/Glimt": {"id": 5444, "xG": 1.4, "xGA": 1.4, "tier": 3, "spec": "Ártico", "pitch": "Sintético"},
        "Slavia Prague": {"id": 2261, "xG": 1.4, "xGA": 1.3, "tier": 3, "spec": "Físico", "pitch": "Natural"},
        "Ajax": {"id": 2692, "xG": 1.6, "xGA": 1.2, "tier": 2, "spec": "Presión", "pitch": "Natural"},
        "Villarreal": {"id": 2819, "xG": 1.7, "xGA": 1.6, "tier": 2, "spec": "Medios", "pitch": "Natural"},
        "Kairat Almaty": {"id": 4726, "xG": 0.9, "xGA": 2.2, "tier": 4, "spec": "Altura", "pitch": "Natural"}
    }

def get_logo(t_id): return f"https://www.sofascore.com/static/images/team-logo/team_{t_id}.png"

st.title("⚽ Football Intelligence Pro v29: Auditoría & Goles")

col1, col2 = st.columns(2)
with col1:
    loc = st.selectbox("Local", list(st.session_state.data_equipos.keys()), key="loc")
    team_l = st.session_state.data_equipos[loc]
    st.image(get_logo(team_l['id']), width=70)
    st.info(f"📋 **LESIONADOS {loc}:** Selecciona para aplicar descuento automático.")
    bajas_l = st.multiselect(f"Bajas Confirmadas {loc}", ["Portero/Defensa (xGA +15%)", "Ataque/Goleador (xG -20%)"], key="bl")

with col2:
    vis = st.selectbox("Visitante", list(st.session_state.data_equipos.keys()), key="vis")
    team_v = st.session_state.data_equipos[vis]
    st.image(get_logo(team_v['id']), width=70)
    st.info(f"📋 **LESIONADOS {vis}:** Selecciona para aplicar descuento automático.")
    bajas_v = st.multiselect(f"Bajas Confirmadas {vis}", ["Portero/Defensa (xGA +15%)", "Ataque/Goleador (xG -20%)"], key="bv")

st.divider()

if st.button("🚀 GENERAR ANÁLISIS MAESTRO"):
    # Lógica de Goles base
    l_l = (team_l["xG"] * team_v["xGA"]) / 1.45
    l_v = (team_v["xG"] * team_l["xGA"]) / 1.45

    # IMPACTO AUTOMÁTICO DE LESIONADOS
    for b in bajas_l:
        if "Portero" in b: l_v *= 1.15
        if "Ataque" in b: l_l *= 0.80
    for b in bajas_v:
        if "Portero" in b: l_l *= 1.15
        if "Ataque" in b: l_v *= 0.80

    total_exp = l_l + l_v

    st.success(f"### Análisis de Goles y Probabilidad: {loc} vs {vis}")
    g1, g2, g3 = st.columns(3)
    g1.metric("Goles Esperados (Total)", f"{total_exp:.2f}")
    g2.metric("Prob. Over 2.5", f"{(1 - (poisson.pmf(0, total_exp) + poisson.pmf(1, total_exp) + poisson.pmf(2, total_exp)))*100:.1f}%")
    g3.metric("Prob. Under 2.5", f"{(poisson.pmf(0, total_exp) + poisson.pmf(1, total_exp) + poisson.pmf(2, total_exp))*100:.1f}%")

    st.error("🚨 ALERTA DE GOL INMINENTE: Tramo 75' - 90' por fatiga defensiva acumulada.")

    # Marcador Maestro
    res_m = []
    for gl in range(6):
        for gv in range(6):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            res_m.append({"m": f"{gl}-{gv}", "p": p * 100})
    best = sorted(res_m, key=lambda x: x['p'], reverse=True)[:5]
    st.session_state.last_pred = best[0]['m']

    st.subheader("🎯 Top 5 Marcadores Maestro")
    m_cols = st.columns(5)
    for idx, m in enumerate(best):
        with m_cols[idx]:
            st.warning(f"**{m['m']}**\n{m['p']:.1f}%")

# --- COMPARADOR RENDIMIENTO VS PREDICCIÓN ---
st.divider()
st.subheader("📊 Auditoría: Rendimiento vs Predicción")
c_aud1, c_aud2, c_aud3 = st.columns(3)
with c_aud1:
    partido_fin = st.selectbox("Partido a Auditar", [f"{loc} vs {vis}", "Bodø/Glimt vs Man City", "Real Madrid vs Mónaco"])
    pred_hecha = st.text_input("Predicción del Sistema", value=st.session_state.get('last_pred', '0-0'))
with c_aud2:
    resultado_fin = st.text_input("Resultado Real Final")
with c_aud3:
    if st.button("⚖️ Auditar Rendimiento"):
        st.session_state.historial_global.append({
            "Partido": partido_fin,
            "Predicción": pred_hecha,
            "Real": resultado_fin,
            "Efectividad": "✅ ACIERTO" if pred_hecha == resultado_fin else "❌ DESVIACIÓN"
        })

if st.session_state.historial_global:
    st.table(pd.DataFrame(st.session_state.historial_global))