import streamlit as st
import requests

st.title("Teste de Conexão Corrigido: API-Football")

# Busca a chave cadastrada na plataforma web do Streamlit
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    st.error("A variável 'API_KEY' não foi encontrada nos Secrets!")
    st.stop()

# URL CORRIGIDA: Servidor oficial de dados + endpoint de status
url = "https://api-sports.io"

headers = {
    'x-apisports-key': api_key  
}

if st.button("Testar Conexão Oficial"):
    with st.spinner("Autenticando..."):
        try:
            # Faz a requisição GET simples e gratuita de status
            response = requests.get(url, headers=headers)
            data = response.json()
            
            # Valida se o servidor respondeu 200 e se não há erros na estrutura do JSON
            if response.status_code == 200 and not data.get("errors"):
                st.success("Conexão validada! Sua API_Football está funcionando. 🎉")
                
                # Exibe informações do plano direto na tela do app
                status_resposta = data["response"]
                st.write(f"**Plano Atual:** {status_resposta['subscription']['plan']}")
                st.write(f"**Requisições do Dia:** {status_resposta['requests']['current']} / {status_resposta['requests']['limit_day']}")
            else:
                st.error("A API rejeitou a credencial. Verifique se o código colado no site está correto.")
                st.json(data.get("errors", data))
                
        except Exception as e:
            st.error(f"Erro de conexão com o servidor: {e}")
