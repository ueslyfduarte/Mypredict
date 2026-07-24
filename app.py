import streamlit as st
import pandas as pd

st.set_page_config(page_title="Predições de Futebol", page_icon="⚽", layout="wide")
st.title("📊 Análise de Dados Históricos - Open Data")
st.subheader("Extração de Estatísticas para Modelos de Predição")

# Links oficiais e estáveis da Temporada 24/25 do Football-Data.co.uk
LIGAS_CSV = {
    "Premier League (Inglaterra) 24/25": "https://football-data.co.uk",
    "La Liga (Espanha) 24/25": "https://football-data.co.uk",
    "Serie A (Itália) 24/25": "https://football-data.co.uk",
    "Bundesliga (Alemanha) 24/25": "https://football-data.co.uk"
}

liga_selecionada = st.selectbox("Selecione a Competição para Analisar:", list(LIGAS_CSV.keys()))

@st.cache_data(ttl=3600)
def carregar_dados_abertos(url):
    try:
        # Carrega o CSV direto da URL pública usando tratamento nativo do Pandas
        df = pd.read_csv(url)
        
        # Filtra as colunas principais para o seu modelo de previsão
        colunas_uteis = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS', 'HST', 'AST']
        df_filtrado = df[[col for col in colunas_uteis if col in df.columns]].dropna()
        
        return df_filtrado
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
        return None

with st.spinner("Carregando banco de dados de partidas..."):
    df_partidas = carregar_dados_abertos(LIGAS_CSV[liga_selecionada])

if df_partidas is not None and not df_partidas.empty:
    st.success(f"Base de dados da {liga_selecionada} carregada com sucesso!")
    
    # Exibe a tabela interativa limpa
    st.dataframe(df_partidas, use_container_width=True)
    
    # Informações auxiliares das colunas para modelagem
    st.markdown("### 🏆 Guia de Métricas Avançadas Carregadas:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total de Jogos Processados", value=len(df_partidas))
    with col2:
        st.write("**FTHG / FTAG**: Gols do Mandante / Visitante")
        st.write("**FTR**: Resultado (H=Mandante, A=Visitante, D=Empate)")
    with col3:
        st.write("**HS / AS**: Chutes do Mandante / Visitante")
        st.write("**HST / AST**: Chutes no Alvo do Mandante / Visitante")
else:
    st.warning("Nenhum dado pôde ser extraído deste campeonato.")
