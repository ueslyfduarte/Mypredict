import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# =========================================================================
# CONFIGURAÇÃO DA PÁGINA - TEMA PRETO E DOURADO
# =========================================================================
st.set_page_config(
    page_title="MyPredict by Ferry v0.6",
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
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
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
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin: 20px 0;
        box-shadow: 0 8px 25px rgba(255,215,0,0.4);
    }
    .result-win { background: linear-gradient(135deg, #0a3d0a, #1a5c1a); border: 2px solid #ffd700; color: #a5d6a7; }
    .result-draw { background: linear-gradient(135deg, #3d3500, #5c5200); border: 2px solid #ffd700; color: #ffe082; }
    .market-card {
        background: linear-gradient(135deg, #1a1a00, #2a2a00);
        border: 1px solid #ffd700;
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        text-align: center;
        color: #ffffff;
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
    st.markdown("<p style='color: #ffd700; font-size: 18px; margin-top: 0;'>v0.6 • Inteligência Estatística no Futebol</p>", unsafe_allow_html=True)

st.markdown("<div class='welcome-card'>", unsafe_allow_html=True)
st.markdown("""
### 👋 Bem-vindo ao MyPredict!

O **MyPredict** é um sistema avançado de análise e previsão de partidas de futebol baseado no **Método FMP (Fator de Modulação de Prateleira)**.  
Ele cruza estatísticas brutas com um motor matemático que avalia força ofensiva, defensiva, consistência e resposta psicológica, gerando probabilidades para diversos mercados.
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='quote'>\"O futebol é a coisa mais importante entre as menos importantes.\"<br>— <b>Arrigo Sacchi</b></div>", unsafe_allow_html=True)

# =========================================================================
# MENU LATERAL
# =========================================================================
st.sidebar.title("⚙️ Navegação")
aba = st.sidebar.radio("", ["🔌 API (Dados Reais)", "🌐 Dados Online (Seleção)", "🧮 Simulador Manual", "⏪ Backtesting"])

# =========================================================================
# FUNÇÕES AUXILIARES
# =========================================================================
FOOTBALL_DATA_API_KEY = st.secrets.get("FOOTBALL_DATA_API_KEY", "")

def buscar_partidas_time(team_id, limit=10):
    url = f"https://api.football-data.org/v4/teams/{team_id}/matches?status=FINISHED&limit={limit}"
    headers = {}
    if FOOTBALL_DATA_API_KEY:
        headers["X-Auth-Token"] = FOOTBALL_DATA_API_KEY
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
        return resp.json().get("matches", [])
    except:
        return None

def calcular_medias_partidas(matches, team_id):
    if not matches:
        return None
    total_goals = 0
    n = len(matches)
    for m in matches:
        if m["homeTeam"]["id"] == team_id:
            total_goals += m["score"]["fullTime"]["home"]
        else:
            total_goals += m["score"]["fullTime"]["away"]
    return {"gols": total_goals / n, "chutes": None, "chutes_gol": None, "xg": None}

# =========================================================================
# MOTOR MATEMÁTICO (COMPLETO)
# =========================================================================
# (Incluo aqui as funções essenciais; as demais podem ser mantidas da versão anterior)
def normalizar_por_media(valor_time, referencia, inverter=False):
    if referencia == 0: return 50.0
    razao = valor_time / referencia
    nota = razao * 50
    if inverter: nota = 100 - nota
    return max(0.0, min(100.0, nota))

def calcular_fmp(prat_time, prat_rival, tipo):
    elite = ["Elite Absoluta"]; media_alta = ["Alta", "Média"]; baixa = ["Baixa", "Crítica"]
    if prat_time in elite and prat_rival in media_alta + baixa: return 0.60 if tipo == "ataque" else 1.40
    elif prat_time in baixa and prat_rival in elite: return 1.30 if tipo == "ataque" else 0.70
    elif prat_time in media_alta and prat_rival in elite: return 1.30 if tipo == "ataque" else 0.70
    else: return 1.00

def classificar_prateleira(overall):
    if overall >= 86: return "Elite Absoluta"
    elif overall >= 78: return "Alta"
    elif overall >= 70: return "Média"
    elif overall >= 60: return "Baixa"
    else: return "Crítica"

def calcular_overall(estatisticas_time, medias_liga, prat_time, prat_rival,
                     pesos_ataque, pesos_defesa, pesos_fdm, pesos_resist,
                     historico_im, medianas_time=None):
    # Simplificação para a aba online (apenas ataque e defesa)
    fvo = 50.0; fco = 50.0; frd = 50.0; fcd_def = 50.0
    if pesos_ataque:
        nota_total = 0.0; peso_total = 0.0
        for k, v in pesos_ataque.items():
            if k in estatisticas_time and estatisticas_time[k] is not None:
                nota = normalizar_por_media(estatisticas_time[k], medias_liga.get(k, 1))
                nota_total += nota * v
                peso_total += v
        if peso_total > 0: fvo = nota_total / peso_total
    if pesos_defesa:
        nota_total = 0.0; peso_total = 0.0
        for k, v in pesos_defesa.items():
            if k in estatisticas_time and estatisticas_time[k] is not None:
                nota = normalizar_por_media(estatisticas_time[k], medias_liga.get(k, 1), inverter=True)
                nota_total += nota * v
                peso_total += v
        if peso_total > 0: frd = nota_total / peso_total
    ataque = (fvo * 0.60) + (fco * 0.40)
    defesa = (frd * 0.60) + (fcd_def * 0.40)
    overall = (ataque * 0.50) + (defesa * 0.50)  # simplificação
    return {'overall': max(0.0, min(100.0, overall)), 'ataque': ataque, 'defesa': defesa}

def calcular_im(cc3, cc5, geral_3, geral_5, geral_10, bonus_zebra, tab_din):
    bloco_campo = (cc3 * 0.65) + (cc5 * 0.35); bloco_geral = (geral_3 * 0.50) + (geral_5 * 0.35) + (geral_10 * 0.15)
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
# ABA API
# =========================================================================
if aba == "🔌 API (Dados Reais)":
    st.header("🔌 Buscar Dados da API-Football")
    API_KEY = st.secrets.get("API_FOOTBALL_KEY", "")
    if not API_KEY:
        st.error("Chave API não encontrada nos secrets.")
    else:
        time_nome = st.text_input("Nome do time (ex: Flamengo)")
        if st.button("Buscar Time"):
            headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
            url = "https://v3.football.api-sports.io/teams"
            resp = requests.get(url, headers=headers, params={"search": time_nome})
            if resp.status_code == 200:
                dados = resp.json()
                st.json(dados)
            else:
                st.error(f"Erro {resp.status_code}")

# =========================================================================
# ABA DADOS ONLINE COM SELEÇÃO (CORRIGIDA)
# =========================================================================
elif aba == "🌐 Dados Online (Seleção)":
    st.header("🌐 Dados Online – Selecione Liga e Times")
    st.caption("Escolha a liga e os times. Se a API falhar, usamos estimativas.")

    TIMES_POR_LIGA = {
        "Brasileirão Série A": ["Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Santos", "Internacional", "Grêmio", "Atlético Mineiro", "Cruzeiro", "Fluminense"],
        "Premier League": ["Arsenal", "Aston Villa", "Chelsea", "Liverpool", "Manchester City", "Manchester United", "Tottenham", "Newcastle", "Brighton", "West Ham"],
        "La Liga": ["Real Madrid", "Barcelona", "Atlético Madrid", "Sevilla", "Valencia", "Real Sociedad", "Betis", "Athletic Bilbao", "Villarreal", "Getafe"],
        "Série A Italiana": ["Juventus", "Inter", "Milan", "Napoli", "Roma", "Lazio", "Atalanta", "Fiorentina", "Torino", "Bologna"],
        "Bundesliga": ["Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen", "Eintracht Frankfurt", "Borussia M'gladbach", "Wolfsburg", "Freiburg", "Hoffenheim", "Augsburg"]
    }

    ligas = list(TIMES_POR_LIGA.keys())
    col1, col2 = st.columns(2)
    with col1:
        liga_a = st.selectbox("Liga do Time A", ligas, key="la")
        times_a = TIMES_POR_LIGA[liga_a]
        time_a_nome = st.selectbox("Time A (Mandante)", times_a, key="ta")
    with col2:
        liga_b = st.selectbox("Liga do Time B", ligas, key="lb")
        times_b = TIMES_POR_LIGA[liga_b]
        time_b_nome = st.selectbox("Time B (Visitante)", times_b, key="tb")

    if st.button("🔎 Buscar Dados"):
        # Valores padrão
        med_a = {"gols": 1.4, "chutes": None, "chutes_gol": None, "xg": None}
        med_b = {"gols": 1.4, "chutes": None, "chutes_gol": None, "xg": None}
        # Tenta API
        try:
            league_map = {"Brasileirão Série A": "BSA", "Premier League": "PL", "La Liga": "PD",
                          "Série A Italiana": "SA", "Bundesliga": "BL1"}
            code_a = league_map.get(liga_a, "BSA"); code_b = league_map.get(liga_b, "BSA")
            # Obter IDs
            def get_id(name, code):
                url = f"https://api.football-data.org/v4/competitions/{code}/teams"
                headers = {}
                if FOOTBALL_DATA_API_KEY: headers["X-Auth-Token"] = FOOTBALL_DATA_API_KEY
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    for t in resp.json().get("teams", []):
                        if name.lower() in t["name"].lower():
                            return t["id"]
                return None
            id_a = get_id(time_a_nome, code_a)
            id_b = get_id(time_b_nome, code_b)
            if id_a and id_b:
                matches_a = buscar_partidas_time(id_a)
                matches_b = buscar_partidas_time(id_b)
                if matches_a: med_a = calcular_medias_partidas(matches_a, id_a)
                if matches_b: med_b = calcular_medias_partidas(matches_b, id_b)
        except:
            pass

        st.session_state.dados_a = med_a
        st.session_state.dados_b = med_b
        st.session_state.nomes = (time_a_nome, time_b_nome)
        st.success("Dados carregados!")

    if "dados_a" in st.session_state:
        med_a = st.session_state.dados_a
        med_b = st.session_state.dados_b
        nome_a, nome_b = st.session_state.nomes
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{nome_a}**")
            st.write(med_a)
        with col2:
            st.write(f"**{nome_b}**")
            st.write(med_b)

        with st.expander("🛡️ Dados defensivos"):
            med_a['gols_sofridos'] = st.number_input(f"Gols Sofridos {nome_a}", 0.0, 10.0, 1.0)
            med_b['gols_sofridos'] = st.number_input(f"Gols Sofridos {nome_b}", 0.0, 10.0, 1.0)

        col1, col2 = st.columns(2)
        with col1:
            rod_a = st.number_input("Rodada A", 1, 38, 20)
            pos_a = st.slider("Posição A", 0, 100, 60)
        with col2:
            rod_b = st.number_input("Rodada B", 1, 38, 20)
            pos_b = st.slider("Posição B", 0, 100, 40)

        if st.button("⚡ GERAR MYPREDICT"):
            # Lógica de cálculo simplificada
            est_a = {k:v for k,v in med_a.items() if v is not None}
            est_b = {k:v for k,v in med_b.items() if v is not None}
            medias_liga = {'gols': 1.4, 'gols_sofridos': 1.2}
            res_a = calcular_overall(est_a, medias_liga, "Média", "Média", {'gols':1.0}, {'gols_sofridos':1.0}, {}, {}, [])
            res_b = calcular_overall(est_b, medias_liga, "Média", "Média", {'gols':1.0}, {'gols_sofridos':1.0}, {}, {}, [])
            im_a,_,_,_,_ = calcular_im(50,50,50,50,50,0,50)
            im_b,_,_,_,_ = calcular_im(50,50,50,50,50,0,50)
            irc_a,_,_,_,_,_,_,_,_ = calcular_irc(rod_a, pos_a, "Média", 0,0,0,0,0,0)
            irc_b,_,_,_,_,_,_,_,_ = calcular_irc(rod_b, pos_b, "Média", 0,0,0,0,0,0)
            imp_a = calcular_imp(res_a['overall'], im_a, irc_a)
            imp_b = calcular_imp(res_b['overall'], im_b, irc_b)
            prob_a, prob_e, prob_b = calcular_probabilidades(imp_a, imp_b)
            st.metric(f"{nome_a}", f"{imp_a:.1f}")
            st.metric(f"{nome_b}", f"{imp_b:.1f}")
            st.write(f"Probabilidades: {nome_a} {prob_a:.1f}% | Empate {prob_e:.1f}% | {nome_b} {prob_b:.1f}%")

# =========================================================================
# ABA SIMULADOR MANUAL (PLACEHOLDER)
# =========================================================================
elif aba == "🧮 Simulador Manual":
    st.header("🧮 Simulador Manual")
    st.info("Em manutenção. Volte em breve.")

# =========================================================================
# ABA BACKTESTING (PLACEHOLDER)
# =========================================================================
elif aba == "⏪ Backtesting":
    st.header("⏪ Backtesting")
    st.info("Em manutenção. Volte em breve.")

# =========================================================================
# RODAPÉ
# =========================================================================
st.sidebar.divider()
st.sidebar.caption("MyPredict by Ferry v0.6")
st.sidebar.caption(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
