import streamlit as st
import pandas as pd
from scipy.stats import poisson

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Global Predictor Elite", layout="wide")

# --- DATA MAESTRA DE TORNEOS ---
TORNEOS = ["INGLESA", "ESPAÑOLA", "ALEMANA", "ITALIANA", "PERUANA", "FRANCESA", 
           "PORTUGUESA", "BRASILEÑA", "ARGENTINA", "CHAMPIONS LEAGUE", "EUROPA LEAGUE"]

# --- FUNCIÓN DE CARGA DINÁMICA (Simulando el Scraper Global) ---
def obtener_equipos_liga(liga):
    # En el futuro, esto leerá directamente de tu predicciones_futbol.db
    if liga == "INGLESA": return ["Manchester City", "Liverpool", "Arsenal", "Brighton", "Spurs"]
    if liga == "ESPAÑOLA": return ["Real Madrid", "Barcelona", "Atletico", "Girona"]
    if liga == "PERUANA": return ["Universitario", "Alianza Lima", "Sporting Cristal", "Melgar"]
    return ["Equipo A", "Equipo B", "Equipo C"]

def obtener_jugadores_equipo(equipo):
    # Solución a la captura: Siempre devuelve datos para evitar "No options to select"
    return [
        {"n": "Estrella Creativa", "r": 8.1, "t": "Motor", "i": 0.15},
        {"n": "Goleador Elite", "r": 7.9, "t": "Finalizador", "i": 0.12},
        {"n": "Defensa Central", "r": 7.7, "t": "Muro", "i": 0.18}
    ]

# --- MOTOR DE CÁLCULO ---
class MotorGlobal:
    @staticmethod
    def predecir(l_l, l_v, ref_media):
        prob_btts = (1 - poisson.pmf(0, l_l)) * (1 - poisson.pmf(0, l_v)) * 100
        corners = (l_l + l_v) * 2.8
        tarjetas = ref_media * 1.05
        
        marcadores = []
        for gl in range(4):
            for gv in range(4):
                p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
                marcadores.append({"m": f"{gl}-{gv}", "p": p * 100})
        return {"btts": prob_btts, "corners": corners, "tarjetas": tarjetas, 
                "marcadores": sorted(marcadores, key=lambda x: x['p'], reverse=True)[:3]}

# --- INTERFAZ VISUAL ---
st.title("⚽ Predictor Pro: Sistema Global de Inteligencia Deportiva")

# Creación de Pestañas por Liga
tabs = st.tabs(TORNEOS)

for i, tab in enumerate(tabs):
    with tab:
        st.subheader(f"Análisis Técnico: {TORNEOS[i]}")
        
        col1, col2 = st.columns(2)
        equipos = obtener_equipos_liga(TORNEOS[i])
        
        with col1:
            st.markdown("### 🏠 Local")
            loc = st.selectbox(f"Equipo Local ({TORNEOS[i]})", equipos, key=f"loc_{i}")
            jugadores_l = obtener_jugadores_equipo(loc)
            bajas_l = st.multiselect(f"Bajas confirmadas: {loc}", [j['n'] for j in jugadores_l], key=f"b_l_{i}")
            racha_l = st.multiselect(f"Racha {loc} (Últ. 5)", ["V", "E", "D"], key=f"r_l_{i}")

        with col2:
            st.markdown("### ✈️ Visitante")
            vis = st.selectbox(f"Equipo Visitante ({TORNEOS[i]})", equipos, key=f"vis_{i}")
            jugadores_v = obtener_jugadores_equipo(vis)
            bajas_v = st.multiselect(f"Bajas confirmadas: {vis}", [j['n'] for j in jugadores_v], key=f"b_v_{i}")
            racha_v = st.multiselect(f"Racha {vis} (Últ. 5)", ["V", "E", "D"], key=f"r_v_{i}")

        st.divider()
        
        # Módulo de Árbitro
        c_ref, c_calc = st.columns([1, 2])
        with c_ref:
            st.subheader("👨‍⚖️ Árbitro")
            ref_name = st.text_input("Nombre del Árbitro", "Designación Pendiente", key=f"ref_n_{i}")
            ref_media = st.slider("Media histórica de tarjetas", 2.0, 9.0, 4.0, key=f"ref_m_{i}")
            st.info("💡 Buscamos estos datos en WhoScored o FBRef.")

        if st.button(f"🚀 GENERAR PREDICCIÓN: {loc} vs {vis}", key=f"btn_{i}"):
            # Lógica de Impacto (Simplificada para la interfaz)
            imp_l = len(bajas_l) * 0.12
            imp_v = len(bajas_v) * 0.12
            l_l = 2.0 * 1.15 * (1 - imp_l)
            l_v = 1.4 * 0.85 * (1 - imp_v)
            
            res = MotorGlobal.predecir(l_l, l_v, ref_media)
            
            st.success(f"### Resultado del Análisis")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Ambos Anotan", f"{res['btts']:.1f}%")
            m2.metric("Córners", f"{res['corners']:.1f}")
            m3.metric("Tarjetas Totales", f"{res['tarjetas']:.1f}")
            m4.metric("Goles Esperados", f"{l_l + l_v:.2f}")

            st.subheader("🎯 Marcadores Exactos Probables")
            cols = st.columns(3)
            for j, m in enumerate(res['marcadores']):
                cols[j].warning(f"**{m['m']}** ({m['p']:.1f}%)")