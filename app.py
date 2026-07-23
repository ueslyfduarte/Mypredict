import streamlit as st

# =========================================================================
# ⚽ MYPREDICT - PROJETO DE PREDIÇÃO ESPORTIVA
# 📝 RESUMO DAS REGRAS E PARÂMETROS DO IMA INCORPORADOS:
# - Pesos de Recência (Ideia B): 18% Geral | 32% 5 Casa/Fora | 50% 3 Casa/Fora
# - Pontuações: Vitória=3.0, Empate=1.0, Derrota=0.0
# - Bônus Crítico Real vs Alto/Elite: Vitória = 4.0 | Empate = 1.5
# - Punições Alto/Elite vs Crítico: Empate = 0.5 | Derrota = -2.0
# - Trava de Segurança por Projeção Inicial e Transição de Temporada (Subidas/Descidas)
# - Nivelamento de Copas (Prateleiras Nacionais Estreitadas): A=1.00, B=0.78, C=0.58, D=0.42
# =========================================================================

st.set_page_config(page_title="MyPredict", page_icon="⚽", layout="wide")

# Banco de dados fixo para a maquete celular
DADOS_LIGAS = {
    "Campeonato Brasileiro (Série A)": {
        "Tipo": "Liga",
        "Prateleira": 1.00,
        "Times": ["Flamengo", "Palmeiras", "São Paulo", "Atlético-MG", "Botafogo", "Corinthians", "Grêmio", "Internacional"]
    },
    "Premier League": {
        "Tipo": "Liga",
        "Prateleira": 1.00,
        "Times": ["Manchester City", "Arsenal", "Liverpool", "Chelsea", "Manchester United", "Tottenham", "Aston Villa", "Newcastle"]
    },
    "Copa do Brasil": {
        "Tipo": "Copa",
        "Times": ["Flamengo", "Palmeiras", "Sport (Série B)", "Amazonas (Série B)", "Volta Redonda (Série C)", "Sousa (Série D)"]
    }
}

# Dicionário de Projeção Pré-Campeonato (Para a Trava de Segurança do IMA)
PROJECAO_INICIAL = {
    "Flamengo": "ELITE", "Palmeiras": "ELITE", "Manchester City": "ELITE", "Arsenal": "ELITE",
    "São Paulo": "ALTO", "Atlético-MG": "ALTO", "Liverpool": "ALTO", "Chelsea": "ALTO",
    "Botafogo": "MÉDIO", "Internacional": "MÉDIO", "Manchester United": "MÉDIO", "Tottenham": "MÉDIO",
    "Grêmio": "BAIXO", "Aston Villa": "BAIXO", "Newcastle": "BAIXO",
    "Corinthians": "CRÍTICO", "Sport (Série B)": "CRÍTICO", "Amazonas (Série B)": "CRÍTICO", 
    "Volta Redonda (Série C)": "CRÍTICO", "Sousa (Série D)": "CRÍTICO"
}

# Dicionário de Prateleiras Competitivas Nacionais para Copas
PRATELEIRAS_NACIONAIS = {
    "Série A": 1.00,
    "Série B": 0.78,
    "Série C": 0.58,
    "Série D": 0.42
}

# Inicialização do Monitoramento Diário na Barra Lateral
st.sidebar.title("🚨 Monitoramento Diário")
st.sidebar.write("Jogos aprovados para checar a escalação 1 hora antes:")

if "jogos_monitorados" not in st.session_state:
    st.session_state.jogos_monitorados = []

# Exibição do Monitoramento Lateral
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
times_disponiveis = DADOS_LIGAS[liga_selecionada]["Times"]
tipo_campeonato = DADOS_LIGAS[liga_selecionada]["Tipo"]

col_casa, col_fora = st.columns(2)
with col_casa:
    time_casa = st.selectbox("🏠 Time da Casa (Mandante):", times_disponiveis, index=0)
with col_fora:
    time_fora = st.selectbox("🚀 Time de Fora (Visitante):", times_disponiveis, index=1)

# Gerenciamento de Estado do Relatório (Abordagem B: Session State para Estabilidade no Celular)
if "mostrar_relatorio" not in st.session_state:
    st.session_state.mostrar_relatorio = False
if "ultimo_confronto" not in st.session_state:
    st.session_state.ultimo_confronto = ""

st.write("")
if st.button("🚀 Gerar Relatório MyPredict", type="primary"):
    if time_casa == time_fora:
        st.error("Erro: O time da casa não pode ser igual ao time de fora!")
        st.session_state.mostrar_relatorio = False
    else:
        st.session_state.mostrar_relatorio = True
        st.session_state.ultimo_confronto = f"{time_casa} x {time_fora} ({liga_selecionada})"

# Bloco Isolado do Relatório (Garante estabilidade ao clicar em outros botões)
if st.session_state.mostrar_relatorio:
    st.divider()
    st.header(f"📊 Relatório Estratégico: {time_casa} vs {time_fora}")
    st.caption(f"Competição: {liga_selecionada} | Formato: {tipo_campeonato}")

    # Bloco Visual dos Índices Secretos
    st.subheader("🧠 Métricas Estratégicas do Seu Método")
    m1, m2, m3 = st.columns(3)
    
    with m1: 
        # O valor numérico final do IMA entrará aqui após as conexões de dados
        st.metric(
            label="📊 Índice IMA", 
            value="Calculando...", 
            delta="Pesos: 18% | 32% | 50%", 
            delta_color="normal"
        )
    with m2: 
        st.metric(label="🎯 Índice IOVR", value="Bloqueado", delta="Aguardando Conceito")
    with m3: 
        st.metric(label="🧠 Índice IFP", value="Bloqueado", delta="Aguardando Conceito")

    st.divider()

    # Seção de Tomada de Decisão e Monitoramento
    st.subheader("🎲 Tomada de Decisão")
    
    if st.button("➕ Adicionar ao Monitoramento Diário"):
        if st.session_state.ultimo_confronto not in st.session_state.jogos_monitorados:
            st.session_state.jogos_monitorados.append(st.session_state.ultimo_confronto)
            st.toast("Jogo adicionado à barra lateral com sucesso!")
            st.rerun()
        else:
            st.warning("Este jogo já está sendo monitorado!")

