# ui/styles.py — Estilos do MyPredict 2.0 (Painel EA Sports)
import streamlit as st

def injetar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        * { font-family: 'Inter', sans-serif; }

        .stApp {
            background: linear-gradient(135deg, #0a0a0f 0%, #14141f 50%, #0a0a0f 100%);
            background-attachment: fixed;
        }

        /* Títulos */
        .main-title {
            font-size: 3.2rem;
            font-weight: 900;
            text-align: center;
            background: linear-gradient(135deg, #ffd700, #ffaa00);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
            letter-spacing: -1px;
        }
        .subtitle {
            text-align: center;
            color: #aaa;
            font-size: 0.9rem;
            margin-bottom: 2rem;
            letter-spacing: 3px;
            text-transform: uppercase;
        }
        .section-title {
            font-size: 1.8rem;
            font-weight: 800;
            text-align: center;
            color: #ffd700;
            margin: 32px 0 16px 0;
            letter-spacing: -0.5px;
        }

        /* Times - Cards de Confronto */
        .confronto-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 30px;
            margin: 20px 0 30px 0;
        }
        .time-card {
            background: rgba(20, 20, 35, 0.95);
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 20px;
            padding: 20px 25px;
            text-align: center;
            min-width: 200px;
            backdrop-filter: blur(10px);
        }
        .time-card.destaque {
            border: 2px solid #ffd700;
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.3);
        }
        .time-nome {
            font-size: 1.6rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 8px;
        }
        .time-detalhe {
            font-size: 0.85rem;
            color: #ccc;
        }
        .vs-divider {
            font-size: 2rem;
            font-weight: 900;
            color: #ffd700;
        }

        /* Painel de Atributos */
        .atributo-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }
        .atributo-card {
            background: rgba(20, 20, 35, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 12px 16px;
            display: flex;
            flex-direction: column;
        }
        .atributo-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .atributo-nome {
            font-size: 0.9rem;
            font-weight: 600;
            color: #fff;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .atributo-valor {
            font-size: 1.8rem;
            font-weight: 900;
            color: #ffd700;
        }
        .atributo-barra {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 4px;
        }
        .atributo-barra-preenchimento {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
        }

        /* Cores das barras por categoria */
        .ataque { background: linear-gradient(90deg, #ff4444, #ff6b6b); }
        .defesa { background: linear-gradient(90deg, #4488ff, #6ba3ff); }
        .meio { background: linear-gradient(90deg, #44bb44, #6fda6f); }
        .cons { background: linear-gradient(90deg, #ffaa00, #ffcc44); }
        .res { background: linear-gradient(90deg, #aa44ff, #cc88ff); }
        .global { background: linear-gradient(90deg, #ffd700, #ffed4a); }

        /* Tabela de Jogos */
        .jogos-tabela {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            color: #fff;
            font-size: 0.9rem;
        }
        .jogos-tabela th {
            color: #ffd700;
            font-weight: 600;
            padding: 6px 8px;
            border-bottom: 1px solid #333;
            text-align: left;
            font-size: 0.8rem;
            text-transform: uppercase;
        }
        .jogos-tabela td {
            padding: 6px 8px;
            border-bottom: 1px solid #222;
        }
        .resultado-V { color: #4caf50; font-weight: 700; }
        .resultado-E { color: #ffc107; font-weight: 700; }
        .resultado-D { color: #f44336; font-weight: 700; }

        /* Estatísticas Pequenas */
        .stat-pequena {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.05);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            color: #ddd;
        }
        .stat-pequena span {
            color: #ffd700;
            font-weight: 700;
        }

        /* Botão */
        .stButton > button {
            background: linear-gradient(135deg, #ffd700, #ff8c00);
            color: #000;
            border: none;
            font-weight: 700;
            font-size: 1.1rem;
            border-radius: 14px;
            padding: 14px 28px;
            letter-spacing: 1px;
            box-shadow: 0 4px 20px rgba(255,215,0,0.4);
            transition: all 0.2s;
        }
        .stButton > button:hover {
            transform: scale(1.03);
            box-shadow: 0 8px 30px rgba(255,215,0,0.6);
        }

        /* Expander */
        .streamlit-expanderHeader {
            color: #ffd700;
            font-weight: 600;
        }

        /* Métricas Streamlit */
        [data-testid="stMetricValue"] {
            color: #ffd700;
            font-size: 2rem;
        }
        [data-testid="stMetricLabel"] {
            color: #aaa;
        }

        /* Ajustes gerais de texto */
        p, label, .stMarkdown, .stCaption {
            color: #ddd;
        }
        .stNumberInput label, .stTextInput label, .stSelectbox label {
            color: #fff !important;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)
