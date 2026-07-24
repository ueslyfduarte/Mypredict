import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA API-FOOTBALL (Regra 1) ---
BASE_URL = "https://api-sports.io"

# Busca a chave de forma segura dos Secrets do Streamlit
# No Streamlit Cloud, configure em: Settings -> Secrets
# Conteúdo do Secret: API_SPORTS_KEY = "sua_chave_aqui"
if "API_SPORTS_KEY" in st.secrets:
    API_KEY = st.secrets["API_SPORTS_KEY"]
else:
    st.error("Chave API_SPORTS_KEY não encontrada nos Secrets do Streamlit.")
    st.stop()

HEADERS = {
    "x-apisports-key": API_KEY  # Cabeçalho correto (Regra 1)
}

# --- FUNÇÃO HELPER PARA REQUISIÇÕES (Regra 5) ---
def fazer_requisicao(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        dados = response.json()
        
        # Validação de erros da API-Football (Regra 5)
        if "errors" in dados and dados["errors"]:
            st.error(f"Erro retornado pela API: {dados['errors']}")
            st.json(dados)  # Exibe o JSON bruto do erro
            return None
            
        if "response" in dados and not dados["response"]:
            st.warning(f"Aviso: Resposta vazia para o endpoint /{endpoint}.")
            return None
            
        return dados["response"]
    except Exception as e:
        st.error(f"Falha na conexão com o endpoint /{endpoint}: {e}")
        return None

# --- INTERFACE DO STREAMLIT ---
st.title("⚽ Depurador API-Football v3")
st.sidebar.header("Configurações de Teste")

# Inputs baseados na sequência de testes (Regra 6)
liga_id = st.sidebar.number_input("ID da Liga (Ex: 39 - Premier League)", value=39)
temporada = st.sidebar.number_input("Ano da Temporada (Ex: 2024)", value=2024)
data_teste = st.sidebar.date_input("Data para buscar partidas", datetime.today())

# Abas para organizar a sequência de testes (Regra 6)
aba_a, aba_b, aba_c, aba_d, aba_e = st.tabs([
    "A) Lista Partidas", 
    "B) Estatísticas Ao Vivo", 
    "C) Histórico H2H", 
    "D) Forma do Time", 
    "E) Classificação"
])

# --- PASSO A: Buscar Partidas e IDs (Regra 6a) ---
with aba_a:
    st.header("Passo A: Buscar Partidas e IDs reais")
    data_str = data_teste.strftime("%Y-%m-%d")
    
    if st.button("Executar Passo A"):
        params = {"date": data_str, "league": liga_id, "season": temporada}
        partidas = fazer_requisicao("fixtures", params)
        
        if partidas:
            st.success(f"Encontradas {len(partidas)} partidas.")
            for jogo in partidas:
                fix_id = jogo["fixture"]["id"]
                home = jogo["teams"]["home"]["name"]
                home_id = jogo["teams"]["home"]["id"]
                away = jogo["teams"]["away"]["name"]
                away_id = jogo["teams"]["away"]["id"]
                status = jogo["fixture"]["status"]["short"]
                
                st.write(f"🆔 **ID:** `{fix_id}` | {home} (ID: `{home_id}`) vs {away} (ID: `{away_id}`) | Status: **{status}**")
            
            # Guarda a resposta bruta para validação (Regra 7)
            st.subheader("JSON Bruto da Resposta")
            st.json(partidas[:1]) # Mostra apenas o primeiro para não travar a tela

# --- PASSO B: Estatísticas da Partida (Regra 2 & 6b) ---
with aba_b:
    st.header("Passo B: Estatísticas Ao Vivo / Finalizadas")
    st.info("Regra: Teste primeiro em uma partida FINALIZADA.")
    fixture_id_input = st.number_input("Insira um Fixture ID real obtido no Passo A", value=0)
    
    if st.button("Executar Passo B") and fixture_id_input > 0:
        params = {"fixture": fixture_id_input}
        estatisticas = fazer_requisicao("fixtures/statistics", params)
        if estatisticas:
            st.success("Dados de estatísticas retornados com sucesso!")
            st.json(estatisticas)

# --- PASSO C: Confronto Direto H2H (Regra 3 & 6c) ---
with aba_c:
    st.header("Passo C: Análise Histórica - H2H")
    home_id_input = st.number_input("ID do Time da Casa", value=0, key="h2h_home")
    away_id_input = st.number_input("ID do Time Visitante", value=0, key="h2h_away")
    
    if st.button("Executar Passo C") and home_id_input > 0 and away_id_input > 0:
        params = {"h2h": f"{home_id_input}-{away_id_input}", "last": 10}
        h2h_dados = fazer_requisicao("fixtures/headtohead", params)
        if h2h_dados:
            st.success("Dados de H2H retornados!")
            st.json(h2h_dados)

# --- PASSO D: Forma do Time (Regra 3, 4 & 6d) ---
with aba_d:
    st.header("Passo D: Forma Recente do Time")
    st.info("Regra: Requer obrigatoriamente o parâmetro season.")
    team_id_input = st.number_input("ID do Time", value=0, key="form_team")
    
    if st.button("Executar Passo D") and team_id_input > 0:
        params = {"team": team_id_input, "season": temporada, "last": 10}
        forma_dados = fazer_requisicao("fixtures", params)
        if forma_dados:
            st.success("Dados de forma do time retornados!")
            st.json(forma_dados)

# --- PASSO E: Classificação (Regra 3 & 6e) ---
with aba_e:
    st.header("Passo E: Classificação da Liga")
    if st.button("Executar Passo E"):
        params = {"league": liga_id, "season": temporada}
        classificacao = fazer_requisicao("standings", params)
        if classificacao:
            st.success("Classificação retornada com sucesso!")
            st.json(classificacao)
