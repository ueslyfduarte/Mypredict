import streamlit as st

# Configuração da página para celular e PC
st.set_page_config(page_title="MyPredict", page_icon="⚽", layout="wide")

# =========================================================================
# 📦 BANCO DE DADOS FIXO (Gasta ZERO créditos de API)
# =========================================================================
DADOS_LIGAS = {
    "Campeonato Brasileiro": ["Flamengo", "Palmeiras", "São Paulo", "Atlético-MG", "Botafogo", "Corinthians", "Grêmio", "Internacional"],
    "Premier League": ["Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United", "Tottenham", "Aston Villa", "Newcastle"]
}

# =========================================================================
# 🎛️ MENU LATERAL (Sua lista de monitoramento diário)
# =========================================================================
st.sidebar.title("🚨 Monitoramento Diário")
st.sidebar.write("Jogos aprovados para checar a escalação 1 hora antes:")

# Criando um espaço na memória para guardar os jogos favoritados
if "jogos_monitorados" not in st.session_state:
    st.session_state.jogos_monitorados = []

# Exibe os jogos que você salvou na barra lateral
if st.session_state.jogos_monitorados:
    for jogo in st.session_state.jogos_monitorados:
        st.sidebar.info(f"⏳ {jogo}")
else:
    st.sidebar.caption("Nenhum jogo monitorado ainda.")

# =========================================================================
# 🏛️ PAINEL CENTRAL (Área de Trabalho)
# =========================================================================
st.success("👋 Bem-vindo ao MyPredict! Sua estação inteligente de análise esportiva.")
st.title("⚽ MyPredict - Análise Pré-Jogo")

# --- BLOCO 1: ESCOLA DO CENÁRIO (Sem gastar créditos) ---
st.subheader("🔍 Configurar Cenário da Partida")

# Escolha da Liga
liga_selecionada = st.selectbox("Selecione a Liga / Campeonato:", list(DADOS_LIGAS.keys()))

# Listar os times baseados na liga escolhida
times_disponiveis = DADOS_LIGAS[liga_selecionada]

# Colunas para escolher os times lado a lado no celular
col_casa, col_fora = st.columns(2)

with col_casa:
    time_casa = st.selectbox("🏠 Time da Casa (Mandante):", times_disponiveis, index=0)

with col_fora:
    # Coloca o segundo time da lista por padrão para não dar erro de duplicado
    time_fora = st.selectbox("🚀 Time de Fora (Visitante):", times_disponiveis, index=1)

# Botão central para disparar as análises do seu método
st.write("")
botao_analisar = st.button("🚀 Gerar Relatório MyPredict", type="primary")

# --- EXECUÇÃO DA ANÁLISE ---
if botao_analisar:
    if time_casa == time_fora:
        st.error("Erro: O time da casa não pode ser igual ao time de fora!")
    else:
        st.divider()
        st.header(f"📊 Relatório: {time_casa} vs {time_fora}")
        st.caption(f"Competição: {liga_selecionada}")

        # --- BLOCO 2 & 3: ANÁLISE INICIAL (MÉTRICAS DE POSIÇÃO) ---
        st.subheader("📈 Análise de Posição e Momento")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### 🏠 {time_casa} (Dados de Casa)")
            st.write("📌 **Posição Geral Atual:** 4º Lugar *(Dado fictício da API)*")
            st.write("🔥 **Posição de Momento (Últimos 5 jogos em Casa):** 2º Lugar")
            
        with c2:
            st.markdown(f"### 🚀 {time_fora} (Dados de Fora)")
            st.write("📌 **Posição Geral Atual:** 9º Lugar *(Dado fictício da API)*")
            st.write("🔥 **Posição de Momento (Últimos 5 jogos Fora):** 18º Lugar")

        st.divider()

        # --- SEU MÉTODO SECRETO (IM, IOVR, IFP) ---
        st.subheader("🧠 Métricas Estratégicas do Seu Método")
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label="📊 Índice IM", value="Aguardando Fórmula", delta="Pendente")
        with m2:
            st.metric(label="🎯 Índice IOVR", value="Aguardando Fórmula", delta="Pendente")
        with m3:
            st.metric(label="🧠 Índice IFP", value="Aguardando Fórmula", delta="Pendente")

        st.divider()

        # --- BLOCO DE AÇÃO: MONITORAMENTO ---
        st.subheader("🎲 Tomada de Decisão")
        st.write("Encontrou valor com base nas métricas acima? Adicione para monitorar as escalações mais tarde.")
        
        nome_confronto = f"{time_casa} x {time_fora} ({liga_selecionada})"
        
        # Cria o botão de salvar
        if st.button("➕ Adicionar ao Monitoramento Diário"):
            if nome_confronto not in st.session_state.jogos_monitorados:
                st.session_state.jogos_monitorados.append(nome_confronto)
                st.toast("Jogo adicionado à barra lateral! Rerodando...")
                st.rerun()
