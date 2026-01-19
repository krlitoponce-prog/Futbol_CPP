import streamlit as st
import sqlite3
import pandas as pd
from scipy.stats import poisson

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Predictor Pro Premier", layout="wide")

# --- LISTA OFICIAL PREMIER LEAGUE 2025/26 ---
equipos_20 = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", 
    "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town", 
    "Leicester City", "Liverpool", "Manchester City", "Manchester United", 
    "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham Hotspur", 
    "West Ham United", "Wolverhampton"
]

class MotorAvanzado:
    def calcular_poisson_con_cuotas(self, l_local, l_visitante):
        resultados = []
        for g_l in range(5):
            for g_v in range(5):
                prob = poisson.pmf(g_l, l_local) * poisson.pmf(g_v, l_visitante)
                prob_pct = prob * 100
                cuota_justa = 1 / prob if prob > 0 else 0
                resultados.append({
                    'marcador': f"{g_l}-{g_v}",
                    'prob': prob_pct,
                    'cuota_justa': cuota_justa
                })
        return sorted(resultados, key=lambda x: x['prob'], reverse=True)[:5]

st.title("⚽ Predictor Elite: Premier League & Comparador de Valor")
motor = MotorAvanzado()

# --- PANEL DE SELECCIÓN ---
col_l, col_v = st.columns(2)
with col_l:
    st.subheader("Casa (Local)")
    equipo_l = st.selectbox("Selecciona Equipo Local", equipos_20, index=12) # Man City defecto
    baja_creativa = st.slider(f"Nivel de bajas creativas ({equipo_l})", 0, 100, 0)

with col_v:
    st.subheader("Visita (Visitante)")
    equipo_v = st.selectbox("Selecciona Equipo Visitante", equipos_20, index=11) # Liverpool defecto
    baja_defensiva = st.slider(f"Vulnerabilidad defensiva por bajas ({equipo_v})", 0, 100, 0)

# --- CÁLCULO DE PROBABILIDAD ---
# Lambdas base (esto se automatizará con el scraper después)
l_l = 2.1 * (1 - (baja_creativa / 100))
l_v = 1.4 * (1 + (baja_defensiva / 100))

if st.button("🚀 ANALIZAR MARCADORES Y CUOTAS"):
    st.divider()
    res = motor.calcular_poisson_con_cuotas(l_l, l_v)
    
    st.subheader(f"Top 5 Resultados: {equipo_l} vs {equipo_v}")
    
    # Mostrar tarjetas de resultados
    cols = st.columns(5)
    for i, r in enumerate(res):
        with cols[i]:
            st.metric(label=f"Marcador {r['marcador']}", value=f"{r['prob']:.1f}%")
            st.caption(f"Cuota Justa: {r['cuota_justa']:.2f}")

    # --- COMPARADOR DE CUOTAS ---
    st.divider()
    st.subheader("⚖️ Comparador de Valor vs Casas de Apuestas")
    
    # Simulamos cuotas de mercado para comparar
    data_valor = []
    for r in res:
        cuota_mercado = r['cuota_justa'] * 0.9  # Simulación: las casas suelen pagar menos
        ventaja = (r['prob']/100 * cuota_mercado) - 1
        data_valor.append({
            "Marcador": r['marcador'],
            "Nuestra Probabilidad": f"{r['prob']:.1f}%",
            "Nuestra Cuota Justa": round(r['cuota_justa'], 2),
            "Cuota en Casa Apuestas": round(cuota_mercado + 1.0, 2), # Ajuste visual
            "¿Hay Valor?": "✅ SÍ" if ventaja > 0 else "❌ NO"
        })
    
    st.table(pd.DataFrame(data_valor))
    
        
    st.info("""
    **Interpretación del Marcador Exacto:**
    El porcentaje indicado es la probabilidad estadística de que ese resultado ocurra. 
    Un 10% de probabilidad equivale a una cuota de 10.00. Si la casa de apuestas paga más de 10.00, tienes una apuesta con 'Valor'.
    """)