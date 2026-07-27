# app.py — MyPredict 2.0 (Universal)
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
from data_source_worldfootball import obter_slug_liga

# ... (CSS e layout como antes)

with st.sidebar:
    st.markdown("<h2 style='color: #ffd700;'>⚙️ Configuração</h2>", unsafe_allow_html=True)
    liga_nome = st.text_input("Nome da Liga", "Brasileirão")
    temporada = st.number_input("Temporada", min_value=2015, max_value=2026, value=2024)
    st.markdown("---")
    time_casa = st.text_input("Time da casa", "Flamengo")
    time_fora = st.text_input("Time de fora", "Palmeiras")
    gerar = st.button("⚡ Gerar MyPredict", type="primary", use_container_width=True)

if gerar:
    st.session_state.analise_feita = True

if 'analise_feita' in st.session_state and st.session_state.analise_feita:
    with st.spinner("Descobrindo liga e obtendo dados..."):
        try:
            # Converter nome da liga em slug
            liga_slug = obter_slug_liga(liga_nome)
            if not liga_slug:
                st.error(f"Não foi possível encontrar a liga '{liga_nome}'. Verifique o nome.")
                st.stop()
            
            class_ant = classificação_anterior(liga_slug, temporada)
            if not class_ant:
                st.error(f"Classificação não disponível para {liga_nome} {temporada}.")
                st.stop()
            
            prateleiras = gerar_prateleiras(liga_slug, temporada)

            # Dados dos times (usando o slug)
            dados_casa = obter_dados_ovrall_time(time_casa, liga_slug, temporada, class_ant)
            dados_fora = obter_dados_ovrall_time(time_fora, liga_slug, temporada, class_ant)
            
            # ... (cálculos do IMA, MPV, mercados como antes, mas passando 'liga_slug' onde necessário)
            # As funções do data_loader que recebiam 'liga' agora devem receber 'liga_slug'.
            # Certifique-se de que todas as chamadas estejam consistentes.
            
        except Exception as e:
            st.error(f"Erro: {str(e)}")
