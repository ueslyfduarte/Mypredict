import streamlit as st

# Configuração do tema inicial (deixa o app limpo e profissional)
st.set_page_config(page_title="MyPredict", page_icon="⚽", layout="wide")

# --- MENU LATERAL (Branco/Neutro por padrão, reservado para monitoramento) ---
st.sidebar.title("🚨 Monitoramento")
st.sidebar.write("Os jogos favoritados para acompanhar 1 hora antes aparecerão aqui.")

# --- ÁREA CENTRAL ---

# Mensagem de Boas-Vindas em Verde (Cor de Sucesso)
st.success("👋 Bem-vindo ao MyPredict! Sua estação inteligente de análise e predição esportiva.")

# Título Principal do App
st.title("⚽ MyPredict - Analytics")

# --- CONTEÚDO DOS CANTOS (Organizado em 3 Colunas) ---
# Criamos 3 colunas na tela para distribuir as informações sobre futebol
col1, col2, col3 = st.columns(3)

with col1:
    # Caixa Azul Informática (Fácil de ler)
    st.info("📈 **Estatísticas Avançadas**\n\nCruzamos dados históricos de gols, posse de bola e finalizações para criar modelos matemáticos precisos.")

with col2:
    # Caixa Branca/Cinza Padrão
    st.markdown("### 🏆 Ligas Cobertas\nPronto para analisar os principais campeonatos do mundo, incluindo Brasileirão, Premier League e Champions League.")

with col3:
    # Outra Caixa Azul Informativa
    st.info("🧠 **Fator Psicológico**\n\nFique de olho! Nosso sistema monitora notícias de última hora e desfalques que mudam o rumo do jogo.")

# Deixamos um espaço respiratório em branco
st.write("")
st.write("")

# --- ÁREA DE PESQUISA (Layout Inicial) ---
st.subheader("🔍 Iniciar Nova Análise")

# Caixa de seleção ou digitação para o usuário
time_pesquisado = st.text_input("Digite o nome do time que você deseja avaliar:", placeholder="Ex: Flamengo, Real Madrid, Palmeiras...")

# Exibe uma mensagem amigável caso você digite algo
if time_pesquisado:
    st.write(f"Buscando informações para: **{time_pesquisado}**... (A conexão com as APIs será configurada no próximo passo)")
