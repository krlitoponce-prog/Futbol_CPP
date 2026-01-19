import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Predictor Pro Total", layout="wide")

# --- BASE DE DATOS DE JUGADORES ESTRELLA (Simulación de Scraper) ---
# En una fase final, esto se llenará automáticamente desde tu SQLite
jugadores_db = {
    "Manchester City": [
        {"nombre": "Kevin De Bruyne", "rating": 8.1, "rol": "Creatividad", "impacto": 0.20},
        {"nombre": "Erling Haaland", "rating": 7.9, "rol": "Goleador", "impacto": 0.15},
        {"nombre": "Rodri", "rating": 8.0, "rol": "Defensa/Motor", "impacto": 0.18}
    ],
    "Liverpool": [
        {"nombre": "Mohamed Salah", "rating": 7.8, "rol": "Goleador", "impacto": 0.15},
        {"nombre": "Virgil van Dijk", "rating": 7.7, "rol": "Defensa", "impacto": 0.22},
        {"nombre": "Trent Alexander-Arnold", "rating": 7.6, "rol": "Creatividad", "impacto": 0.12}
    ],
    "Arsenal": [
        {"nombre": "Bukayo Saka", "rating": 7.9, "rol": "Goleador/Creativo", "impacto": 0.17},
        {"nombre": "William Saliba", "rating": 7.5, "rol": "Defensa", "impacto": 0.15}
    ]
}

equipos_20 = sorted(["Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town", "Leicester City", "Liverpool", "Manchester City", "Manchester United", "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham Hotspur", "West Ham United", "Wolverhampton"])

class MotorElite:
    @staticmethod
    def calcular_probabilidades(l_l, l_v, l_corners_base=10.5, l_cards_base=4.2):
        # 1. Goles y BTTS
        prob_l_0 = poisson.pmf(0, l_l)
        prob_v_0 = poisson.pmf(0, l_v)
        prob_btts = (1 - prob_l_0) * (1 - prob_v_0) * 100
        
        # 2. Marcadores Exactos
        marcadores = []
        for gl in range(4):
            for gv in range(4):
                p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
                marcadores.append({"m": f"{gl}-{gv}", "p": p * 100})
        
        # 3. Córners y Tarjetas (Poisson)
        exp_corners = (l_l + l_v) * 2.5 # Estimación simple basada en fuerza de ataque
        exp_tarjetas = l_cards_base 
        
        return {
            "btts": prob_btts,
            "marcadores": sorted(marcadores, key=lambda x: x['p'], reverse=True)[:3],
            "corners": round(exp_corners, 1),
            "tarjetas": round(exp_tarjetas, 1)
        }

st.title("⚽ Predictor Inteligente de Rendimiento")
st.markdown("---")

# --- SELECCIÓN DE EQUIPOS Y BAJAS ---
col1, col2 = st.columns(2)

with col1:
    st.header("🏠 Local")
    loc = st.selectbox("Equipo Local", equipos_20, index=12)
    bajas_loc = st.multiselect(f"Bajas de {loc}", [j['nombre'] for j in jugadores_db.get(loc, [])])
    
    # Cálculo de impacto automático
    impacto_ataque_l = 0
    impacto_defensa_l = 0
    for b in bajas_loc:
        jugador = next(item for item in jugadores_db[loc] if item["nombre"] == b)
        if jugador['rol'] in ['Creatividad', 'Goleador']: impacto_ataque_l += jugador['impacto']
        if jugador['rol'] == 'Defensa': impacto_defensa_l += jugador['impacto']

with col2:
    st.header("✈️ Visitante")
    vis = st.selectbox("Equipo Visitante", equipos_20, index=11)
    bajas_vis = st.multiselect(f"Bajas de {vis}", [j['nombre'] for j in jugadores_db.get(vis, [])])
    
    impacto_ataque_v = 0
    impacto_defensa_v = 0
    for b in bajas_vis:
        jugador = next(item for item in jugadores_db[vis] if item["nombre"] == b)
        if jugador['rol'] in ['Creatividad', 'Goleador']: impacto_ataque_v += jugador['impacto']
        if jugador['rol'] == 'Defensa': impacto_defensa_v += jugador['impacto']

# --- LÓGICA DE RENDIMIENTO LOCAL/VISITA ---
# Factor campo: Local suele tener un lambda 15% mayor
l_local = 1.8 * 1.15 * (1 - impacto_ataque_l) * (1 + impacto_defensa_v)
l_visita = 1.2 * 0.85 * (1 - impacto_ataque_v) * (1 + impacto_defensa_l)

if st.button("📊 GENERAR PREDICCIÓN COMPLETA"):
    data = MotorElite.calcular_probabilidades(l_local, l_visita)
    
    # --- RESULTADOS PRINCIPALES ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Prob. Ambos Anotan", f"{data['btts']:.1f}%")
    c2.metric("Córners Estimados", data['corners'])
    c3.metric("Tarjetas Totales", data['tarjetas'])
    c4.metric("Goles Totales (O/U 2.5)", f"{l_local + l_visita:.2f}")

    st.subheader("🎯 Marcadores Exactos más Probables")
    m_cols = st.columns(3)
    for i, m in enumerate(data['marcadores']):
        m_cols[i].success(f"**{m['m']}** ({m['p']:.1f}%)")

    # --- COMPARADOR DE CUOTAS (VALUE) ---
    st.markdown("---")
    st.subheader("⚖️ Comparador de Valor (Betting Value)")
    
    cuota_btts_mercado = 1.95 # Esto vendría del scraper
    prob_btts_decimal = data['btts'] / 100
    cuota_justa = 1 / prob_btts_decimal if prob_btts_decimal > 0 else 0
    
    v_col1, v_col2 = st.columns(2)
    v_col1.write(f"Nuestra Cuota Justa (BTTS): **{cuota_justa:.2f}**")
    v_col1.write(f"Cuota de Mercado: **{cuota_btts_mercado:.2f}**")
    
    if cuota_btts_mercado > cuota_justa:
        v_col2.info("✅ **VALOR DETECTADO** en 'Ambos Anotan'")
    else:
        v_col2.error("❌ No hay valor en este mercado")

    st.info(f"""
    **Análisis de Juego:** La ausencia de {', '.join(bajas_loc) if bajas_loc else 'ninguna estrella'} en el local y {', '.join(bajas_vis) if bajas_vis else 'ninguna estrella'} en la visita, 
    ha alterado la fluidez del juego. El equipo local jugando en casa mantiene una ventaja del 15%, 
    pero su capacidad de crear peligro ha bajado un {impacto_ataque_l*100:.0f}% debido a las bajas.
    """)