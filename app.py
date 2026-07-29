# app.py — MyPredict 2.0 (simplificado)
import streamlit as st
from interfaces import tela_automatico, tela_manual
from automatico import inicializar_estado, carregar_ligas, buscar_temporadas, buscar_times, executar_automatico
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
    tela_manual()
