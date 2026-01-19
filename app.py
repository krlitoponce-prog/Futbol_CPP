import streamlit as st
import sqlite3
import pandas as pd

# 1. Configuración de página (DEBE SER LA PRIMERA LÍNEA DE STREAMLIT)
st.set_page_config(page_title="Predicciones Premier", layout="wide")

# 2. Lógica de Base de Datos
def inicializar_db():
    conn = sqlite3.connect('predicciones_futbol.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS equipos (id_equipo INTEGER PRIMARY KEY, nombre TEXT, elo_actual REAL)')
    conn.commit()
    conn.close()

# 3. Interfaz Visual
st.title("⚽ Sistema de Predicción: Premier League")
st.sidebar.header("Panel de Control")

inicializar_db()

st.write("### Análisis de Próximos Partidos")

# Simulación de los datos que procesará tu scraper
col1, col2 = st.columns(2)

with col1:
    st.info("**Manchester City vs Liverpool**")
    st.warning("⚠️ Baja detectada: Kevin De Bruyne (Motor del equipo)")
    st.write("Impacto en marcador: Tendencia al UNDER 2.5 goles.")

with col2:
    st.info("**Arsenal vs Chelsea**")
    st.success("✅ Plantillas completas")
    st.write("Probabilidad Local: 62% | Cuota sugerida: 1.65")

if st.button("Ejecutar Simulación de Marcador Exacto"):
    st.balloons()
    st.success("Cálculo completado: El marcador más probable es 1 - 1")