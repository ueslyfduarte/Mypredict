# app.py — MyPredict 2.0 (maestro que orquestra tudo)
import streamlit as st
import json
from interfaces import tela_automatico, tela_manual, extrair_jogos, para_float
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from data_loader import (
    gerar_prateleiras, obter_ultimos_jogos_com_heranca, extrair_recortes_ima,
    obter_dados_ovrall_time, classificação_anterior
)
from data_source_api_football import listar_ligas, listar_temporadas, get_api_usage

# ------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------
with st.sidebar:
    st.markdown("# MyPredict 2.0")
    modo = st.radio("Modo", ["Automático (API)", "Manual"])

# ------------------------------------------------------------
# MODO AUTOMÁTICO
# ------------------------------------------------------------
if modo == "Automático (API)":
    # Inicializa estado
    if 'ligas_carregadas' not in st.session_state:
        st.session_state.ligas_carregadas = False
        st.session_state.lista_ligas = []
        st.session_state.temporadas = {}
        st.session_state.times_carregados = {}

    if not st.session_state.ligas_carregadas:
        with st.spinner("Conectando à API-Football..."):
            try:
                ligas_dict = listar_ligas()
                st.session_state.lista_ligas = sorted(ligas_dict.keys())
                st.session_state.ligas_dict = ligas_dict
                st.session_state.ligas_carregadas = True
            except Exception as e:
                st.session_state.erro_ligas = str(e)
    else:
        st.session_state.erro_ligas = None

    # Carrega temporadas sob demanda
    if 'temporadas' not in st.session_state:
        st.session_state.temporadas = {}
    liga_nome_atual = st.session_state.get('sel_liga')
    if liga_nome_atual:
        liga_id = st.session_state.ligas_dict.get(liga_nome_atual)
        if liga_id and liga_id not in st.session_state.temporadas:
            with st.spinner("Buscando temporadas..."):
                try:
                    st.session_state.temporadas[liga_nome_atual] = listar_temporadas(liga_id)
                except:
                    st.session_state.temporadas[liga_nome_atual] = []

    # Chama o rosto automático
    uso, limite = get_api_usage() if st.session_state.ligas_carregadas else (0, 100)
    liga_nome, temporada, time_casa, time_fora, buscar, gerar, chave_times = tela_automatico(
        lista_ligas=st.session_state.lista_ligas,
        temporadas_disponiveis=st.session_state.temporadas,
        times_carregados=st.session_state.times_carregados,
        uso_api=uso, limite_api=limite,
        msg_erro=st.session_state.get('erro_ligas'),
        resultados=st.session_state.get('resultados_auto')
    )

    if buscar:
        with st.spinner("Obtendo classificação..."):
            try:
                class_ant = classificação_anterior(liga_nome, temporada)
                st.session_state.times_carregados[chave_times] = sorted(class_ant.values()) if class_ant else []
            except Exception as e:
                st.session_state.erro_times = str(e)

    if gerar:
        with st.spinner("Calculando..."):
            try:
                class_ant = classificação_anterior(liga_nome, temporada)
                if not class_ant:
                    st.error("Classificação indisponível.")
                    st.stop()
                prateleiras = gerar_prateleiras(liga_nome, temporada)
                dados_casa = obter_dados_ovrall_time(time_casa, liga_nome, temporada, class_ant)
                dados_fora = obter_dados_ovrall_time(time_fora, liga_nome, temporada, class_ant)
                jogos_casa = obter_ultimos_jogos_com_heranca(time_casa, liga_nome, temporada, class_ant, 20)
                rec_casa = extrair_recortes_ima(jogos_casa, True)
                jogos_fora = obter_ultimos_jogos_com_heranca(time_fora, liga_nome, temporada, class_ant, 20)
                rec_fora = extrair_recortes_ima(jogos_fora, False)

                ima_casa = calcular_ima(time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                                        rec_casa['5CF'], rec_casa['3CF'], prateleiras)
                ima_fora = calcular_ima(time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                                        rec_fora['5CF'], rec_fora['3CF'], prateleiras)

                mpv_casa = calcular_mpv(ima_casa, 50, 50)
                mpv_fora = calcular_mpv(ima_fora, 50, 50)
                bonus_casa = calcular_bonus_casa(dados_casa.get('diff_aprov_casa_fora'))
                p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

                over25 = prob_over_2_5(
                    dados_casa.get('gols_media'), dados_fora.get('gols_media'),
                    dados_casa.get('gols_sofridos_media'), dados_fora.get('gols_sofridos_media')
                )
                gols_esp_casa = _gols_esperados(dados_casa.get('gols_media'), dados_fora.get('gols_sofridos_media'), MEDIA_GOLS_CASA_LIGA)
                gols_esp_fora = _gols_esperados(dados_fora.get('gols_media'), dados_casa.get('gols_sofridos_media'), MEDIA_GOLS_FORA_LIGA)
                btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)
                gol_ht = prob_gol_ht(
                    dados_casa.get('gols_ht_media'), dados_fora.get('gols_ht_media'),
                    dados_casa.get('gols_ht_sofridos_media'), dados_fora.get('gols_ht_sofridos_media')
                )
                esc = prob_over_escanteios(
                    dados_casa.get('escanteios_media'), dados_fora.get('escanteios_media'),
                    dados_casa.get('escanteios_sofridos_media'), dados_fora.get('escanteios_sofridos_media')
                )

                st.session_state.resultados_auto = {
                    'time_casa': time_casa, 'time_fora': time_fora,
                    'p1': p1, 'pX': pX, 'p2': p2,
                    'rec_p1': (p1 is not None and p1 >= 0.60),
                    'rec_p2': (p2 is not None and p2 >= 0.60),
                    'over25': over25, 'btts': btts, 'gol_ht': gol_ht, 'esc': esc,
                    'ima_casa': ima_casa, 'ima_fora': ima_fora,
                    'mpv_casa': mpv_casa, 'mpv_fora': mpv_fora,
                }
                st.rerun()

# ------------------------------------------------------------
# MODO MANUAL
# ------------------------------------------------------------
else:
    # Inicializa estado
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
    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

    entrada, calcular = tela_manual(st.session_state)

    if calcular:
        if len(st.session_state.jogos_casa) < 10 or len(st.session_state.jogos_fora) < 10:
            st.error("São necessários 10 jogos para cada time.")
            st.stop()
        if not st.session_state.ovrall_casa or not st.session_state.ovrall_fora:
            st.error("Métricas OVRall não encontradas.")
            st.stop()

        prat_casa = obter_prateleira(st.session_state.pos_casa)
        prat_fora = obter_prateleira(st.session_state.pos_fora)
        prateleiras = {st.session_state.time_casa: prat_casa, st.session_state.time_fora: prat_fora}
        for j in st.session_state.jogos_casa + st.session_state.jogos_fora:
            if j['adversario'] not in prateleiras:
                prateleiras[j['adversario']] = "Media"
        for adv, prat in st.session_state.prateleiras_extra.items():
            if adv in prateleiras:
                prateleiras[adv] = prat

        rec_casa = {
            '10G': st.session_state.jogos_casa[:10], '5G': st.session_state.jogos_casa[:5], '3G': st.session_state.jogos_casa[:3],
            '5CF': [j for j in st.session_state.jogos_casa if j['mandante']][:5],
            '3CF': [j for j in st.session_state.jogos_casa if j['mandante']][:3],
        }
        rec_fora = {
            '10G': st.session_state.jogos_fora[:10], '5G': st.session_state.jogos_fora[:5], '3G': st.session_state.jogos_fora[:3],
            '5CF': [j for j in st.session_state.jogos_fora if j['mandante']][:5],
            '3CF': [j for j in st.session_state.jogos_fora if j['mandante']][:3],
        }

        ima_casa = calcular_ima(st.session_state.time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                                rec_casa['5CF'], rec_casa['3CF'], prateleiras)
        ima_fora = calcular_ima(st.session_state.time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                                rec_fora['5CF'], rec_fora['3CF'], prateleiras)

        dados_liga = {k: [st.session_state.ovrall_casa.get(k, 0) or 0, st.session_state.ovrall_fora.get(k, 0) or 0] for k in set(st.session_state.ovrall_casa) | set(st.session_state.ovrall_fora)}
        ovrall_val_casa = calcular_ovrall(st.session_state.ovrall_casa, dados_liga)
        ovrall_val_fora = calcular_ovrall(st.session_state.ovrall_fora, dados_liga)

        ic_val_casa = calcular_ic(st.session_state.ic_casa)
        ic_val_fora = calcular_ic(st.session_state.ic_fora)

        mpv_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
        mpv_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

        bonus_casa = calcular_bonus_casa(st.session_state.ovrall_casa.get('diff_aprov_casa_fora') or 0)
        p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

        over25 = prob_over_2_5(
            st.session_state.ovrall_casa.get('gols_media'), st.session_state.ovrall_fora.get('gols_media'),
            st.session_state.ovrall_casa.get('gols_sofridos_media'), st.session_state.ovrall_fora.get('gols_sofridos_media'),
            media_casa=st.session_state.media_gols_casa, media_fora=st.session_state.media_gols_fora
        )
        gols_esp_casa = _gols_esperados(st.session_state.ovrall_casa.get('gols_media'), st.session_state.ovrall_fora.get('gols_sofridos_media'), st.session_state.media_gols_casa)
        gols_esp_fora = _gols_esperados(st.session_state.ovrall_fora.get('gols_media'), st.session_state.ovrall_casa.get('gols_sofridos_media'), st.session_state.media_gols_fora)
        btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)
        gol_ht = prob_gol_ht(
            st.session_state.ovrall_casa.get('gols_ht_media', 0.5) or 0.5,
            st.session_state.ovrall_fora.get('gols_ht_media', 0.5) or 0.5,
            st.session_state.ovrall_casa.get('gols_ht_sofridos_media', 0.5) or 0.5,
            st.session_state.ovrall_fora.get('gols_ht_sofridos_media', 0.5) or 0.5,
            media_ht_casa=st.session_state.media_ht_casa, media_ht_fora=st.session_state.media_ht_fora
        )
        esc = prob_over_escanteios(
            st.session_state.ovrall_casa.get('escanteios_media', 5.0) or 5.0,
            st.session_state.ovrall_fora.get('escanteios_media', 5.0) or 5.0,
            st.session_state.ovrall_casa.get('escanteios_sofridos_media', 5.0) or 5.0,
            st.session_state.ovrall_fora.get('escanteios_sofridos_media', 5.0) or 5.0,
            media_casa=st.session_state.media_esc_casa, media_fora=st.session_state.media_esc_fora
        )

        st.subheader("📊 Resultados")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Vitória Casa", f"{p1:.1%}")
        with col2: st.metric("Empate", f"{pX:.1%}")
        with col3: st.metric("Vitória Fora", f"{p2:.1%}")

        st.markdown("---")
        col4, col5 = st.columns(2)
        with col4: st.metric("Over 2.5 gols", f"{over25:.1%}" if over25 else "N/D")
        with col5: st.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")

        st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")
        st.metric("Over Escanteios", f"{esc:.1%}" if esc else "N/D")

        with st.expander("📊 Métricas detalhadas"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{st.session_state.time_casa}**")
                st.write(f"IMA: {ima_casa:.1f}, OVRall: {ovrall_val_casa:.1f}, IC: {ic_val_casa:.1f}, MPV: {mpv_casa:.1f}")
            with c2:
                st.markdown(f"**{st.session_state.time_fora}**")
                st.write(f"IMA: {ima_fora:.1f}, OVRall: {ovrall_val_fora:.1f}, IC: {ic_val_fora:.1f}, MPV: {mpv_fora:.1f}")
