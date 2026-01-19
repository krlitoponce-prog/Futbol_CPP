import streamlit as st
import pandas as pd
from scipy.stats import poisson
import plotly.graph_objects as go

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Football Intelligence Pro", layout="wide")

# (Mantén aquí tu diccionario DATA_MASTER con todas las ligas y equipos)

def calcular_1x2(l_l, l_v):
    """Calcula probabilidades de Victoria Local, Empate y Visitante."""
    prob_l, prob_e, prob_v = 0, 0, 0
    for gl in range(10):
        for gv in range(10):
            p = poisson.pmf(gl, l_l) * poisson.pmf(gv, l_v)
            if gl > gv: prob_l += p
            elif gl == gv: prob_e += p
            else: prob_v += p
    return prob_l, prob_e, prob_v

# --- INTERFAZ ---
st.title("🏆 Sistema de Inteligencia Deportiva: Análisis Elite")

# (Pestañas de Ligas...)

# --- DENTRO DEL BOTÓN DE GENERAR PREDICCIÓN ---
# (Asumiendo que ya calculamos l_l y l_v según xG y Altitud)

if st.button("🚀 GENERAR ANÁLISIS COMPLETO"):
    res = motor_global(l_l, l_v, d_l["alt"], d_v["alt"])
    p_l, p_e, p_v = calcular_1x2(l_l, l_v)
    
    col_izq, col_der = st.columns([1, 1])

    with col_izq:
        st.subheader("📊 Probabilidades 1X2")
        fig = go.Figure(data=[go.Pie(
            labels=['Victoria Local', 'Empate', 'Victoria Visitante'],
            values=[p_l, p_e, p_v],
            hole=.3,
            marker_colors=['#2ecc71', '#95a5a6', '#e74c3c']
        )])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig, use_container_width=True)

    with col_der:
        st.subheader("🎯 Marcadores & Cuotas")
        st.write("El marcador resaltado tiene la **mayor probabilidad estadística**.")
        
        cols_m = st.columns(5)
        for idx, m in enumerate(res['marcadores']):
            with cols_m[idx]:
                # RESALTADO DEL MÁS PROBABLE (El primero de la lista)
                if idx == 0:
                    color = "inverse" # Resalta en color fuerte (azul/verde)
                    label = "🔥 MÁS PROBABLE"
                else:
                    color = "normal"
                    label = f"Opción {idx+1}"
                
                st.metric(label=label, value=m['m'], delta=f"{m['p']:.1f}%", delta_color=color)
                st.caption(f"Cuota Justa: {100/m['p']:.2f}")
                st.success(f"Pinnacle: **{round(100/m['p']*0.97, 2)}**")

    # (Resto de métricas: BTTS, Córners, Tarjetas...)