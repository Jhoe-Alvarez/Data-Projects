"""
Estilos CSS personalizados con tema WhatsApp Web
"""
import streamlit as st
from config.settings import COLORS


def aplicar_estilos():
    """Aplica los estilos CSS globales de la aplicación"""
    
    css = f"""
    <style>
        :root {{
            --shell-width: 1240px;
        }}

        /* ========================
           FONDO PRINCIPAL
           ======================== */
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(37, 211, 102, 0.16), transparent 30%),
                radial-gradient(circle at top right, rgba(18, 140, 126, 0.12), transparent 24%),
                linear-gradient(180deg, #071017 0%, {COLORS['background']} 38%, #081018 100%);
        }}

        .block-container {{
            max-width: var(--shell-width);
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }}
        
        /* ========================
           OCULTAR ELEMENTOS DE STREAMLIT
           ======================== */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* ========================
           TARJETAS Y MÉTRICAS
           ======================== */
        [data-testid="stMetric"] {{
            background: linear-gradient(180deg, rgba(32, 44, 51, 0.96), rgba(12, 20, 25, 0.96));
            padding: 1rem 1.1rem;
            border-radius: 18px;
            border: 1px solid rgba(37, 211, 102, 0.12);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.26);
        }}

        div[data-testid="stMetric"] {{
            background-color: transparent;
        }}
        
        div[data-testid="stMetricValue"] {{
            color: {COLORS['accent_green']} !important;
            font-size: 1.95rem !important;
            font-weight: bold;
        }}
        
        div[data-testid="stMetricLabel"] {{
            color: {COLORS['text_primary']} !important;
            font-size: 0.9rem !important;
            letter-spacing: 0.02em;
        }}

        div[data-testid="stMetricDelta"] {{
            color: {COLORS['text_secondary']} !important;
        }}
        
        /* ========================
           TÍTULOS Y TEXTO
           ======================== */
        h1, h2, h3, h4 {{
            color: {COLORS['accent_green']} !important;
            font-family: 'Aptos', 'Trebuchet MS', 'Segoe UI', sans-serif;
            letter-spacing: -0.02em;
        }}
        
        p, div, span, label {{
            color: {COLORS['text_primary']} !important;
        }}

        hr {{
            border-color: rgba(37, 211, 102, 0.12) !important;
        }}
        
        /* ========================
           CONTENEDORES PERSONALIZADOS
           ======================== */
        .element-container {{
            color: {COLORS['text_primary']};
        }}
        
        /* Burbuja de mensaje verde (estilo WhatsApp) */
        .mensaje-verde {{
            background-color: {COLORS['bubble_green']};
            color: {COLORS['black']} !important;
            padding: 15px 20px;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            max-width: 90%;
        }}
        
        /* Burbuja oscura (contenedores de información) */
        .mensaje-oscuro {{
            background: linear-gradient(180deg, rgba(32, 44, 51, 0.97), rgba(15, 22, 28, 0.97));
            color: {COLORS['text_primary']} !important;
            padding: 1.2rem 1.25rem;
            border-radius: 18px;
            margin: 1rem 0;
            border: 1px solid rgba(37, 211, 102, 0.08);
            box-shadow: 0 16px 30px rgba(0, 0, 0, 0.28);
        }}
        
        .mensaje-oscuro h3 {{
            margin-top: 0;
        }}
        
        /* Header personalizado tipo WhatsApp */
        .whatsapp-header {{
            background:
                radial-gradient(circle at top right, rgba(37, 211, 102, 0.16), transparent 30%),
                linear-gradient(135deg, {COLORS['accent_dark_green']} 0%, #0d665f 48%, {COLORS['accent_teal']} 100%);
            padding: 1.4rem 1.5rem;
            border-radius: 24px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 18px 36px rgba(0,0,0,0.28);
            border: 1px solid rgba(255, 255, 255, 0.06);
        }}

        .hero-copy {{
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }}

        .hero-chip-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.15rem;
        }}

        .hero-chip {{
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: rgba(7, 20, 19, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: {COLORS['text_secondary']} !important;
            font-size: 0.82rem;
        }}

        .hero-subtitle {{
            color: {COLORS['text_secondary']} !important;
            margin: 0;
            font-size: 0.95rem;
            max-width: 60rem;
        }}

        .hero-title {{
            margin: 0;
            color: #ffffff !important;
            font-size: 2rem;
            line-height: 1.05;
        }}

        .hero-icon {{
            font-size: 3rem;
            line-height: 1;
            width: 3.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            filter: drop-shadow(0 8px 14px rgba(0, 0, 0, 0.24));
        }}

        .surface-card {{
            background: linear-gradient(180deg, rgba(32, 44, 51, 0.96), rgba(18, 26, 33, 0.96));
            border: 1px solid rgba(37, 211, 102, 0.1);
            border-radius: 22px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 18px 30px rgba(0, 0, 0, 0.24);
        }}

        .surface-card--compact {{
            padding: 0.95rem 1rem;
        }}

        .surface-label {{
            color: {COLORS['text_secondary']} !important;
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            margin-bottom: 0.45rem;
        }}

        .surface-title {{
            margin: 0 0 0.25rem 0;
            font-size: 1.05rem;
            color: #ffffff !important;
        }}

        .surface-text {{
            margin: 0;
            color: {COLORS['text_secondary']} !important;
            line-height: 1.6;
        }}

        .step-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin: 1rem 0 1.1rem 0;
        }}

        .step-card {{
            background: linear-gradient(180deg, rgba(32, 44, 51, 0.95), rgba(14, 21, 26, 0.98));
            border: 1px solid rgba(37, 211, 102, 0.09);
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 14px 24px rgba(0, 0, 0, 0.2);
            min-height: 132px;
        }}

        .step-number {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            background: rgba(37, 211, 102, 0.16);
            color: {COLORS['accent_green']} !important;
            font-weight: 700;
            margin-bottom: 0.8rem;
        }}

        .step-title {{
            margin: 0 0 0.3rem 0;
            color: #ffffff !important;
            font-weight: 700;
        }}

        .step-text {{
            margin: 0;
            color: {COLORS['text_secondary']} !important;
            line-height: 1.55;
            font-size: 0.95rem;
        }}

        .insight-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 0.35rem 0 0.35rem 0;
        }}

        .insight-card {{
            background: linear-gradient(180deg, rgba(24, 35, 41, 0.96), rgba(11, 17, 21, 0.98));
            border: 1px solid rgba(37, 211, 102, 0.1);
            border-radius: 18px;
            padding: 0.95rem 1rem;
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
        }}

        .insight-kicker {{
            display: block;
            color: {COLORS['text_secondary']} !important;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.11em;
            margin-bottom: 0.35rem;
        }}

        .insight-value {{
            display: block;
            font-size: 1.18rem;
            font-weight: 700;
            color: #ffffff !important;
            margin-bottom: 0.2rem;
        }}

        .insight-detail {{
            color: {COLORS['text_secondary']} !important;
            font-size: 0.92rem;
            line-height: 1.45;
        }}

        .section-shell {{
            margin-top: 1.25rem;
        }}

        .section-shell h2 {{
            color: #ffffff !important;
            margin-bottom: 0.65rem;
        }}
        
        /* ========================
           GRÁFICOS
           ======================== */
        .js-plotly-plot {{
            background: linear-gradient(180deg, rgba(32, 44, 51, 0.95), rgba(14, 21, 26, 0.98)) !important;
            border-radius: 18px;
            padding: 0.75rem;
            border: 1px solid rgba(37, 211, 102, 0.08);
        }}
        
        /* ========================
           UPLOADER DE ARCHIVOS
           ======================== */
        [data-testid="stFileUploader"] {{
            background: linear-gradient(180deg, rgba(32, 44, 51, 0.96), rgba(14, 21, 26, 0.98));
            border-radius: 20px;
            padding: 1rem;
            border: 1px solid rgba(37, 211, 102, 0.08);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.2);
        }}
        
        [data-testid="stFileUploader"] section {{
            border: 1.5px dashed {COLORS['accent_green']};
            border-radius: 16px;
            padding: 0.45rem;
        }}
        
        [data-testid="stFileUploader"] section:hover {{
            border-color: {COLORS['hover_green']};
            background-color: rgba(37, 211, 102, 0.05);
        }}
        
        /* ========================
           BOTONES
           ======================== */
        .stButton > button {{
            background: linear-gradient(135deg, {COLORS['accent_green']} 0%, {COLORS['accent_teal']} 100%);
            color: {COLORS['black']};
            border: none;
            border-radius: 999px;
            padding: 0.7rem 1.25rem;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 10px 22px rgba(37, 211, 102, 0.15);
        }}
        
        .stButton > button:hover {{
            background-color: {COLORS['hover_green']};
            box-shadow: 0 4px 8px rgba(37, 211, 102, 0.3);
            transform: translateY(-1px);
        }}
        
        /* ========================
           EXPANDER
           ======================== */
        [data-testid="stExpander"] {{
            background: linear-gradient(180deg, rgba(32, 44, 51, 0.94), rgba(14, 21, 26, 0.96));
            border-radius: 18px;
            border: 1px solid rgba(37, 211, 102, 0.12);
        }}
        
        [data-testid="stExpander"] div[role="button"] {{
            color: {COLORS['accent_green']} !important;
        }}
        
        /* ========================
           DATAFRAME
           ======================== */
        [data-testid="stDataFrame"] {{
            background-color: {COLORS['container']};
            border-radius: 16px;
            overflow: hidden;
        }}
        
        /* ========================
           SPINNER
           ======================== */
        .stSpinner > div {{
            border-top-color: {COLORS['accent_green']} !important;
        }}
        
        /* ========================
           ALERTAS Y NOTIFICACIONES
           ======================== */
        .stAlert {{
            background-color: rgba(32, 44, 51, 0.94);
            color: {COLORS['text_primary']} !important;
            border-radius: 14px;
        }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
