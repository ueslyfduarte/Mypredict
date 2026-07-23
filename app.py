import streamlit as st
import requests

st.title("Teste de Conexão: Servidor Alternativo")

# Busca a chave cadastrada na plataforma web do Streamlit
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    st.error("A variável 'API_KEY' não foi encontrada nos Secrets!")
    st.stop()

# URL DO SERVIDOR ALTERNATIVO OFICIAL (Burlar o bloqueio do link principal)
url = "https://rapidapi.com"

headers = {
    'x-apisports-key': api_key
}

if st.button("Testar Servidor Alternativo"):
    with st.spinner("Conectando ao servidor alternativo..."):
        try:
            # Faz a requisição usando a biblioteca padrão requests
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                st.error(f"O servidor alternativo retornou erro: {response.status_code}")
                st.code(response.text[:500])
            else:
                data = response.json()
                
                if not data.get("errors"):
                    st.success("Conexão validada com sucesso pelo servidor alternativo! 🎉")
                    
                    status_resposta = data["response"]
                    st.write(f"**Plano Atual:** {status_resposta['subscription']['plan']}")
                    st.write(f"**Requisições do Dia:** {status_resposta['requests']['current']} / {status_resposta['requests']['limit_day']}")
                else:
                    st.error("Chave recusada pelo servidor alternativo.")
                    st.json(data.get("errors"))
                    
        except Exception as e:
            st.error(f"Erro ao tentar conectar: {e}")
