import streamlit as st
from data_loader import (
    gerar_prateleiras, obter_ultimos_jogos_com_heranca, extrair_recortes_ima,
    obter_dados_ovrall_time, classificação_anterior
)
from ratings import calcular_ima, calcular_mpv
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from data_source_fbref_pro import WF_LEAGUES as LEAGUES

# ------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------
st.set_page_config(page_title="MyPredict 2.0", layout="centered")

# ------------------------------------------------------------
# CSS personalizado (preto, prata, dourado)
# ------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #c0c0c0; }
    h1, h2, h3 { color: #ffd700 !important; }
    div[data-testid="metric-container"] {
        background-color: #1e1e1e; border: 1px solid #333;
        border-radius: 10px; padding: 10px; color: #ffd700 !important;
    }
    div[data-testid="metric-container"] label { color: #c0c0c0 !important; }
    div.stButton > button {
        background-color: #ffd700; color: #0e1117;
        border: none; font-weight: bold; border-radius: 8px;
        width: 100%; font-size: 18px; padding: 12px;
    }
    div.stButton > button:hover {
        background-color: #ffed4a; box-shadow: 0px 0px 15px #ffd700;
    }
    .selo-ouro {
        background: linear-gradient(145deg, #ffd700, #b8860b);
        color: #0e1117; font-weight: 900; text-align: center;
        border-radius: 50%; width: 120px; height: 120px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 14px;
        box-shadow: 0px 0px 25px #ffd700; animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 10px #ffd700; }
        50% { box-shadow: 0 0 30px #ffd700; }
        100% { box-shadow: 0 0 10px #ffd700; }
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Título e frase
# ------------------------------------------------------------
st.markdown("<h1 style='text-align: center;'>⚽ MyPredict 2.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #c0c0c0;'>"
            "“O futebol é a única coisa que me emociona mais do que a ciência.”<br>"
            "— Albert Einstein (adaptado)</p>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Seletores
# ------------------------------------------------------------
lista_ligas = sorted(LEAGUES.keys())
liga_nome = st.selectbox("Selecione a liga", lista_ligas, index=0)
temporada = st.number_input("Temporada", min_value=2015, max_value=2026, value=2024)

# Inicializa variáveis
class_ant = None
lista_times = []

# Tenta carregar a classificação, mas não trava se falhar
with st.spinner("Carregando classificação..."):
    try:
        class_ant = classificação_anterior(liga_nome, temporada)
        if class_ant:
            lista_times = sorted(class_ant.values())
    except Exception as e:
        st.warning(f"Não foi possível carregar a classificação: {e}")

# Se não conseguiu classificação, mostra campos de texto para os times
if not lista_times:
    st.info("Digite os nomes dos times manualmente (ex.: 'Flamengo', 'Palmeiras').")
    col1, col2 = st.columns(2)
    with col1:
        time_casa = st.text_input("Time da casa", value="Flamengo")
    with col2:
        time_fora = st.text_input("Time de fora", value="Palmeiras")
else:
    col1, col2 = st.columns(2)
    with col1:
        time_casa = st.selectbox("Time da casa", lista_times)
    with col2:
        time_fora = st.selectbox("Time de fora", lista_times, index=min(1, len(lista_times)-1))

# ------------------------------------------------------------
# Botão de ação – sempre visível
# ------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
gerar = st.button("⚡ Gerar MyPredict", use_container_width=True)

# ------------------------------------------------------------
# Execução da análise
# ------------------------------------------------------------
if gerar:
    with st.spinner("Calculando..."):
        try:
            if not class_ant:
                # Se não temos classificação, não podemos gerar prateleiras.
                # Mas ainda podemos tentar rodar com prateleiras vazias? O método precisa delas.
                st.error("Classificação indisponível. Verifique a liga e temporada.")
                st.stop()

            prateleiras = gerar_prateleiras(liga_nome, temporada)

            dados_casa = obter_dados_ovrall_time(time_casa, liga_nome, temporada, class_ant)
            dados_fora = obter_dados_ovrall_time(time_fora, liga_nome, temporada, class_ant)
            if not dados_casa or not dados_fora:
                st.error("Partidas não encontradas para um dos times.")
                st.stop()

            # Resto do código de cálculo (IMA, MPV, mercados, exibição)
            # ... (mantenha o restante do bloco que já estava funcionando, 
            #      copiado do app.py anterior completo)
            #
            # Como o restante é grande, confirme se você tem a parte de cálculo e exibição.
            # Se não tiver, eu posso fornecer o bloco completo novamente.
            
        except Exception as e:
            st.error(f"Erro: {str(e)}")
