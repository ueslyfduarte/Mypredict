import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="MyPredict", page_icon="⚽", layout="wide")
st.title("🏆 MyPredict: DataScout")
st.subheader("Análise Estatística Avançada para Previsões")

# 1. Puxa a chave segura do Streamlit
api_key = st.secrets["MINHA_API_KEY"]
headers = {
    'x-apisports-key': api_key,
    'User-Agent': '',
    'Accept': '*/*'
}

# Dicionário com os IDs das ligas na API-Sports
LIGAS = {
    "Brasileirão Série A": 71,
    "Premier League (Inglaterra)": 39,
    "La Liga (Espanha)": 140,
    "Champions League": 2
}

liga_selecionada = st.selectbox("Selecione a Competição:", list(LIGAS.keys()))
id_liga = LIGAS[liga_selecionada]

# Ajuste automático de temporada para o ano corrente (2026)
ano_temporada = 2026

@st.cache_data(ttl=600)  # Evita gastar seus créditos a cada clique
def buscar_classificacao(league_id, season):
    url = f"https://api-sports.io{league_id}&season={season}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("response", [])
        return None
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

with st.spinner("Buscando dados atualizados da API..."):
    dados = buscar_classificacao(id_liga, ano_temporada)

if dados:
    try:
        # A API retorna uma lista. Pegamos o primeiro item dela.
        liga_data = dados[0]["league"]
        # Dentro de standings, os dados ficam na primeira posição da lista interna
        tabela = liga_data["standings"][0]
        
        lista_times = []
        for item in tabela:
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
        # Exibe a tabela interativa lindamente na tela do celular ou Xbox
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}. Pode ser que a temporada {ano_temporada} ainda não tenha dados gerados para esta liga.")
else:
    st.error("Não foi possível carregar os dados. Verifique suas credenciais nos segredos do Streamlit.")
