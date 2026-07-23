import streamlit as st
import requests
from datetime import datetime

# Configuração visual nativa do Streamlit
st.set_page_config(page_title="MyPredicts", layout="wide")

# ---------------------------------------------------------------------
# [MÓDULO 1] ACESSO DA API E CONFIGURAÇÕES GLOBAIS
# ---------------------------------------------------------------------

# Inicialização global das variáveis para evitar erros de compilação
id_liga_selecionada = None
nome_liga_selecionada = None
ano_temporada_real = None
temporada_rotulo_selecionado = None
id_time_selecionado = None
nome_time_selecionado = None
dict_times = {}

if "MINHA_API_KEY" in st.secrets:
    HEADERS = {
        'x-apisports-key': st.secrets["MINHA_API_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
else:
    st.error("⚠️ ERRO CRÍTICO: Configure a tag 'MINHA_API_KEY' no painel do Streamlit.")
    st.stop()

BASE_URL = "https://api-sports.io"


# CONTADOR DE AÇÕES DIÁRIAS (PROTEÇÃO DA CONTA FREE)
hoje_str = datetime.today().strftime('%Y-%m-%d')

if "data_contador" not in st.session_state:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

if st.session_state["data_contador"] != hoje_str:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

def registrar_acao():
    """Incrementa o contador a cada ação para controle do plano Free"""
    st.session_state["contador_acoes"] += 1


# FUNÇÕES DE REQUISIÇÃO (MANDATÓRIAS COM CACHE DE 24H)
@st.cache_data(ttl=86400)
def buscar_dados_ligas_completas():
    try:
        url = f"{BASE_URL}/leagues"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except:
        return []

@st.cache_data(ttl=86400)
def buscar_teams_por_league_api(league_id, ano_temporada):
    try:
        url = f"{BASE_URL}/teams"
        parametros = {"league": league_id, "season": ano_temporada}
        response = requests.get(url, headers=HEADERS, params=parametros)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            mapeamento_teams = {item["team"]["name"]: item["team"]["id"] for item in dados}
            return dict(sorted(mapeamento_teams.items()))
        return {}
    except:
        return {}


# ---------------------------------------------------------------------
# [MÓDULO RESTRITO] CAIXA DE FERRAMENTAS (CÁLCULOS ESCONDIDOS - APENAS LÓGICA)
# ---------------------------------------------------------------------
def calcular_media_gols(gols_marcados, partidas_jogadas):
    if partidas_jogadas > 0:
        return round(gols_marcados / partidas_jogadas, 2)
    return 0.0

def calcular_probabilidade_btts(jogos_ambas_marcam, total_jogos):
    if total_jogos > 0:
        return round((jogos_ambas_marcam / total_jogos) * 100, 1)
    return 0.0

# Escreva seus próximos cálculos matemáticos puramente como funções aqui embaixo...


# ---------------------------------------------------------------------
# [MÓDULO 2] ENTRADAS PRINCIPAIS DO APP (BEM NO TOPO DO DESIGN)
# ---------------------------------------------------------------------
st.title("📊 MyPredicts")

dados_ligas = buscar_dados_ligas_completas()

if dados_ligas:
    dict_leagues = {item["league"]["name"]: item for item in dados_ligas}
    lista_nomes_ligas = sorted(list(dict_leagues.keys()))
    
    # 1. Seleção da Liga (Formato rolar ou pesquisar)
    nome_liga_selecionada = st.selectbox(
        "Selecione a Liga:",
        options=lista_nomes_ligas,
        index=0
    )
    
    objeto_liga = dict_leagues[nome_liga_selecionada]
    id_liga_selecionada = objeto_liga["league"]["id"]
    
    # Filtro Dinâmico: Filtra apenas a Temporada Atual e a Passada
    lista_seasons = objeto_liga["seasons"]
    opcoes_temporadas = {}
    for s in lista_seasons:
        ano_base = s["year"]
        data_inicio = datetime.strptime(s["start"], "%Y-%m-%d")
        data_fim = datetime.strptime(s["end"], "%Y-%m-%d")
        
        rotulo = f"{data_inicio.year}/{data_fim.year}" if data_inicio.year != data_fim.year else f"{ano_base}"
        opcoes_temporadas[rotulo] = ano_base

    # Organiza e seleciona estritamente as duas últimas (Atual e Passada)
    lista_rotulos_ordenados = sorted(list(opcoes_temporadas.keys()), reverse=True)[:2]
    
    # 2. Seleção da Temporada (Filtro restrito)
    temporada_rotulo_selecionado = st.selectbox(
        "Selecione a Temporada (Atual ou Passada):",
        options=lista_rotulos_ordenados,
        index=0
    )
    ano_temporada_real = opcoes_temporadas[temporada_rotulo_selecionado]
    
    # 3. Seleção do Time (Formato rolar ou pesquisar)
    dict_times = buscar_teams_por_league_api(league_id=id_liga_selecionada, ano_temporada=ano_temporada_real)
    
    if dict_times:
        nome_time_selecionado = st.selectbox(
            "Selecione o Time:",
            options=list(dict_times.keys()),
            index=0
        )
        id_time_selecionado = dict_times[nome_time_selecionado]
    else:
        st.warning("Nenhum clube listado nesta liga para o período selecionado.")
else:
    st.warning("Conectando aos servidores da API Football...")


# ESPAÇAMENTO LIMPO APENAS ENTRE MÓDULOS PRINCIPAIS
st.write("")
st.write("")
st.divider()
st.write("")
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 3] CORPO DO APP: INTERFACE EXPOSITIVA E LEITURA DOS DADOS
# ---------------------------------------------------------------------
st.subheader("📈 Análise de Desempenho e Predições")

if id_time_selecionado:
    st.info(f"Dados prontos para o MyPredicts. Clube: {nome_time_selecionado} | ID: {id_time_selecionado}")
    
    # Espaço livre abaixo para você chamar seus gráficos e tabelas usando as defs da caixa de ferramentas
else:
    st.info("Aguardando a seleção completa de uma Liga e de um Time no topo da tela.")


# ESPAÇAMENTO LIMPO APENAS ENTRE MÓDULOS PRINCIPAIS
st.write("")
st.write("")
st.divider()
st.write("")
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 4] MONITORAMENTO DIÁRIO DE CONSUMO (CONTA FREE)
# ---------------------------------------------------------------------
st.subheader("📊 Painel de Controle de Requisições")

col1, col2 = st.columns(2)
with col1:
    st.metric(label="Ações Efetuadas Hoje", value=st.session_state["contador_acoes"])

with col2:
    limite_free = 100
    restantes = max(0, limite_free - st.session_state["contador_acoes"])
    st.metric(label="Créditos Restantes Garantidos", value=restantes)
