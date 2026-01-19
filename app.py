import streamlit as st
import sqlite3
import pandas as pd
import requests
from scipy.stats import poisson

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Predictor Elite Premier", layout="wide")

# --- CLASE PRINCIPAL DEL SISTEMA ---
class MotorPrediccion:
    def __init__(self):
        self.db = 'predicciones_futbol.db'
        self.inicializar_db()

    def inicializar_db(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        # Tabla de partidos (Historial y Próximos)
        c.execute('''CREATE TABLE IF NOT EXISTS partidos 
                     (id INTEGER PRIMARY KEY, fecha TEXT, local TEXT, visitante TEXT, 
                      goles_l INTEGER, goles_v INTEGER, xG_l REAL, xG_v REAL)''')
        conn.commit()
        conn.close()

    def scrapear_premier_actual(self):
        """
        Simulación de scraping de SofaScore/FBRef para la temporada 2025/26.
        En producción, aquí se integrarían las peticiones API.
        """
        datos = [
            ('2026-01-18', 'Man City', 'Liverpool', 2, 2, 1.8, 1.5),
            ('2026-01-18', 'Arsenal', 'Chelsea', 1, 0, 2.1, 0.9)
        ]
        conn = sqlite3.connect(self.db)
        df = pd.DataFrame(datos, columns=['fecha', 'local', 'visitante', 'goles_l', 'goles_v', 'xG_l', 'xG_v'])
        df.to_sql('partidos', conn, if_exists='append', index=False)
        conn.close()
        return "✅ Datos de la temporada actual sincronizados."

    def calcular_poisson(self, l_local, l_visitante):
        """Calcula matriz de probabilidad para marcador exacto."""
        probabilidades = []
        for g_l in range(5):
            for g_v in range(5):
                prob = poisson.pmf(g_l, l_local) * poisson.pmf(g_v, l_visitante)
                probabilidades.append({'marcador': f"{g_l}-{g_v}", 'prob': prob * 100})
        return sorted(probabilidades, key=lambda x: x['prob'], reverse=True)[:5]

# --- INTERFAZ DE USUARIO (Streamlit) ---
st.title("⚽ Predictor de Fútbol Avanzado (Basado en IDUS Sevilla)")
motor = MotorPrediccion()

# Barra lateral para acciones
with st.sidebar:
    st.header("⚙️ Gestión de Datos")
    if st.button("Sincronizar Liga Inglesa (SofaScore)"):
        msg = motor.scrapear_premier_actual()
        st.success(msg)

st.header("📊 Análisis de Partido y Bajas")

# Formulario de Predicción
col_l, col_v = st.columns(2)
with col_l:
    equipo_l = st.selectbox("Local", ["Man City", "Arsenal", "Liverpool", "Man Utd"])
    baja_motor = st.checkbox(f"¿Falta el 'Motor' del {equipo_l}? (Ej. De Bruyne)")
with col_v:
    equipo_v = st.selectbox("Visitante", ["Chelsea", "Spurs", "Newcastle", "Aston Villa"])
    baja_muro = st.checkbox(f"¿Falta el 'Muro' del {equipo_v}? (Ej. Van Dijk)")

# Lógica de Ajuste
l_l = 1.9  # Media base local
l_v = 1.1  # Media base visitante

if baja_motor: l_l *= 0.85  # Penalización por falta de creación
if baja_muro: l_v += 0.3    # Bonus para el rival por debilidad defensiva

if st.button("🚀 Calcular Marcador Exacto"):
    st.divider()
    res = motor.calcular_poisson(l_l, l_v)
    
    st.subheader(f"Probabilidades para {equipo_l} vs {equipo_v}")
    
    cols = st.columns(len(res))
    for i, r in enumerate(res):
        with cols[i]:
            st.metric(label=f"Marcador: {r['marcador']}", value=f"{r['prob']:.1f}%")
    
    
    
    st.info(f"**Análisis Técnico:** La ausencia de piezas clave ha desplazado el marcador más probable hacia un resultado de {'bajos goles' if baja_motor else 'alta vulnerabilidad'}.")