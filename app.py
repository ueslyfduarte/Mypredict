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

# CONTADOR DIÁRIO DE CONTROLE (CONTA FREE)
hoje_str = datetime.today().strftime('%Y-%m-%d')
if "data_contador" not in st.session_state:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

if st.session_state["data_contador"] != hoje_str:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

def registrar_acao():
    st.session_state["contador_acoes"] += 1


# ---------------------------------------------------------------------
# [MÓDULO RESTRITO] CAIXA DE FERRAMENTAS (FUNÇÕES DE CONEXÃO E CÁLCULO)
# ---------------------------------------------------------------------

@st.cache_data(ttl=86400)
def API_buscar_todas_leagues():
    """Consome a API para listar todas as ligas cadastradas"""
    try:
        url = f"{BASE_URL}/leagues"
        response = requests.get(url, headers=HEADERS, timeout=12)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except:
        return []

@st.cache_data(ttl=86400)
def API_buscar_teams_por_league(league_id, ano_temporada):
    """Consome a API para listar todos os clubes de uma liga e temporada"""
    try:
        url = f"{BASE_URL}/teams"
        parametros = {"league": league_id, "season": ano_temporada}
        response = requests.get(url, headers=HEADERS, params=parametros, timeout=12)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            mapeamento = {item["team"]["name"]: item["team"]["id"] for item in dados}
            return dict(sorted(mapeamento.items()))
        return {}
    except:
        return {}

def API_buscar_confrontos_diretos(team_a_id, team_b_id):
    """Consome a API para obter o histórico real H2H entre os dois times"""
    try:
        url = f"{BASE_URL}/fixtures/headtohead"
        parametros = {"h2h": f"{team_a_id}-{team_b_id}"}
        response = requests.get(url, headers=HEADERS, params=parametros, timeout=15)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except:
        return []

# Espaço reservado para inclusão de novas fórmulas matemáticas futuramente
def calcular_percentual_vitorias(historico_partidas, id_time_alvo):
    """Exemplo de cálculo estatístico interno usando dados reais obtidos do H2H"""
    if not historico_partidas:
        return 0.0
    vitorias = 0
    for partida in historico_partidas:
        if partida["teams"]["home"]["id"] == id_time_alvo and partida["teams"]["home"]["winner"]:
            vitorias += 1
        elif partida["teams"]["away"]["id"] == id_time_alvo and partida["teams"]["away"]["winner"]:
            vitorias += 1
    return round((vitorias / len(historico_partidas)) * 100, 1)


# ---------------------------------------------------------------------
# [MÓDULO 2] ENTRADAS PRINCIPAIS DO APP (SELEÇÃO EM CASCATA NO TOPO)
# ---------------------------------------------------------------------
st.title("📊 MyPredicts")

# Baixa as ligas disponíveis diretamente da API Football
dados_api_leagues = API_buscar_todas_leagues()

if dados_api_leagues:
    dict_leagues = {item["league"]["name"]: item for item in dados_api_leagues}
    lista_nomes_ligas = sorted(list(dict_leagues.keys()))
    
    # 1. SELETOR DE LIGA (Pesquisar ou Rolar)
    nome_liga_selecionada = st.selectbox("Selecione a Liga:", options=lista_nomes_ligas)
    objeto_liga = dict_leagues[nome_liga_selecionada]
    id_liga_selecionada = objeto_liga["league"]["id"]
    
    # Processamento dinâmico de datas para extrair apenas Atual e Passada
    lista_seasons = objeto_liga["seasons"]
    opcoes_temporadas = {}
    for s in lista_seasons:
        ano_base = s["year"]
        data_inicio = datetime.strptime(s["start"], "%Y-%m-%d")
        data_fim = datetime.strptime(s["end"], "%Y-%m-%d")
        rotulo = f"{data_inicio.year}/{data_fim.year}" if data_inicio.year != data_fim.year else f"{ano_base}"
        opcoes_temporadas[rotulo] = ano_base

    lista_rotulos_ordenados = sorted(list(opcoes_temporadas.keys()), reverse=True)[:2]
    
    # 2. SELETOR DE TEMPORADA (Restrito a duas opções)
    temporada_rotulo_selecionado = st.selectbox("Selecione a Temporada:", options=lista_rotulos_ordenados)
    ano_temporada_real = opcoes_temporadas[temporada_rotulo_selecionado]
    
    # 3. SELETOR DOS CLUBES EM CASCATA
    dict_times = API_buscar_teams_por_league(league_id=id_liga_selecionada, ano_temporada=ano_temporada_real)
    
    if dict_times:
        col_a, col_b = st.columns(2)
        with col_a:
            nome_time_a = st.selectbox("Selecione o Time A (Mandante):", options=list(dict_times.keys()), key="time_a")
            id_time_a = dict_times[nome_time_a]
        with col_b:
            nome_time_b = st.selectbox("Selecione o Time B (Visitante):", options=list(dict_times.keys()), key="time_b")
            id_time_b = dict_times[nome_time_b]
            
        # Botão principal de processamento
        st.write("")
        botao_gerar = st.button("🔥 Gerar MyPredict", use_container_width=True)
    else:
        st.warning("Nenhum clube retornado pela API para esta temporada.")
        botao_gerar = False
else:
    st.error("Falha ao estabelecer conexão inicial com a API Football. Verifique sua API Key ou limite de requisições.")
    botao_gerar = False


# ESPAÇAMENTO LIMPO ENTRE MÓDULOS PRINCIPAIS
st.write("")
st.divider()
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 3] CORPO DO APP: INTERFACE EXPOSITIVA E PROCESSAMENTO DO BOTÃO
# ---------------------------------------------------------------------
st.subheader("📈 Análise de Desempenho e Predições")

if botao_gerar:
    if id_time_a != id_time_b:
        # Incrementa o contador de uso diário
        registrar_acao()
        
        with st.spinner("Buscando dados históricos e confrontos diretos em tempo real..."):
            # Faz a requisição de Head to Head real na API Football
            dados_confrontos = API_buscar_confrontos_diretos(id_time_a, id_time_b)
            
        if dados_confrontos:
            st.success(f"Análise gerada para {nome_time_a} vs {nome_time_b}!")
            
            # Executa cálculo da caixa de ferramentas usando os dados baixados
            win_rate_a = calcular_percentual_vitorias(dados_confrontos, id_time_a)
            
            # Exibição dos resultados reais na tela
            st.metric(label=f"Taxa de Vitória histórica do {nome_time_a} neste confronto", value=f"{win_rate_a}%")
            st.write(f"Total de partidas avaliadas no histórico recente: {len(dados_confrontos)}")
        else:
            st.warning("Nenhum confronto direto recente registrado na API para estes dois clubes.")
    else:
        st.error("Por favor, selecione dois times diferentes para realizar a comparação de confrontos.")
else:
    st.info("Aguardando a definição do confronto e o clique em 'Gerar MyPredict' para iniciar o download de estatísticas.")


# ESPAÇAMENTO LIMPO ENTRE MÓDULOS PRINCIPAIS
st.write("")
st.divider()
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
