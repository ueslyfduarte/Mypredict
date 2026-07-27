import streamlit as st
from data_loader import (
    gerar_prateleiras, obter_ultimos_jogos_com_heranca, extrair_recortes_ima,
    obter_dados_ovrall_time, classificação_anterior
)
from ratings import calcular_ima, calcular_mpv
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

st.set_page_config(page_title="MyPredict 2.0", layout="centered")
st.title("MyPredict 2.0 – Teste ao vivo")

liga = 'Brasileirão'
temporada = 2024
time_casa = st.text_input("Time da casa", "Flamengo")
time_fora = st.text_input("Time de fora", "Palmeiras")

if st.button("Prever"):
    with st.spinner("Buscando dados e calculando..."):
        class_ant = classificação_anterior(liga, temporada)
        prateleiras = gerar_prateleiras(liga, temporada)

        dados_casa = obter_dados_ovrall_time(time_casa, liga, temporada, class_ant)
        dados_fora = obter_dados_ovrall_time(time_fora, liga, temporada, class_ant)

        if not dados_casa or not dados_fora:
            st.error("Não foi possível carregar os dados. Verifique os nomes ou a conexão.")
            st.stop()

        # IMA
        jogos_casa = obter_ultimos_jogos_com_heranca(time_casa, liga, temporada, class_ant, n=20)
        rec_casa = extrair_recortes_ima(jogos_casa, True)
        jogos_fora = obter_ultimos_jogos_com_heranca(time_fora, liga, temporada, class_ant, n=20)
        rec_fora = extrair_recortes_ima(jogos_fora, False)

        ima_casa = calcular_ima(time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                                rec_casa['5CF'], rec_casa['3CF'], prateleiras)
        ima_fora = calcular_ima(time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                                rec_fora['5CF'], rec_fora['3CF'], prateleiras)

        # OVRall e IC temporários
        ovrall_casa = 50.0
        ovrall_fora = 50.0
        ic_casa = 50.0
        ic_fora = 50.0

        mpv_casa = calcular_mpv(ima_casa, ovrall_casa, ic_casa)
        mpv_fora = calcular_mpv(ima_fora, ovrall_fora, ic_fora)
        bonus_casa = calcular_bonus_casa(dados_casa.get('diff_aprov_casa_fora'))

        p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

        over25 = prob_over_2_5(
            dados_casa.get('gols_media'), dados_fora.get('gols_media'),
            dados_casa.get('gols_sofridos_media'), dados_fora.get('gols_sofridos_media')
        )

        gols_esp_casa = _gols_esperados(dados_casa.get('gols_media'), dados_fora.get('gols_sofridos_media'), MEDIA_GOLS_CASA_LIGA)
        gols_esp_fora = _gols_esperados(dados_fora.get('gols_media'), dados_casa.get('gols_sofridos_media'), MEDIA_GOLS_FORA_LIGA)
        btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora) if gols_esp_casa and gols_esp_fora else None

        gol_ht = prob_gol_ht(
            dados_casa.get('gols_ht_media'), dados_fora.get('gols_ht_media'),
            dados_casa.get('gols_ht_sofridos_media'), dados_fora.get('gols_ht_sofridos_media')
        )

    st.subheader("Probabilidades")
    col1, col2, col3 = st.columns(3)
    col1.metric("Casa", f"{p1:.1%}")
    col2.metric("Empate", f"{pX:.1%}")
    col3.metric("Fora", f"{p2:.1%}")

    col4, col5 = st.columns(2)
    col4.metric("Over 2.5 gols", f"{over25:.1%}" if over25 else "N/D")
    col5.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")
    st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")

    st.caption(f"MPV {time_casa}: {mpv_casa:.1f} | MPV {time_fora}: {mpv_fora:.1f} | Bônus casa: {bonus_casa:.1f}")
    st.caption(f"IMA {time_casa}: {ima_casa:.1f} | IMA {time_fora}: {ima_fora:.1f}")
