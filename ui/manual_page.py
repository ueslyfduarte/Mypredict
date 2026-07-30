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
                'gols_media': bench_gols_casa,
                'gols_sofridos_media': bench_gols_fora,
                'posse_media': bench_posse,
                'finalizacoes_alvo_media': bench_fin_alvo,
                'xg_media': bench_xg,
                'escanteios_media': bench_esc,
                'gols_ht_media': bench_ht,
                'btts_pct': bench_btts / 100.0,
            }

    # ---------- Aba ANALISAR ----------
    with tab_analise:
        st.subheader("🎮 Analisar Confronto")
        col_casa, col_fora = st.columns(2)

        def form_time(tipo, key_prefix):
            with st.container():
                st.markdown(f"### {'🏠 Time Casa' if tipo == 'casa' else '🏟️ Time Fora'}")
                nome = st.text_input("Nome do Time", value="Arsenal" if tipo == 'casa' else "Chelsea", key=f"{key_prefix}_nome")
                pos = st.number_input("Posição", 1, 20, value=1 if tipo == 'casa' else 5, key=f"{key_prefix}_pos")
                prat_proj = st.selectbox("Prateleira Projetada", ["Elite", "Alta", "Media", "Baixa", "Critica"], key=f"{key_prefix}_prat")
                st.markdown("**Médias por Jogo**")
                c1, c2, c3 = st.columns(3)
                gols = c1.number_input("⚽ Gols", 0.0, 5.0, 1.8, 0.1, key=f"{key_prefix}_gols")
                gols_s = c2.number_input("🛡️ Gols Sofr.", 0.0, 5.0, 0.9, 0.1, key=f"{key_prefix}_gols_s")
                posse = c3.number_input("📊 Posse %", 0, 100, 55, key=f"{key_prefix}_posse")
                fin = c1.number_input("🎯 Fin. Alvo", 0.0, 15.0, 5.2, 0.5, key=f"{key_prefix}_fin")
                xg = c2.number_input("📈 xG", 0.0, 4.0, 1.6, 0.1, key=f"{key_prefix}_xg")
                esc = c3.number_input("🏁 Escanteios", 0.0, 15.0, 5.5, 0.5, key=f"{key_prefix}_esc")
                gols_ht = c1.number_input("⏱️ Gols HT", 0.0, 5.0, 0.8, 0.1, key=f"{key_prefix}_gols_ht")
                btts_pct = c2.number_input("🤝 BTTS %", 0.0, 100.0, 50.0, 5.0, key=f"{key_prefix}_btts") / 100.0

                return {
                    'nome': nome, 'pos': pos, 'prat_proj': prat_proj,
                    'stats': {
                        'gols_media': gols, 'gols_sofridos_media': gols_s,
                        'posse_media': posse, 'finalizacoes_alvo_media': fin,
                        'xg_media': xg, 'escanteios_media': esc,
                        'gols_ht_media': gols_ht, 'btts_pct': btts_pct,
                        'conversao': 0.25, 'desvio_pontos': 0.5,
                        'pontos_pos_desvantagem_media': 1.0,
                    }
                }

        with col_casa:
            dados_casa = form_time('casa', 'c')
            st.markdown("**📋 Últimos 10 Jogos**")
            default_jogos = pd.DataFrame([
                {"Res.": "V", "Adversário": "", "Prat. Adv.": "Media", "GP": 0, "GC": 0}
                for _ in range(10)
            ])
            jogos_casa_df = st.data_editor(
                default_jogos,
                column_config={
                    "Res.": st.column_config.SelectboxColumn(options=["V", "E", "D"]),
                    "Prat. Adv.": st.column_config.SelectboxColumn(options=["Elite", "Alta", "Media", "Baixa", "Critica"]),
                },
                num_rows="fixed",
                key="casa_jogos",
                use_container_width=True,
            )
            jogos_casa_list = jogos_casa_df.to_dict('records')
            for j in jogos_casa_list:
                j['resultado'] = j.pop('Res.')
                j['adversario'] = j.pop('Adversário')
                j['prateleira_adv'] = j.pop('Prat. Adv.')
                j['gols_pro'] = j.pop('GP')
                j['gols_contra'] = j.pop('GC')
                j['mandante'] = True

        with col_fora:
            dados_fora = form_time('fora', 'f')
            st.markdown("**📋 Últimos 10 Jogos**")
            default_jogos_f = pd.DataFrame([
                {"Res.": "V", "Adversário": "", "Prat. Adv.": "Media", "GP": 0, "GC": 0}
                for _ in range(10)
            ])
            jogos_fora_df = st.data_editor(
                default_jogos_f,
                column_config={
                    "Res.": st.column_config.SelectboxColumn(options=["V", "E", "D"]),
                    "Prat. Adv.": st.column_config.SelectboxColumn(options=["Elite", "Alta", "Media", "Baixa", "Critica"]),
                },
                num_rows="fixed",
                key="fora_jogos",
                use_container_width=True,
            )
            jogos_fora_list = jogos_fora_df.to_dict('records')
            for j in jogos_fora_list:
                j['resultado'] = j.pop('Res.')
                j['adversario'] = j.pop('Adversário')
                j['prateleira_adv'] = j.pop('Prat. Adv.')
                j['gols_pro'] = j.pop('GP')
                j['gols_contra'] = j.pop('GC')
                j['mandante'] = False

        with st.expander("🧠 Ajustes de Contexto (opcional)"):
            col_ic1, col_ic2 = st.columns(2)
            with col_ic1:
                st.markdown(f"**{dados_casa['nome']}**")
                ic_casa = {
                    'confronto_direto': st.slider(f"Aproveitamento contra {dados_fora['nome']} (%)", 0, 100, 50, key="ic_cd_c") / 100,
                    'fator_casa': st.slider("Aproveitamento como mandante (%)", 0, 100, 60, key="ic_fc_c") / 100,
                }
            with col_ic2:
                st.markdown(f"**{dados_fora['nome']}**")
                ic_fora = {
                    'confronto_direto': 1.0 - ic_casa['confronto_direto'],
                    'fator_casa': st.slider("Aproveitamento como visitante (%)", 0, 100, 40, key="ic_fc_f") / 100,
                }

            st.markdown("**Odds de Mercado (opcional, apenas para Edge)**")
            col_odds1, col_odds2, col_odds3 = st.columns(3)
            odd_casa = col_odds1.number_input("Odd Casa (1X2)", 1.0, 50.0, 2.0, 0.01, key="odd_casa")
            odd_empate = col_odds2.number_input("Odd Empate", 1.0, 50.0, 3.5, 0.01, key="odd_empate")
            odd_fora = col_odds3.number_input("Odd Fora", 1.0, 50.0, 3.8, 0.01, key="odd_fora")
            col_odds4, col_odds5, col_odds6 = st.columns(3)
            odd_over = col_odds4.number_input("Odd Over 2.5", 1.0, 50.0, 1.9, 0.01, key="odd_over")
            odd_btts = col_odds5.number_input("Odd BTTS", 1.0, 50.0, 1.8, 0.01, key="odd_btts")
            odd_ht = col_odds6.number_input("Odd Gol 1º Tempo", 1.0, 50.0, 1.9, 0.01, key="odd_ht")
            odd_esc = st.number_input("Odd Over 8.5 Escanteios", 1.0, 50.0, 2.0, 0.01, key="odd_esc")
            odds_dict = {
                'odd_casa': odd_casa, 'odd_empate': odd_empate, 'odd_fora': odd_fora,
                'odd_over': odd_over, 'odd_btts': odd_btts, 'odd_ht': odd_ht, 'odd_esc': odd_esc,
            }

        if st.button("⚡ Calcular Análise Completa", use_container_width=True, type="primary"):
            dados = {
                'time_casa': dados_casa['nome'], 'time_fora': dados_fora['nome'],
                'pos_casa': dados_casa['pos'], 'pos_fora': dados_fora['pos'],
                'prat_casa': dados_casa['prat_proj'], 'prat_fora': dados_fora['prat_proj'],
                'ovrall_casa': dados_casa['stats'], 'ovrall_fora': dados_fora['stats'],
                'jogos_casa': jogos_casa_list, 'jogos_fora': jogos_fora_list,
                'ic_casa': ic_casa, 'ic_fora': ic_fora,
                'odds': odds_dict,
                'media_gols_casa': st.session_state.get('media_gols_casa_liga', MEDIA_GOLS_CASA_LIGA),
                'media_gols_fora': st.session_state.get('media_gols_fora_liga', MEDIA_GOLS_FORA_LIGA),
                'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
                'media_esc_casa': 5.0, 'media_esc_fora': 4.5,
                'prateleiras_extra': {},
                'benchmarks_usr': st.session_state.get('benchmarks_usr', None),
            }
            pkl_path = st.session_state.get('pkl_path', 'calibration_params.pkl')
            res, err = executar_manual(dados, pkl_path)
            if err:
                st.error(err)
            else:
                show_results_manual(res)
                st.info(random.choice([
                    "Os números nunca ganham jogos, mas mostram onde as batalhas serão vencidas.",
                    "Em cada passe, em cada desarme, existe uma rota. Nós só a colorimos.",
                ]))
