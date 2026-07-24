import streamlit as st
import requests

# 1. Configuração da página do Streamlit
st.title("⚽ Meu App de Análise Esportiva")
st.write("Dados conectados diretamente da API-Football")

# 2. Insira sua chave da API aqui
API_KEY = "SUA_CHAVE_AQUI"

# 3. Definição dos cabeçalhos de autenticação da API
headers = {
    'x-rapidapi-host': "v3.football.api-sports.io",
    'x-rapidapi-key': API_KEY
}

# 4. URL para buscar as ligas de futebol
url = "https://api-sports.io"

# 5. Botão no Streamlit para buscar os dados
if st.button("Buscar Ligas Disponíveis"):
    with st.spinner("Carregando dados da API..."):
        try:
            response = requests.get(url, headers=headers)
            data = response.json()
            
            # Verifica se a API retornou dados com sucesso
            if response.status_code == 200 and "response" in data:
                ligas = data["response"]
                
                st.success(f"Sucesso! Encontradas {len(ligas)} ligas.")
                
                # Mostra as 10 primeiras ligas na tela do seu app
                for item in ligas[:10]:
                    nome_liga = item["league"]["name"]
                    pais = item["country"]["name"]
                    st.write(f"🏆 **{nome_liga}** ({pais})")
            else:
                st.error("Erro na API. Verifique sua chave ou limite de requisições.")
                st.json(data) # Mostra o erro exato que a API retornou
                
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
