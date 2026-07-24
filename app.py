import streamlit as st
import requests
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="MyPredicts", layout="wide")

# ---------------------------------------------------------------------
# [MÓDULO 1] CONFIGURAÇÕES DA API
# ---------------------------------------------------------------------
if "MINHA_API_KEY" in st.secrets:
    HEADERS = {'x-apisports-key': st.secrets["MINHA_API_KEY"]}
else:
    st.error("⚠️ Configure a tag 'MINHA_API_KEY' no painel do Streamlit.")
    st.stop()

BASE_URL = "https://api-sports.io"

if "contador_acoes" not in st.session_state:
    st.session_state["contador_acoes"] = 0

def registrar_acao():
    st.session_state["contador_acoes"] += 1


# ---------------------------------------------------------------------
# [MÓDULO RESTRITO] CAIXA DE FERRAMENTAS (REQUISIÇÕES REAIS)
# ---------------------------------------------------------------------

# IDs oficiais das suas Top 8 Ligas na API Football
TOP_8_IDS = [71, 39, 140, 135, 78, 61, 2, 13]

@st.cache_data(ttl=86400)
def api_buscar_top_8_dinamico():
    """Gasta exatamente 1 requisição para trazer os dados reais e atualizados das Top 8"""
    try:
        # Transforma a lista de IDs em uma string separada por vírgulas: '71,39,140...'
        ids_string = ",".join(map(str, TOP_8_IDS))
        url = f"{BASE_URL}/leagues"
        response = requests.get(url, headers=HEADERS, params={"ids": ids_string}, timeout=12)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except:
        return []

@st.cache_data(ttl=86400)
def api_buscar_uma_liga_por_nome(nome_pesquisa):
    """Busca cirurgicamente apenas uma liga caso queira sair das Top 8"""
    try:
        url = f"{BASE_URL}/leagues"
        response = requests.get(url, headers=HEADERS, params={"search": nome_pesquisa}, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except:
        return []

@st.cache_data(ttl=86400)
def api_buscar_times_por_liga(id_liga, ano_temporada):
    try:
        url = f"{BASE_URL}/teams"
        response = requests.get(url, headers=HEADERS, params={"league": id_liga, "season": ano_temporada}, timeout=10)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            return dict(sorted({item["team"]["name"]: item["team"]["id"] for item in dados}.items()))
        return {}
    except:
        return {}

@st.cache_data(ttl=3600)
def api_buscar_h2h(id_time_a, id_time_b):
    try:
        url = f"{BASE_URL}/fixtures/headtohead"
        response = requests.get(url, headers=HEADERS, params={"h2h": f"{id_time_a}-{id_time_b}"}, timeout=12)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except:
        return []


# ---------------------------------------------------------------------
# [MÓDULO 2] ENTRADAS DO APLICATIVO (TOPO DO DESIGN)
# ---------------------------------------------------------------------
st.title("📊 MyPredicts")

modo_liga = st.radio("Origem da Competição:", options=["🏆 Escolher das Top 8 (Gasta 1 req)", "🔍 Pesquisar Outra Liga (Sob Demanda)"], horizontal=True)

dados_da_liga_escolhida = None

if modo_liga == "🏆 Escolher das Top 8 (Gasta 1 req)":
    # Faz a chamada leve focada apenas nos 8 IDs
    lista_top_8 = api_buscar_top_8_dinamico()
    if lista_top_8:
        dict_top_8 = {f"{item['league']['name']} ({item['country']['name']})": item for item in lista_top_8}
        liga_selecionada = st.selectbox("Selecione a Liga Principal:", options=sorted(list(dict_top_8.keys())))
        dados_da_liga_escolhida = dict_top_8[liga_selecionada]
    else:
        st.error("Não foi possível conectar à API para puxar as Top 8. Verifique sua chave ou o limite por minuto.")
else:
    termo_busca = st.text_input("Digite o nome exato ou parte da liga (Ex: Copa do Brasil, Championship...):", value="")
    if termo_busca:
        lista_busca = api_buscar_uma_liga_por_nome(termo_busca)
        if lista_busca:
            dict_busca = {f"{item['league']['name']} ({item['country']['name']})": item for item in lista_busca}
            liga_selecionada = st.selectbox("Selecione a competição encontrada:", options=sorted(list(dict_busca.keys())))
            dados_da_liga_escolhida = dict_busca[liga_selecionada]
        else:
            st.warning("Nenhuma liga encontrada com este nome na API.")

# Se tivermos os dados reais da liga (seja do Top 8 ou da busca)
if dados_da_liga_escolhida:
    id_liga_final = dados_da_liga_escolhida["league"]["id"]
    
    # Monta as temporadas reais daquela liga específica (Trata Brasil vs Europa perfeitamente)
    lista_seasons = dados_da_liga_escolhida.get("seasons", [])
    opcoes_seasons = {}
    for s in lista_seasons:
        year = s["year"]
        try:
            start_date = datetime.strptime(s["start"], "%Y-%m-%d")
            end_date = datetime.strptime(s["end"], "%Y-%m-%d")
            rotulo = f"{start_date.year}/{end_date.year}" if start_date.year != end_date.year else f"{year}"
        except:
            rotulo = f"{year}"
        opcoes_seasons[rotulo] = year
        
    # Pega apenas as duas últimas cadastradas (Atual e Passada)
    rotulos_ordenados = sorted(list(opcoes_seasons.keys()), reverse=True)[:2]
    
    rotulo_temporada = st.selectbox("Selecione a Temporada (Atual ou Passada):", options=rotulos_ordenados)
    ano_temporada = opcoes_seasons[rotulo_temporada]
    
    # Busca os clubes reais da competição baseados no ID e no ano correto
    dict_times = api_buscar_times_por_liga(id_liga_final, ano_temporada)
    
    if dict_times:
        col1, col2 = st.columns(2)
        with col1:
            time_a = st.selectbox("Time A (Mandante):", options=list(dict_times.keys()), key="ta")
            id_a = dict_times[time_a]
        with col2:
            time_b = st.selectbox("Time B (Visitante):", options=list(dict_times.keys()), key="tb")
            id_b = dict_times[time_b]
            
        st.write("")
        botao_gerar = st.button("🔥 Gerar MyPredict", use_container_width=True)
    else:
        st.warning("Nenhum clube retornado pela API. Sua chave pode ter estourado o limite de 10 requisições por minuto. Aguarde um instante.")
        botao_gerar = False
else:
    botao_gerar = False


# Espaçamento limpo entre módulos
st.write("")
st.divider()
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 3] EXIBIÇÃO E PROCESSAMENTO DOS DADOS (CORPO)
# ---------------------------------------------------------------------
st.subheader("📈 Análise de Desempenho e Predições")

if botao_gerar:
    if id_a != id_b:
        registrar_acao()
        
        with st.spinner("Analisando histórico de confrontos diretos em tempo real..."):
            confrontos = api_buscar_h2h(id_a, id_b)
            
        if confrontos:
            st.success(f"Confronto analisado: {time_a} vs {time_b}")
            st.write(f"Total de jogos recentes encontrados na API: **{len(confrontos)}**")
            
            ultimo_jogo = confrontos[0]  # Pega o confronto mais recente da lista
            data_jogo = ultimo_jogo["fixture"]["date"][:10]
            placar_home = ultimo_jogo["goals"]["home"]
            placar_away = ultimo_jogo["goals"]["away"]
            st.info(f"Último confronto registrado ({data_jogo}): {ultimo_jogo['teams']['home']['name']} {placar_home} x {placar_away} {ultimo_jogo['teams']['away']['name']}")
        else:
            st.warning("Nenhum histórico de confronto direto recente encontrado para estes dois clubes nesta liga.")
    else:
        st.error("Por favor, selecione dois clubes diferentes para realizar a análise.")
else:
    st.info("Defina a liga, os times e clique em 'Gerar MyPredict'.")


# Espaçamento limpo entre módulos
st.write("")
st.divider()
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 4] MONITORAMENTO DIÁRIO
# ---------------------------------------------------------------------
st.subheader("📊 Painel de Controle de Requisições")
st.metric(label="Ações Efetuadas Hoje", value=st.session_state["contador_acoes"])
