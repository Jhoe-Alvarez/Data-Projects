"""
Funciones para procesar y limpiar archivos de chat de WhatsApp
"""
import pandas as pd
import re
from config.settings import MESSAGE_PATTERN, SYSTEM_MESSAGES


def limpiar_chat_whatsapp(contenido):
    """
    Limpia y estructura el contenido de un archivo de chat de WhatsApp
    
    Args:
        contenido (str): Contenido del archivo de chat exportado
        
    Returns:
        pd.DataFrame: DataFrame con columnas: fecha, hora, autor, mensaje, fecha_completa
        None: Si no se pudieron extraer mensajes
    """
    # Procesar línea por línea para evitar que los mensajes del sistema se mezclen
    datos_limpios = []
    mensaje_actual = None

    for linea in contenido.splitlines():
        linea = linea.strip()
        if not linea:
            continue

        coincidencia = re.match(
            r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s(\d{1,2}:\d{2}(?:\s?[ap]\.?\s?m\.?)?)\s-\s(?:(.*?):\s)?(.*)$',
            linea
        )

        if coincidencia:
            fecha, hora, autor, mensaje = coincidencia.groups()
            autor = limpiar_nombre_autor(autor or '')
            mensaje = mensaje.strip().replace('\n', ' ')

            # Si la línea no tiene autor, normalmente es un mensaje del sistema
            if not autor:
                mensaje_actual = None
                continue

            # Filtrar mensajes del sistema y autores no válidos
            if es_mensaje_sistema(mensaje) or es_autor_sistema(autor):
                mensaje_actual = None
                continue

            mensaje_actual = {
                'fecha': fecha.strip(),
                'hora': hora.strip(),
                'autor': autor,
                'mensaje': mensaje
            }
            datos_limpios.append(mensaje_actual)
            continue

        # Continuación de mensaje multilínea
        if mensaje_actual is not None:
            mensaje_actual['mensaje'] = f"{mensaje_actual['mensaje']} {linea}".strip()
            if es_mensaje_sistema(mensaje_actual['mensaje']):
                datos_limpios.pop()
                mensaje_actual = None
    
    if not datos_limpios:
        return None
    
    # Crear DataFrame
    df = pd.DataFrame(datos_limpios)
    
    # Convertir fecha y hora a datetime
    df = agregar_fecha_completa(df)
    
    return df


def limpiar_nombre_autor(autor):
    """
    Limpia el nombre del autor eliminando caracteres no deseados
    
    Args:
        autor (str): Nombre del autor
        
    Returns:
        str: Nombre limpio
    """
    # Quitar @
    autor = autor.replace('@', '')
    # Quitar espacios extra
    autor = ' '.join(autor.split())
    # Quitar caracteres especiales al inicio/final
    autor = autor.strip('~+-_.')
    return autor


def es_mensaje_sistema(mensaje):
    """
    Verifica si un mensaje es un mensaje del sistema de WhatsApp
    
    Args:
        mensaje (str): Texto del mensaje
        
    Returns:
        bool: True si es mensaje del sistema, False en caso contrario
    """
    mensaje_lower = mensaje.lower()
    return any(sistema in mensaje_lower for sistema in SYSTEM_MESSAGES)


def es_autor_sistema(autor):
    """
    Verifica si el "autor" es en realidad un mensaje del sistema
    (como cambios de foto de perfil, etc.)
    
    Args:
        autor (str): Nombre del supuesto autor
        
    Returns:
        bool: True si es del sistema, False si es un usuario real
    """
    if not autor:
        return True
    
    autor_lower = autor.lower()
    
    # Frases que indican que no es un usuario real
    frases_sistema = [
        'cambió',
        'eliminó',
        'quitó',
        'agregó',
        'añadió',
        'salió',
        'creó',
        'se unió',
        'ahora es',
        'ya no es',
        'foto de perfil',
        'imagen de perfil',
        'administrador'
    ]
    
    return any(frase in autor_lower for frase in frases_sistema)


def agregar_fecha_completa(df):
    """
    Agrega una columna 'fecha_completa' con el datetime completo
    
    Args:
        df (pd.DataFrame): DataFrame con columnas 'fecha' y 'hora'
        
    Returns:
        pd.DataFrame: DataFrame con columna adicional 'fecha_completa'
    """
    try:
        df['fecha_completa'] = pd.to_datetime(
            df['fecha'] + ' ' + df['hora'],
            format='mixed',
            dayfirst=True,
            errors='coerce'
        )
        # Eliminar filas con fechas inválidas
        df = df.dropna(subset=['fecha_completa'])
    except Exception as e:
        # Si falla la conversión, continuar sin la columna fecha_completa
        print(f"Advertencia: No se pudo convertir fechas: {e}")
    
    return df


def obtener_estadisticas_basicas(df):
    """
    Calcula estadísticas básicas del chat
    
    Args:
        df (pd.DataFrame): DataFrame con los mensajes
        
    Returns:
        dict: Diccionario con estadísticas
    """
    stats = {
        'total_mensajes': len(df),
        'total_participantes': len(df['autor'].unique()),
        'autores': df['autor'].unique().tolist(),
        'promedio_por_persona': len(df) / len(df['autor'].unique()) if len(df['autor'].unique()) > 0 else 0,
    }
    
    # Calcular días de conversación
    if 'fecha_completa' in df.columns and not df['fecha_completa'].isna().all():
        fecha_min = df['fecha_completa'].min()
        fecha_max = df['fecha_completa'].max()
        stats['dias_conversacion'] = (fecha_max - fecha_min).days
        stats['fecha_inicio'] = fecha_min
        stats['fecha_fin'] = fecha_max
    else:
        stats['dias_conversacion'] = None
    
    return stats


def obtener_mensajes_por_autor(df):
    """
    Cuenta mensajes por cada autor
    
    Args:
        df (pd.DataFrame): DataFrame con los mensajes
        
    Returns:
        pd.DataFrame: DataFrame con columnas 'Autor' y 'Mensajes'
    """
    mensajes_por_autor = df['autor'].value_counts().reset_index()
    mensajes_por_autor.columns = ['Autor', 'Mensajes']
    return mensajes_por_autor


def obtener_actividad_por_hora(df):
    """
    Calcula la actividad de mensajes por hora del día
    
    Args:
        df (pd.DataFrame): DataFrame con los mensajes
        
    Returns:
        pd.DataFrame: DataFrame con columnas 'Hora' y 'Mensajes'
        None: Si no hay datos de fecha_completa
    """
    if 'fecha_completa' not in df.columns:
        return None
    
    df['hora_num'] = df['fecha_completa'].dt.hour
    actividad_hora = df['hora_num'].value_counts().sort_index().reset_index()
    actividad_hora.columns = ['Hora', 'Mensajes']
    
    return actividad_hora


def preparar_texto_para_ia(df, max_mensajes=500):
    """
    Prepara el texto del chat para análisis con IA
    
    Args:
        df (pd.DataFrame): DataFrame con los mensajes
        max_mensajes (int): Número máximo de mensajes a incluir
        
    Returns:
        str: Texto formateado para la IA
    """
    # Tomar los últimos N mensajes para no exceder límites
    df_muestra = df.tail(max_mensajes) if len(df) > max_mensajes else df
    
    texto_chat = "\n".join([
        f"{row['autor']}: {row['mensaje']}"
        for _, row in df_muestra.iterrows()
    ])
    
    return texto_chat
