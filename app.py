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
    'User-Agent': 'Mozilla/5.0',
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

@st.cache_data(ttl=600)
def buscar_classificacao(league_id, season):
    # Mudamos aqui! A URL base fica limpa e fixa
    url = "https://api-sports.io"
    
    # O próprio Python vai juntar esses parâmetros na URL com as barras e os '?' corretos
    parametros = {
        "league": league_id,
        "season": season
    }
    
    try:
        response = requests.get(url, headers=headers, params=parametros)
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
        # Acessa o primeiro item da lista de resposta da API
        liga_data = dados[0]["league"]
        
        # Isola a tabela real de times
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
            
        df = pd.DataFrame(lista_times)
        
        st.success(f"Dados do {liga_selecionada} carregados com sucesso!")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Erro ao processar a resposta do servidor: {e}.")
else:
    st.error("Não foi possível carregar os dados. Verifique sua credencial ou se o plano está ativo.")
