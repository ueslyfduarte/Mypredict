import streamlit as st
import requests

st.title("Teste de Conexão: API-Football")

# Busca a chave cadastrada direto no painel do Streamlit Web
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    st.error("A variável 'API_KEY' não foi encontrada nos Secrets do Streamlit!")
    st.stop()

# Configuração oficial da API-Football
url = "https://api-sports.io"
headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': api_key
}

if st.button("Testar Conexão com API-Football"):
    with st.spinner("Consultando status da conta..."):
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            
            # Valida se a requisição deu certo e se não há mensagens de erro da API
            if response.status_code == 200 and not data.get("errors"):
                st.success("Conexão com a API-Football validada com sucesso! 🎉")
                
                # Exibe dados de consumo do seu plano
                conta = data["response"]["account"]
                requisicoes = data["response"]["requests"]
                
                st.write(f"**Usuário:** {conta['firstname']} {conta['lastname']}")
                st.write(f"**E-mail:** {conta['email']}")
                st.metric(label="Requisições Usadas Hoje", value=f"{requisicoes['current']} / {requisicoes['limit_day']}")
            else:
                st.error("A API retornou um erro de autenticação. Verifique sua chave nos Secrets.")
                st.json(data.get("errors", data))
                
        except Exception as e:
            st.error(f"Erro de rede ou conexão: {e}")
