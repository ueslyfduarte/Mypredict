O erro SyntaxError: invalid syntax no elif indica que a estrutura if/elif está quebrada — o primeiro if (if aba == "🧮 Simulador Manual":) deve existir antes de qualquer elif. No código que você tem, pode ser que a aba do Simulador Manual tenha sido removida ou mal fechada.

Vou te fornecer o código completo e corrigido, com as duas abas perfeitamente estruturadas. Substitua todo o conteúdo do seu app.py por este:

```python
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# =========================================================================
# CONFIGURAÇÃO DA PÁGINA - TEMA PRETO E DOURADO
# =========================================================================
st.set_page_config(
    page_title="MyPredict by Ferry v1.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# CSS CUSTOMIZADO
# =========================================================================
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 2px solid #ffd700; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    h1, h2, h3 { color: #ffd700 !important; font-weight: 700; letter-spacing: 1px; }
    h2 { border-bottom: 2px solid #ffd700; padding-bottom: 8px; }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a00, #2a2a00);
        border: 1px solid #ffd700;
        border-radius: 15px;
        padding: 20px;
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(255,215,0,0.2);
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover { border-color: #ffea80; box-shadow: 0 6px 25px rgba(255,215,0,0.5); }
    div[data-testid="stMetric"] label { color: #ffd700 !important; font-weight: 600; }
    div.stButton > button {
        background: linear-gradient(135deg, #4d3e00, #1a1a00);
        color: #ffd700;
        border: 2px solid #ffd700;
        border-radius: 12px;
        font-weight: bold;
        font-size: 18px;
        padding: 12px 30px;
        transition: 0.3s;
        letter-spacing: 1px;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #6b5200, #4d3e00);
        border-color: #ffea80;
        box-shadow: 0 0 25px rgba(255,215,0,0.7);
        transform: scale(1.02);
    }
    .welcome-card {
        background: linear-gradient(135deg, #1a1a00, #0d0d0d);
        border: 1px solid #ffd700;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 20px rgba(255,215,0,0.2);
    }
    .quote {
        font-style: italic;
        color: #ffd700;
        font-size: 20px;
        border-left: 5px solid #ffd700;
        padding-left: 25px;
        margin: 30px 0;
        background: rgba(255,215,0,0.05);
        padding: 15px 25px;
        border-radius: 0 10px 10px 0;
    }
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #1a1a00, #0d0d0d);
        border: 1px solid #ffd700;
        border-radius: 10px;
        color: #ffd700;
        font-weight: 600;
    }
    .streamlit-expanderHeader:hover { border-color: #ffea80; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>textarea {
        background-color: #1a1a00;
        color: white;
        border: 1px solid #ffd700;
        border-radius: 8px;
    }
    .stDataFrame {
        background-color: #0d0d0d;
        border: 1px solid #ffd700;
        border-radius: 10px;
        overflow: hidden;
    }
    .stDataFrame thead th { background-color: #ffd700 !important; color: #0a0a0a !important; font-weight: bold; }
    .stDataFrame tbody td { background-color: #1a1a00; color: #ffffff; border-bottom: 1px solid #2a2a00; }
    .stDataFrame tbody tr:hover td { background-color: #2a2a00 !important; color: #ffd700 !important; }
    .result-banner {
        padding: 20px; border-radius: 15px; text-align: center; font-size: 24px;
        font-weight: bold; margin: 20px 0; box-shadow: 0 8px 25px rgba(255,215,0,0.4);
    }
    .result-win { background: linear-gradient(135deg, #0a3d0a, #1a5c1a); border: 2px solid #ffd700; color: #a5d6a7; }
    .result-draw { background: linear-gradient(135deg, #3d3500, #5c5200); border: 2px solid #ffd700; color: #ffe082; }
    .market-card {
        background: linear-gradient(135deg, #1a1a00, #2a2a00);
        border: 1px solid #ffd700; border-radius: 10px; padding: 15px; margin: 8px 0;
        text-align: center; color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# CABEÇALHO
# =========================================================================
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("<div style='font-size: 60px; text-align: center;'>⚽</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin-bottom: 0;'>MyPredict by Ferry</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #ffd700; font-size: 18px; margin-top: 0;'>v1.0 • Inteligência Estatística no Futebol</p>", unsafe_allow_html=True)

st.markdown("<div class='welcome-card'>", unsafe_allow_html=True)
st.markdown("""
### 👋 Bem-vindo ao MyPredict!
O **MyPredict** é um sistema avançado de análise e previsão de partidas de futebol baseado no **Método FMP (Fator de Modulação de Prateleira)**.
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='quote'>\"O futebol é a coisa mais importante entre as menos importantes.\"<br>— <b>Arrigo Sacchi</b></div>", unsafe_allow_html=True)

# =========================================================================
# MENU LATERAL
# =========================================================================
st.sidebar.title("⚙️ Navegação")
aba = st.sidebar.radio("", ["🧮 Simulador Manual", "📊 Backtesting Offline"])

# =========================================================================
# FUNÇÕES MATEMÁTICAS (MANTIDAS)
# =========================================================================
def normalizar_por_media(valor_time, referencia, inverter=False):
    if referencia == 0: return 50.0
    razao = valor_time / referencia
    nota = razao * 50
    if inverter: nota = 100 - nota
    return max(0.0, min(100.0, nota))

def calcular_im(cc3, cc5, geral_3, geral_5, geral_10, bonus_zebra, tab_din):
    bloco_campo = (cc3 * 0.65) + (cc5 * 0.35)
    bloco_geral = (geral_3 * 0.50) + (geral_5 * 0.35) + (geral_10 * 0.15)
    im = (bloco_campo * 0.45) + (bloco_geral * 0.35) + (tab_din * 0.20) + bonus_zebra
    return max(0.0, min(100.0, im)), bloco_campo, bloco_geral, tab_din, bonus_zebra

def calcular_irc(rodada, nota_posicao, prospeccao, orgulho_ferido, revanche,
                 sequencia, pressao_torcida, importancia, desfalques, fatores_empiricos=None):
    def fac(r):
        if r <= 10: return 0.30
        elif r <= 25: return 0.60
        elif r <= 33: return 0.85
        else: return 1.00
    fpt = -10 if (prospeccao == "Elite Absoluta" and rodada <= 10) else 0
    urgencia = nota_posicao + fpt
    fatores = urgencia + orgulho_ferido + revanche + sequencia + pressao_torcida + importancia + desfalques
    if fatores_empiricos:
        fatores += fatores_empiricos.get('if_val', 0) + fatores_empiricos.get('fcf_val', 0) + fatores_empiricos.get('vcd_val', 0)
    nota = 50 + fatores * fac(rodada)
    return max(0.0, min(100.0, nota)), fac(rodada), urgencia, orgulho_ferido, revanche, sequencia, pressao_torcida, importancia, desfalques

def calcular_imp(overall, im, irc): return (overall + im + irc) / 3
def calcular_probabilidades(nota_a, nota_b):
    diff = nota_a - nota_b
    prob_a = 35 + diff * 0.5; prob_b = 35 - diff * 0.3; prob_empate = 30 - abs(diff) * 0.2
    prob_a = max(5, min(85, prob_a)); prob_b = max(5, min(85, prob_b)); prob_empate = max(5, min(50, prob_empate))
    total = prob_a + prob_empate + prob_b
    return prob_a/total*100, prob_empate/total*100, prob_b/total*100

# =========================================================================
# ABA SIMULADOR MANUAL (COMPLETA)
# =========================================================================
if aba == "🧮 Simulador Manual":
    st.header("🧮 Simulador com Estatísticas Brutas e Momento Completo")
    st.caption("Preencha o Painel Inicial e marque as estatísticas. Use as listas para cálculo automático de média/mediana.")

    col1, col2 = st.columns(2)
    with col1:
        nome_a = st.text_input("Nome Time A (Mandante)", "Flamengo")
    with col2:
        nome_b = st.text_input("Nome Time B (Visitante)", "Vasco")

    with st.expander("📊 Médias da Liga (Referência)", expanded=False):
        cols = st.columns(6)
        med_liga = {}
        med_liga['atq'] = cols[0].number_input("Atq", 0.0, 100.0, 12.0)
        med_liga['atq_perigosos'] = cols[1].number_input("Atq Perigosos", 0.0, 100.0, 6.0)
        med_liga['chutes'] = cols[2].number_input("Chutes", 0.0, 100.0, 14.0)
        med_liga['chutes_gol'] = cols[3].number_input("Chutes Gol", 0.0, 100.0, 5.0)
        med_liga['gols'] = cols[4].number_input("Gols Marcados", 0.0, 100.0, 1.4)
        med_liga['xg'] = cols[5].number_input("xG", 0.0, 100.0, 1.5)
        cols2 = st.columns(6)
        med_liga['atq_sofridos'] = cols2[0].number_input("Atq Sofridos", 0.0, 100.0, 10.0)
        med_liga['atq_perigosos_sofridos'] = cols2[1].number_input("Atq Perigosos Sofridos", 0.0, 100.0, 5.0)
        med_liga['chutes_sofridos'] = cols2[2].number_input("Chutes Sofridos", 0.0, 100.0, 12.0)
        med_liga['chutes_gol_sofridos'] = cols2[3].number_input("Chutes Gol Sofridos", 0.0, 100.0, 4.0)
        med_liga['gols_sofridos'] = cols2[4].number_input("Gols Sofridos", 0.0, 100.0, 1.2)
        med_liga['xg_cedido'] = cols2[5].number_input("xG Cedido", 0.0, 100.0, 1.3)

    def criar_seletores_time(prefixo, nome_time, mando):
        st.subheader(f"📈 {nome_time} ({'Mandante' if mando == 'C' else 'Visitante'})")
        tab_din = 50.0
        nota_posicao = 50.0
        prospeccao = "Média"
        aprov_5j = 50

        with st.expander("📋 Painel Inicial: Posicionamento e Prospecção", expanded=True):
            col_pos1, col_pos2 = st.columns(2)
            posicao_real = col_pos1.number_input("Posição Real na Tabela", 1, 20, 5, key=f"{prefixo}_pos_real")
            aprov_5j = col_pos2.slider("Aproveitamento nos Últimos 5 Jogos (%)", 0, 100, 60, key=f"{prefixo}_aprov_5j")
            prospeccao = st.selectbox("Prospecção Teórica Ideal (Prateleira)",
                                      ["Elite Absoluta", "Alta", "Média", "Baixa", "Crítica"],
                                      key=f"{prefixo}_prosp_painel")
            nota_posicao = 100.0 - (posicao_real - 1) * (100.0 / 19.0)
            nota_posicao = max(0.0, min(100.0, nota_posicao))
            pos_momentanea = 21.0 - (aprov_5j / 100.0) * 20.0
            mult_prat = 1.6 if prospeccao in ["Elite Absoluta"] else (1.0 if prospeccao in ["Alta", "Média"] else 0.0)
            tab_din = 50.0 + (posicao_real - pos_momentanea) * mult_prat
            tab_din = max(0.0, min(100.0, tab_din))
            st.caption(f"🔹 Nota Posição (IRC): {nota_posicao:.1f} | Tabela Dinâmica (IM): {tab_din:.1f}")

        estatisticas = {}
        medianas = {}
        p_atk, p_def, p_fdm, p_res = {}, {}, {}, {}

        # Ataque
        with st.expander("⚽ Ataque", expanded=False):
            st.caption("Marque as estatísticas e use as listas para média/mediana automática.")
            usar_lista = st.checkbox("Usar listas de valores (últimos 10 jogos)", key=f"{prefixo}_list_ataque")
            cols = st.columns(3)
            if cols[0].checkbox("Atq", key=f"{prefixo}_atq"):
                if usar_lista:
                    txt = st.text_area("Lista Atq (ex: 12,15,10...)", "12,15,10,14,13,11,16,14,15,12", key=f"{prefixo}_atq_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['atq'] = media
                        medianas['atq'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['atq'] = cols[0].number_input("Média", 0.0, 100.0, 15.0, key=f"{prefixo}_atq_v")
                p_atk['atq'] = 0.20
            if cols[1].checkbox("Atq Perigosos", key=f"{prefixo}_atq_per"):
                if usar_lista:
                    txt = st.text_area("Lista Atq Perigosos", "6,7,5,8,6,7,5,9,6,7", key=f"{prefixo}_atq_per_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['atq_perigosos'] = media
                        medianas['atq_perigosos'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['atq_perigosos'] = cols[1].number_input("Média", 0.0, 100.0, 7.0, key=f"{prefixo}_atq_per_v")
                p_atk['atq_perigosos'] = 0.20
            if cols[2].checkbox("Chutes", key=f"{prefixo}_chutes"):
                if usar_lista:
                    txt = st.text_area("Lista Chutes", "16,14,18,15,17,13,19,16,14,15", key=f"{prefixo}_chutes_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['chutes'] = media
                        medianas['chutes'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['chutes'] = cols[2].number_input("Média", 0.0, 100.0, 16.0, key=f"{prefixo}_chutes_v")
                p_atk['chutes'] = 0.20
                p_fdm['chutes'] = 0.20
            cols2 = st.columns(3)
            if cols2[0].checkbox("Chutes Gol", key=f"{prefixo}_chutes_gol"):
                if usar_lista:
                    txt = st.text_area("Lista Chutes Gol", "5,6,4,7,5,6,4,8,5,6", key=f"{prefixo}_chutes_gol_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['chutes_gol'] = media
                        medianas['chutes_gol'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['chutes_gol'] = cols2[0].number_input("Média", 0.0, 100.0, 6.0, key=f"{prefixo}_chutes_gol_v")
                p_atk['chutes_gol'] = 0.20
            if cols2[1].checkbox("Gols Marcados", key=f"{prefixo}_gols"):
                if usar_lista:
                    txt = st.text_area("Lista Gols", "2,1,3,0,2,2,1,4,2,1", key=f"{prefixo}_gols_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['gols'] = media
                        medianas['gols'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['gols'] = cols2[1].number_input("Média", 0.0, 100.0, 2.0, key=f"{prefixo}_gols_v")
                p_atk['gols'] = 0.20
            if cols2[2].checkbox("xG", key=f"{prefixo}_xg"):
                if usar_lista:
                    txt = st.text_area("Lista xG", "1.8,1.5,2.2,0.8,1.9,2.0,1.3,2.5,1.7,1.4", key=f"{prefixo}_xg_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['xg'] = media
                        medianas['xg'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['xg'] = cols2[2].number_input("Média", 0.0, 100.0, 1.8, key=f"{prefixo}_xg_v")
                p_atk['xg'] = 0.20

        # Defesa
        with st.expander("🛡️ Defesa", expanded=False):
            usar_lista = st.checkbox("Usar listas de valores (últimos 10 jogos)", key=f"{prefixo}_list_def")
            cols = st.columns(3)
            if cols[0].checkbox("Atq Sofridos", key=f"{prefixo}_atq_sof"):
                if usar_lista:
                    txt = st.text_area("Lista Atq Sofridos", "8,6,10,7,9,5,11,8,7,9", key=f"{prefixo}_atq_sof_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['atq_sofridos'] = media
                        medianas['atq_sofridos'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['atq_sofridos'] = cols[0].number_input("Média", 0.0, 100.0, 8.0, key=f"{prefixo}_atq_sof_v")
                p_def['atq_sofridos'] = 0.20
            if cols[1].checkbox("Atq Perigosos Sofridos", key=f"{prefixo}_atq_per_sof"):
                if usar_lista:
                    txt = st.text_area("Lista Atq Perigosos Sofridos", "3,4,2,5,3,4,2,6,3,4", key=f"{prefixo}_atq_per_sof_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['atq_perigosos_sofridos'] = media
                        medianas['atq_perigosos_sofridos'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['atq_perigosos_sofridos'] = cols[1].number_input("Média", 0.0, 100.0, 4.0, key=f"{prefixo}_atq_per_sof_v")
                p_def['atq_perigosos_sofridos'] = 0.20
            if cols[2].checkbox("Chutes Sofridos", key=f"{prefixo}_chutes_sof"):
                if usar_lista:
                    txt = st.text_area("Lista Chutes Sofridos", "10,8,12,9,11,7,13,10,9,11", key=f"{prefixo}_chutes_sof_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['chutes_sofridos'] = media
                        medianas['chutes_sofridos'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['chutes_sofridos'] = cols[2].number_input("Média", 0.0, 100.0, 10.0, key=f"{prefixo}_chutes_sof_v")
                p_def['chutes_sofridos'] = 0.20
                p_fdm['chutes_sofridos'] = 0.20
            cols2 = st.columns(3)
            if cols2[0].checkbox("Chutes Gol Sofridos", key=f"{prefixo}_chutes_gol_sof"):
                if usar_lista:
                    txt = st.text_area("Lista Chutes Gol Sofridos", "3,2,4,1,3,2,4,3,2,3", key=f"{prefixo}_chutes_gol_sof_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['chutes_gol_sofridos'] = media
                        medianas['chutes_gol_sofridos'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['chutes_gol_sofridos'] = cols2[0].number_input("Média", 0.0, 100.0, 3.0, key=f"{prefixo}_chutes_gol_sof_v")
                p_def['chutes_gol_sofridos'] = 0.20
            if cols2[1].checkbox("Gols Sofridos", key=f"{prefixo}_gols_sof"):
                if usar_lista:
                    txt = st.text_area("Lista Gols Sofridos", "0,1,0,2,1,0,1,1,0,1", key=f"{prefixo}_gols_sof_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['gols_sofridos'] = media
                        medianas['gols_sofridos'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['gols_sofridos'] = cols2[1].number_input("Média", 0.0, 100.0, 0.8, key=f"{prefixo}_gols_sof_v")
                p_def['gols_sofridos'] = 0.20
            if cols2[2].checkbox("xG Cedido", key=f"{prefixo}_xg_ced"):
                if usar_lista:
                    txt = st.text_area("Lista xG Cedido", "0.8,1.0,0.5,1.2,0.9,0.7,1.1,1.0,0.6,0.9", key=f"{prefixo}_xg_ced_list")
                    media, mediana, _ = processar_lista_estatistica(txt)
                    if media:
                        estatisticas['xg_cedido'] = media
                        medianas['xg_cedido'] = mediana
                        st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
                else:
                    estatisticas['xg_cedido'] = cols2[2].number_input("Média", 0.0, 100.0, 1.0, key=f"{prefixo}_xg_ced_v")
                p_def['xg_cedido'] = 0.20

        # Resistência
        with st.expander("💪 Resistência à Pressão", expanded=False):
            cols = st.columns(2)
            if cols[0].checkbox("Pontos Recuperados (0-100)", key=f"{prefixo}_pontos_rec"):
                estatisticas['pontos_recuperados'] = cols[0].number_input("Nota", 0.0, 100.0, 60.0, key=f"{prefixo}_pontos_rec_v")
                p_res['pontos_recuperados'] = 1.0
            if cols[1].checkbox("Gols Finais (75'-90')", key=f"{prefixo}_gols_fin"):
                estatisticas['gols_finais'] = cols[1].number_input("Nota", 0.0, 100.0, 70.0, key=f"{prefixo}_gols_fin_v")
                p_res['gols_finais'] = 1.0

        # IM, Histórico IM, IRC
        with st.expander("📈 Índice de Momento (IM)", expanded=False):
            st.markdown("**Condição de Campo**")
            cc3 = st.slider(f"Últimos 3 jogos em {'casa' if mando == 'C' else 'fora'}", 0, 100, 65, key=f"{prefixo}_cc3")
            cc5 = st.slider(f"Últimos 5 jogos em {'casa' if mando == 'C' else 'fora'}", 0, 100, 60, key=f"{prefixo}_cc5")
            st.markdown("**Geral**")
            g3 = st.slider("Últimos 3 jogos gerais", 0, 100, 68, key=f"{prefixo}_g3")
            g5 = st.slider("Últimos 5 jogos gerais", 0, 100, 64, key=f"{prefixo}_g5")
            g10 = st.slider("Últimos 10 jogos gerais", 0, 100, 60, key=f"{prefixo}_g10")
            bonus_zebra = st.number_input("Bônus de Zebra (+15 se ativado)", 0, 15, 0, key=f"{prefixo}_zebra")

        with st.expander("📉 Histórico IM (últimos 5 jogos)", expanded=False):
            hist_im = [st.number_input(f"IM jogo {i+1}", 0.0, 100.0, 50.0, key=f"{prefixo}_im_hist{i}") for i in range(5)]

        prat = st.selectbox("Prateleira do time (para FMP)",
                            ["Elite Absoluta", "Alta", "Média", "Baixa", "Crítica"],
                            key=f"{prefixo}_prat_fmp")

        with st.expander("🧠 IRC (Psicológico / Contextual)", expanded=False):
            rodada = st.number_input("Rodada", 1, 38, 20, key=f"{prefixo}_rod")
            orgulho = st.slider("Orgulho Ferido (0-30)", 0, 30, 0, key=f"{prefixo}_org")
            revanche = st.slider("Revanche (0-20)", 0, 20, 0, key=f"{prefixo}_rev")
            st.markdown("---")
            st.markdown("**Fatores Contextuais**")
            sequencia = st.slider("Sequência (+/-10)", -10, 10, 0, key=f"{prefixo}_seq")
            pressao = st.slider("Pressão da Torcida (-10 a +15)", -10, 15, 0, key=f"{prefixo}_pressao")
            importancia = st.selectbox("Importância do Jogo", [0, 10, 20], key=f"{prefixo}_imp")
            desfalques = st.slider("Desfalques Graves (-15 a 0)", -15, 0, 0, key=f"{prefixo}_desf")
            st.markdown("---")
            st.markdown("**🧪 Fatores Empíricos Automáticos**")
            usar_empiricos = st.checkbox("Ativar fatores empíricos", value=True, key=f"{prefixo}_usar_emp")
            if usar_empiricos:
                if_val = (aprov_5j - 50) * 0.3
                st.caption(f"Ímpeto de Forma (IF): {if_val:.1f}")
                fcf_val = (cc3 - 50) * 0.25
                st.caption(f"Fortaleza Casa/Fora (FCF): {fcf_val:.1f}")
                vitorias_cd = st.number_input("Vitórias nos últimos 5 confrontos diretos", 0, 5, 2, key=f"{prefixo}_vcd_vit")
                derrotas_cd = 5 - vitorias_cd
                vcd_val = max(-15, min(15, (vitorias_cd * 6) - (derrotas_cd * 4)))
                st.caption(f"Vantagem Confronto Direto (VCD): {vcd_val:.1f}")
                fatores_emp = {'if_val': if_val, 'fcf_val': fcf_val, 'vcd_val': vcd_val}
            else:
                fatores_emp = None

        im_params = (cc3, cc5, g3, g5, g10, bonus_zebra, tab_din)
        irc_params = (rodada, nota_posicao, prospeccao, orgulho, revanche,
                      sequencia, pressao, importancia, desfalques, fatores_emp)
        return (estatisticas, medianas, p_atk, p_def, p_fdm, p_res, hist_im, prat,
                im_params, irc_params, prospeccao)

    (est_a, med_a, p_atk_a, p_def_a, p_fdm_a, p_res_a, hist_im_a, prat_a,
     im_params_a, irc_params_a, prosp_a) = criar_seletores_time("a", nome_a, "C")
    st.divider()
    (est_b, med_b, p_atk_b, p_def_b, p_fdm_b, p_res_b, hist_im_b, prat_b,
     im_params_b, irc_params_b, prosp_b) = criar_seletores_time("b", nome_b, "F")

    if st.button("⚡ GERAR MYPREDICT", use_container_width=True):
        def calc_overall_simples(est, med_liga):
            fvo = normalizar_por_media(est.get('gols', 1.4), med_liga.get('gols', 1.4))
            frd = normalizar_por_media(est.get('gols_sofridos', 1.2), med_liga.get('gols_sofridos', 1.2), inverter=True)
            return (fvo * 0.5) + (frd * 0.5)
        ovr_a = calc_overall_simples(est_a, med_liga)
        ovr_b = calc_overall_simples(est_b, med_liga)
        im_a, _, _, _, _ = calcular_im(*im_params_a)
        im_b, _, _, _, _ = calcular_im(*im_params_b)
        irc_a, _, _, _, _, _, _, _, _ = calcular_irc(*irc_params_a)
        irc_b, _, _, _, _, _, _, _, _ = calcular_irc(*irc_params_b)
        imp_a = calcular_imp(ovr_a, im_a, irc_a)
        imp_b = calcular_imp(ovr_b, im_b, irc_b)
        prob_a, prob_e, prob_b = calcular_probabilidades(imp_a, imp_b)

        st.header("📊 Resultado MyPredict")
        col1, col2, col3 = st.columns(3)
        col1.metric(f"🏠 {nome_a}", f"{imp_a:.1f}", f"OVR: {ovr_a:.1f}")
        col2.metric("⚖️ Diferença", f"{imp_a - imp_b:+.1f}")
        col3.metric(f"🚌 {nome_b}", f"{imp_b:.1f}", f"OVR: {ovr_b:.1f}")
        st.subheader("🎯 Probabilidades de Resultado")
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Vitória {nome_a}", f"{prob_a:.1f}%")
        c2.metric("Empate", f"{prob_e:.1f}%")
        c3.metric(f"Vitória {nome_b}", f"{prob_b:.1f}%")
        if prob_a > prob_b and prob_a > prob_e:
            st.success(f"🏆 Previsão: Vitória do {nome_a}")
        elif prob_b > prob_a and prob_b > prob_e:
            st.success(f"🏆 Previsão: Vitória do {nome_b}")
        else:
            st.warning("🤝 Previsão: Empate")

# =========================================================================
# ABA BACKTESTING OFFLINE (COM LIMPEZA DE STRINGS)
# =========================================================================
elif aba == "📊 Backtesting Offline":
    st.header("📊 Backtesting Walk‑Forward – Leitura Robusta de CSV (com limpeza)")
    st.caption("Cole todo o conteúdo do CSV. O sistema detecta o separador e limpa os nomes dos times automaticamente.")

    texto_dados = st.text_area("Cole os dados da temporada", height=250,
                               placeholder="Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,...")

    if st.button("▶️ Iniciar Simulação Completa"):
        if not texto_dados.strip():
            st.error("Insira os dados dos jogos.")
        else:
            try:
                # Auto-detecção de separador (vírgula, tab, etc.)
                df = pd.read_csv(io.StringIO(texto_dados), sep=None, engine='python')
                df.columns = [c.strip().lower().replace('"', '') for c in df.columns]

                obrigatorias = ['hometeam', 'awayteam', 'fthg', 'ftag']
                if any(c not in df.columns for c in obrigatorias):
                    st.error(f"Colunas obrigatórias não encontradas. Disponíveis: {list(df.columns)}")
                else:
                    # Limpeza dos nomes dos times (remove aspas e espaços)
                    df['hometeam'] = df['hometeam'].astype(str).str.strip().str.replace('"', '')
                    df['awayteam'] = df['awayteam'].astype(str).str.strip().str.replace('"', '')
                    st.success(f"CSV lido! {len(df)} jogos encontrados.")
                    st.write("**Exemplos de nomes limpos:**", df['hometeam'].head(3).tolist())

                    # Estruturas da simulação
                    times_stats = {}
                    resultados = []
                    progresso = st.progress(0)
                    total_jogos = len(df)

                    # Contadores de desempenho
                    st.session_state.acertos_por_mercado = {merc: 0 for merc in ['1X2', 'Gol HT', 'Over 1.5 FT', 'Over 2.5 FT', 'Ambas Marcam', 'Over 1.5 HT', 'Escanteios (média)']}
                    st.session_state.total_por_mercado = {merc: 0 for merc in st.session_state.acertos_por_mercado}
                    st.session_state.lucro_por_mercado = {merc: 0.0 for merc in st.session_state.acertos_por_mercado}

                    for idx, row in df.iterrows():
                        mandante = row['hometeam']
                        visitante = row['awayteam']
                        gols_m = int(row['fthg'])
                        gols_v = int(row['ftag'])

                        # Colunas opcionais
                        gols_ht_m = int(row['hthg']) if 'hthg' in df.columns and not pd.isna(row['hthg']) else None
                        gols_ht_v = int(row['htag']) if 'htag' in df.columns and not pd.isna(row['htag']) else None
                        chutes_m = float(row['hs']) if 'hs' in df.columns and not pd.isna(row['hs']) else None
                        chutes_v = float(row['as']) if 'as' in df.columns and not pd.isna(row['as']) else None
                        chutes_gol_m = float(row['hst']) if 'hst' in df.columns and not pd.isna(row['hst']) else None
                        chutes_gol_v = float(row['ast']) if 'ast' in df.columns and not pd.isna(row['ast']) else None
                        escanteios_m = float(row['hc']) if 'hc' in df.columns and not pd.isna(row['hc']) else None
                        escanteios_v = float(row['ac']) if 'ac' in df.columns and not pd.isna(row['ac']) else None

                        # Funções get_stats / update_stats (idênticas)
                        def get_stats(time_name):
                            if time_name not in times_stats:
                                return {
                                    'gols': 1.4, 'gols_sofridos': 1.2,
                                    'gols_ht': 0.6, 'gols_sofridos_ht': 0.5,
                                    'chutes': 12.0, 'chutes_sofridos': 12.0,
                                    'chutes_gol': 4.5, 'chutes_gol_sofridos': 4.5,
                                    'escanteios': 5.0, 'escanteios_sofridos': 5.0,
                                    'jogos': 0,
                                    'hist_gols': [], 'hist_gols_sofridos': [],
                                    'hist_gols_ht': [], 'hist_gols_sofridos_ht': [],
                                    'hist_chutes': [], 'hist_chutes_sofridos': [],
                                    'hist_chutes_gol': [], 'hist_chutes_gol_sofridos': [],
                                    'hist_escanteios': [], 'hist_escanteios_sofridos': [],
                                    'hist_ambas': [], 'hist_over25': [], 'hist_over15': [],
                                    'hist_over15_ht': [], 'hist_gol_ht': []
                                }
                            return times_stats[time_name]

                        stats_a = get_stats(mandante)
                        stats_b = get_stats(visitante)

                        # Cálculo do Overall simplificado (apenas gols)
                        est_a = {'gols': stats_a['gols'], 'gols_sofridos': stats_b['gols']}
                        est_b = {'gols': stats_b['gols'], 'gols_sofridos': stats_a['gols']}
                        medias_liga = {'gols': 1.4, 'gols_sofridos': 1.2}
                        def calc_overall(est):
                            fvo = normalizar_por_media(est['gols'], medias_liga['gols'])
                            frd = normalizar_por_media(est['gols_sofridos'], medias_liga['gols_sofridos'], inverter=True)
                            return (fvo * 0.5) + (frd * 0.5)
                        ovr_a = calc_overall(est_a)
                        ovr_b = calc_overall(est_b)
                        im_a, _, _, _, _ = calcular_im(50, 50, 50, 50, 50, 0, 50)
                        im_b, _, _, _, _ = calcular_im(50, 50, 50, 50, 50, 0, 50)
                        irc_a, _, _, _, _, _, _, _, _ = calcular_irc(20, 50, "Média", 0, 0, 0, 0, 0, 0)
                        irc_b, _, _, _, _, _, _, _, _ = calcular_irc(20, 50, "Média", 0, 0, 0, 0, 0, 0)
                        imp_a = calcular_imp(ovr_a, im_a, irc_a)
                        imp_b = calcular_imp(ovr_b, im_b, irc_b)
                        prob_1x2 = calcular_probabilidades(imp_a, imp_b)

                        # Mercados (frequência)
                        def prob_mercado(lista_a, lista_b):
                            if not lista_a or not lista_b: return None
                            return (sum(lista_a)/len(lista_a) + sum(lista_b)/len(lista_b)) / 2.0

                        mercados = {}
                        if stats_a['hist_gol_ht'] and stats_b['hist_gol_ht']:
                            mercados['Gol HT'] = prob_mercado(stats_a['hist_gol_ht'], stats_b['hist_gol_ht'])
                        if stats_a['hist_over15'] and stats_b['hist_over15']:
                            mercados['Over 1.5 FT'] = prob_mercado(stats_a['hist_over15'], stats_b['hist_over15'])
                        if stats_a['hist_over25'] and stats_b['hist_over25']:
                            mercados['Over 2.5 FT'] = prob_mercado(stats_a['hist_over25'], stats_b['hist_over25'])
                        if stats_a['hist_ambas'] and stats_b['hist_ambas']:
                            mercados['Ambas Marcam'] = prob_mercado(stats_a['hist_ambas'], stats_b['hist_ambas'])
                        if stats_a['hist_over15_ht'] and stats_b['hist_over15_ht']:
                            mercados['Over 1.5 HT'] = prob_mercado(stats_a['hist_over15_ht'], stats_b['hist_over15_ht'])
                        if stats_a['hist_escanteios'] and stats_b['hist_escanteios']:
                            media_esc_a = np.mean(stats_a['hist_escanteios']) if stats_a['hist_escanteios'] else 0
                            media_esc_b = np.mean(stats_b['hist_escanteios']) if stats_b['hist_escanteios'] else 0
                            mercados['Escanteios (média)'] = (media_esc_a + media_esc_b) / 2.0

                        # Resultados reais
                        real_1x2 = "Vitória Mandante" if gols_m > gols_v else ("Vitória Visitante" if gols_m < gols_v else "Empate")
                        real_gol_ht = (gols_ht_m + gols_ht_v) > 0 if (gols_ht_m is not None and gols_ht_v is not None) else None
                        real_over15_ft = (gols_m + gols_v) > 1
                        real_over25_ft = (gols_m + gols_v) > 2
                        real_ambas = (gols_m > 0 and gols_v > 0)
                        real_over15_ht = (gols_ht_m + gols_ht_v) > 1 if (gols_ht_m is not None and gols_ht_v is not None) else None
                        real_escanteios = (escanteios_m + escanteios_v) if (escanteios_m is not None and escanteios_v is not None) else None

                        previsao_1x2 = "Vitória Mandante" if prob_1x2[0] > prob_1x2[1] and prob_1x2[0] > prob_1x2[2] else ("Vitória Visitante" if prob_1x2[1] > prob_1x2[0] and prob_1x2[1] > prob_1x2[2] else "Empate")
                        acerto_1x2 = "Sim" if previsao_1x2 == real_1x2 else "Não"

                        resultados.append({
                            'Jogo': f"{mandante} vs {visitante}",
                            'Placar': f"{gols_m}x{gols_v}",
                            'Prob 1X2': f"{prob_1x2[0]:.1f}%/{prob_1x2[2]:.1f}%/{prob_1x2[1]:.1f}%",
                            'Previsão 1X2': previsao_1x2,
                            'Real 1X2': real_1x2,
                            'Acerto 1X2': acerto_1x2
                        })

                        # Atualiza contadores
                        st.session_state.total_por_mercado['1X2'] += 1
                        if acerto_1x2 == "Sim":
                            st.session_state.acertos_por_mercado['1X2'] += 1
                            st.session_state.lucro_por_mercado['1X2'] += (1.0 / (prob_1x2[0]/100) - 1) if previsao_1x2 == "Vitória Mandante" else ((1.0 / (prob_1x2[1]/100) - 1) if previsao_1x2 == "Vitória Visitante" else (1.0 / (prob_1x2[2]/100) - 1))
                        else:
                            st.session_state.lucro_por_mercado['1X2'] -= 1

                        for nome, prob in mercados.items():
                            if prob is None: continue
                            st.session_state.total_por_mercado[nome] += 1
                            if nome == 'Escanteios (média)':
                                if real_escanteios and abs(prob - real_escanteios) <= 1.5:
                                    st.session_state.acertos_por_mercado[nome] += 1
                                    st.session_state.lucro_por_mercado[nome] += 0.8
                                else:
                                    st.session_state.lucro_por_mercado[nome] -= 1
                            else:
                                if (nome == 'Gol HT' and real_gol_ht == (prob > 0.5)) or \
                                   (nome == 'Over 1.5 FT' and real_over15_ft == (prob > 0.5)) or \
                                   (nome == 'Over 2.5 FT' and real_over25_ft == (prob > 0.5)) or \
                                   (nome == 'Ambas Marcam' and real_ambas == (prob > 0.5)) or \
                                   (nome == 'Over 1.5 HT' and real_over15_ht == (prob > 0.5)):
                                    st.session_state.acertos_por_mercado[nome] += 1
                                    st.session_state.lucro_por_mercado[nome] += (1.0 / max(prob, 0.01)) - 1
                                else:
                                    st.session_state.lucro_por_mercado[nome] -= 1

                        # Atualiza históricos
                        def update_stats(time, gf, gc, gf_ht=None, gc_ht=None, chutes=None, chutes_sof=None,
                                         chutes_gol=None, chutes_gol_sof=None, escanteios=None, escanteios_sof=None):
                            if time not in times_stats: get_stats(time)
                            s = times_stats[time]
                            s['jogos'] += 1
                            s['hist_gols'].append(gf); s['hist_gols_sofridos'].append(gc)
                            if len(s['hist_gols']) > 10: s['hist_gols'].pop(0)
                            if len(s['hist_gols_sofridos']) > 10: s['hist_gols_sofridos'].pop(0)
                            s['gols'] = np.mean(s['hist_gols'])
                            s['gols_sofridos'] = np.mean(s['hist_gols_sofridos'])
                            if gf_ht is not None and gc_ht is not None:
                                s['hist_gols_ht'].append(gf_ht); s['hist_gols_sofridos_ht'].append(gc_ht)
                                if len(s['hist_gols_ht']) > 10: s['hist_gols_ht'].pop(0)
                                if len(s['hist_gols_sofridos_ht']) > 10: s['hist_gols_sofridos_ht'].pop(0)
                                s['gols_ht'] = np.mean(s['hist_gols_ht'])
                                s['gols_sofridos_ht'] = np.mean(s['hist_gols_sofridos_ht'])
                            if chutes is not None:
                                s['hist_chutes'].append(chutes)
                                if len(s['hist_chutes']) > 10: s['hist_chutes'].pop(0)
                                s['chutes'] = np.mean(s['hist_chutes'])
                            if chutes_sof is not None:
                                s['hist_chutes_sofridos'].append(chutes_sof)
                                if len(s['hist_chutes_sofridos']) > 10: s['hist_chutes_sofridos'].pop(0)
                                s['chutes_sofridos'] = np.mean(s['hist_chutes_sofridos'])
                            if chutes_gol is not None:
                                s['hist_chutes_gol'].append(chutes_gol)
                                if len(s['hist_chutes_gol']) > 10: s['hist_chutes_gol'].pop(0)
                                s['chutes_gol'] = np.mean(s['hist_chutes_gol'])
                            if chutes_gol_sof is not None:
                                s['hist_chutes_gol_sofridos'].append(chutes_gol_sof)
                                if len(s['hist_chutes_gol_sofridos']) > 10: s['hist_chutes_gol_sofridos'].pop(0)
                                s['chutes_gol_sofridos'] = np.mean(s['hist_chutes_gol_sofridos'])
                            if escanteios is not None:
                                s['hist_escanteios'].append(escanteios)
                                if len(s['hist_escanteios']) > 10: s['hist_escanteios'].pop(0)
                                s['escanteios'] = np.mean(s['hist_escanteios'])
                            if escanteios_sof is not None:
                                s['hist_escanteios_sofridos'].append(escanteios_sof)
                                if len(s['hist_escanteios_sofridos']) > 10: s['hist_escanteios_sofridos'].pop(0)
                                s['escanteios_sofridos'] = np.mean(s['hist_escanteios_sofridos'])
                            s['hist_ambas'].append(1 if (gf > 0 and gc > 0) else 0)
                            s['hist_over25'].append(1 if (gf + gc) > 2 else 0)
                            s['hist_over15'].append(1 if (gf + gc) > 1 else 0)
                            if gf_ht is not None and gc_ht is not None:
                                s['hist_gol_ht'].append(1 if (gf_ht + gc_ht) > 0 else 0)
                                s['hist_over15_ht'].append(1 if (gf_ht + gc_ht) > 1 else 0)
                            for lista in ['hist_ambas', 'hist_over25', 'hist_over15', 'hist_gol_ht', 'hist_over15_ht']:
                                if len(s[lista]) > 10: s[lista].pop(0)

                        update_stats(mandante, gols_m, gols_v, gols_ht_m, gols_ht_v, chutes_m, chutes_v, chutes_gol_m, chutes_gol_v, escanteios_m, escanteios_v)
                        update_stats(visitante, gols_v, gols_m, gols_ht_v, gols_ht_m, chutes_v, chutes_m, chutes_gol_v, chutes_gol_m, escanteios_v, escanteios_m)

                        progresso.progress((idx + 1) / total_jogos)

                    # Exibição
                    df_res = pd.DataFrame(resultados)
                    st.subheader("📋 Resultados dos Jogos")
                    st.dataframe(df_res, use_container_width=True, hide_index=True)

                    st.subheader("📈 Desempenho por Mercado")
                    resumo = []
                    for mercado in st.session_state.acertos_por_mercado:
                        total = st.session_state.total_por_mercado[mercado]
                        if total > 0:
                            acertos = st.session_state.acertos_por_mercado[mercado]
                            lucro = st.session_state.lucro_por_mercado[mercado]
                            roi = (lucro / total) * 100
                            resumo.append({
                                'Mercado': mercado,
                                'Apostas': total,
                                'Acertos': acertos,
                                'Taxa de Acerto': f"{acertos/total*100:.1f}%",
                                'Lucro/Prejuízo': f"{lucro:.2f} u",
                                'ROI': f"{roi:.1f}%"
                            })
                    if resumo:
                        df_resumo = pd.DataFrame(resumo)
                        st.dataframe(df_resumo, use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhum mercado pôde ser avaliado com os dados fornecidos.")
                    st.success("Simulação concluída!")

            except Exception as e:
                st.error(f"Erro ao processar os dados: {e}")

# =========================================================================
# RODAPÉ
# =========================================================================
st.sidebar.divider()
st.sidebar.caption("MyPredict by Ferry v1.0")
st.sidebar.caption(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
```

Agora a estrutura está perfeita: o if do Simulador Manual está completo, seguido pelo elif do Backtesting. Substitua todo o arquivo e faça o commit. O app voltará a funcionar! 🚀
