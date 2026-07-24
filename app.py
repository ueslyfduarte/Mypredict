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

# CONTADOR DIÁRIO DE AÇÕES (CONTA FREE)
hoje_str = datetime.today().strftime('%Y-%m-%d')

if "data_contador" not in st.session_state:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

if st.session_state["data_contador"] != hoje_str:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

def registrar_acao():
    """Chame esta função sempre que o usuário executar uma consulta paga à API"""
    st.session_state["contador_acoes"] += 1


# ---------------------------------------------------------------------
# [MÓDULO RESTRITO - PARTE 1] FUNÇÕES DE CONEXÃO DIRETA DA API
# ---------------------------------------------------------------------

# IDs das principais ligas mundiais (Top 8 + Copas) para puxar de forma cirúrgica
TOP_LIGAS_IDS = [71, 72, 39, 140, 135, 78, 61, 2, 13, 3] # Ex: Brasileirão, Premier League, UCL, Libertadores...

@st.cache_data(ttl=86400)
def api_buscar_leagues_direto():
    """Gasta exatamente 1 requisição para trazer as configurações e temporadas das ligas no topo"""
    try:
        ids_string = ",".join(map(str, TOP_LIGAS_IDS))
        url = f"{BASE_URL}/leagues"
        response = requests.get(url, headers=HEADERS, params={"ids": ids_string}, timeout=12)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except:
        return []

@st.cache_data(ttl=86400)
def api_buscar_times_por_liga(id_liga, ano_temporada):
    """Busca a lista de clubes associada à liga e temporada escolhidas"""
    try:
        url = f"{BASE_URL}/teams"
        response = requests.get(url, headers=HEADERS, params={"league": id_liga, "season": ano_temporada}, timeout=12)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            return dict(sorted({item["team"]["name"]: item["team"]["id"] for item in dados}.items()))
        return {}
    except:
        return {}


# ---------------------------------------------------------------------
# [MÓDULO 2] INTERFACE DE ENTRADA (SELETORES E BOTÃO REAL NO TOPO)
# ---------------------------------------------------------------------
st.title("📊 MyPredicts")

# Dispara a busca automática e real direto no endpoint da API Football
dados_api_leagues = api_buscar_leagues_direto()

if dados_api_leagues:
    # Mapeia dinamicamente os nomes das ligas com seus respectivos objetos de resposta da API
    dict_ligas_reais = {f"{item['league']['name']} ({item['country']['name']})": item for item in dados_api_leagues}
    lista_nomes_ligas = sorted(list(dict_ligas_reais.keys()))
    
    # 1. SELETOR DE COMPETIÇÃO (Formato rolar ou pesquisar)
    nome_liga_selecionada = st.selectbox(
        "🏆 Selecione a Competição:",
        options=lista_nomes_ligas,
        index=0,
        help="Escolha ou pesquise o campeonato na lista real entregue pela API."
    )
    
    objeto_liga = dict_ligas_reais[nome_liga_selecionada]
    id_liga_selecionada = objeto_liga["league"]["id"]
    
    # Processa as datas reais de início e fim fornecidas pela API para tratar calendários híbridos (Brasil vs Europa)
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

    # Restringe a exibição estritamente às duas últimas (Atual e Passada)
    lista_rotulos_ordenados = sorted(list(opcoes_temporadas.keys()), reverse=True)[:2]
    
    # 2. SELETOR DE TEMPORADA (Atual ou Passada)
    temporada_rotulo_selecionado = st.selectbox(
        "📅 Selecione a Temporada (Atual ou Passada):",
        options=lista_rotulos_ordenados,
        index=0
    )
    ano_temporada_real = opcoes_temporadas[temporada_rotulo_selecionado]
    
    # 3. SELEÇÃO EM CASCATA DOS TIMES (Busca real baseada nas escolhas anteriores)
    dict_times_reais = api_buscar_times_por_liga(id_liga_selecionada, ano_temporada_real)
    
    if dict_times_reais:
        col_a, col_b = st.columns(2)
        
        with col_a:
            time_a = st.selectbox(
                "🏠 Selecione o Time A (Mandante):",
                options=list(dict_times_reais.keys()),
                index=0,
                key="mandante_real"
            )
            id_time_a = dict_times_reais[time_a]
            
        with col_b:
            time_b = st.selectbox(
                "🚌 Selecione o Time B (Visitante):",
                options=list(dict_times_reais.keys()),
                index=0,
                key="visitante_real"
            )
            id_time_b = dict_times_reais[time_b]
            
        # 4. BOTÃO PRINCIPAL DE DISPARO DO CRUNCH DE DADOS
        st.write("")
        botao_gerar = st.button("🔥 Gerar MyPredict", use_container_width=True, on_click=registrar_acao)
    else:
        st.warning("⚠️ Limite por minuto atingido ou nenhum clube listado para os parâmetros selecionados.")
        botao_gerar = False
else:
    st.error("❌ Falha de conexão inicial com a API Football. Verifique se o seu token ('MINHA_API_KEY') está devidamente configurado.")
    botao_gerar = False


# ESPAÇAMENTO COMPACTO APENAS ENTRE OS MÓDULOS DO APLICATIVO
st.write("")
st.divider()
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 3] RESERVADO: CAIXA DE FERRAMENTAS (INVISÍVEL NA INTERFACE)
# ---------------------------------------------------------------------
# Reúna abaixo todas as suas futuras defs lógicas e fórmulas matemáticas.

def calcular_probabilidades_confronto():
    """Sua fórmula matemática de Win Rate e BTTS será inserida aqui"""
    pass


# ---------------------------------------------------------------------
# [MÓDULO 4] PROCESSAMENTO DE SAÍDA E ANÁLISE DE DADOS
# ---------------------------------------------------------------------
st.subheader("📈 Análise de Desempenho e Predições")

if botao_gerar:
    if id_time_a != id_time_b:
        st.success(f"⚡ Estrutura do MyPredict disparada para: {time_a} x {time_b}")
        # As chamadas reais de estatísticas e H2H usando os IDs 'id_time_a' e 'id_time_b' serão conectadas aqui.
    else:
        st.error("Erro: Selecione dois clubes diferentes para realizar a análise de confronto.")
else:
    st.caption("Aguardando a definição do confronto e o clique em 'Gerar MyPredict'.")
