import streamlit as st
import requests

st.title("⚽ Teste de Conexão - API-Football")

# 1. A chave é criada primeiro
try:
    API_KEY = st.secrets["MINHA_API_KEY"]
except Exception:
    st.error("Erro: A variável 'MINHA_API_KEY' não foi encontrada nos Secrets do Streamlit.")
    st.stop()

# 2. Agora os cabeçalhos usam a chave que já existe
API_URL = "https://api-sports.io"

headers = {
    "x-apisports-key": API_KEY,
    "Accept": "application/json"
}

# 3. Execução da chamada
if st.button("Testar Ligação com a API"):
    with st.spinner("Conectando..."):
        try:
            response = requests.get(API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            dados = response.json()
            st.success("Conectado com sucesso!")
            st.json(dados)
            
        except Exception as e:
            st.error(f"Erro ao conectar: {e}")
