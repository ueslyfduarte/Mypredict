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

# CONTADOR DIÁRIO (PLANO FREE)
hoje_str = datetime.today().strftime('%Y-%m-%d')
if "data_contador" not in st.session_state:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

if st.session_state["data_contador"] != hoje_str:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

def registrar_acao():
    st.session_state["contador_acoes"] += 1


# FUNÇÕES DE REQUISIÇÃO (COM TRATAMENTO DE ERROS SEGURO)
@st.cache_data(ttl=86400)
def buscar_dados_ligas_completas():
    try:
        url = f"{BASE_URL}/leagues"
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            resultado = response.json().get("response", [])
            if resultado:
                return resultado
        st.error(f"A API retornou código {response.status_code}. Usando lista padrão local para economizar créditos.")
        return []
    except Exception as e:
        return []

@st.cache_data(ttl=86400)
def buscar_teams_por_league_api(league_id, ano_temporada):
    try:
        url = f"{BASE_URL}/teams"
        parametros = {"league": league_id, "season": ano_temporada}
        response = requests.get(url, headers=HEADERS, params=parametros, timeout=10)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            mapeamento_teams = {item["team"]["name"]: item["team"]["id"] for item in dados}
            return dict(sorted(mapeamento_teams.items()))
        return {}
    except:
        return {}


# ---------------------------------------------------------------------
# [MÓDULO RESTRITO] CAIXA DE FERRAMENTAS (APENAS CÁLCULOS INTERNOS)
# ---------------------------------------------------------------------
def calcular_media_gols(gols_marcados, partidas_jogadas):
    if partidas_jogadas > 0:
        return round(gols_marcados / partidas_jogadas, 2)
    return 0.0

def buscar_confrontos_diretos_api(team_a_id, team_b_id):
    """Busca o histórico H2H entre os dois clubes selecionados"""
    # Exemplo de chamada futura: /fixtures/headtohead?h2h=id_a-id_b
    pass


# ---------------------------------------------------------------------
# [MÓDULO 2] ENTRADAS PRINCIPAIS DO APP (TOPO DO DESIGN)
# ---------------------------------------------------------------------
st.title("📊 MyPredicts")

dados_ligas = buscar_dados_ligas_completas()

# SE A API FALHAR OU DEMORAR, LISTA BACKUP DE SEGURANÇA PARA NÃO TRAVAR SEU DESIGN
if not dados_ligas:
    st.warning("⚠️ Temporariamente sem resposta da API. Carregando modo de segurança local.")
    dict_leagues_mock = {
        "Brasileirão Série A": {"league": {"id": 71}, "seasons": [{"year": 2026, "start": "2026-04-01", "end": "2026-12-01"}, {"year": 2025, "start": "2025-04-01", "end": "2025-12-01"}]},
        "Premier League": {"league": {"id": 39}, "seasons": [{"year": 2025, "start": "2025-08-11", "end": "2026-05-19"}]},
        "La Liga": {"league": {"id": 140}, "seasons": [{"year": 2025, "start": "2025-08-12", "end": "2026-05-26"}]}
    }
    lista_nomes_ligas = list(dict_leagues_mock.keys())
    dict_leagues = dict_leagues_mock
else:
    dict_leagues = {item["league"]["name"]: item for item in dados_ligas}
    lista_nomes_ligas = sorted(list(dict_leagues.keys()))

# 1. SELEÇÃO DA LIGA (Rolar ou Pesquisar)
nome_liga_selecionada = st.selectbox("Selecione a Liga:", options=lista_nomes_ligas)

objeto_liga = dict_leagues[nome_liga_selecionada]
id_liga_selecionada = objeto_liga["league"]["id"]

# Processamento de temporadas (Atual e Passada)
lista_seasons = objeto_liga["seasons"]
opcoes_temporadas = {}
for s in lista_seasons:
    ano_base = s["year"]
    data_inicio = datetime.strptime(s["start"], "%Y-%m-%d")
    data_fim = datetime.strptime(s["end"], "%Y-%m-%d")
    rotulo = f"{data_inicio.year}/{data_fim.year}" if data_inicio.year != data_fim.year else f"{ano_base}"
    opcoes_temporadas[rotulo] = ano_base

lista_rotulos_ordenados = sorted(list(opcoes_temporadas.keys()), reverse=True)[:2]

# 2. SELEÇÃO DA TEMPORADA
temporada_rotulo_selecionado = st.selectbox("Selecione a Temporada (Atual ou Passada):", options=lista_rotulos_ordenados)
ano_temporada_real = opcoes_temporadas[temporada_rotulo_selecionado]

# 3. SELEÇÃO EM CASCATA: TIME A E TIME B
dict_times = buscar_teams_por_league_api(league_id=id_liga_selecionada, ano_temporada=ano_temporada_real)

if not dict_times:
    # Backup local caso mude de liga rápido demais e a API demore a responder
    dict_times = {"Selecione uma liga válida": 0}

col_a, col_b = st.columns(2)
with col_a:
    nome_time_a = st.selectbox("Selecione o Time A (Mandante):", options=list(dict_times.keys()), key="time_a")
    id_time_a = dict_times[nome_time_a]

with col_b:
    nome_time_b = st.selectbox("Selecione o Time B (Visitante):", options=list(dict_times.keys()), key="time_b")
    id_time_b = dict_times[nome_time_b]

# BOTÃO DE DISPARO DA CRUNCH DE DADOS
st.write("")
botao_gerar = st.button("🔥 Gerar MyPredict", use_container_width=True)

# ESPAÇAMENTO LIMPO ENTRE MÓDULOS PRINCIPAIS
st.write("")
st.divider()
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 3] CORPO DO APP: INTERFACE EXPOSITIVA E EXECUÇÃO
# ---------------------------------------------------------------------
st.subheader("📈 Análise de Desempenho e Predições")

if botao_gerar:
    if id_time_a != 0 and id_time_b != 0 and id_time_a != id_time_b:
        registrar_acao() # Conta o clique no painel Free
        
        st.success(f"⚡ MyPredict Gerado com Sucesso para o confronto: {nome_time_a} vs {nome_time_b}!")
        st.info(f"Parâmetros de busca enviados -> Liga ID: {id_liga_selecionada} | Temporada: {ano_temporada_real}")
        
        # Coloque suas chamadas de renderização de confrontos ou tabelas matemáticas aqui dentro deste bloco...
    elif id_time_a == id_time_b and id_time_a != 0:
        st.error("Erro: O Time A não pode ser igual ao Time B para uma análise de confronto.")
    else:
        st.info("Por favor, selecione times válidos nos seletores acima.")
else:
    st.info("Aguardando clique no botão 'Gerar MyPredict' para processar e baixar as estatísticas dos confrontos.")


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
