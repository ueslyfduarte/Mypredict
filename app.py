import streamlit as str
import requests
import pandas as pd

# 1. Configuração inicial da página
st.set_page_config(page_title="Dashboard de Futebol", layout="wide")
st.title("⚽ Estatísticas de Futebol em Tempo Real")

# 2. Configurações da API (Exemplo com API-Football via RapidAPI)
API_URL = "https://rapidapi.com" # Substitua pelo endpoint desejado
API_KEY = st.secrets["API_KEY"] # Forma segura de guardar sua chave no Streamlit Cloud

headers = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": "://rapidapi.com"
}

# 3. Função para buscar dados com cache (Evita estourar o limite de requisições)
@st.cache_data(ttl=3600) # Guarda os dados por 1 hora
def buscar_dados_futebol(url, headers):
    try:
        resposta = requests.get(url, headers=headers)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar na API: {e}")
        return None

# 4. Execução e exibição dos dados
dados = buscar_dados_futebol(API_URL, headers)

if dados:
    st.success("Dados carregados com sucesso!")
    # Transforme o JSON em DataFrame para exibir tabelas limpas
    df = pd.DataFrame(dados.get("response", []))
    st.dataframe(df)

