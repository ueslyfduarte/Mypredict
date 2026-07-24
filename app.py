import streamlit as st
import requests
from datetime import datetime

st.title("⚽ Central de Jogos ao Vivo e do Dia")

# 1. Conexão automática com os Secrets salvos no site
API_KEY_FOOTBALL = st.secrets["MINHA_API_KEY"]

# 2. Função para buscar os jogos de hoje
@st.cache_data(ttl=600)  # Atualiza os dados a cada 10 minutos
def buscar_jogos_hoje():
    hoje = datetime.today().strftime('%Y-%m-%d')
    url = "https://api-sports.io"
    
    # Parâmetros para buscar os jogos da data atual
    querystring = {"date": hoje}
    
    headers = {
        'x-rapidapi-host': 'v3.football.api-sports.io',
        'x-rapidapi-key': API_KEY_FOOTBALL
    }
    
    resposta = requests.get(url, headers=headers, params=querystring)
    return resposta.json().get("response", [])

# 3. Execução e exibição na tela
lista_jogos = buscar_jogos_hoje()

if not lista_jogos:
    st.info("Nenhum jogo encontrado para a data de hoje.")
else:
    for jogo in lista_jogos:
        liga = jogo['league']['name']
        paiz = jogo['league']['country']
        home = jogo['teams']['home']['name']
        away = jogo['teams']['away']['name']
        
        # Placar (se já tiver começado ou terminado)
        gols_home = jogo['goals']['home']
        gols_away = jogo['goals']['away']
        status = jogo['fixture']['status']['long']
        
        # Formatação visual simples
        with st.container():
            st.markdown(f"**{liga} ({paiz})** - *{status}*")
            if gols_home is not None:
                st.write(f"🏠 {home} **{gols_home}** x **{gols_away}** {away} 🚌")
            else:
                st.write(f"🏠 {home} x {away} 🚌")
            st.divider()
