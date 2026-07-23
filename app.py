import streamlit as st
import requests
import pandas as pd

# 1. Configuração obrigatória no topo da página
st.set_page_config(page_title="Dashboard de Futebol", layout="wide")

st.title("⚽ Estatísticas de Futebol em Tempo Real")

# 2. Resgata a chave salva de forma segura nas Secrets do Streamlit
try:
    API_KEY = st.secrets["API_KEY"]
except KeyError:
    st.error("Aviso: Adicione a sua 'API_KEY' nas configurações (Secrets) do painel do Streamlit.")
    st.stop()

# Cabeçalhos padrão para quem assina direto no Dashboard da API-Football
HEADERS = {
    "x-apisports-key": API_KEY
}
URL_JOGOS_HOJE = "https://api-sports.io" # Substitua pela data atual se desejar

# 3. Função de busca com cache para economizar sua cota gratuita diária
@st.cache_data(ttl=900) # Mantém na memória por 15 minutos (900 segundos)
def buscar_jogos_do_dia():
    try:
        resposta = requests.get(URL_JOGOS_HOJE, headers=HEADERS)
        resposta.raise_for_status()
        return resposta.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na conexão com a API: {e}")
        return None

# 4. Processamento dos dados na tela
dados_api = buscar_jogos_do_dia()

if dados_api and "response" in dados_api and dados_api["response"]:
    st.subheader("📅 Partidas Agendadas para Hoje")
    
    lista_partidas = []
    for partida in dados_api["response"]:
        lista_partidas.append({
            "Campeonato": partida["league"]["name"],
            "Mandante": partida["teams"]["home"]["name"],
            "Placar Casa": partida["goals"]["home"],
            "Placar Fora": partida["goals"]["away"],
            "Visitante": partida["teams"]["away"]["name"],
            "Status": partida["fixture"]["status"]["long"]
        })
        
    df_jogos = pd.DataFrame(lista_partidas)
    st.dataframe(df_jogos, use_container_width=True)
else:
    st.warning("Nenhum dado retornado. Verifique se sua chave está correta ou se esgotou o limite de requisições de hoje.")
