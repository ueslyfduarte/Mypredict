import streamlit as st
import requests

st.title("Teste de Conexão Corrigido: API-Football")

# Busca a chave cadastrada na plataforma web do Streamlit
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    st.error("A variável 'API_KEY' não foi encontrada nos Secrets!")
    st.stop()

# URL oficial e segura de status
url = "https://api-sports.io"

# Adicionado User-Agent para evitar que o servidor rejeite a conexão do Python
headers = {
    'x-apisports-key': api_key,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}

if st.button("Testar Conexão Oficial"):
    with st.spinner("Autenticando..."):
        try:
            # Faz a requisição de status
            response = requests.get(url, headers=headers)
            
            # Mostra o erro real se o servidor não retornar sucesso antes de tentar ler o JSON
            if response.status_code != 200:
                st.error(f"O servidor retornou um código de erro: {response.status_code}")
                st.text("Texto retornado pelo servidor:")
                st.code(response.text[:500]) # Exibe o começo do erro para sabermos o que é
            else:
                data = response.json()
                
                # Valida se não há erros na estrutura interna do JSON da API
                if not data.get("errors"):
                    st.success("Conexão validada! Sua API_Football está funcionando. 🎉")
                    
                    status_resposta = data["response"]
                    st.write(f"**Plano Atual:** {status_resposta['subscription']['plan']}")
                    st.write(f"**Requisições do Dia:** {status_resposta['requests']['current']} / {status_resposta['requests']['limit_day']}")
                else:
                    st.error("A API rejeitou a credencial. Verifique se a sua chave nos Secrets está certa.")
                    st.json(data.get("errors"))
                    
        except Exception as e:
            st.error(f"Erro inesperado no aplicativo: {e}")
