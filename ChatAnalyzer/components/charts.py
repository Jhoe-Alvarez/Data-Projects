"""
Funciones para crear gráficos con Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import io
import base64
from config.settings import COLORS
from utils.emoji_utils import obtener_top_emojis


def crear_grafico_mensajes_por_autor(df):
    """
    Crea un gráfico de barras con los mensajes por persona
    
    Args:
        df (pd.DataFrame): DataFrame con columna 'autor'
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de barras
    """
    # Contar mensajes por autor
    mensajes_por_autor = df['autor'].value_counts().reset_index()
    mensajes_por_autor.columns = ['Autor', 'Mensajes']
    
    fig = px.bar(
        mensajes_por_autor,
        x='Autor',
        y='Mensajes',
        title='📊 Mensajes por Persona',
        color='Mensajes',
        color_continuous_scale=[COLORS['container'], COLORS['accent_green']],
        template='plotly_dark'
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['container'],
        font=dict(color=COLORS['text_primary'], size=12),
        title_font_size=18,
        title_font_color=COLORS['accent_green'],
        xaxis_title="Persona",
        yaxis_title="Cantidad de Mensajes",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    fig.update_traces(
        marker_line_color=COLORS['accent_green'],
        marker_line_width=1.5,
        opacity=0.8
    )
    
    return fig


def crear_grafico_actividad_por_hora(df):
    """
    Crea un gráfico de línea con la actividad por hora del día
    
    Args:
        df (pd.DataFrame): DataFrame con columna 'fecha_completa'
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de línea
        None: Si no hay datos de fecha_completa
    """
    if 'fecha_completa' not in df.columns:
        return None
    
    # Extraer hora y contar mensajes
    df['hora_num'] = df['fecha_completa'].dt.hour
    actividad_hora = df['hora_num'].value_counts().sort_index().reset_index()
    actividad_hora.columns = ['Hora', 'Mensajes']
    
    # Asegurar que todas las horas estén representadas (0-23)
    todas_horas = pd.DataFrame({'Hora': range(24)})
    actividad_hora = todas_horas.merge(actividad_hora, on='Hora', how='left').fillna(0)
    
    fig = px.line(
        actividad_hora,
        x='Hora',
        y='Mensajes',
        title='⏰ Actividad por Hora del Día',
        markers=True,
        template='plotly_dark'
    )
    
    fig.update_traces(
        line_color=COLORS['accent_green'],
        line_width=3,
        marker=dict(
            size=8,
            color=COLORS['bubble_green'],
            line=dict(color=COLORS['accent_green'], width=2)
        )
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['container'],
        font=dict(color=COLORS['text_primary'], size=12),
        title_font_size=18,
        title_font_color=COLORS['accent_green'],
        xaxis_title="Hora del Día",
        yaxis_title="Cantidad de Mensajes",
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=2,
            range=[-0.5, 23.5]
        ),
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='x unified'
    )
    
    return fig


def crear_grafico_calor_actividad(df):
    """
    Crea un mapa de calor de actividad por día de la semana y hora.

    Args:
        df (pd.DataFrame): DataFrame con columna 'fecha_completa'

    Returns:
        plotly.graph_objects.Figure: Gráfico de mapa de calor
        None: Si no hay datos de fecha_completa
    """
    if 'fecha_completa' not in df.columns:
        return None

    df_calor = df.copy()
    df_calor['hora'] = df_calor['fecha_completa'].dt.hour
    df_calor['dia_semana'] = df_calor['fecha_completa'].dt.day_name()

    orden_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    etiquetas_dias = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo',
    }

    actividad = (
        df_calor.groupby(['dia_semana', 'hora'])
        .size()
        .reset_index(name='Mensajes')
    )

    pivote = actividad.pivot(index='dia_semana', columns='hora', values='Mensajes').reindex(orden_dias).fillna(0)
    pivote.index = [etiquetas_dias[dia] for dia in pivote.index]
    pivote = pivote[[col for col in range(24)]]

    fig = go.Figure(
        data=go.Heatmap(
            z=pivote.values,
            x=[f"{hora:02d}:00" for hora in range(24)],
            y=pivote.index.tolist(),
            colorscale=[
                [0, COLORS['background']],
                [0.35, COLORS['accent_dark_green']],
                [1, COLORS['accent_green']],
            ],
            hovertemplate='Día: %{y}<br>Hora: %{x}<br>Mensajes: %{z}<extra></extra>',
            colorbar=dict(title='Mensajes')
        )
    )

    fig.update_layout(
        title='🔥 Mapa de Calor de Actividad',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['container'],
        font=dict(color=COLORS['text_primary'], size=12),
        title_font_size=18,
        title_font_color=COLORS['accent_green'],
        xaxis_title='Hora del día',
        yaxis_title='Día de la semana',
        margin=dict(l=40, r=40, t=60, b=40),
    )

    return fig


def crear_grafico_top_emojis(df, n=5):
    """
    Crea un gráfico de barras con los emojis más usados
    
    Args:
        df (pd.DataFrame): DataFrame con columna 'mensaje'
        n (int): Número de emojis top a mostrar
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de barras
        None: Si no hay emojis en los mensajes
    """
    # Obtener top emojis
    top_emojis = obtener_top_emojis(df['mensaje'].tolist(), n=n)
    
    if not top_emojis:
        return None
    
    # Crear DataFrame para Plotly
    df_emojis = pd.DataFrame(top_emojis, columns=['Emoji', 'Cantidad'])
    
    fig = px.bar(
        df_emojis,
        x='Emoji',
        y='Cantidad',
        title=f'😀 Top {n} Emojis Más Usados',
        color='Cantidad',
        color_continuous_scale=[COLORS['container'], COLORS['bubble_green']],
        template='plotly_dark',
        text='Cantidad'
    )
    
    fig.update_traces(
        textposition='outside',
        marker_line_color=COLORS['accent_green'],
        marker_line_width=1.5,
        textfont_size=14
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['container'],
        font=dict(color=COLORS['text_primary'], size=12),
        title_font_size=18,
        title_font_color=COLORS['accent_green'],
        xaxis_title="Emoji",
        yaxis_title="Cantidad de Usos",
        xaxis=dict(tickfont=dict(size=30)),  # Emojis más grandes
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def crear_grafico_mensajes_por_dia(df):
    """
    Crea un gráfico de línea con mensajes por día
    
    Args:
        df (pd.DataFrame): DataFrame con columna 'fecha_completa'
        
    Returns:
        plotly.graph_objects.Figure: Gráfico de línea
        None: Si no hay datos de fecha_completa
    """
    if 'fecha_completa' not in df.columns:
        return None
    
    # Extraer fecha y contar mensajes
    df['fecha_solo'] = df['fecha_completa'].dt.date
    mensajes_por_dia = df['fecha_solo'].value_counts().sort_index().reset_index()
    mensajes_por_dia.columns = ['Fecha', 'Mensajes']
    
    fig = px.line(
        mensajes_por_dia,
        x='Fecha',
        y='Mensajes',
        title='📅 Mensajes por Día',
        template='plotly_dark'
    )
    
    fig.update_traces(
        line_color=COLORS['accent_teal'],
        line_width=2,
        fill='tozeroy',
        fillcolor=f"rgba(18, 140, 126, 0.2)"
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['container'],
        font=dict(color=COLORS['text_primary'], size=12),
        title_font_size=18,
        title_font_color=COLORS['accent_green'],
        xaxis_title="Fecha",
        yaxis_title="Cantidad de Mensajes",
        margin=dict(l=40, r=40, t=60, b=40),
        hovermode='x unified'
    )
    
    return fig


def crear_nube_palabras(df):
    """
    Crea una nube de palabras con los mensajes más frecuentes
    
    Args:
        df (pd.DataFrame): DataFrame con columna 'mensaje'
        
    Returns:
        str: Imagen en base64 de la nube de palabras
        None: Si no se pudo crear
    """
    try:
        # Combinar todos los mensajes
        texto_completo = ' '.join(df['mensaje'].astype(str).tolist())
        
        # Palabras comunes en español a ignorar
        stopwords_es = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'ser', 'se', 'no', 'haber',
            'por', 'con', 'su', 'para', 'como', 'estar', 'tener', 'le', 'lo', 'todo',
            'pero', 'más', 'hacer', 'o', 'poder', 'decir', 'este', 'ir', 'otro', 'ese',
            'si', 'me', 'ya', 'ver', 'porque', 'dar', 'cuando', 'él', 'muy', 'sin',
            'vez', 'mucho', 'saber', 'qué', 'sobre', 'mi', 'alguno', 'mismo', 'yo',
            'también', 'hasta', 'año', 'dos', 'querer', 'entre', 'así', 'primero',
            'desde', 'grande', 'eso', 'ni', 'nos', 'llegar', 'pasar', 'tiempo', 'ella',
            'sí', 'día', 'uno', 'bien', 'poco', 'deber', 'entonces', 'poner', 'cosa',
            'tanto', 'hombre', 'parecer', 'nuestro', 'tan', 'donde', 'ahora', 'parte',
            'después', 'vida', 'quedar', 'siempre', 'creer', 'hablar', 'llevar', 'dejar',
            'nada', 'cada', 'seguir', 'menos', 'nuevo', 'encontrar', 'algo', 'solo',
            'aunque', 'país', 'contra', 'aquí', 'casa', 'último', 'salir', 'gente',
            'multimedia', 'omitido', 'http', 'https', 'www', 'com', 'es', 'al', 'del',
            'los', 'las', 'una', 'unos', 'unas', 'te', 'ti', 'tu', 'tus', 'ese', 'esa',
            'q', 'jaja', 'jeje', 'jajaja', 'jejeje', 'xd', 'ok', 'vale'
        }
        
        # Crear nube de palabras
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color=COLORS['background'],
            colormap='Greens',
            stopwords=stopwords_es,
            max_words=100,
            relative_scaling=0.5,
            min_font_size=10
        ).generate(texto_completo)
        
        # Crear figura de matplotlib
        fig = plt.figure(figsize=(10, 5), facecolor=COLORS['background'])
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        
        # Convertir a imagen base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', facecolor=COLORS['background'], bbox_inches='tight')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        
        return img_base64
        
    except Exception as e:
        print(f"Error al crear nube de palabras: {e}")
        return None


def crear_todos_los_graficos(df):
    """
    Crea todos los gráficos principales del dashboard
    
    Args:
        df (pd.DataFrame): DataFrame con los mensajes procesados
        
    Returns:
        dict: Diccionario con todos los gráficos
    """
    graficos = {
        'mensajes_por_autor': crear_grafico_mensajes_por_autor(df),
        'actividad_por_hora': crear_grafico_actividad_por_hora(df),
        'calor_actividad': crear_grafico_calor_actividad(df),
        'top_emojis': crear_grafico_top_emojis(df),
        'mensajes_por_dia': crear_grafico_mensajes_por_dia(df),
        'nube_palabras': crear_nube_palabras(df)
    }
    
    return graficos
