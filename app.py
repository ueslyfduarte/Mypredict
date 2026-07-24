import streamlit as st
import requests
from datetime import datetime
import time

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
# SISTEMA DE CAPTURA AUTOMÁTICA BLINDADO (EVITA TRAVAMENTO GLOBAL)
# ---------------------------------------------------------------------

@st.cache_data(ttl=86400)
def api_requisitar_ligas_seguro():
    """Busca as ligas na API com sistema de tentativa dupla em caso de lentidão"""
    url = f"{BASE_URL}/leagues"
    for tentativa in range(2):  # Tenta até 2 vezes antes de usar o plano de contingência
        try:
            response = requests.get(url, headers=HEADERS, timeout=8)
            if response.status_code == 200:
                resultado = response.json().get("response", [])
                if resultado and isinstance(resultado, list) and len(resultado) > 0:
                    return resultado
            time.sleep(1)  # Aguarda 1 segundo antes da nova tentativa
        except:
            time.sleep(1)
            
    # RETORNO COMPACTO DE CONTINGÊNCIA (Garante que os seletores nunca sumam da tela)
    return [
        {
            "league": {"id": 71, "name": "Brasileirão Série A"},
            "seasons": [{"year": 2026, "start": "2026-01-01", "end": "2026-12-31"}, {"year": 2025, "start": "2025-01-01", "end": "2025-12-31"}]
        },
        {
            "league": {"id": 39, "name": "Premier League"},
            "seasons": [{"year": 2025, "start": "2025-08-01", "end": "2026-05-31"}, {"year": 2024, "start": "2024-08-01", "end": "2025-05-31"}]
        },
        {
            "league": {"id": 140, "name": "La Liga"},
            "seasons": [{"year": 2025, "start": "2025-08-01", "end": "2026-05-31"}, {"year": 2024, "start": "2024-08-01", "end": "2025-05-31"}]
        }
    ]

# Executa e persiste obrigatoriamente a lista estruturada na memória global
if "dados_api_leagues" not in st.session_state or not st.session_state["dados_api_leagues"]:
    st.session_state["dados_api_leagues"] = api_requisitar_ligas_seguro()


# ---------------------------------------------------------------------
# [MÓDULO RESTRITO] CAIXA DE FERRAMENTAS (FUNÇÕES DE CONEXÃO E CÁLCULO)
# ---------------------------------------------------------------------

@st.cache_data(ttl=86400)
def API_buscar_teams_por_league(league_id, ano_temporada):
    try:
        url = f"{BASE_URL}/teams"
        parametros = {"league": league_id, "season": ano_temporada}
        response = requests.get(url, headers=HEADERS, params=parametros, timeout=10)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            if dados:
                mapeamento = {item["team"]["name"]: item["team"]["id"] for item in dados}
                return dict(sorted(mapeamento.items()))
        return {}
    except:
        return {}

def API_buscar_confrontos_diretos(team_a_id, team_b_id):
    try:
        url = f"{BASE_URL}/fixtures/headtohead"
        parametros = {"h2h": f"{team_a_id}-{team_b_id}"}
        response = requests.get(url, headers=HEADERS, params=parametros, timeout=12)
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

dados_api_leagues = st.session_state["dados_api_leagues"]

# Monta o mapa de dados garantindo estrutura de dicionário válida
dict_leagues = {item["league"]["name"]: item for item in dados_api_leagues if "league" in item}
lista_nomes_ligas = sorted(list(dict_leagues.keys()))

# 1. SELETOR DE LIGA (Pesquisar ou Rolar)
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
temporada_rotulo_selecionado = st.selectbox("Selecione a Temporada:", options=lista_rotulos_ordenados)
ano_temporada_real = opcoes_temporadas[temporada_rotulo_selecionado]

# 3. SELETOR DOS CLUBES EM CASCATA
dict_times = API_buscar_teams_por_league(league_id=id_liga_selecionada, ano_temporada=ano_temporada_real)

# Fallback visual caso os clubes demorem para carregar devido ao limite por minuto da API
if not dict_times:
    st.caption("⚠️ Sincronizando clubes da liga selecionada na API... Se a lista persistir em branco, aguarde alguns segundos e atualize a página.")
    dict_times = {"Aguardando dados da API...": 0}

col_a, col_b = st.columns(2)
with col_a:
    nome_time_a = st.selectbox("Selecione o Time A (Mandante):", options=list(dict_times.keys()), key="time_a")
    id_time_a = dict_times[nome_time_a]
with col_b:
    nome_time_b = st.selectbox("Selecione o Time B (Visitante):", options=list(dict_times.keys()), key="time_b")
    id_time_b = dict_times[nome_time_b]
    
st.write("")
botao_gerar = st.button("🔥 Gerar MyPredict", use_container_width=True)


# ESPAÇAMENTO LIMPO ENTRE MÓDULOS PRINCIPAIS
st.write("")
st.divider()
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 3] CORPO DO APP: INTERFACE EXPOSITIVA E PROCESSAMENTO DO BOTÃO
# ---------------------------------------------------------------------
st.subheader("📈 Análise de Desempenho e Predições")

if botao_gerar:
    if id_time_a != 0 and id_time_b != 0 and id_time_a != id_time_b:
        registrar_acao()
        
        with st.spinner("Buscando dados históricos e confrontos diretos em tempo real..."):
            dados_confrontos = API_buscar_confrontos_diretos(id_time_a, id_time_b)
            
        if dados_confrontos:
            st.success(f"Análise gerada para {nome_time_a} vs {nome_time_b}!")
            
            # Chamada da função matemática da caixa de ferramentas
            win_rate_a = calcular_percentual_vitorias(dados_confrontos, id_time_a)
            
            st.metric(label=f"Taxa de Vitória histórica do {nome_time_a} neste confronto", value=f"{win_rate_a}%")
            st.write(f"Total de partidas avaliadas no histórico recente: {len(dados_confrontos)}")
        else:
            st.warning("Nenhum confronto direto recente registrado na API para estes dois clubes nesta liga específica.")
    elif id_time_a == id_time_b and id_time_a != 0:
        st.error("Por favor, escolha dois clubes diferentes para gerar o confronto.")
    else:
        st.info("Aguardando carregamento dos dados dos clubes selecionados.")
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
