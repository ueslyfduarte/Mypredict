import streamlit as st
import requests
import pandas as pd

# 1. Configuração de autenticação e segurança
# Guarde suas chaves no arquivo .streamlit/secrets.toml para produção
API_KEY = st.secrets.get("api_football_key", "SUA_CHAVE_AQUI")
API_HOST = "v3.football.api-sports.io"

# 2. Função de busca com cache (essencial para economizar sua cota da API)
@st.cache_data(ttl=3600)  # Guarda o resultado em cache por 1 hora (3600 segundos)
def buscar_dados_futebol(endpoint, params=None):
    url = f"https://{API_HOST}/{endpoint}"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API-Football: {e}")
        return None

# 3. Interface no Streamlit
st.title("⚽ Dashboard API-Football")

# Campo para o usuário digitar o ID do campeonato (Ex: 71 para o Brasileirão)
league_id = st.number_input("Digite o ID da Liga:", min_value=1, value=71)
season = st.number_input("Digite o Ano da Temporada (Ano atual ou anterior):", min_value=2010, max_value=2026, value=2026)

if st.button("Buscar Classificação"):
    with st.spinner("Acessando dados da API..."):
        # Endpoint de classificação (standings)
        endpoint = "standings"
        parametros = {"league": league_id, "season": season}
        
        dados = buscar_dados_futebol(endpoint, params=parametros)
        
        if dados and "response" in dados and dados["response"]:
            st.success("Dados carregados!")
            
            # Estruturando os dados retornados em um DataFrame para exibição amigável
            try:
                liga_info = dados["response"][0]["league"]
                st.subheader(f"Tabela de: {liga_info['name']} - {liga_info['country']}")
                
                tabela_dados = liga_info["standings"][0]
                
                # Criando uma lista limpa para o Pandas DataFrame
                lista_times = []
                for item in tabela_dados:
                    lista_times.append({
                        "Posição": item["rank"],
                        "Time": item["team"]["name"],
                        "Pontos": item["points"],
                        "Jogos": item["all"]["played"],
                        "Vitórias": item["all"]["win"],
                        "Saldos de Gols": item["goalsDiff"]
                    })
                
                df = pd.DataFrame(lista_times).set_index("Posição")
                st.dataframe(df, use_container_width=True) # Exibe como tabela interativa
                
            except (KeyError, IndexError):
                st.warning("Formato de resposta inesperado ou liga sem classificação disponível.")
        else:
            st.error("Nenhum dado encontrado para os parâmetros informados.")
