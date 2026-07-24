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
        'x-apisports-key': st.secrets["MINHA_API_KEY"]
    }
else:
    st.error("⚠️ ERRO CRÍTICO: Configure a tag 'MINHA_API_KEY' no painel do Streamlit.")
    st.stop()

BASE_URL = "https://api-sports.io"

# CONTADOR DIÁRIO DE CONTROLE
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
def api_requisitar_todas_leagues():
    """Busca todas as ligas disponíveis diretamente da API Football"""
    try:
        url = f"{BASE_URL}/leagues"
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json().get("response", [])
        else:
            st.error(f"Erro de resposta do servidor da API: Código {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Falha física de conexão com a API: {e}")
        return []

@st.cache_data(ttl=86400)
def API_buscar_teams_por_league(league_id, ano_temporada):
    try:
        url = f"{BASE_URL}/teams"
        parametros = {"league": league_id, "season": ano_temporada}
        response = requests.get(url, headers=HEADERS, params=parametros, timeout=15)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            mapeamento = {item["team"]["name"]: item["team"]["id"] for item in dados}
            return dict(sorted(mapeamento.items()))
        return {}
    except:
        return {}

def API_buscar_confrontos_diretos(team_a_id, team_b_id):
    try:
        url = f"{BASE_URL}/fixtures/headtohead"
        parametros = {"h2h": f"{team_a_id}-{team_b_id}"}
        response = requests.get(url, headers=HEADERS, params=parametros, timeout=15)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except:
        return []

def calcular_percentual_vitorias(historico_partidas, id_time_alvo):
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
# [MÓDULO 2] ENTRADAS PRINCIPAIS DO APP (SELETORES E BOTÃO NO TOPO)
# ---------------------------------------------------------------------
st.title("📊 MyPredicts")

# Faz a chamada real e obrigatória logo na inicialização da página
dados_api_leagues = api_requisitar_todas_leagues()

if dados_api_leagues:
    dict_leagues = {f"{item['league']['name']} ({item['country']['name']})": item for item in dados_api_leagues}
    lista_nomes_ligas = sorted(list(dict_leagues.keys()))
    
    # 1. SELETOR DE LIGA
    nome_liga_selecionada = st.selectbox("Selecione a Liga:", options=lista_nomes_ligas)
    objeto_liga = dict_leagues[nome_liga_selecionada]
    id_liga_selecionada = objeto_liga["league"]["id"]
    
    # Processamento de temporadas (Atual e Passada)
    lista_seasons = objeto_liga.get("seasons", [])
    opcoes_temporadas = {}
    for s in lista_seasons:
        ano_base = s["year"]
        try:
            data_inicio = datetime.strptime(s["start"], "%Y-%m-%d")
            data_fim = datetime.strptime(s["end"], "%Y-%m-%d")
            rotulo = f"{data_inicio.year}/{data_fim.year}" if data_inicio.year != data_fim.year else f"{ano_base}"
        except:
            rotulo = f"{ano_base}"
        opcoes_temporadas[rotulo] = ano_base

    lista_rotulos_ordenados = sorted(list(opcoes_temporadas.keys()), reverse=True)[:2]
    
    # 2. SELETOR DE TEMPORADA
    temporada_rotulo_selecionado = st.selectbox("Selecione a Temporada (Atual ou Passada):", options=lista_rotulos_ordenados)
    ano_temporada_real = opcoes_temporadas[temporada_rotulo_selecionado]
    
    # 3. SELETOR DOS CLUBES EM CASCATA REAL
    dict_times = API_buscar_teams_por_league(league_id=id_liga_selecionada, ano_temporada=ano_temporada_real)
    
    if dict_times:
        col_a, col_b = st.columns(2)
        with col_a:
            nome_time_a = st.selectbox("Selecione o Time A (Mandante):", options=list(dict_times.keys()), key="time_a")
            id_time_a = dict_times[nome_time_a]
        with col_b:
            nome_time_b = st.selectbox("Selecione o Time B (Visitante):", options=list(dict_times.keys()), key="time_b")
            id_time_b = dict_times[nome_time_b]
            
        st.write("")
        botao_gerar = st.button("🔥 Gerar MyPredict", use_container_width=True)
    else:
        st.warning("Nenhum clube retornado pela API para esta temporada.")
        botao_gerar = False
else:
    st.info("Aguardando carregamento inicial das ligas... Se este aviso persistir, certifique-se de que sua chave inserida no painel do Streamlit está ativa e sem espaços vazios.")
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
        registrar_acao()
        
        with st.spinner(f"Buscando histórico real H2H entre {nome_time_a} e {nome_time_b}..."):
            dados_confrontos = API_buscar_confrontos_diretos(id_time_a, id_time_b)
            
        if dados_confrontos:
            st.success(f"Análise gerada para {nome_time_a} vs {nome_time_b}!")
            
            win_rate_a = calcular_percentual_vitorias(dados_confrontos, id_time_a)
            win_rate_b = calcular_percentual_vitorias(dados_confrontos, id_time_b)
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric(label=f"Vitórias do {nome_time_a} no H2H", value=f"{win_rate_a}%")
            with c2:
                st.metric(label=f"Vitórias do {nome_time_b} no H2H", value=f"{win_rate_b}%")
                
            st.write(f"Total de partidas computadas no histórico da API: {len(dados_confrontos)}")
        else:
            st.warning("Nenhum confronto direto recente registrado na API para estes dois clubes nesta competição.")
    else:
        st.error("Por favor, selecione dois clubes diferentes para realizar a comparação.")
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
