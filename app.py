import streamlit as st
import pandas as pd

st.set_page_config(page_title="Predições de Futebol", page_icon="⚽", layout="wide")
st.title("📊 Análise de Dados Históricos - Open Data")
st.subheader("Extração de Estatísticas para Modelos de Predição")

# URLs dos arquivos CSV consolidados das ligas (Temporada atual)
LIGAS_CSV = {
    "Premier League (Inglaterra)": "https://football-data.co.uk",
    "La Liga (Espanha)": "https://football-data.co.uk",
    "Serie A (Itália)": "https://football-data.co.uk",
    "Bundesliga (Alemanha)": "https://football-data.co.uk"
}

liga_selecionada = st.selectbox("Selecione a Competição para Analisar:", list(LIGAS_CSV.keys()))

@st.cache_data(ttl=3600)
def carregar_dados_abertos(url):
    try:
        # Carrega o CSV direto da fonte pública via Pandas
        df = pd.read_csv(url)
        
        # Seleciona apenas as colunas principais de interesse para predições
        # HomeTeam = Mandante, AwayTeam = Visitante, FTHG = Gols Mandante, FTAG = Gols Visitante, FTR = Resultado Final
        colunas_uteis = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG', 'FTR', 'HS', 'AS', 'HST', 'AST']
        
        # Filtra o DataFrame caso as colunas existam no arquivo
        df_filtrado = df[[col1 for col1 in colunas_uteis if col1 in df.columns]]
        return df_filtrado
    except Exception as e:
        st.error(f"Erro ao carregar base de dados: {e}")
        return None

with st.spinner("Carregando histórico de partidas do servidor público..."):
    df_partidas = carregar_dados_abertos(LIGAS_CSV[liga_selecionada])

if df_partidas is not None:
    st.success(f"Histórico de {liga_selecionada} carregado com sucesso!")
    
    # Exibe o histórico de todos os jogos ocorridos na temporada
    st.markdown("### 🗓️ Histórico de Partidas Realizadas")
    st.dataframe(df_partidas, use_container_width=True)
    
    # Gera uma tabela de classificação dinâmica baseada nos resultados calculados
    st.markdown("### 🏆 Significado das principais colunas para seu modelo:")
    st.write("- **FTHG / FTAG**: Gols do Mandante / Gols do Visitante")
    st.write("- **HS / AS**: Chutes do Mandante / Chutes do Visitante")
    st.write("- **HST / AST**: Chutes no Alvo do Mandante / Chutes no Alvo do Visitante")
