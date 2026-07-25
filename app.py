import streamlit as st
import requests

# Título do app
st.title("🏃 Meu Primeiro Teste")

# Aqui pegamos sua chave secreta
API_KEY = st.secrets["API_FOOTBALL_KEY"]

# Perguntamos pro usuário um time
time = st.text_input("Digite o nome de um time (ex: Flamengo):")

# Quando ele clicar no botão
if st.button("Buscar Time"):
    if time:
        # Preparamos o "pedido" pra API
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
        
        url = "https://v3.football.api-sports.io/teams"
        params = {"search": time}
        
        # Fazemos o pedido
        resposta = requests.get(url, headers=headers, params=params)
        dados = resposta.json()
        
        # Mostramos o resultado
        st.write("Resultado encontrado:")
        st.json(dados)
