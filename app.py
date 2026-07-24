import streamlit as st
import requests

st.title("⚽ Painel de Futebol - API-Football")

# 1. Puxa a sua chave de forma segura dos Secrets do Streamlit
try:
    API_KEY = st.secrets["MINHA_API_KEY"]
except Exception:
    st.error("Erro: A variável 'MINHA_API_KEY' não foi configurada nos Secrets do Streamlit.")
    st.stop()

# 2. Configura os parâmetros de acesso da API-Football
# Usando a URL v3 oficial do serviço
API_URL = "https://api-sports.io"

# O cabeçalho PRECISA ser exatamente 'x-apisports-key' para este site
headers = {
    "x-apisports-key": API_KEY,
    "Accept": "application/json"
}

# 3. Interface do usuário
st.write("Clique no botão abaixo para testar a conexão e listar as ligas disponíveis.")

if st.button("Carregar Ligas de Futebol"):
    with st.spinner("Buscando dados no servidor da API-Football..."):
        try:
            # Faz a chamada HTTP de forma segura
            response = requests.get(API_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            dados = response.json()
            
            # Verifica se o servidor retornou algum erro interno de API (ex: chave errada)
            if dados.get("errors"):
                st.error(f"A API retornou um erro: {dados['errors']}")
            else:
                st.success("Conexão efetuada com sucesso!")
                
                # Exibe a quantidade de ligas encontradas
                total_ligas = len(dados.get("response", []))
                st.metric(label="Total de Ligas Disponíveis", value=total_ligas)
                
                # Mostra o JSON bruto estruturado na tela
                st.json(dados)
                
        except requests.exceptions.HTTPError as e:
            st.error(f"Erro de comunicação HTTP: {e}")
        except requests.exceptions.RequestException:
            st.error("Não foi possível conectar aos servidores da API-Football. Verifique sua conexão.")
