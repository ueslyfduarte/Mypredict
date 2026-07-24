import streamlit as st
import requests

# Configuração da página do Streamlit
st.set_page_config(page_title="MyPredicts", page_icon="🎲")
st.title("🎲 MyPredicts - Painel de Conexões")

# 1. Recuperação das chaves configuradas na aba Secrets do Streamlit
API_FOOTBALL = st.secrets["MINHA_API_KEY"]
API_FOOTYSTATS = st.secrets["API_FOOTYSTATS"]

# ==========================================
# TESTE DE CONEXÃO 1: API-FOOTBALL
# ==========================================
st.subheader("1. Conexão API-Football")

url_football = "https://api-sports.io"
headers_football = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': API_FOOTBALL
}

try:
    # Executa a requisição enviando as chaves nos cabeçalhos (headers)
    req_fb = requests.get(url_football, headers=headers_football)
    
    if req_fb.status_code == 200:
        st.success("Conexão com API-Football estabelecida com sucesso!")
        st.json(req_fb.json())
    else:
        st.error(f"Erro na API-Football. Status HTTP: {req_fb.status_code}")
except Exception as e:
    st.error(f"Falha ao conectar na API-Football: {e}")

st.divider()

# ==========================================
# TESTE DE CONEXÃO 2: FOOTYSTATS
# ==========================================
st.subheader("2. Conexão FootyStats")

url_footystats = "https://footystats.org"
# Isola a chave como parâmetro para evitar que ela se misture com a URL base
parametros_footystats = {"key": API_FOOTYSTATS}

try:
    # Executa a requisição usando params= para anexar a chave de forma segura
    req_fs = requests.get(url_footystats, params=parametros_footystats)
    
    if req_fs.status_code == 200:
        st.success("Conexão com FootyStats estabelecida com sucesso!")
        st.json(req_fs.json())
    else:
        st.error(f"Erro na FootyStats. Status HTTP: {req_fs.status_code}")
except Exception as e:
    st.error(f"Falha ao conectar na FootyStats: {e}")
