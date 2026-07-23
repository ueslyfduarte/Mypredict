import streamlit as st
import requests
from datetime import datetime

# Configuração da página para layout expandido
st.set_page_config(layout="wide")

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


# CONTADOR DE AÇÕES DIÁRIAS (CONTA FREE)
hoje_str = datetime.today().strftime('%Y-%m-%d')

if "data_contador" not in st.session_state:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

if st.session_state["data_contador"] != hoje_str:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

def registrar_acao():
    st.session_state["contador_acoes"] += 1


# FUNÇÕES DE REQUISIÇÃO COM CACHE
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
# [MÓDULO 2] SELEÇÃO DE COMPETIÇÕES E CLUBES (SISTEMA DE BUSCA)
# ---------------------------------------------------------------------
st.title("⚽ Aplicativo Estatístico de Futebol")

dados_ligas = buscar_dados_ligas_completas()

if dados_ligas:
    dict_leagues = {item["league"]["name"]: item for item in dados_ligas}
    lista_nomes_ligas = sorted(list(dict_leagues.keys()))
    
    # Seleção da Liga (Rolar ou Pesquisar)
    nome_liga_selecionada = st.selectbox(
        "Selecione a Liga:",
        options=lista_nomes_ligas,
        index=0
    )
    
    objeto_liga = dict_leagues[nome_liga_selecionada]
    id_liga_selecionada = objeto_liga["league"]["id"]
    
    # Sistema dinâmico de Temporadas conforme o campeonato escolhido
    lista_seasons = objeto_liga["seasons"]
    opcoes_temporadas = {}
    for s in lista_seasons:
        ano_base = s["year"]
        data_inicio = datetime.strptime(s["start"], "%Y-%m-%d")
        data_fim = datetime.strptime(s["end"], "%Y-%m-%d")
        
        rotulo = f"{data_inicio.year}/{data_fim.year}" if data_inicio.year != data_fim.year else f"{ano_base}"
        opcoes_temporadas[rotulo] = ano_base

    lista_rotulos_ordenados = sorted(list(opcoes_temporadas.keys()), reverse=True)
    
    temporada_rotulo_selecionado = st.selectbox(
        "Selecione a Temporada:",
        options=lista_rotulos_ordenados,
        index=0
    )
    ano_temporada_real = opcoes_temporadas[temporada_rotulo_selecionado]
    
    # Seleção do Time baseado na Liga e Temporada (Rolar ou Pesquisar)
    dict_times = buscar_teams_por_league_api(league_id=id_liga_selecionada, ano_temporada=ano_temporada_real)
    
    if dict_times:
        nome_time_selecionado = st.selectbox(
            "Selecione o Time:",
            options=list(dict_times.keys()),
            index=0
        )
        id_time_selecionado = dict_times[nome_time_selecionado]
    else:
        st.warning("Nenhum clube encontrado para esta temporada.")
        id_time_selecionado = None
else:
    st.warning("Aguardando carregamento de dados da API...")


# CRIAÇÃO DE ESPAÇAMENTO RELEVANTE E LIMPO APENAS ENTRE OS MÓDULOS
st.write("")
st.write("")
st.write("")
st.divider()
st.write("")
st.write("")
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 3] RESERVADO: CAIXA DE FERRAMENTAS (ONDE ENTRARÃO OS CÁLCULOS)
# ---------------------------------------------------------------------
st.header("🧰 Caixa de Ferramentas")

# Interface limpa aguardando seus blocos lógicos matemáticos
if st.button("Executar Cálculos", on_click=registrar_acao):
    if dados_ligas and dict_times and id_time_selecionado:
        st.success(f"Processando métricas de {nome_time_selecionado} ({temporada_rotulo_selecionado})...")
        # Seu bloco de código matemático entrará diretamente aqui
    else:
        st.info("Por favor, selecione uma combinação válida de Liga, Temporada e Time primeiro.")


# CRIAÇÃO DE ESPAÇAMENTO RELEVANTE E LIMPO APENAS ENTRE OS MÓDULOS
st.write("")
st.write("")
st.write("")
st.divider()
st.write("")
st.write("")
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 4] MONITORAMENTO DIÁRIO (CONTA FREE)
# ---------------------------------------------------------------------
st.header("📊 Painel de Controle API")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="Ações Executadas Hoje", 
        value=st.session_state["contador_acoes"]
    )

with col2:
    limite_free = 100
    restantes = max(0, limite_free - st.session_state["contador_acoes"])
    st.metric(
        label="Ações Restantes no Plano", 
        value=restantes
    )
