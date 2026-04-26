"""
Integración con Google Gemini para análisis de chat con IA
"""
import streamlit as st
import google.generativeai as genai
from config.settings import (
    GEMINI_MODEL,
    MAX_MESSAGES_FOR_AI,
    AI_ANALYSIS_PROMPT_TEMPLATE
)
from utils.data_processing import preparar_texto_para_ia


def configurar_gemini():
    """
    Configura la API de Gemini desde secrets o variable de entorno
    
    Returns:
        bool: True si la configuración fue exitosa, False en caso contrario
    """
    try:
        # Intenta obtener desde st.secrets
        api_key = st.secrets.get("GOOGLE_API_KEY", None)
        if api_key:
            genai.configure(api_key=api_key)
            return True
    except Exception as e:
        print(f"No se pudo cargar API Key desde secrets: {e}")
    
    # Alternativa: Variable de entorno manual (para desarrollo local)
    # Descomenta y reemplaza con tu clave si trabajas localmente
    # genai.configure(api_key="TU_CLAVE_AQUÍ")
    # return True
    
    return False


def verificar_gemini_disponible():
    """
    Verifica si Gemini está configurado y disponible
    
    Returns:
        bool: True si está disponible, False en caso contrario
    """
    return configurar_gemini()


def analizar_chat_con_gemini(df):
    """
    Envía el chat a Gemini para análisis psicológico profundo
    
    Args:
        df (pd.DataFrame): DataFrame con los mensajes del chat
        
    Returns:
        str: Análisis generado por Gemini
        str: Mensaje de error si falló
    """
    try:
        # Preparar el texto del chat
        texto_chat = preparar_texto_para_ia(df, max_mensajes=MAX_MESSAGES_FOR_AI)
        
        # Crear el prompt completo
        prompt = AI_ANALYSIS_PROMPT_TEMPLATE.format(chat_text=texto_chat)
        
        # Generar análisis con Gemini
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        error_str = str(e)
        
        # Detectar error de cuota excedida
        if "429" in error_str or "quota" in error_str.lower():
            error_msg = f"""
⚠️ **Cuota de API Excedida**

Tu API Key gratuita ha alcanzado su límite diario de uso.

**📊 Mientras tanto, disfruta de las visualizaciones:**
- ✅ Gráficos estadísticos disponibles
- ✅ Métricas de participación
- ✅ Análisis de emojis
- ✅ Actividad por hora

**🔧 Soluciones:**

1. **Esperar** hasta mañana (las cuotas se renuevan cada 24h)
2. **Nueva API Key**: Crea otra en https://makersuite.google.com/app/apikey
3. **Plan de pago**: Considera Google AI Studio con plan pago para uso ilimitado

**💡 Tip:** El análisis básico (sin IA) sigue funcionando perfectamente.
"""
        else:
            error_msg = f"""
⚠️ **Error al conectar con Gemini**

**Detalles del error:**
{error_str[:500]}

**Posibles soluciones:**
1. Verifica tu conexión a internet
2. Revisa que la API Key sea válida
3. Intenta con otra API Key
4. Verifica en: https://ai.dev/rate-limit

**Mientras tanto:** La app sigue funcionando con todos los gráficos y estadísticas.
"""
        return error_msg


def generar_analisis_resumido(df):
    """
    Genera un análisis resumido sin usar IA (alternativa local)
    
    Args:
        df (pd.DataFrame): DataFrame con los mensajes
        
    Returns:
        str: Análisis básico en formato texto
    """
    from utils import obtener_estadisticas_basicas, obtener_mensajes_por_autor
    
    stats = obtener_estadisticas_basicas(df)
    mensajes_por_autor = obtener_mensajes_por_autor(df)
    
    # Calcular participación
    autor_principal = mensajes_por_autor.iloc[0]
    porcentaje_principal = (autor_principal['Mensajes'] / stats['total_mensajes']) * 100
    
    analisis = f"""
🔍 **Análisis Básico del Chat**

**Estadísticas Generales:**
- Total de mensajes: {stats['total_mensajes']:,}
- Participantes: {stats['total_participantes']}
- Promedio por persona: {stats['promedio_por_persona']:.1f} mensajes

**Participación:**
- **{autor_principal['Autor']}** es quien más participa con {autor_principal['Mensajes']:,} mensajes ({porcentaje_principal:.1f}%)

**Observaciones:**
- La conversación se extiende por {stats['dias_conversacion']} días
- Hay un total de {stats['total_mensajes']:,} intercambios registrados

---

💡 **Nota:** Este es un análisis básico. Para obtener un análisis psicológico profundo con IA, configura tu API Key de Google Gemini.
"""
    
    return analisis


def obtener_analisis(df, usar_ia=True):
    """
    Obtiene el análisis del chat (con IA o básico)
    
    Args:
        df (pd.DataFrame): DataFrame con los mensajes
        usar_ia (bool): Si True, intenta usar IA; si False, usa análisis básico
        
    Returns:
        tuple: (texto_analisis, es_con_ia)
    """
    if usar_ia and verificar_gemini_disponible():
        analisis = analizar_chat_con_gemini(df)
        return analisis, True
    else:
        analisis = generar_analisis_resumido(df)
        return analisis, False
