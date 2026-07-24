import streamlit as st
import pandas as pd
import cloudscraper

st.set_page_config(page_title="Predições de Futebol", page_icon="⚽", layout="wide")
st.title("📊 Análise de Dados Históricos - FBref")
st.subheader("Extração de Estatísticas Avançadas sem API")

# Mapeamento de URLs do FBref para as principais competições
LIGAS = {
    "Brasileirão Série A": "https://fbref.com",
    "Premier League (Inglaterra)": "https://fbref.com",
    "La Liga (Espanha)": "https://fbref.com",
    "Champions League": "https://fbref.com"
}

liga_selecionada = st.selectbox("Selecione a Competição para Analisar:", list(LIGAS.keys()))

@st.cache_data(ttl=3600)  # Guarda os dados por 1 hora para o app abrir instantaneamente
def raspar_dados_fbref(url):
    try:
        # Cria o scraper que simula um navegador real para evitar bloqueios do Cloudflare
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        
        if response.status_code == 200:
            # O pandas lê as tabelas de dentro do código HTML capturado pelo cloudscraper
            tabelas = pd.read_html(response.text)
            
            # A primeira tabela (índice 0) é a classificação geral do campeonato
            df_classificacao = tabelas[0]
            
            # Remove colunas vazias ou de notas que o FBref costuma criar
            if 'Notes' in df_classificacao.columns:
                df_classificacao = df_classificacao.drop(columns=['Notes'])
                
            return df_classificacao
        else:
            st.error(f"O FBref rejeitou a conexão. Código de status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erro ao processar a raspagem: {e}")
        return None

with st.spinner("Buscando tabelas de estatísticas avançadas direto do FBref..."):
    df_classificacao = raspar_dados_fbref(LIGAS[liga_selecionada])

if df_classificacao is not None:
    st.success(f"Dados de {liga_selecionada} carregados com sucesso!")
    
    # Exibe a tabela interativa lindamente na tela do Streamlit
    st.dataframe(df_classificacao, use_container_width=True)
    
    st.markdown("### 💡 Próximo Passo para o seu Modelo de Predição")
    st.write(
        "Agora que os dados estão estruturados no formato de tabela, você pode usar colunas como "
        "Gols (G), Gols Sofridos (GS) ou o saldo de gols para iniciar análises matemáticas de probabilidade."
    )
