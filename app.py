import streamlit as st
import requests

st.title("🎲 MyPredicts - Teste de Conexão")

# 1. Puxando as chaves diretamente da aba secreta do Streamlit
API_FOOTBALL = st.secrets["MINHA_API_KEY"]
API_FOOTYSTATS = st.secrets["API_FOOTYSTATS"]

# 2. Teste de Conexão Externa 1: API-Football
st.subheader("1. Conexão API-Football")
url_football = "https://api-sports.io"
headers_football = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': API_FOOTBALL
}

try:
    req_fb = requests.get(url_football, headers=headers_football)
    if req_fb.status_code == 200:
        st.success("Conexão com API-Football estabelecida com sucesso!")
        st.json(req_fb.json())
    else:
        st.error(f"Erro na API-Football. Status: {req_fb.status_code}")
except Exception as e:
    st.error(f"Falha ao conectar na API-Football: {e}")

st.divider()

# 3. Teste de Conexão Externa 2: FootyStats
st.subheader("2. Conexão FootyStats")
url_footystats = f"https://footystats.org{API_FOOTYSTATS}"

try:
    req_fs = requests.get(url_footystats)
    if req_fs.status_code == 200:
        st.success("Conexão com FootyStats estabelecida com sucesso!")
        st.json(req_fs.json())
    else:
        st.error(f"Erro na FootyStats. Status: {req_fs.status_code}")
except Exception as e:
    st.error(f"Falha ao conectar na FootyStats: {e}")
