import streamlit as st
import requests
from datetime import datetime




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




# ---------------------------------------------------------------------
# [MÓDULO 2] INICIALIZAÇÃO DA MEMÓRIA DO APP (SESSION STATE)
# ---------------------------------------------------------------------

if "liga_selecionada" not in st.session_state:
    st.session_state.liga_selecionada = ""

if "time_casa" not in st.session_state:
    st.session_state.time_casa = None

if "time_fora" not in st.session_state:
    st.session_state.time_fora = None

if "requisicoes_feitas" not in st.session_state:
    st.session_state.requisicoes_feitas = 0

if "limite_diario" not in st.session_state:
    st.session_state.limite_diario = 100

if "cache_ligas" not in st.session_state:
    st.session_state.cache_ligas = []

if "cache_times" not in st.session_state:
    st.session_state.cache_times = []

if "banco_dados_partida" not in st.session_state:
    st.session_state.banco_dados_partida = {
        "info_liga": {},
        "dados_time_casa": {},
        "dados_time_fora": {},
        "historico_confrontos": {}
    }




# ---------------------------------------------------------------------
# [MÓDULO 3] FUNÇÕES MODULARES (ENGENHARIA DE DADOS OCULTA)
# ---------------------------------------------------------------------

def puxar_todas_ligas():
    if st.session_state.cache_ligas:
        return st.session_state.cache_ligas
        
    url = f"{BASE_URL}/leagues"
    try:
        response = requests.get(url, headers=HEADERS)
        dados_json = response.json()
        
        # Se a API retornou alguma mensagem de erro interna
        if dados_json.get("errors"):
            st.error(f"❌ Erro retornado pela API-Football: {dados_json['errors']}")
            return []
            
        dados = dados_json.get("response", [])
        if response.status_code == 200 and dados:
            st.session_state.cache_ligas = dados
            return dados
        return []
    except Exception as e:
        st.error(f"❌ Falha de conexão com o servidor: {e}")
        return []


def puxar_times_da_liga(id_liga, ano_temporada):
    url = f"{BASE_URL}/teams"
    params = {"league": id_liga, "season": ano_temporada}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        dados = response.json().get("response", [])
        if response.status_code == 200:
            st.session_state.cache_times = dados
            return dados
        return []
    except:
        return []


def extrair_e_armazenar_dados_confronto(id_liga, id_casa, id_fora, ano_temporada):
    url_stats_casa = f"{BASE_URL}/teams/statistics"
    res_casa = requests.get(url_stats_casa, headers=HEADERS, params={"league": id_liga, "season": ano_temporada, "team": id_casa})
    
    url_stats_fora = f"{BASE_URL}/teams/statistics"
    res_fora = requests.get(url_stats_fora, headers=HEADERS, params={"league": id_liga, "season": ano_temporada, "team": id_fora})
    
    url_h2h = f"{BASE_URL}/fixtures/headtohead"
    res_h2h = requests.get(url_h2h, headers=HEADERS, params={"h2h": f"{id_casa}-{id_fora}", "last": 10})

    limit = res_casa.headers.get("x-ratelimit-requests-limit")
    remaining = res_casa.headers.get("x-ratelimit-requests-remaining")
    
    if limit and remaining:
        st.session_state.limite_diario = int(limit)
        st.session_state.requisicoes_feitas = int(limit) - int(remaining)
    else:
        st.session_state.requisicoes_feitas += 3

    st.session_state.banco_dados_partida["info_liga"] = {"id_liga": id_liga, "temporada": ano_temporada}
    st.session_state.banco_dados_partida["dados_time_casa"] = res_casa.json().get("response", {}) if res_casa.status_code == 200 else {}
    st.session_state.banco_dados_partida["dados_time_fora"] = res_fora.json().get("response", {}) if res_fora.status_code == 200 else {}
    st.session_state.banco_dados_partida["historico_confrontos"] = res_h2h.json().get("response", []) if res_h2h.status_code == 200 else []




# ---------------------------------------------------------------------
# [MÓDULO 4] MONITOR DE CONSUMO DA API (TOPO DA PÁGINA)
# ---------------------------------------------------------------------

col_req1, col_req2 = st.columns(2)

with col_req1:
    st.metric(label="📊 Requisições Gastas Hoje", value=st.session_state.requisicoes_feitas)

with col_req2:
    st.metric(label="🚨 Limite do Seu Plano", value=st.session_state.limite_diario)

st.write("")
st.write("")
st.divider()
st.write("")
st.write("")




# ---------------------------------------------------------------------
# [MÓDULO 5] INTERFACE DE ENTRADA EXCLUSIVA (SELEÇÃO EM CASCATA)
# ---------------------------------------------------------------------

st.header("🎯 Configuração da Partida")
st.write("*(Clique nos campos abaixo e digite para pesquisar)*")
st.write("")

# Botão de emergência para limpar travamentos na memória do navegador
if st.button("🔄 Forçar Atualização/Limpar Memória"):
    st.session_state.cache_ligas = []
    st.session_state.cache_times = []
    st.rerun()

st.write("")

ano_atual = datetime.now().year
lista_anos = [str(ano) for ano in range(ano_atual, ano_atual - 6, -1)]

temporada_selecionada = st.selectbox(
    "Selecione a Temporada/Ano:",
    options=lista_anos,
    index=0
)
ano_api = int(temporada_selecionada)

st.write("")

lista_ligas = puxar_todas_ligas()
opcoes_ligas = {}

for l in lista_ligas:
    anos_disponiveis = [int(seasons['year']) for seasons in l['seasons']]
    if ano_api in anos_disponiveis:
        nome_exibicao = f"{l['league']['name']} ({l['country']['name']})"
        opcoes_ligas[nome_exibicao] = l['league']['id']

lista_nomes_ligas = sorted(list(opcoes_ligas.keys()))

if not lista_nomes_ligas and lista_ligas:
    st.warning(f"⚠️ Nenhuma liga processada para o ano {ano_api}. Tente clicar no botão 'Forçar Atualização' acima.")

default_index = 0
if st.session_state.liga_selecionada in lista_nomes_ligas:
    default_index = lista_nomes_ligas.index(st.session_state.liga_selecionada) + 1

liga_escolhida = st.selectbox(
    "Pesquise e Selecione a Liga ou Copa:",
    options=[""] + lista_nomes_ligas,
    index=default_index
)

if liga_escolhida != st.session_state.liga_selecionada:
    st.session_state.liga_selecionada = liga_escolhida
    st.session_state.cache_times = []

if liga_escolhida != "":
    id_liga_atual = opcoes_ligas[liga_escolhida]
    
    st.write("")
    if st.button("🔍 Buscar Times da Liga", type="secondary"):
        with st.spinner("Buscando clubes participantes na API..."):
            puxar_times_da_liga(id_liga=id_liga_atual, ano_temporada=ano_api)
            st.rerun()
            
    if st.session_state.cache_times:
        st.write("")
        st.write("")
        st.divider()
        st.write("")
        st.write("")
        
        st.subheader("👥 Seleção dos Times")
        st.write("")
        
        opcoes_times = {t['team']['name']: t['team']['id'] for t in st.session_state.cache_times}
        nomes_times = sorted(list(opcoes_times.keys()))
        
        col1, col2 = st.columns(2)
        
        with col1:
            time_casa = st.selectbox("Pesquise o Mandante (Casa):", options=[""] + nomes_times, index=0)
            
        with col2:
            nomes_fora = [t for t in nomes_times if t != time_casa] if time_casa else nomes_times
            time_fora = st.selectbox("Pesquise o Visitante (Fora):", options=[""] + nomes_fora, index=0)
            
        if time_casa != "" and time_fora != "":
            id_casa = opcoes_times[time_casa]
            id_fora = opcoes_times[time_fora]
            
            st.write("")
            st.write("")
            st.divider()
            st.write("")
            st.write("")
            
            if st.session_state.requisicoes_feitas >= st.session_state.limite_diario:
                st.error("❌ Limite diário de requisições atingido!")
            else:
                if st.button("🚀 Carregar e Armazenar Dados do Confronto", type="primary"):
                    with st.spinner(f"Buscando dados na API-Football..."):
                        st.session_state.time_casa = time_casa
                        st.session_state.time_fora = time_fora
                        
                        extrair_e_armazenar_dados_confronto(
                            id_liga=id_liga_atual, 
                            id_casa=id_casa, 
                            id_fora=id_fora, 
                            ano_temporada=ano_api
                        )
                    st.success(f"Dados de {time_casa} x {time_fora} guardados com sucesso!")


