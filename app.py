import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="MyPredict", page_icon="⚽", layout="wide")
st.title("🏆 MyPredict: DataScout")
st.subheader("Análise Estatística Avançada para Previsões")

# 1. Recupera a chave de segurança salva no st.secrets
api_key = st.secrets["MINHA_API_KEY"]
headers = {
    'x-apisports-key': api_key,
    'User-Agent': '',
    'Accept': '*/*'
}

# Dicionário mapeando os IDs oficiais das competições na API-Sports
LIGAS = {
    "Brasileirão Série A": 71,
    "Premier League (Inglaterra)": 39,
    "La Liga (Espanha)": 140,
    "Champions League": 2
}

liga_selecionada = st.selectbox("Selecione a Competição:", list(LIGAS.keys()))
id_liga = LIGAS[liga_selecionada]

# Temporada atual de referência para busca de dados
ano_temporada = 2026

@st.cache_data(ttl=600)  # Guarda os dados na memória por 10 minutos para economizar requisições
def buscar_classificacao(league_id, season):
    # URL formatada corretamente com o '?' separando os parâmetros de busca
    url = f"https://api-sports.io{league_id}&season={season}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("response", [])
        return None
    except Exception as e:
        st.error(f"Erro de conexão com o servidor da API: {e}")
        return None

with st.spinner("Buscando dados atualizados da API..."):
    dados = buscar_classificacao(id_liga, ano_temporada)

if dados:
    try:
        # CORREÇÃO 1: 'dados' é uma lista, então pegamos o índice [0] para acessar o dicionário
        liga_data = dados[0]["league"]
        
        # CORREÇÃO 2: 'standings' é uma lista de listas. O índice [0] isola a tabela de pontos corridos
        tabela_real = liga_data["standings"][0]
        
        lista_times = []
        for item in tabela_real:
            lista_times.append({
                "Posição": item["rank"],
                "Clube": item["team"]["name"],
                "Pontos": item["points"],
                "Jogos": item["all"]["played"],
                "Vitórias": item["all"]["win"],
                "Empates": item["all"]["draw"],
                "Derrotas": item["all"]["lose"],
                "Gols Pró": item["all"]["goals"]["for"],
                "Gols Contra": item["all"]["goals"]["against"],
                "Forma": item.get("form", "-")
            })
            
        # Transforma a lista de dicionários estruturada em uma tabela de dados do Pandas
        df = pd.DataFrame(lista_times)
        
        st.success(f"Dados do {liga_selecionada} carregados com sucesso!")
        # Renderiza a planilha final de forma interativa e adaptada à largura da tela
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Erro ao processar a resposta do servidor: {e}. Certifique-se de que a temporada {ano_temporada} possui dados ativos para esta competição.")
else:
    st.error("Não foi possível carregar os dados. Verifique os logs do console ou suas credenciais nos segredos do Streamlit.")
