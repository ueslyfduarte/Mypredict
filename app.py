import streamlit as st
import requests
from datetime import datetime

# Configuração da Interface do Streamlit
st.set_page_config(page_title="Depurador API-Football", layout="wide")
st.title("⚽ Diagnóstico Estruturado: Checklist de Integração")
st.write("Executando a sequência de testes na ordem exata definida pelo checklist.")

# 1 e 3. Autenticação e Chave Segura via Streamlit Secrets
try:
    API_KEY = st.secrets["API_SPORTS_KEY"]
    headers = {
        'x-apisports-key': API_KEY
    }
    base_url = "https://v3.football.api-sports.io"
    st.success("🔒 Chave 'API_SPORTS_KEY' carregada com sucesso!")
except Exception as e:
    st.error("❌ Erro ao carregar a chave. Verifique as configurações de Secrets no Streamlit.")
    st.stop()

# Data atual para preenchimento automático inteligente (Formato YYYY-MM-DD)
data_hoje = datetime.now().strftime("%Y-%m-%d")

# Criação das 5 Abas Independentes (Item 11)
aba_a, aba_b, aba_c, aba_d, aba_e = st.tabs([
    "a) Buscar Partidas (GET /fixtures)", 
    "b) Estatísticas (GET /fixtures/statistics)", 
    "c) Histórico H2H (GET /fixtures/headtohead)", 
    "d) Forma do Time (GET /fixtures)", 
    "e) Classificação (GET /standings)"
])

# ==========================================
# TESTE A: Obter IDs Reais (Item 11.a e Item 4) - CORRIGIDO COM SEASON
# ==========================================
with aba_a:
    st.header("Etapa A: Buscar Partidas")
    st.write("Retorna apenas a lista de partidas do dia (Item 4).")
    
    data_teste = st.text_input("Data do Teste (YYYY-MM-DD):", value=data_hoje)
    liga_teste = st.text_input("ID da Liga (Premier League padrão = 39):", value="39")
    ano_season_a = st.text_input("Ano da Temporada (Ex: 2026):", value="2026", key="season_a")
    
    # ADICIONADO &season= À URL CONFORME EXIGIDO PELA API
    url_a = f"{base_url}/fixtures?date={data_teste}&league={liga_teste}&season={ano_season_a}"
    st.info(f"🔗 **URL Utilizada:** {url_a}")
    
    if st.button("Executar Etapa A"):
        with st.spinner("Buscando partidas..."):
            try:
                res = requests.get(url_a, headers=headers)
                data = res.json()
                
                st.subheader("Resposta Bruta da API:")
                st.json(data)
                
                # Validação sistemática da resposta (Item 9)
                if "errors" in data and data["errors"]:
                    st.error("❌ Erro retornado pela API. Verifique o JSON acima.")
                elif "response" in data and len(data["response"]) == 0:
                    st.warning("⚠️ Resposta vazia ('response': []). Sem partidas nesta data e temporada específicas.")
                else:
                    st.success("✅ Partida localizada com sucesso!")
                    # Como response é uma lista [], pegamos o primeiro item [0]
                    jogo = data["response"][0] 
                    st.write(f"• **ID da Partida (fixture id):** `{jogo['fixture']['id']}`")
                    st.write(f"• **ID Time Casa (home id):** `{jogo['teams']['home']['id']}` — {jogo['teams']['home']['name']}")
                    st.write(f"• **ID Time Fora (away id):** `{jogo['teams']['away']['id']}` — {jogo['teams']['away']['name']}")
            except Exception as e:
                st.error(f"Falha de execução: {e}")


# ==========================================
# TESTE B: Estatísticas Detalhadas (Item 11.b e Item 5)
# ==========================================
with aba_b:
    st.header("Etapa B: Estatísticas ao Vivo / Pós-Jogo")
    st.write("Item 5: Use um ID real de partida finalizada obtido na Etapa A.")
    
    id_partida = st.text_input("Insira o fixture ID real:", key="fixture_b")
    
    url_b = f"{base_url}/fixtures/statistics?fixture={id_partida}"
    st.info(f"🔗 **URL Utilizada:** {url_b}")
    
    if st.button("Executar Etapa B") and id_partida:
        with st.spinner("Buscando estatísticas detalhadas..."):
            try:
                res = requests.get(url_b, headers=headers)
                data = res.json()
                st.subheader("Resposta Bruta da API:")
                st.json(data)
            except Exception as e:
                st.error(f"Falha de execução: {e}")

# ==========================================
# TESTE C: Confronto Direto Histórico (Item 11.c e Item 6)
# ==========================================
with aba_c:
    st.header("Etapa C: Análise Histórica (H2H)")
    st.write("Item 6: Confrontos diretos entre dois clubes específicos.")
    
    col1, col2 = st.columns(2)
    with col1: id_casa = st.text_input("ID Time Casa:", key="home_c")
    with col2: id_fora = st.text_input("ID Time Fora:", key="away_c")
    
    url_c = f"{base_url}/fixtures/headtohead?h2h={id_casa}-{id_fora}&last=10"
    st.info(f"🔗 **URL Utilizada:** {url_c}")
    
    if st.button("Executar Etapa C") and id_casa and id_fora:
        with st.spinner("Buscando histórico H2H..."):
            try:
                res = requests.get(url_c, headers=headers)
                data = res.json()
                st.subheader("Resposta Bruta da API:")
                st.json(data)
            except Exception as e:
                st.error(f"Falha de execução: {e}")

# ==========================================
# TESTE D: Desempenho Recente do Time (Item 11.d, 6 e 7)
# ==========================================
with aba_d:
    st.header("Etapa D: Forma Recente do Time")
    st.write("Item 7: É obrigatório incluir o ano da temporada (season) nesta chamada.")
    
    id_time = st.text_input("ID do Time:", key="team_d")
    ano_season_d = st.text_input("Ano da Temporada (Ex: 2024, 2025, 2026):", value="2026", key="season_d")
    
    url_d = f"{base_url}/fixtures?team={id_time}&season={ano_season_d}&last=10"
    st.info(f"🔗 **URL Utilizada:** {url_d}")
    
    if st.button("Executar Etapa D") and id_time:
        with st.spinner("Buscando forma do clube..."):
            try:
                res = requests.get(url_d, headers=headers)
                data = res.json()
                st.subheader("Resposta Bruta da API:")
                st.json(data)
            except Exception as e:
                st.error(f"Falha de execução: {e}")

# ==========================================
# TESTE E: Tabela de Classificação (Item 11.e, 6 e 7)
# ==========================================
with aba_e:
    st.header("Etapa E: Tabela de Classificação")
    st.write("Item 6 e 7: Retorna as posições atuais exigindo liga e temporada.")
    
    id_liga_e = st.text_input("ID da Liga para Classificação:", value="39", key="league_e")
    ano_season_e = st.text_input("Ano da Temporada:", value="2026", key="season_e")
    
    url_e = f"{base_url}/standings?league={id_liga_e}&season={ano_season_e}"
    st.info(f"🔗 **URL Utilizada:** {url_e}")
    
    if st.button("Executar Etapa E"):
        with st.spinner("Buscando tabela de classificação..."):
            try:
                res = requests.get(url_e, headers=headers)
                data = res.json()
                st.subheader("Resposta Bruta da API:")
                st.json(data)
            except Exception as e:
                st.error(f"Falha de execução: {e}")
