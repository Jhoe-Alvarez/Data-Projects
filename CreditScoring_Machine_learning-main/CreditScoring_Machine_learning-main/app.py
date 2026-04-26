import streamlit as st
import pandas as pd
import pickle
import numpy as np

# 1. Configuración de la página
st.set_page_config(
    page_title="Evaluación Crediticia",
    page_icon="🏦",
    layout="centered"
)

st.title("🏦 Sistema de Scoring Crediticio")
st.markdown("Esta herramienta utiliza Inteligencia Artificial para evaluar la probabilidad de incumplimiento de pago (Default) en solicitantes de crédito.")
st.markdown("---")

# 2. Cargar el modelo entrenado
try:
    with open("modelo_riesgo_credito.pkl", "rb") as file:
        model = pickle.load(file)
except FileNotFoundError:
    st.error("⚠️ Error: No se encontró el archivo 'modelo_riesgo_credito.pkl'.")
    st.stop()

# 3. Panel Lateral (Sidebar) para Ingreso de Datos
st.sidebar.header("📝 Datos del Solicitante")
st.sidebar.markdown("Ingrese la información financiera:")

# --- VARIABLES DEL MODELO (Adaptadas a tu Dataset) ---

# A. Datos Personales
edad = st.sidebar.number_input("Edad del Cliente", min_value=18, max_value=100, value=35)
dependientes = st.sidebar.number_input("Número de Dependientes", min_value=0, max_value=20, value=0)

# B. Situación Financiera
ingreso_mensual = st.sidebar.number_input("Ingreso Mensual ($)", min_value=0.0, value=5000.0, step=100.0)
ratio_deuda = st.sidebar.number_input("Ratio Deuda/Ingreso (Ej: 0.30 es 30%)", min_value=0.0, max_value=5.0, value=0.30, step=0.01)

# C. Comportamiento Crediticio (Las variables más fuertes)
uso_credito = st.sidebar.slider("Porcentaje de Uso de Líneas de Crédito", 0.0, 1.0, 0.10, help="1.0 significa que tiene las tarjetas al tope.")
creditos_abiertos = st.sidebar.number_input("Número de Créditos Abiertos", min_value=0, value=2)
prestamos_inmob = st.sidebar.number_input("Préstamos Inmobiliarios", min_value=0, value=0)

# D. Historial de Morosidad (Peligro)
st.sidebar.markdown("---")
st.sidebar.subheader("🚩 Historial de Pagos")
moras_30_59 = st.sidebar.number_input("Veces en mora (30-59 días)", min_value=0, value=0)
moras_60_89 = st.sidebar.number_input("Veces en mora (60-89 días)", min_value=0, value=0)
moras_90 = st.sidebar.number_input("Veces en mora (+90 días)", min_value=0, value=0)

# 4. Botón de Predicción
if st.button("🔍 Evaluar Riesgo de Crédito", type="primary"):

    # Crear DataFrame con los nombres EXACTOS de las columnas que usaste al entrenar
    input_data = pd.DataFrame({
        'porcentaje_uso_credito_no_garantizado': [uso_credito],
        'edad_cliente': [edad],
        'num_moras_30_59_dias': [moras_30_59],
        'ratio_deuda_ingreso': [ratio_deuda],
        'ingreso_mensual': [ingreso_mensual],
        'num_creditos_y_prestamos_abiertos': [creditos_abiertos],
        'num_moras_90_dias': [moras_90],
        'num_prestamos_inmobiliarios': [prestamos_inmob],
        'num_moras_60_89_dias': [moras_60_89],
        'num_dependientes': [dependientes]
    })

    # Realizar predicción
    try:
        # Obtenemos la probabilidad de ser Clase 1 (Moroso)
        probabilidad = model.predict_proba(input_data)[0][1]
        score_riesgo = round(probabilidad * 100, 2)
    except Exception as e:
        st.error(f"Error al predecir: {e}")
        st.stop()

    # 5. Mostrar Resultados
    st.subheader("📊 Resultado del Análisis")

    # Definimos el umbral de negocio (0.35 según tu Fase 5)
    UMBRAL_CORTE = 35.0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Probabilidad de Impago", f"{score_riesgo}%")

    with col2:
        if score_riesgo < 20:
            st.success("✅ RIESGO BAJO")
            mensaje = "El cliente califica para el crédito estándar."
        elif score_riesgo < UMBRAL_CORTE:
            st.warning("⚠️ RIESGO MEDIO")
            mensaje = "El cliente califica, pero se sugiere revisar garantías adicionales."
        else:
            st.error("🚫 RIESGO ALTO (Rechazo Sugerido)")
            mensaje = "La probabilidad de impago supera el límite de seguridad del banco."

    # Barra de progreso visual
    st.progress(int(score_riesgo))
    st.info(mensaje)

    # Detalle técnico (opcional)
    with st.expander("Ver detalle de variables ingresadas"):
        st.dataframe(input_data)
