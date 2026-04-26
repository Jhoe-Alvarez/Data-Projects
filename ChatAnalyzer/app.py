"""
Chatlyzer - Aplicación Principal
Análisis de chats de WhatsApp

Aplicación modular para analizar conversaciones de WhatsApp
con visualizaciones interactivas y estadísticas del chat.
"""

import streamlit as st
import json

# Importar módulos personalizados
from config import PAGE_CONFIG, TEXTS
from components import (
    aplicar_estilos,
    mostrar_header,
    mostrar_metricas,
    mostrar_error_archivo,
    mostrar_seccion_titulo,
    mostrar_burbuja_mensaje,
    agregar_espaciado,
    mostrar_instrucciones_exportacion
)
from utils import (
    limpiar_chat_whatsapp,
    obtener_estadisticas_basicas
)
from components.charts import crear_todos_los_graficos
from utils.emoji_utils import obtener_top_emojis


# ========================
# CONFIGURACIÓN DE PÁGINA
# ========================
st.set_page_config(**PAGE_CONFIG)


# ========================
# INTERFAZ PRINCIPAL
# ========================
def main():
    """Función principal de la aplicación"""
    
    # Aplicar estilos CSS personalizados
    aplicar_estilos()
    
    # Mostrar header
    mostrar_header()
    
    agregar_espaciado(1)
    
    # Mostrar instrucciones de exportación
    mostrar_instrucciones_exportacion()
    
    # Uploader de archivo
    archivo = st.file_uploader(
        TEXTS['upload_label'],
        type=['txt'],
        help=TEXTS['upload_help']
    )

    if archivo is None:
        mostrar_panel_bienvenida()
        return
    
    # Procesar archivo si fue subido
    procesar_archivo(archivo)


def mostrar_panel_bienvenida():
    """Muestra una guía visual antes de cargar un archivo."""
    st.markdown(
        """
        <div class="surface-card section-shell">
            <div class="surface-label">Antes de empezar</div>
            <h2 class="surface-title">Sube tu exportación de WhatsApp y deja que el panel se ordene solo.</h2>
            <p class="surface-text">Vas a ver primero un resumen, luego los gráficos más importantes y al final la vista previa técnica. Todo corre localmente.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='step-grid'>" , unsafe_allow_html=True)
    pasos = [
        ("1", "Exporta el chat", "Desde WhatsApp elige Exportar chat y guarda el .txt sin multimedia."),
        ("2", "Carga el archivo", "Súbelo aquí para que la app limpie los mensajes del sistema."),
        ("3", "Revisa el análisis", "Explora participantes, actividad, emojis y la nube de palabras."),
    ]
    for numero, titulo, texto in pasos:
        st.markdown(f"""
        <div class="step-card">
            <div class="step-number">{numero}</div>
            <div class="step-title">{titulo}</div>
            <div class="step-text">{texto}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def procesar_archivo(archivo):
    """
    Procesa el archivo de chat y muestra todos los análisis
    
    Args:
        archivo: Archivo subido por el usuario
    """
    # Leer y procesar archivo
    contenido = archivo.read().decode('utf-8', errors='ignore')
    df = limpiar_chat_whatsapp(contenido)
    
    # Validar que se extrajeran mensajes
    if df is None or len(df) == 0:
        mostrar_error_archivo()
        return
    
    # Obtener estadísticas básicas
    stats = obtener_estadisticas_basicas(df)
    
    # Mostrar métricas principales
    agregar_espaciado(1)
    mostrar_metricas(stats)
    agregar_espaciado(1)

    mostrar_panel_resumen_rapido(df, stats)
    agregar_espaciado(1)

    mostrar_panel_exportacion(df, stats)
    agregar_espaciado(1)
    
    # Sección de Dashboard Analítico
    mostrar_seccion_dashboard(df)
    
    # Vista previa de datos (para debugging)
    mostrar_vista_previa_datos(df)


def mostrar_seccion_dashboard(df):
    """
    Muestra la sección de dashboard con gráficos
    
    Args:
        df: DataFrame con los mensajes procesados
    """
    mostrar_seccion_titulo("Dashboard Analítico", "📈")
    
    # Crear todos los gráficos
    graficos = crear_todos_los_graficos(df)
    
    st.markdown(
        """
        <div class="surface-card section-shell">
            <div class="surface-label">Lectura visual</div>
            <h2 class="surface-title">Ordenado de lo más importante a lo más exploratorio</h2>
            <p class="surface-text">Primero personas y actividad, luego fechas y emojis, y al final la nube de palabras para contexto global.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Organizar en columnas con prioridad visual
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de mensajes por autor
        if graficos['mensajes_por_autor']:
            st.plotly_chart(graficos['mensajes_por_autor'], use_container_width=True)
    
    with col2:
        # Gráfico de actividad por hora
        if graficos['actividad_por_hora']:
            st.plotly_chart(graficos['actividad_por_hora'], use_container_width=True)

    agregar_espaciado(1)

    if graficos['calor_actividad']:
        st.plotly_chart(graficos['calor_actividad'], use_container_width=True)

    agregar_espaciado(1)

    col3, col4 = st.columns(2)

    with col3:
        if graficos['mensajes_por_dia']:
            st.plotly_chart(graficos['mensajes_por_dia'], use_container_width=True)

    with col4:
        if graficos['top_emojis']:
            st.plotly_chart(graficos['top_emojis'], use_container_width=True)
    
    # Nube de palabras (ancho completo)
    agregar_espaciado(1)
    if graficos['nube_palabras']:
        st.markdown("### ☁️ Nube de Palabras Más Frecuentes")
        st.markdown(f"""
        <div class="mensaje-oscuro" style="text-align: center;">
            <img src="data:image/png;base64,{graficos['nube_palabras']}" 
                 style="width: 100%; max-width: 900px; border-radius: 8px;">
        </div>
        """, unsafe_allow_html=True)
        agregar_espaciado(1)


def mostrar_panel_resumen_rapido(df, stats):
    """Muestra un resumen rápido para ordenar la lectura del dashboard."""
    mensajes_por_autor = df['autor'].value_counts()
    autor_top = mensajes_por_autor.index[0]
    cantidad_top = int(mensajes_por_autor.iloc[0])

    if 'fecha_completa' in df.columns and not df['fecha_completa'].isna().all():
        hora_top = int(df['fecha_completa'].dt.hour.value_counts().idxmax())
        hora_detalle = f"{hora_top:02d}:00 a {hora_top:02d}:59"
    else:
        hora_detalle = "No disponible"

    top_emojis = obtener_top_emojis(df['mensaje'].tolist(), n=1)
    emoji_top = top_emojis[0][0] if top_emojis else "—"

    st.markdown(
        f"""
        <div class="insight-grid">
            <div class="insight-card">
                <span class="insight-kicker">Participante dominante</span>
                <span class="insight-value">{autor_top}</span>
                <div class="insight-detail">{cantidad_top:,} mensajes dentro de la conversación.</div>
            </div>
            <div class="insight-card">
                <span class="insight-kicker">Hora con más actividad</span>
                <span class="insight-value">{hora_detalle}</span>
                <div class="insight-detail">Sirve para identificar el tramo más intenso del chat.</div>
            </div>
            <div class="insight-card">
                <span class="insight-kicker">Emoji más repetido</span>
                <span class="insight-value">{emoji_top}</span>
                <div class="insight-detail">Da una pista rápida del tono emocional del grupo.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_panel_exportacion(df, stats):
    """Muestra un panel con descargas para compartir el análisis."""
    resumen = {
        'total_mensajes': int(stats['total_mensajes']),
        'total_participantes': int(stats['total_participantes']),
        'promedio_por_persona': round(stats['promedio_por_persona'], 2),
        'dias_conversacion': stats['dias_conversacion'],
        'autores': stats['autores'],
    }

    csv_bytes = df.to_csv(index=False).encode('utf-8-sig')
    resumen_bytes = json.dumps(resumen, ensure_ascii=False, indent=2, default=str).encode('utf-8')

    st.markdown(
        """
        <div class="surface-card section-shell">
            <div class="surface-label">Exportación</div>
            <h2 class="surface-title">Descarga el análisis para compartirlo o guardarlo</h2>
            <p class="surface-text">Puedes llevarte el chat limpio en CSV y un resumen en JSON con las métricas principales.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Descargar chat limpio (CSV)",
            data=csv_bytes,
            file_name="chat_limpio.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col2:
        st.download_button(
            label="⬇️ Descargar resumen (JSON)",
            data=resumen_bytes,
            file_name="resumen_chat.json",
            mime="application/json",
            use_container_width=True,
        )


def mostrar_vista_previa_datos(df):
    """
    Muestra una vista previa de los datos procesados
    
    Args:
        df: DataFrame con los mensajes procesados
    """
    with st.expander("🔍 Ver datos procesados"):
        st.dataframe(df.head(50), use_container_width=True)
        
        # Información adicional
        st.markdown("---")
        st.markdown(f"""
        **Información del DataFrame:**
        - Total de filas: {len(df):,}
        - Columnas: {', '.join(df.columns.tolist())}
        """)


# ========================
# PUNTO DE ENTRADA
# ========================
if __name__ == "__main__":
    main()

