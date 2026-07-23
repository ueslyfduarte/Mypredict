import streamlit as st

# =========================================================================
# ⚽ MYPREDICT - PROJETO DE PREDIÇÃO ESPORTIVA
# 📝 RESUMO PARA A PRÓXIMA CONVERSA:
# - Repositório público e limpo no GitHub (com chaves seguras no Streamlit Cloud).
# - Layout em verde, azul e branco adaptado para visualização no celular.
# - Menu lateral esquerdo pronto para monitoramento de jogos favoritados.
# - Próximos passos: Implementar os índices IM, IOVR, IFP e a automação do WhatsApp.
# =========================================================================

st.set_page_config(page_title="MyPredict", page_icon="⚽", layout="wide")

# Banco de dados fixo (Gasta ZERO créditos de API)
DADOS_LIGAS = {
    "Campeonato Brasileiro": ["Flamengo", "Palmeiras", "São Paulo", "Atlético-MG", "Botafogo", "Corinthians", "Grêmio", "Internacional"],
    "Premier League": ["Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United", "Tottenham", "Aston Villa", "Newcastle"]
}

# Menu Lateral (Watchlist de Monitoramento)
st.sidebar.title("🚨 Monitoramento Diário")
st.sidebar.write("Jogos aprovados para checar a escalação 1 hora antes:")

if "jogos_monitorados" not in st.session_state:
    st.session_state.jogos_monitorados = []

if st.session_state.jogos_monitorados:
    for jogo in st.session_state.jogos_monitorados:
        st.sidebar.info(f"⏳ {jogo}")
else:
    st.sidebar.caption("Nenhum jogo monitorado ainda.")

# Painel Central
st.success("👋 Bem-vindo ao MyPredict! Sua estação inteligente de análise esportiva.")
st.title("⚽ MyPredict - Análise Pré-Jogo")

st.subheader("🔍 Configurar Cenário da Partida")
liga_selecionada = st.selectbox("Selecione a Liga / Campeonato:", list(DADOS_LIGAS.keys()))
times_disponiveis = DADOS_LIGAS[liga_selecionada]

col_casa, col_fora = st.columns(2)
with col_casa:
    time_casa = st.selectbox("🏠 Time da Casa (Mandante):", times_disponiveis, index=0)
with col_fora:
    time_fora = st.selectbox("🚀 Time de Fora (Visitante):", times_disponiveis, index=1)

st.write("")
botao_analisar = st.button("🚀 Gerar Relatório MyPredict", type="primary")

if botao_analisar:
    if time_casa == time_fora:
        st.error("Erro: O time da casa não pode ser igual ao time de fora!")
    else:
        st.divider()
        st.header(f"📊 Relatório: {time_casa} vs {time_fora}")
        st.caption(f"Competição: {liga_selecionada}")

        st.subheader("📈 Análise de Posição e Momento")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"### 🏠 {time_casa} (Dados de Casa)")
            st.write("📌 **Posição Geral Atual:** Carregando pela API...")
            st.write("🔥 **Posição de Momento (Últimos 5 jogos em Casa):** Recalculando...")
        with c2:
            st.markdown(f"### 🚀 {time_fora} (Dados de Fora)")
            st.write("📌 **Posição Geral Atual:** Carregando pela API...")
            st.write("🔥 **Posição de Momento (Últimos 5 jogos Fora):** Recalculando...")

        st.divider()

        st.subheader("🧠 Métricas Estratégicas do Seu Método")
        m1, m2, m3 = st.columns(3)
        with m1: st.metric(label="📊 Índice IM", value="Pendente", delta="Aguardando Fórmula")
        with m2: st.metric(label="🎯 Índice IOVR", value="Pendente", delta="Aguardando Fórmula")
        with m3: st.metric(label="🧠 Índice IFP", value="Pendente", delta="Aguardando Fórmula")

        st.divider()

        st.subheader("🎲 Tomada de Decisão")
        nome_confronto = f"{time_casa} x {time_fora} ({liga_selecionada})"
        if st.button("➕ Adicionar ao Monitoramento Diário"):
            if nome_confronto not in st.session_state.jogos_monitorados:
                st.session_state.jogos_monitorados.append(nome_confronto)
                st.toast("Jogo adicionado à barra lateral!")
                st.rerun()

