import streamlit as st
import requests

st.set_page_config(page_title="MyPredicts", page_icon="🎲")
st.title("🎲 MyPredicts - Diagnóstico de Chaves")

API_FOOTBALL = st.secrets["MINHA_API_KEY"]
API_FOOTYSTATS = st.secrets["API_FOOTYSTATS"]

# ==========================================
# TESTE 1: API-FOOTBALL (Modo Direto / API-Sports)
# ==========================================
st.subheader("1. Teste API-Football")

url_football = "https://api-sports.io"
# Tentativa usando o cabeçalho nativo da API-Sports
headers_football = {
    'x-apisports-key': API_FOOTBALL
}

try:
    req_fb = requests.get(url_football, headers=headers_football)
    if req_fb.status_code == 200:
        st.success("API-Football Conectada!")
        st.json(req_fb.json())
    else:
        st.error(f"Erro 403: Verifique se sua chave é do plano correto da API-Sports ou se requer a URL do RapidAPI.")
except Exception as e:
    st.error(f"Erro: {e}")

st.divider()

# ==========================================
# TESTE 2: FOOTYSTATS (Endpoint permitido no plano inicial)
# ==========================================
st.subheader("2. Teste FootyStats")

# Mudamos para o endpoint de ligas selecionadas, mais aceito em planos iniciais
url_footystats = "https://footystats.org"
parametros_footystats = {"key": API_FOOTYSTATS}

try:
    req_fs = requests.get(url_footystats, params=parametros_footystats)
    if req_fs.status_code == 200:
        st.success("FootyStats Conectada!")
        st.json(req_fs.json())
    else:
        st.error(f"Erro 403: Sua chave FootyStats não tem permissão para este plano/recurso.")
except Exception as e:
    st.error(f"Erro: {e}")
