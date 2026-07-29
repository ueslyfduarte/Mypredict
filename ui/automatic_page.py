# ui/automatic_page.py — Tela do modo automático
import streamlit as st
from ui.styles import injetar_css
from ui.components import show_api_usage, show_results_auto
from data.api_football import listar_ligas, listar_temporadas
from core.data_loader import classificação_anterior, obter_ultimos_jogos_com_heranca, extrair_recortes_ima, obter_dados_ovrall_time, gerar_prateleiras
from core.calculations import executar_automatico

def render_automatico():
    injetar_css()

    # Inicializar estado
    if 'ligas_carregadas' not in st.session_state:
        st.session_state.ligas_carregadas = False
        st.session_state.lista_ligas = []
        st.session_state.temporadas = {}
        st.session_state.times_carregados = {}
    if 'resultados_auto' not in st.session_state:
        st.session_state.resultados_auto = None

    # Carregar ligas (cache)
    if not st.session_state.ligas_carregadas:
        with st.spinner("Conectando à API-Football..."):
            try:
                ligas_dict = listar_ligas()
                st.session_state.lista_ligas = sorted(ligas_dict.keys())
                st.session_state.ligas_dict = ligas_dict
                st.session_state.ligas_carregadas = True
                st.session_state.erro_ligas = None
            except Exception as e:
                st.session_state.erro_ligas = str(e)

    # Cabeçalho
    st.markdown('<div class="main-title">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">"O futebol não é uma questão de vida ou morte. É muito mais importante que isso." — Bill Shankly</div>', unsafe_allow_html=True)

    if st.session_state.get('erro_ligas'):
        st.error(st.session_state.erro_ligas)

    # Seleção de liga e temporada
    col_liga, col_temp = st.columns([2,1])
    with col_liga:
        liga_nome = st.selectbox("Liga", st.session_state.lista_ligas or [], key="sel_liga")
    with col_temp:
        if liga_nome and liga_nome in st.session_state.ligas_dict:
            liga_id = st.session_state.ligas_dict[liga_nome]
            if liga_id not in st.session_state.temporadas:
                with st.spinner("Buscando temporadas..."):
                    st.session_state.temporadas[liga_id] = listar_temporadas(liga_id)
            temps = st.session_state.temporadas.get(liga_id, [])
            temporada = st.selectbox("Temporada", temps, key="sel_temp") if temps else st.number_input("Temporada", value=2024)
        else:
            temporada = st.number_input("Temporada", value=2024)

    # Buscar times
    chave = f"{liga_nome}_{temporada}"
    buscar = False
    if chave not in st.session_state.times_carregados:
        buscar = st.button("🔍 Buscar Times", use_container_width=True)
    else:
        st.info("Times carregados.")

    if buscar:
        with st.spinner("Obtendo classificação..."):
            try:
                class_ant = classificação_anterior(liga_nome, temporada)
                if class_ant:
                    st.session_state.times_carregados[chave] = sorted(class_ant.values())
                else:
                    st.session_state.times_carregados[chave] = []
            except Exception as e:
                st.error(f"Erro ao carregar times: {e}")
                st.session_state.times_carregados[chave] = []
        st.rerun()

    lista_times = st.session_state.times_carregados.get(chave, [])
    c1, c2 = st.columns(2)
    with c1:
        time_casa = st.selectbox("Casa", lista_times) if lista_times else st.text_input("Time da casa", value="")
    with c2:
        time_fora = st.selectbox("Fora", lista_times, index=min(1, len(lista_times)-1)) if lista_times else st.text_input("Time de fora", value="")

    gerar = st.button("⚡ Gerar MyPredict", use_container_width=True)

    if gerar and time_casa and time_fora and liga_nome:
        with st.spinner("Calculando..."):
            class_ant = classificação_anterior(liga_nome, temporada)
            if not class_ant:
                st.error("Classificação indisponível.")
                return
            prateleiras = gerar_prateleiras(liga_nome, temporada)
            dados_casa = obter_dados_ovrall_time(time_casa, liga_nome, temporada, class_ant)
            dados_fora = obter_dados_ovrall_time(time_fora, liga_nome, temporada, class_ant)
            jogos_casa = obter_ultimos_jogos_com_heranca(time_casa, liga_nome, temporada, class_ant)
            jogos_fora = obter_ultimos_jogos_com_heranca(time_fora, liga_nome, temporada, class_ant)

            res, err = executar_automatico(liga_nome, temporada, time_casa, time_fora, class_ant,
                                           prateleiras, dados_casa, dados_fora, jogos_casa, jogos_fora)
            if err:
                st.error(err)
            else:
                st.session_state.resultados_auto = res
                st.rerun()

    # Exibir resultados
    if st.session_state.resultados_auto:
        show_results_auto(st.session_state.resultados_auto)
