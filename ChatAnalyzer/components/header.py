"""
Componentes de UI reutilizables
"""
import streamlit as st
from config.settings import COLORS, TEXTS


def mostrar_header():
    """Muestra el header principal de la aplicación estilo WhatsApp"""
    st.markdown(f"""
    <div class="whatsapp-header">
        <div class="hero-icon">💬</div>
        <div class="hero-copy">
            <h1 class="hero-title">{TEXTS['header_title']}</h1>
            <p class="hero-subtitle">{TEXTS['header_subtitle']}</p>
            <div class="hero-chip-row">
                <span class="hero-chip">📄 Chat TXT</span>
                <span class="hero-chip">📊 Métricas claras</span>
                <span class="hero-chip">☁️ Nube de palabras</span>
                <span class="hero-chip">🔒 Procesamiento local</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def mostrar_metricas(stats):
    """
    Muestra las métricas principales del chat
    
    Args:
        stats (dict): Diccionario con estadísticas del chat
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💬 Total Mensajes", f"{stats['total_mensajes']:,}")
    
    with col2:
        st.metric("👥 Participantes", stats['total_participantes'])
    
    with col3:
        if stats['dias_conversacion'] is not None:
            st.metric("📅 Días de Chat", f"{stats['dias_conversacion']:,}")
        else:
            st.metric("📅 Días de Chat", "N/A")
    
    with col4:
        st.metric("📊 Promedio/Persona", f"{stats['promedio_por_persona']:.0f}")


def mostrar_burbuja_mensaje(contenido, tipo='oscuro'):
    """
    Muestra contenido en una burbuja tipo WhatsApp
    
    Args:
        contenido (str): Contenido HTML o texto a mostrar
        tipo (str): 'oscuro' o 'verde'
    """
    clase = 'mensaje-oscuro' if tipo == 'oscuro' else 'mensaje-verde'
    
    st.markdown(f"""
    <div class="{clase}">
        {contenido}
    </div>
    """, unsafe_allow_html=True)


def mostrar_advertencia_api():
    """Muestra una nota neutra sobre el análisis local"""
    st.info("La aplicación procesa los chats de WhatsApp de forma local y no requiere configuración adicional.")


def mostrar_seccion_titulo(titulo, icono=""):
    """
    Muestra un título de sección con estilo
    
    Args:
        titulo (str): Título de la sección
        icono (str): Emoji o icono opcional
    """
    st.markdown(f"## {icono} {titulo}" if icono else f"## {titulo}")


def mostrar_error_archivo():
    """Muestra error cuando no se puede procesar el archivo"""
    st.error(TEXTS['error_no_messages'])
    st.info(TEXTS['error_format_info'])


def agregar_espaciado(cantidad=1):
    """
    Agrega espaciado vertical
    
    Args:
        cantidad (int): Número de líneas en blanco
    """
    st.markdown("<br>" * cantidad, unsafe_allow_html=True)


def mostrar_instrucciones_exportacion():
    """Muestra instrucciones para exportar chat de WhatsApp"""
    with st.expander("❓ ¿Cómo exportar mi chat de WhatsApp?"):
        st.markdown("""
        ### 📱 Pasos para exportar tu chat:
        
        1. **Abre WhatsApp** en tu teléfono
        2. **Entra al chat** que quieres analizar
        3. **Toca el nombre** del contacto o grupo (parte superior)
        4. Desplázate hacia abajo y selecciona **"Exportar chat"**
        5. Elige la opción **"Sin multimedia"**
        6. Guarda el archivo `.txt` en tu dispositivo o envíalo a tu computadora
        7. **Sube el archivo** aquí usando el botón de arriba 👆
        
        ---
        
        💡 **Nota:** La aplicación solo procesa el archivo localmente. Tus conversaciones no se almacenan en ningún servidor.
        """)
