import streamlit as st
import pandas as pd
from scipy.stats import poisson

st.set_page_config(page_title="Global Predictor Elite v3", layout="wide")

# --- BASE DE DATOS EXPANDIDA (Ejemplo de lo que el scraper poblará) ---
EQUIPOS_POR_LIGA = {
    "INGLESA": ["Manchester City", "Liverpool", "Arsenal", "Brighton", "Spurs", "Man Utd", "Chelsea", "Newcastle"],
    "ESPAÑOLA": ["Real Madrid", "Barcelona", "Atletico Madrid", "Girona", "Real Sociedad", "Athletic Club"],
    "PERUANA": ["Universitario", "Alianza Lima", "Sporting Cristal", "Melgar", "Cienciano", "ADT"],
    "ALEMANA": ["Bayern Munich", "Bayer Leverkusen", "Dortmund", "RB Leipzig"],
    "ITALIANA": ["Inter", "Juventus", "Milan", "Napoli", "Atalanta"]
}

def obtener_jugadores(equipo):
    # Garantiza que siempre haya opciones para evitar "No options to select"
    return [
        {"n": "Estrella Creativa", "r": 8.2, "i": 0.18},
        {"n": "Goleador Principal", "r": 7.9, "i": 0.15},
        {"n": "Defensa Líder", "r": 7.7, "i": 0.20}
    ]

# --- MOTOR DE CÁLCULO DINÁMICO ---
def realizar_analisis(l_l, l_v, ref_m):
    # Probabilidad Ambos Anotan (BTTS)
    prob_btts = (1 - poisson.pmf(0, l_l)) * (1 - poisson.pmf(0, l_v)) * 100
    
    # Marcadores Exactos
    marcadores = []
    for gl in range(4):
        for gv in range(4):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            marcadores.append({"m": f"{gl}-{gv}", "p": p * 100})
    
    return {
        "btts": prob_btts,
        "corners": (l_l + l_v) * 2.8,
        "tarjetas": ref_m * 1.1,
        "marcadores": sorted(marcadores, key=lambda x: x['p'], reverse=True)[:3]
    }

# --- INTERFAZ POR PESTAÑAS ---
st.title("⚽ Predictor Pro: Inteligencia Deportiva Global")
ligas_nombres = list(EQUIPOS_POR_LIGA.keys()) + ["FRANCESA", "PORTUGUESA", "BRASILEÑA", "ARGENTINA", "CHAMPIONS", "EUROPA LEAGUE"]
tabs = st.tabs(ligas_nombres)

for i, tab in enumerate(tabs):
    nombre_liga = ligas_nombres[i]
    with tab:
        st.header(f"Análisis Técnico: {nombre_liga}")
        
        equipos = EQUIPOS_POR_LIGA.get(nombre_liga, ["Equipo Genérico A", "Equipo Genérico B"])
        
        c1, c2 = st.columns(2)
        with c1:
            loc = st.selectbox("Equipo Local", equipos, key=f"l_{i}")
            jugadores_l = obtener_jugadores(loc)
            bajas_l = st.multiselect(f"Bajas de {loc}", [j['n'] for j in jugadores_l], key=f"bl_{i}")
            racha_l = st.multiselect(f"Racha {loc}", ["V", "E", "D"], key=f"rl_{i}")
        
        with c2:
            vis = st.selectbox("Equipo Visitante", equipos, key=f"v_{i}")
            jugadores_v = obtener_jugadores(vis)
            bajas_v = st.multiselect(f"Bajas de {vis}", [j['n'] for j in jugadores_v], key=f"bv_{i}")
            racha_v = st.multiselect(f"Racha {vis}", ["V", "E", "D"], key=f"rv_{i}")

        st.divider()
        ref_media = st.slider("Media de Tarjetas del Árbitro", 2.0, 9.0, 4.0, key=f"ref_{i}")

        if st.button(f"🚀 GENERAR PREDICCIÓN: {loc} vs {vis}", key=f"btn_{i}"):
            # AJUSTE REAL DE LAMBDAS
            imp_l = len(bajas_l) * 0.15
            imp_v = len(bajas_v) * 0.15
            
            # Cálculo de racha: victorias (+0.1), derrotas (-0.1)
            adj_racha_l = (racha_l.count("V") * 0.1) - (racha_l.count("D") * 0.1)
            adj_racha_v = (racha_v.count("V") * 0.1) - (racha_v.count("D") * 0.1)
            
            # Lambdas finales con factor campo (1.15 para local)
            lambda_l = max(0.5, (1.8 + adj_racha_l) * 1.15 * (1 - imp_l))
            lambda_v = max(0.5, (1.3 + adj_racha_v) * 0.85 * (1 - imp_v))
            
            res = realizar_analisis(lambda_l, lambda_v, ref_media)
            
            st.success("### Resultado del Análisis Dinámico")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Ambos Anotan", f"{res['btts']:.1f}%")
            m2.metric("Córners", f"{res['corners']:.1f}")
            m3.metric("Tarjetas Totales", f"{res['tarjetas']:.1f}")
            m4.metric("Goles Esperados", f"{lambda_l + lambda_v:.2f}")

            st.subheader("🎯 Marcadores Exactos Probables")
            cols = st.columns(3)
            for idx, m in enumerate(res['marcadores']):
                cols[idx].info(f"**{m['m']}** ({m['p']:.1f}%)")