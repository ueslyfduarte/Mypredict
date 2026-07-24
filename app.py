import streamlit as st
import requests
from datetime import datetime

# Configuração visual nativa do Streamlit
st.set_page_config(page_title="MyPredicts", layout="wide")

# ---------------------------------------------------------------------
# [MÓDULO 1] ACESSO DA API E CONFIGURAÇÕES GLOBAIS
# ---------------------------------------------------------------------
if "MINHA_API_KEY" in st.secrets:
    HEADERS = {
        'x-apisports-key': st.secrets["MINHA_API_KEY"]
    }
else:
    st.error("⚠️ ERRO CRÍTICO: Configure a tag 'MINHA_API_KEY' no painel do Streamlit.")
    st.stop()

BASE_URL = "https://api-sports.io"

# CONTADOR DIÁRIO DE AÇÕES (CONTA FREE)
hoje_str = datetime.today().strftime('%Y-%m-%d')

if "data_contador" not in st.session_state:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

if st.session_state["data_contador"] != hoje_str:
    st.session_state["data_contador"] = hoje_str
    st.session_state["contador_acoes"] = 0

def registrar_acao():
    """Chame esta função sempre que o usuário executar uma consulta paga à API"""
    st.session_state["contador_acoes"] += 1


# ---------------------------------------------------------------------
# [MÓDULO 2] INTERFACE DE ENTRADA (SELETORES E BOTÃO REAL NO TOPO)
# ---------------------------------------------------------------------
st.title("📊 MyPredicts")

# Dicionários de estrutura real (Serão alimentados dinamicamente via API posteriormente)
dict_ligas_reais = {}  # Formato futuro: {"Brasileirão Série A": {"id": 71, "seasons": [2026, 2025]}}
dict_times_reais = {}  # Formato futuro: {"Botafogo": 124, "Flamengo": 127}

# 1. SELETOR DE COMPETIÇÃO (Formato rolar ou pesquisar)
liga_selecionada = st.selectbox(
    "🏆 Selecione a Competição:",
    options=list(dict_ligas_reais.keys()) if dict_ligas_reais else ["Selecione uma Liga"],
    index=0,
    help="Digite o nome do campeonato para buscar na lista real da API."
)

# 2. SELETOR DE TEMPORADA (Atual ou Passada)
temporada_selecionada = st.selectbox(
    "📅 Selecione a Temporada:",
    options=["2026", "2025"], # Será filtrado dinamicamente com base nas chaves da liga escolhida acima
    index=0
)

# 3. SELEÇÃO EM CASCATA DOS TIMES (Mandante e Visitante)
col_a, col_b = st.columns(2)

with col_a:
    time_a = st.selectbox(
        "🏠 Selecione o Time A (Mandante):",
        options=list(dict_times_reais.keys()) if dict_times_reais else ["Selecione o Mandante"],
        index=0,
        key="mandante_real"
    )

with col_b:
    time_b = st.selectbox(
        "🚌 Selecione o Time B (Visitante):",
        options=list(dict_times_reais.keys()) if dict_times_reais else ["Selecione o Visitante"],
        index=0,
        key="visitante_real"
    )

# 4. BOTÃO PRINCIPAL DE DISPARO DO CRUNCH DE DADOS
st.write("")
botao_gerar = st.button("🔥 Gerar MyPredict", use_container_width=True, on_click=registrar_acao)


# ESPAÇAMENTO COMPACTO APENAS ENTRE OS MÓDULOS DO APLICATIVO
st.write("")
st.divider()
st.write("")


# ---------------------------------------------------------------------
# [MÓDULO 3] RESERVADO: CAIXA DE FERRAMENTAS (INVISÍVEL NA INTERFACE)
# ---------------------------------------------------------------------
# Reúna abaixo todas as suas futuras defs lógicas e fórmulas matemáticas.

def calcular_probabilidades_confronto():
    """Sua fórmula matemática de Win Rate e BTTS será inserida aqui"""
    pass


# ---------------------------------------------------------------------
# [MÓDULO 4] PROCESSAMENTO DE SAÍDA E ANÁLISE DE DADOS
# ---------------------------------------------------------------------
st.subheader("📈 Análise de Desempenho e Predições")

if botao_gerar:
    # Este bloco executará as consultas reais de Head-to-Head (/fixtures/headtohead)
    # e estatísticas dos clubes puxando as variáveis dos seletores do topo.
    st.info("Estrutura disparada com sucesso. Pronto para receber os payloads de retorno da API Football.")
else:
    st.caption("Aguardando a definição do confronto e o clique em 'Gerar MyPredict'.")
