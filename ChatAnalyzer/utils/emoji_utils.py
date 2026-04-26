"""
Utilidades para procesamiento de emojis
"""
import re
from collections import Counter
from config.settings import EMOJI_PATTERN


def extraer_emojis(texto):
    """
    Extrae todos los emojis de un texto
    
    Args:
        texto (str): Texto del que extraer emojis
        
    Returns:
        list: Lista de emojis encontrados
    """
    patron_emoji = re.compile(EMOJI_PATTERN, flags=re.UNICODE)
    return patron_emoji.findall(str(texto))


def contar_emojis(lista_mensajes):
    """
    Cuenta la frecuencia de emojis en una lista de mensajes
    
    Args:
        lista_mensajes (list): Lista de mensajes de texto
        
    Returns:
        Counter: Contador de emojis con sus frecuencias
    """
    todos_emojis = []
    for mensaje in lista_mensajes:
        todos_emojis.extend(extraer_emojis(mensaje))
    
    return Counter(todos_emojis)


def obtener_top_emojis(lista_mensajes, n=5):
    """
    Obtiene los N emojis más usados
    
    Args:
        lista_mensajes (list): Lista de mensajes de texto
        n (int): Número de emojis top a retornar
        
    Returns:
        list: Lista de tuplas (emoji, cantidad)
    """
    contador = contar_emojis(lista_mensajes)
    return contador.most_common(n)


def tiene_emojis(texto):
    """
    Verifica si un texto contiene emojis
    
    Args:
        texto (str): Texto a verificar
        
    Returns:
        bool: True si contiene emojis, False en caso contrario
    """
    return len(extraer_emojis(texto)) > 0
