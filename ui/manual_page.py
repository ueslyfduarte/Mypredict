import streamlit as st
import pandas as pd
import os
import random
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from core.calculations import executar_manual
from ui.components import show_results_manual
from ui.styles import injetar_css

FRASES_CABECALHO = [
    "Futebol é a arte do imprevisível. Mas o imprevisível também tem padrões.",
    "Tática é saber o que fazer quando não se tem a bola. Estratégia é saber o que fazer com ela. – Johan Cruyff",
    "O futebol não é uma ciência exata, mas a análise pode revelar os caminhos que os olhos não veem.",
]

LIGAS_DISPONIVEIS = {
    "Premier League": "calibration_params.pkl",
    "La Liga": "calibration_laliga.pkl",
    "Brasileirão": "calibration_brasileirao.pkl",
}

def render_manual():
    injetar_css()

    frase = random.choice(FRASES_CABECALHO)
    st.markdown(f"""
    <div style="text-align:center; padding: 30px 0 10px 0;">
        <h1 style="color:#FFD700; font-size:3rem; margin-bottom:0;">MyPredict 2.0</h1>
        <p style="color:#aaa; font-style:italic;">"{frase}"</p>
    </div>
    """, unsafe_allow_html=True)

    tab_liga, tab_analise = st.tabs(["🏆 Liga", "🔍 Analisar"])

    # ---------- Aba LIGA ----------
    with tab_liga:
        col1, col2 = st.columns([3, 1])
        with col1:
            liga_nome = st.selectbox("Liga Ativa", list(LIGAS_DISPONIVEIS.keys()))
        with col2:
            st.write("")
            if st.button("🎮 Carregar Liga", use_container_width=True):
                st.session_state.liga_ativa = liga_nome
                st.session_state.pkl_path = LIGAS_DISPONIVEIS[liga_nome]
                st.success(f"Liga '{liga_nome}' carregada!")

        if st.session_state.get('liga_ativa'):
            st.info(f"🏟️ Liga atual: **{st.session_state.liga_ativa}**")

        # NOVO: Modo Livre
        st.session_state.modo_livre = st.checkbox(
            "🔓 Modo Livre (ignorar modelo calibrado, usar apenas dados manuais)",
            value=st.session_state.get('modo_livre', False),
            help="Quando ativado, as probabilidades são calculadas somente com as fórmulas originais, sem influência do modelo da Premier League. Ideal para ligas sem arquivo .pkl."
        )

        with st.expander("📊 Parâmetros da Liga (personalize)", expanded=False):
            st.caption("Defina os valores de referência da competição. Eles serão usados nos cálculos de OVRall e dimensões táticas.")
            col_bench1, col_bench2, col_bench3 = st.columns(3)
            bench_gols_casa = col_bench1.number_input("Média Gols Casa", 0.0, 5.0, MEDIA_GOLS_CASA_LIGA, key="bench_gols_casa")
            bench_gols_fora = col_bench2.number_input("Média Gols Fora", 0.0, 5.0, MEDIA_GOLS_FORA_LIGA, key="bench_gols_fora")
            bench_posse = col_bench3.number_input("Posse Média (%)", 0.0, 100.0, 50.0, key="bench_posse")
            bench_fin_alvo = col_bench1.number_input("Finalizações Alvo (média)", 0.0, 15.0, 4.0, key="bench_fin_alvo")
            bench_xg = col_bench2.number_input("xG Médio", 0.0, 5.0, 1.3, key="bench_xg")
            bench_esc = col_bench3.number_input("Escanteios Médios", 0.0, 15.0, 5.0, key="bench_esc")
            bench_ht = col_bench1.number_input("Média Gols HT", 0.0, 5.0, 0.7, key="bench_ht")
            bench_btts = col_bench2.number_input("BTTS Médio (%)", 0.0, 100.0, 48.0, key="bench_btts")

            st.session_state.benchmarks_usr = {
                'gols_media': {'mean': bench_gols_casa, 'std': 0.5, 'lower_better': False},
                'gols_sofridos_media': {'mean': bench_gols_fora, 'std': 0.5, 'lower_better': True},
                'posse_media': {'mean': bench_posse, 'std': 10.0, 'lower_better': False},
                'finalizacoes_alvo_media': {'mean': bench_fin_alvo, 'std': 1.5, 'lower_better': False},
                'xg_media': {'mean': bench_xg, 'std': 0.3, 'lower_better': False},
                'escanteios_media': {'mean': bench_esc, 'std': 1.5, 'lower_better': False},
                'gols_ht_media': {'mean': bench_ht, 'std': 0.3, 'lower_better': False},
                'btts_pct': {'mean': bench_btts / 100.0, 'std': 0.1, 'lower_better': False},
            }

    # ---------- Aba ANALISAR ----------
    # (o restante do arquivo permanece igual)
    # ...
