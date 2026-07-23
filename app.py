import streamlit as st
import requests
from datetime import datetime

# Configuração visual nativa do Streamlit
st.set_page_config(page_title="MyPredicts", layout="wide")

# ---------------------------------------------------------------------
# [MÓDULO 1] ACESSO DA API E CONFIGURAÇÕES GLOBAIS
# ---------------------------------------------------------------------
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
    """Chame esta função sempre que realizar um cálculo final ou comando pago"""
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
# [MÓDULO RESTRITO] CAIXA DE FERRAMENTAS (CÁLCULOS ESCONDIDOS)
# ---------------------------------------------------------------------
# Este espaço é puramente lógico. Não gera elementos visuais no app.
# Armazene aqui todas as fórmulas que serão invocadas ao longo do código.

def calcular_media_gols(gols_marcados, partidas_jogadas):
    """Exemplo de cálculo: Retorna a média de gols do time"""
    if partidas_jogadas > 0:
        return round(gols_marcados / partidas_jogadas, 2)
    return 0.0

def calcular_probabilidade_btts(jogos_ambas_marcam, total_jogos):
    """Exemplo de cálculo: Retorna a porcentagem de Ambas Marcam (BTTS)"""
    if total_jogos > 0:
        return round((jogos_ambas_marcam / total_jogos) * 100, 1)
    return 0.0

# 💻 Adicione suas novas funções matemáticas e de cruzamento de dados logo abaixo...


# ---------------------------------------------------------------------
# [MÓDULO 2] ENTRADAS PRINCIPAIS DO APP (BEM NO TOPO)
# ---------------------------------------------------------------------
st.title("📊 MyPredicts")

dados_ligas = buscar_dados_ligas_completas()

if dados_ligas:
    dict_leagues = {item["league"]["name"]: item for item in dados_ligas}
    lista_nomes_ligas = sorted(list(dict_leagues.keys()))
    
    # 1. SELEÇÃO DA LIGA (Formato rolar ou pesquisar)
    nome_liga_selecionada = st.selectbox(
        "Selecione a Liga:",
        options=lista_nomes_ligas,
        index=0
    )
    
    objeto_liga = dict_leagues[nome_liga_selecionada]
    id_liga_selecionada = objeto_liga["league"]["id"]
    
    # FILTRO RESTRETO: Filtra dinamicamente APENAS a Temporada Atual e a Passada
    lista_seasons = objeto_liga["seasons"]
    opcoes_temporadas = {}
    for s in lista_seasons:
        ano_base = s["year"]
        data_inicio = datetime.strptime(s["start"], "%Y-%m-%d")
        data_fim = datetime.strptime(s["end"], "%Y-%m-%d")
        
        rotulo = f"{data_inicio.year}/{data_fim.year}" if data_inicio.year != data_fim.year else f"{ano_base}"
        opcoes_temporadas[rotulo] = ano_base

    # Organiza em ordem decrescente e captura os dois primeiros índices (Atual e Passada)
    lista_rotulos_ordenados = sorted(list(opcoes_temporadas.keys()), reverse=True)[:2]
    
    # 2. SELEÇÃO DA TEMPORADA (Apenas as duas últimas válidas do campeonato)
    temporada_rotulo_selecionado = st.selectbox(
        "Selecione a Temporada (Atual ou Passada):",
        options=lista_rotulos_ordenados,
        index=0
    )
    ano_temporada_real = opcoes_temporadas[temporada_rotulo_selecionado]
    
    # 3. SELEÇÃO DO TIME (Formato rolar ou pesquisar)
    # Todos os dados de elenco e dados estruturais do time são baixados aqui automaticamente
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
        id_time_selecionado = None
else:
    st.warning("Conectando aos servidores da API Football...")


# ESPAÇAMENTO LIMPO APENAS ENTRE MÓDULOS PRINCIPAIS
st.write("")
st.write("")
st.divider()
st.write("")
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 3] CORPO DO APP: INTERFACE EXPOSITIVA E EXECUÇÃO DE DADOS
# ---------------------------------------------------------------------
# A partir daqui você desenvolve seus gráficos, tabelas e chamadas de tela.

st.subheader("📈 Análise de Desempenho e Predições")

if id_time_selecionado:
    st.info(f"Dados prontos para processamento. Clube: {nome_time_selecionado} | ID: {id_time_selecionado}")
    
    # Exemplo prático de como você chamará sua caixa de ferramentas futuramente:
    # media_gols = calcular_media_gols(gols_marcados=45, partidas_jogadas=20)
    # st.write(f"Média do time: {media_gols}")


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

    )
