# app.py — MyPredict 2.0
import streamlit as st
from interfaces import tela_automatico, tela_manual
from automatico import inicializar_estado, carregar_ligas, buscar_temporadas, buscar_times, executar_automatico
from manual import executar_manual, processar_texto_ia
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from data_source_api_football import get_api_usage

with st.sidebar:
    st.markdown("# MyPredict 2.0")
    modo = st.radio("Modo", ["Automático (API)", "Manual"])

if modo == "Automático (API)":
    inicializar_estado()
    carregar_ligas()
    uso, limite = get_api_usage() if st.session_state.get('ligas_carregadas') else (0, 100)
    liga_nome, temporada, time_casa, time_fora, buscar, gerar, chave_times = tela_automatico(
        st.session_state.get('lista_ligas', []),
        st.session_state.get('temporadas', {}),
        st.session_state.get('times_carregados', {}),
        uso, limite,
        st.session_state.get('erro_ligas'),
        st.session_state.get('resultados_auto')
    )
    if liga_nome:
        buscar_temporadas(liga_nome)
    if buscar:
        buscar_times(liga_nome, temporada)
        st.rerun()
    if gerar:
        res, err = executar_automatico(liga_nome, temporada, time_casa, time_fora)
        if err:
            st.error(err)
        else:
            st.session_state.resultados_auto = res
            st.rerun()

else:
    defaults = {
        'time_casa': "Flamengo", 'time_fora': "Palmeiras",
        'pos_casa': 1, 'pos_fora': 2,
        'jogos_casa': [], 'jogos_fora': [],
        'ovrall_casa': {}, 'ovrall_fora': {},
        'ic_casa': {}, 'ic_fora': {},
        'media_gols_casa': MEDIA_GOLS_CASA_LIGA, 'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
        'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
        'media_esc_casa': 5.0, 'media_esc_fora': 4.5,
        'prateleiras_extra': {}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    entrada, calcular = tela_manual(st.session_state)

    if entrada == "Colar resposta da IA" and st.session_state.get('ia_text') and st.session_state.get('processar_click'):
        texto = st.session_state.ia_text
        dados = processar_texto_ia(texto)
        for chave, valor in dados.items():
            st.session_state[chave] = valor
        st.session_state.processar_click = False
        st.success("Texto processado com sucesso!")
        st.rerun()

    if calcular:
        res, err = executar_manual(st.session_state)
        if err:
            st.error(err)
        else:
            st.session_state.resultados_manual = res
            st.rerun()

    if st.session_state.get('resultados_manual'):
        res = st.session_state.resultados_manual
        st.subheader("📊 Resultados")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Vitória Casa", f"{res['p1']:.1%}")
        with col2: st.metric("Empate", f"{res['pX']:.1%}")
        with col3: st.metric("Vitória Fora", f"{res['p2']:.1%}")

        st.markdown("---")
        col4, col5 = st.columns(2)
        with col4: st.metric("Over 2.5 gols", f"{res['over25']:.1%}" if res['over25'] else "N/D")
        with col5: st.metric("Ambas Marcam", f"{res['btts']:.1%}" if res['btts'] else "N/D")

        st.metric("Gol no 1º tempo", f"{res['gol_ht']:.1%}" if res['gol_ht'] else "N/D")
        st.metric("Over Escanteios", f"{res['esc']:.1%}" if res['esc'] else "N/D")

        with st.expander("📊 Métricas detalhadas"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{res['time_casa']}**")
                st.write(f"IMA: {res['ima_casa']:.1f}, OVRall: {res['ovrall_casa']:.1f}, IC: {res['ic_casa']:.1f}, MPV: {res['mpv_casa']:.1f}")
            with c2:
                st.markdown(f"**{res['time_fora']}**")
                st.write(f"IMA: {res['ima_fora']:.1f}, OVRall: {res['ovrall_fora']:.1f}, IC: {res['ic_fora']:.1f}, MPV: {res['mpv_fora']:.1f}")
