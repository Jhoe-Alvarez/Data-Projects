"""
Configuración y constantes de la aplicación Chatlyzer
"""

# ========================
# COLORES DE WHATSAPP
# ========================
COLORS = {
    'background': '#0b141a',           # Fondo principal oscuro
    'container': '#202c33',            # Contenedores y tarjetas
    'bubble_green': '#dcf8c6',         # Burbujas de mensaje (resultados)
    'text_primary': '#e9edef',         # Texto principal
    'text_secondary': '#d9fdd3',       # Texto secundario
    'accent_green': '#25d366',         # Verde principal de WhatsApp
    'accent_dark_green': '#075e54',    # Verde oscuro
    'accent_teal': '#128c7e',          # Verde azulado
    'hover_green': '#20ba5a',          # Verde hover
    'black': '#000000',                # Negro para contraste
}

# ========================
# CONFIGURACIÓN DE PÁGINA
# ========================
PAGE_CONFIG = {
    'page_title': 'Chatlyzer',
    'page_icon': '💬',
    'layout': 'wide',
    'initial_sidebar_state': 'collapsed'
}

# ========================
# MENSAJES DEL SISTEMA A FILTRAR
# ========================
SYSTEM_MESSAGES = [
    'mensajes y llamadas están cifrados',
    'mensajes están cifrados',
    'cifrados de extremo a extremo',
    'multimedia omitido',
    'se cambió este grupo',
    'cambiaste el ícono del grupo',
    'cambiaste el icono del grupo',
    'cambió la descripción del grupo',
    'cambió el ícono del grupo',
    'cambio el ícono del grupo',
    'cambio el icono del grupo',
    'cambió la configuración del grupo',
    'cambió su foto de perfil',
    'cambió la foto de perfil',
    'cambió tu foto de perfil',
    'cambió la foto del grupo',
    'eliminó la foto del grupo',
    'quitó la foto del grupo',
    'salió',
    'salió del grupo',
    'te agregó',
    'agregó a',
    'añadió a',
    'eliminó a',
    'quitó a',
    'creó el grupo',
    'creó este grupo',
    'cambió el número',
    'cambió de número',
    'cambiaste el número',
    'imagen omitida',
    'video omitido',
    'audio omitido',
    'sticker omitido',
    'gif omitido',
    'documento omitido',
    'contacto omitido',
    'ubicación omitida',
    'encuesta omitida',
    'llamada perdida',
    'videollamada perdida',
    'llamada de voz',
    'llamada de video',
    'se unió usando el enlace',
    'ahora eres administrador',
    'ya no eres administrador',
]

# ========================
# REGEX PATTERNS
# ========================
# Patrón para extraer mensajes de WhatsApp
# Formato: DD/MM/YYYY, HH:MM - Autor: Mensaje
MESSAGE_PATTERN = r'(\d{1,2}/\d{1,2}/\d{2,4}),?\s(\d{1,2}:\d{2}(?:\s?[ap]\.?\s?m\.?)?)\s?-\s?(.*?):\s(.+?)(?=\d{1,2}/\d{1,2}/\d{2,4}|$)'

# Patrón para extraer emojis
EMOJI_PATTERN = (
    "["
    "\U0001F600-\U0001F64F"  # emoticonos
    "\U0001F300-\U0001F5FF"  # símbolos & pictogramas
    "\U0001F680-\U0001F6FF"  # transporte & símbolos de mapa
    "\U0001F1E0-\U0001F1FF"  # banderas
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+"
)

# ========================
# TEXTOS DE LA INTERFAZ
# ========================
TEXTS = {
    'header_title': 'Chatlyzer',
    'header_subtitle': 'Análisis de chats de WhatsApp',
    'upload_label': '📤 Sube tu archivo de chat de WhatsApp (.txt)',
    'upload_help': 'Exporta el chat desde WhatsApp: Menú > Más > Exportar chat (sin multimedia)',
    'error_no_messages': '❌ No se pudieron extraer mensajes del archivo. Verifica el formato.',
    'error_format_info': 'El archivo debe ser una exportación oficial de WhatsApp.',
}
