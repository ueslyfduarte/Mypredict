# manual_app.py — MyPredict 2.0 (entrada manual completa)
import streamlit as st
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

def show():
    st.title("MyPredict 2.0 – Modo Manual")
    st.markdown("Preencha todos os campos abaixo para calcular as métricas e mercados.")

    # Times
    col1, col2 = st.columns(2)
    with col1:
        time_casa = st.text_input("Time da Casa", "Flamengo")
    with col2:
        time_fora = st.text_input("Time da Fora", "Palmeiras")

    # Prateleiras
    st.subheader("🏷 Projeção de Prateleiras")
    pos_casa = st.number_input("Posição do time da casa", 1, 20, 1)
    pos_fora = st.number_input("Posição do time da fora", 1, 20, 2)
    prat_casa = obter_prateleira(pos_casa)
    prat_fora = obter_prateleira(pos_fora)
    st.write(f"Casa: **{prat_casa}** – Fora: **{prat_fora}**")

    prateleiras = {time_casa: prat_casa, time_fora: prat_fora}

    # IMA – Jogos recentes
    st.subheader("📊 IMA – Últimos jogos")
    st.markdown("Informe os **10 últimos jogos** de cada time. Os 5 primeiros serão usados como 'últimos 5 gerais', os 3 primeiros como 'últimos 3 gerais', e os mandantes/visitantes para os recortes de casa/fora.")

    def input_jogos(prefixo):
        jogos = []
        for i in range(1, 11):
            st.markdown(f"**Jogo {i}**")
            c1, c2, c3 = st.columns(3)
            res = c1.selectbox("Resultado", ["V", "E", "D"], key=f"{prefixo}_res_{i}")
            adv = c2.text_input("Adversário", key=f"{prefixo}_adv_{i}")
            mand = c3.checkbox("Mandante?", key=f"{prefixo}_mand_{i}")
            if adv:
                jogos.append({"resultado": res, "adversario": adv, "mandante": mand})
        return jogos

    st.markdown("**Jogos do time da casa**")
    jogos_casa = input_jogos("casa")
    st.markdown("**Jogos do time da fora**")
    jogos_fora = input_jogos("fora")

    # OVRall – Estatísticas da temporada
    st.subheader("📈 OVRall – Estatísticas da Temporada")
    st.markdown("Preencha as médias (por jogo) para cada time. Campos vazios serão ignorados (o OVRall redistribui os pesos).")

    def input_ovrall(prefixo):
        return {
            'gols_media': st.number_input("Gols marcados (média)", value=1.5, key=f"{prefixo}_gols"),
            'gols_sofridos_media': st.number_input("Gols sofridos (média)", value=1.0, key=f"{prefixo}_gols_sof"),
            'xg_media': st.number_input("xG (média)", value=0.0, key=f"{prefixo}_xg"),
            'xga_media': st.number_input("xGA (média)", value=0.0, key=f"{prefixo}_xga"),
            'finalizacoes_alvo_media': st.number_input("Finalizações no alvo (média)", value=4.0, key=f"{prefixo}_faz"),
            'finalizacoes_alvo_sofridas_media': st.number_input("Finalizações no alvo sofridas (média)", value=3.0, key=f"{prefixo}_faz_sof"),
            'chutes_media': st.number_input("Chutes totais (média)", value=12.0, key=f"{prefixo}_chutes"),
            'desarmes_intercep_media': st.number_input("Desarmes + Interceptações (média)", value=15.0, key=f"{prefixo}_desarmes"),
            'posse_media': st.slider("Posse de bola (%)", 0, 100, 50, key=f"{prefixo}_posse"),
            'passes_certos_pct': st.slider("Passes certos (%)", 0, 100, 80, key=f"{prefixo}_passes"),
            'passes_chave_media': st.number_input("Passes-chave (média)", value=2.0, key=f"{prefixo}_pchave"),
            'assistencias_media': st.number_input("Assistências (média)", value=1.0, key=f"{prefixo}_assist"),
            'conversao': st.number_input("Conversão de finalizações (%)", value=10.0, key=f"{prefixo}_conv"),
            'clean_sheets_pct': st.slider("Jogos sem sofrer gols (%)", 0, 100, 30, key=f"{prefixo}_cs"),
            'desvio_pontos': st.number_input("Desvio padrão dos pontos", value=1.0, key=f"{prefixo}_dp"),
            'desvio_gols_pro': st.number_input("Desvio padrão gols marcados", value=1.2, key=f"{prefixo}_dgp"),
            'desvio_gols_sofridos': st.number_input("Desvio padrão gols sofridos", value=1.1, key=f"{prefixo}_dgs"),
            'pontos_pos_desvantagem_media': st.number_input("Pontos após sair atrás (média)", value=0.5, key=f"{prefixo}_ppd"),
            'gols_ultimos_15min_media': st.number_input("Gols nos últimos 15 min (média)", value=0.3, key=f"{prefixo}_g15"),
            'pontos_apos_derrota_media': st.number_input("Pontos após derrota (média)", value=1.0, key=f"{prefixo}_pad"),
            'diff_aprov_casa_fora': st.number_input("Diferença aprovação casa-fora (%)", value=10.0, key=f"{prefixo}_diff"),
            'aprov_viradas_favor': st.number_input("Aproveitamento viradas a favor (%)", value=20.0, key=f"{prefixo}_vf"),
            'aprov_viradas_contra': st.number_input("Aproveitamento viradas contra (%)", value=15.0, key=f"{prefixo}_vc"),
        }

    st.text("Time da Casa")
    ovrall_casa = input_ovrall("casa_ovr")
    st.text("Time da Fora")
    ovrall_fora = input_ovrall("fora_ovr")

    # IC – Fatores contextuais
    st.subheader("🧠 IC – Fatores Contextuais")
    def input_ic(prefixo):
        return {
            'confronto_direto': st.slider("Confronto direto (%)", 0, 100, 50, key=f"{prefixo}_cd"),
            'mesmo_escalao': st.slider("Mesmo escalão (%)", 0, 100, 50, key=f"{prefixo}_me"),
            'contra_escalao_adversario': st.slider("Contra escalão adversário (%)", 0, 100, 50, key=f"{prefixo}_ce"),
            'fator_casa': st.slider("Fator casa (%)", 0, 100, 50, key=f"{prefixo}_fc"),
            'odds': st.number_input("Odd (opcional)", value=0.0, key=f"{prefixo}_odds"),
        }

    ic_casa = input_ic("casa_ic")
    ic_fora = input_ic("fora_ic")

    if st.button("Calcular MyPredict Manual"):
        # Montar recortes IMA
        rec_casa = {
            '10G': jogos_casa[:10], '5G': jogos_casa[:5], '3G': jogos_casa[:3],
            '5CF': [j for j in jogos_casa if j['mandante']][:5],
            '3CF': [j for j in jogos_casa if j['mandante']][:3],
        }
        rec_fora = {
            '10G': jogos_fora[:10], '5G': jogos_fora[:5], '3G': jogos_fora[:3],
            '5CF': [j for j in jogos_fora if j['mandante']][:5],
            '3CF': [j for j in jogos_fora if j['mandante']][:3],
        }

        ima_casa = calcular_ima(time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                                rec_casa['5CF'], rec_casa['3CF'], prateleiras)
        ima_fora = calcular_ima(time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                                rec_fora['5CF'], rec_fora['3CF'], prateleiras)

        # OVRall (precisa de referência da liga; usamos os dois times como referência)
        dados_liga = {k: [ovrall_casa.get(k, 0), ovrall_fora.get(k, 0)] for k in set(ovrall_casa) | set(ovrall_fora)}
        ovrall_val_casa = calcular_ovrall(ovrall_casa, dados_liga)
        ovrall_val_fora = calcular_ovrall(ovrall_fora, dados_liga)

        ic_val_casa = calcular_ic(ic_casa)
        ic_val_fora = calcular_ic(ic_fora)

        mpv_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
        mpv_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

        bonus_casa = calcular_bonus_casa(ovrall_casa.get('diff_aprov_casa_fora', 0))
        p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

        over25 = prob_over_2_5(
            ovrall_casa.get('gols_media'), ovrall_fora.get('gols_media'),
            ovrall_casa.get('gols_sofridos_media'), ovrall_fora.get('gols_sofridos_media')
        )

        gols_esp_casa = _gols_esperados(ovrall_casa.get('gols_media'),
                                        ovrall_fora.get('gols_sofridos_media'),
                                        MEDIA_GOLS_CASA_LIGA)
        gols_esp_fora = _gols_esperados(ovrall_fora.get('gols_media'),
                                        ovrall_casa.get('gols_sofridos_media'),
                                        MEDIA_GOLS_FORA_LIGA)
        btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)

        gol_ht = prob_gol_ht(
            ovrall_casa.get('gols_ht_media', 0.5),
            ovrall_fora.get('gols_ht_media', 0.5),
            ovrall_casa.get('gols_ht_sofridos_media', 0.5),
            ovrall_fora.get('gols_ht_sofridos_media', 0.5)
        )

        esc = prob_over_escanteios(
            ovrall_casa.get('escanteios_media', 5.0),
            ovrall_fora.get('escanteios_media', 5.0),
            ovrall_casa.get('escanteios_sofridos_media', 5.0),
            ovrall_fora.get('escanteios_sofridos_media', 5.0)
        )

        st.subheader("📊 Resultados")
        col1, col2, col3 = st.columns(3)
        col1.metric("Vitória Casa", f"{p1:.1%}")
        col2.metric("Empate", f"{pX:.1%}")
        col3.metric("Vitória Fora", f"{p2:.1%}")

        col4, col5 = st.columns(2)
        col4.metric("Over 2.5", f"{over25:.1%}")
        col5.metric("Ambas Marcam", f"{btts:.1%}")

        st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")
        st.metric("Over Escanteios", f"{esc:.1%}" if esc else "N/D")

        with st.expander("📊 Métricas detalhadas"):
            st.write(f"**{time_casa}** – IMA: {ima_casa:.1f}, OVRall: {ovrall_val_casa:.1f}, IC: {ic_val_casa:.1f}, MPV: {mpv_casa:.1f}")
            st.write(f"**{time_fora}** – IMA: {ima_fora:.1f}, OVRall: {ovrall_val_fora:.1f}, IC: {ic_val_fora:.1f}, MPV: {mpv_fora:.1f}")
