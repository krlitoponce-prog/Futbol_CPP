import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Global Football Predictor Pro", layout="wide")

# --- DATA MAESTRA DE LIGAS Y TORNEOS ---
LIGAS = {
    "INGLESA": {"id": 17, "paises": "Inglaterra"},
    "ESPAÑOLA": {"id": 8, "paises": "España"},
    "ALEMANA": {"id": 35, "paises": "Alemania"},
    "ITALIANA": {"id": 23, "paises": "Italia"},
    "PERUANA": {"id": 948, "paises": "Perú"},
    "FRANCESA": {"id": 34, "paises": "Francia"},
    "PORTUGUESA": {"id": 238, "paises": "Portugal"},
    "BRASILEÑA": {"id": 325, "paises": "Brasil"},
    "ARGENTINA": {"id": 155, "paises": "Argentina"},
    "CHAMPIONS LEAGUE": {"id": 7, "paises": "Europa"},
    "EUROPE LEAGUE": {"id": 677, "paises": "Europa"}
}

# --- SIMULACIÓN DE BASE DE DATOS GLOBAL ---
# Esta sección se alimenta automáticamente del scraper que desarrollamos
def obtener_data_equipo(nombre_equipo):
    # Simulación de jugadores estrella por equipo
    return [
        {"n": "Estrella Ataque", "r": 8.2, "t": "Goleador", "i": 0.18},
        {"n": "Motor Medio", "r": 7.9, "t": "Creativo", "i": 0.15},
        {"n": "Central Muro", "r": 7.7, "t": "Defensa", "i": 0.20}
    ]

# --- MOTOR DE CÁLCULO AVANZADO ---
class MotorGlobal:
    @staticmethod
    def calcular_todo(l_l, l_v, racha_l, racha_v, ref_cards):
        # Ajuste por Forma (Racha)
        # Cada victoria en la racha (+1) suma 0.05 al lambda
        l_l += (sum(racha_l) * 0.05)
        l_v += (sum(racha_v) * 0.05)
        
        # Probabilidades de Goles (Poisson)
        prob_btts = (1 - poisson.pmf(0, l_l)) * (1 - poisson.pmf(0, l_v)) * 100
        
        marcadores = []
        for gl in range(4):
            for gv in range(4):
                p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
                marcadores.append({"m": f"{gl}-{gv}", "p": p * 100})
        
        return {
            "btts": prob_btts,
            "marcadores": sorted(marcadores, key=lambda x: x['p'], reverse=True)[:3],
            "corners": (l_l + l_v) * 2.8,
            "tarjetas": ref_cards * 1.1
        }

# --- INTERFAZ STREAMLIT ---
st.title("🌍 Sistema de Predicción de Fútbol a Gran Escala")
st.sidebar.header("🏆 Selección de Torneo")
liga_sel = st.sidebar.selectbox("Liga / Competición", list(LIGAS.keys()))

st.header(f"Análisis Técnico: {liga_sel}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Local")
    eq_l = st.text_input("Nombre Equipo Local", "Manchester City")
    bajas_l = st.multiselect(f"Bajas de {eq_l}", [j['n'] for j in obtener_data_equipo(eq_l)])
    racha_l = st.multiselect(f"Racha {eq_l} (Últ. 5)", ["V", "E", "D"], key="rl", help="V=Victoria, E=Empate, D=Derrota")
    # Convertir racha a valores numéricos
    racha_l_val = [1 if x=="V" else -0.5 if x=="D" else 0 for x in racha_l]

with col2:
    st.subheader("✈️ Visitante")
    eq_v = st.text_input("Nombre Equipo Visitante", "Real Madrid")
    bajas_v = st.multiselect(f"Bajas de {eq_v}", [j['n'] for j in obtener_data_equipo(eq_v)])
    racha_v = st.multiselect(f"Racha {eq_v} (Últ. 5)", ["V", "E", "D"], key="rv")
    racha_v_val = [1 if x=="V" else -0.5 if x=="D" else 0 for x in racha_v]

st.divider()
col_ref, col_stats = st.columns([1, 2])

with col_ref:
    st.subheader("👨‍⚖️ Árbitro")
    ref_name = st.text_input("Nombre del Árbitro", "Anthony Taylor")
    ref_media = st.slider("Media de Tarjetas del Árbitro", 2.0, 8.0, 4.0)

if st.button("🚀 GENERAR PREDICCIÓN GLOBAL"):
    # Lógica de impacto de bajas
    impacto_l = len(bajas_l) * 0.15
    impacto_v = len(bajas_v) * 0.15
    
    # Lambdas base ajustados por Localía y Bajas
    l_l = 2.0 * (1.15) * (1 - impacto_l)
    l_v = 1.4 * (0.85) * (1 - impacto_v)
    
    res = MotorGlobal.calcular_todo(l_l, l_v, racha_l_val, racha_v_val, ref_media)
    
    # Visualización de Resultados
    st.success(f"### Predicción Final: {eq_l} vs {eq_v}")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Ambos Anotan (BTTS)", f"{res['btts']:.1f}%")
    m2.metric("Córners Totales", f"{res['corners']:.1f}")
    m3.metric("Tarjetas Totales", f"{res['tarjetas']:.1f}")
    m4.metric("Goles Esperados", f"{l_l + l_v:.2f}")

    

    st.subheader("🎯 Marcadores Exactos Probables")
    cols = st.columns(3)
    for i, m in enumerate(res['marcadores']):
        cols[i].info(f"**{m['m']}** \n\n Probabilidad: {m['p']:.1f}%")

    st.info(f"""
    **Informe de Inteligencia:** - El factor de racha de {eq_l} ha modificado su expectativa goleadora en un {sum(racha_l_val)*5}%.
    - El árbitro {ref_name} tiene una tendencia {'Alta' if ref_media > 4 else 'Baja'} de amonestaciones, lo que ajusta el mercado de tarjetas.
    - Se detecta valor si la cuota del marcador {res['marcadores'][0]['m']} es superior a {100/res['marcadores'][0]['p']:.2f}.
    """)