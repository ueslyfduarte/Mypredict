# manual_app.py — MyPredict 2.0 (entrada manual completa, estatísticas lado a lado)
import streamlit as st
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

def metrica_dupla(label, key_casa, key_fora, valor_padrao=0.0, step=0.1, format="%.2f"):
    """Exibe dois checkboxes + dois campos numéricos lado a lado."""
    col1, col2 = st.columns(2)
    ativo_casa = col1.checkbox(f"Casa", value=True, key=f"{key_casa}_ativo")
    val_casa = col1.number_input(label, value=valor_padrao, step=step, format=format, key=f"{key_casa}_valor")

    ativo_fora = col2.checkbox(f"Fora", value=True, key=f"{key_fora}_ativo")
    val_fora = col2.number_input(label, value=valor_padrao, step=step, format=format, key=f"{key_fora}_valor")
    return (val_casa if ativo_casa else None), (val_fora if ativo_fora else None)

def show():
    st.title("MyPredict 2.0 – Modo Manual")
    st.markdown("Preencha os campos abaixo. **Desmarque o checkbox de uma métrica para ignorá‑la** – o peso será redistribuído automaticamente.")

    # Times
    col1, col2 = st.columns(2)
    with col1:
        time_casa = st.text_input("Time da Casa", "Flamengo")
    with col2:
        time_fora = st.text_input("Time da Fora", "Palmeiras")

    st.divider()
    st.subheader("🏷 Projeção de Prateleiras")
    c1, c2 = st.columns(2)
    pos_casa = c1.number_input("Posição do time da casa", 1, 20, 1)
    pos_fora = c2.number_input("Posição do time da fora", 1, 20, 2)
    prat_casa = obter_prateleira(pos_casa)
    prat_fora = obter_prateleira(pos_fora)
    st.write(f"Casa: **{prat_casa}** – Fora: **{prat_fora}**")
    prateleiras = {time_casa: prat_casa, time_fora: prat_fora}

    st.divider()
    st.subheader("📊 IMA – Últimos jogos")
    st.markdown("Informe os **10 últimos jogos** de cada time. Os recortes são automáticos.")

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

    st.divider()
    st.subheader("📈 OVRall – Estatísticas da Temporada")
    st.markdown("Marque/desmarque os checkboxes para incluir ou ignorar cada métrica.")

    ovrall_casa = {}
    ovrall_fora = {}

    # Lista de métricas com seus defaults
    metricas_ovrall = [
        ("Gols marcados (média)", "gols_media", 1.5),
        ("Gols sofridos (média)", "gols_sofridos_media", 1.0),
        ("xG (média)", "xg_media", 0.0),
        ("xGA (média)", "xga_media", 0.0),
        ("Finalizações no alvo (média)", "finalizacoes_alvo_media", 4.0),
        ("Finalizações no alvo sofridas (média)", "finalizacoes_alvo_sofridas_media", 3.0),
        ("Chutes totais (média)", "chutes_media", 12.0),
        ("Desarmes + Interceptações (média)", "desarmes_intercep_media", 15.0),
        ("Posse de bola (%)", "posse_media", 50.0, 1.0, "%.0f"),
        ("Passes certos (%)", "passes_certos_pct", 80.0, 1.0, "%.0f"),
        ("Passes-chave (média)", "passes_chave_media", 2.0),
        ("Assistências (média)", "assistencias_media", 1.0),
        ("Conversão de finalizações (%)", "conversao", 10.0, 1.0, "%.0f"),
        ("Jogos sem sofrer gols (%)", "clean_sheets_pct", 30.0, 1.0, "%.0f"),
        ("Desvio padrão dos pontos", "desvio_pontos", 1.0),
        ("Desvio padrão gols marcados", "desvio_gols_pro", 1.2),
        ("Desvio padrão gols sofridos", "desvio_gols_sofridos", 1.1),
        ("Pontos após sair atrás (média)", "pontos_pos_desvantagem_media", 0.5),
        ("Gols nos últimos 15 min (média)", "gols_ultimos_15min_media", 0.3),
        ("Pontos após derrota (média)", "pontos_apos_derrota_media", 1.0),
        ("Diferença aprovação casa-fora (%)", "diff_aprov_casa_fora", 10.0, 1.0, "%.0f"),
        ("Aproveitamento viradas a favor (%)", "aprov_viradas_favor", 20.0, 1.0, "%.0f"),
        ("Aproveitamento viradas contra (%)", "aprov_viradas_contra", 15.0, 1.0, "%.0f"),
    ]

    for label, key, *rest in metricas_ovrall:
        default = rest[0] if rest else 0.0
        step = rest[1] if len(rest) > 1 else 0.1
        fmt = rest[2] if len(rest) > 2 else "%.2f"
        vc, vf = metrica_dupla(label, f"casa_{key}", f"fora_{key}", default, step, fmt)
        ovrall_casa[key] = vc
        ovrall_fora[key] = vf

    st.divider()
    st.subheader("🧠 IC – Fatores Contextuais")
    ic_casa = {}
    ic_fora = {}

    metricas_ic = [
        ("Confronto direto (%)", "confronto_direto", 50.0, 1.0, "%.0f"),
        ("Mesmo escalão (%)", "mesmo_escalao", 50.0, 1.0, "%.0f"),
        ("Contra escalão adversário (%)", "contra_escalao_adversario", 50.0, 1.0, "%.0f"),
        ("Fator casa (%)", "fator_casa", 50.0, 1.0, "%.0f"),
        ("Odd (opcional)", "odds", 0.0),
    ]

    for label, key, *rest in metricas_ic:
        default = rest[0] if rest else 0.0
        step = rest[1] if len(rest) > 1 else 0.1
        fmt = rest[2] if len(rest) > 2 else "%.2f"
        vc, vf = metrica_dupla(label, f"casa_{key}", f"fora_{key}", default, step, fmt)
        ic_casa[key] = vc
        ic_fora[key] = vf

    st.divider()
    if st.button("Calcular MyPredict Manual"):
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

        # OVRall: usa os dois times como referência da liga
        dados_liga = {k: [ovrall_casa.get(k, 0) or 0, ovrall_fora.get(k, 0) or 0] for k in set(ovrall_casa) | set(ovrall_fora)}
        ovrall_val_casa = calcular_ovrall(ovrall_casa, dados_liga)
        ovrall_val_fora = calcular_ovrall(ovrall_fora, dados_liga)

        ic_val_casa = calcular_ic(ic_casa)
        ic_val_fora = calcular_ic(ic_fora)

        mpv_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
        mpv_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

        bonus_casa = calcular_bonus_casa(ovrall_casa.get('diff_aprov_casa_fora') or 0)
        p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

        over25 = prob_over_2_5(
            ovrall_casa.get('gols_media') or 1.5, ovrall_fora.get('gols_media') or 1.5,
            ovrall_casa.get('gols_sofridos_media') or 1.0, ovrall_fora.get('gols_sofridos_media') or 1.0
        )

        gols_esp_casa = _gols_esperados(ovrall_casa.get('gols_media') or 1.5,
                                        ovrall_fora.get('gols_sofridos_media') or 1.0,
                                        MEDIA_GOLS_CASA_LIGA)
        gols_esp_fora = _gols_esperados(ovrall_fora.get('gols_media') or 1.5,
                                        ovrall_casa.get('gols_sofridos_media') or 1.0,
                                        MEDIA_GOLS_FORA_LIGA)
        btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)

        gol_ht = prob_gol_ht(
            ovrall_casa.get('gols_ht_media', 0.5) or 0.5,
            ovrall_fora.get('gols_ht_media', 0.5) or 0.5,
            ovrall_casa.get('gols_ht_sofridos_media', 0.5) or 0.5,
            ovrall_fora.get('gols_ht_sofridos_media', 0.5) or 0.5
        )

        esc = prob_over_escanteios(
            ovrall_casa.get('escanteios_media', 5.0) or 5.0,
            ovrall_fora.get('escanteios_media', 5.0) or 5.0,
            ovrall_casa.get('escanteios_sofridos_media', 5.0) or 5.0,
            ovrall_fora.get('escanteios_sofridos_media', 5.0) or 5.0
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
