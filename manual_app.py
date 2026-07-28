# manual_app.py — MyPredict 2.0 (com preenchimento em lote, prateleiras ajustáveis e vírgula)
import streamlit as st
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

# ------------------------------------------------------------
# Função auxiliar para converter string com vírgula em float
# ------------------------------------------------------------
def para_float(valor_str):
    if valor_str is None or valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        return None

# ------------------------------------------------------------
# Lista ordenada de métricas (usada para preenchimento em lote)
# ------------------------------------------------------------
METRICAS_OVRALL = [
    "gols_media", "gols_sofridos_media", "xg_media", "xga_media",
    "finalizacoes_alvo_media", "finalizacoes_alvo_sofridas_media",
    "chutes_media", "desarmes_intercep_media", "posse_media",
    "passes_certos_pct", "passes_chave_media", "assistencias_media",
    "conversao", "clean_sheets_pct", "desvio_pontos", "desvio_gols_pro",
    "desvio_gols_sofridos", "pontos_pos_desvantagem_media",
    "gols_ultimos_15min_media", "pontos_apos_derrota_media",
    "diff_aprov_casa_fora", "aprov_viradas_favor", "aprov_viradas_contra"
]

METRICAS_IC = [
    "confronto_direto", "mesmo_escalao", "contra_escalao_adversario",
    "fator_casa", "odds"
]

# ------------------------------------------------------------
# CSS para colorir as colunas dos times
# ------------------------------------------------------------
st.markdown("""
<style>
    .col-casa {
        background-color: #1a1a1a;
        border: 2px solid #ffd700;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .col-fora {
        background-color: #1a1a1a;
        border: 2px solid #c0c0c0;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .col-header {
        color: #ffd700;
        font-weight: 600;
        text-align: center;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Função auxiliar para exibir métrica em duas colunas (com text_input)
# ------------------------------------------------------------
def metrica_lado_a_lado(label, key_casa, key_fora, valor_padrao="0.0"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="col-casa">', unsafe_allow_html=True)
        st.markdown(f'<div class="col-header">{label}</div>', unsafe_allow_html=True)
        ativo = st.checkbox("Ativar", value=True, key=f"{key_casa}_ativo")
        val_str = st.text_input("Valor", value=valor_padrao, key=f"{key_casa}_valor")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="col-fora">', unsafe_allow_html=True)
        st.markdown(f'<div class="col-header">{label}</div>', unsafe_allow_html=True)
        ativo_f = st.checkbox("Ativar", value=True, key=f"{key_fora}_ativo")
        val_str_f = st.text_input("Valor", value=valor_padrao, key=f"{key_fora}_valor")
        st.markdown('</div>', unsafe_allow_html=True)
    return (para_float(val_str) if ativo else None), (para_float(val_str_f) if ativo_f else None)

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
    modo_ima = st.radio("Modo de preenchimento", ["Manual", "Colar dados (CSV)"], key="modo_ima")
    
    jogos_casa = []
    jogos_fora = []
    
    if modo_ima == "Manual":
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
    else:
        st.markdown("Cole os dados dos jogos no formato: `Resultado, Adversário, Mandante (S/N)` – uma linha por jogo, 10 linhas para cada time.")
        col_csv1, col_csv2 = st.columns(2)
        with col_csv1:
            st.markdown("**Time da casa**")
            texto_casa = st.text_area("Cole aqui os 10 jogos do time da casa", height=200, key="csv_casa")
            if st.button("Carregar jogos da casa"):
                linhas = texto_casa.strip().split('\n')
                for linha in linhas[:10]:
                    partes = [p.strip() for p in linha.split(',')]
                    if len(partes) >= 3:
                        res = partes[0]
                        adv = partes[1]
                        mand = partes[2].upper() == 'S'
                        jogos_casa.append({"resultado": res, "adversario": adv, "mandante": mand})
                st.success(f"{len(jogos_casa)} jogos carregados!")
        with col_csv2:
            st.markdown("**Time da fora**")
            texto_fora = st.text_area("Cole aqui os 10 jogos do time da fora", height=200, key="csv_fora")
            if st.button("Carregar jogos da fora"):
                linhas = texto_fora.strip().split('\n')
                for linha in linhas[:10]:
                    partes = [p.strip() for p in linha.split(',')]
                    if len(partes) >= 3:
                        res = partes[0]
                        adv = partes[1]
                        mand = partes[2].upper() == 'S'
                        jogos_fora.append({"resultado": res, "adversario": adv, "mandante": mand})
                st.success(f"{len(jogos_fora)} jogos carregados!")

    # Atribuir prateleira padrão e permitir ajuste
    for jogo in jogos_casa + jogos_fora:
        if jogo['adversario'] not in prateleiras:
            prateleiras[jogo['adversario']] = "Media"

    with st.expander("Ajustar prateleiras dos adversários"):
        adversarios = sorted(set(j['adversario'] for j in jogos_casa + jogos_fora if j['adversario'] not in [time_casa, time_fora]))
        for adv in adversarios:
            prateleiras[adv] = st.selectbox(
                f"Prateleira de {adv}",
                ["Elite", "Alta", "Media", "Baixa", "Critica"],
                index=2,
                key=f"prat_{adv}"
            )

    st.divider()
    st.subheader("📈 OVRall – Estatísticas da Temporada")
    modo_ovrall = st.radio("Modo de preenchimento", ["Manual", "Preencher em lote"], key="modo_ovrall")
    
    ovrall_casa = {}
    ovrall_fora = {}
    
    if modo_ovrall == "Manual":
        st.markdown("Marque/desmarque os checkboxes para incluir ou ignorar cada métrica. Use **vírgula** como separador decimal (ex.: 1,42).")
        metricas_ovrall_labels = [
            ("Gols marcados (média)", "gols_media", "1.5"),
            ("Gols sofridos (média)", "gols_sofridos_media", "1.0"),
            ("xG (média)", "xg_media", "0.0"),
            ("xGA (média)", "xga_media", "0.0"),
            ("Finalizações no alvo (média)", "finalizacoes_alvo_media", "4.0"),
            ("Finalizações no alvo sofridas (média)", "finalizacoes_alvo_sofridas_media", "3.0"),
            ("Chutes totais (média)", "chutes_media", "12.0"),
            ("Desarmes + Interceptações (média)", "desarmes_intercep_media", "15.0"),
            ("Posse de bola (%)", "posse_media", "50.0"),
            ("Passes certos (%)", "passes_certos_pct", "80.0"),
            ("Passes-chave (média)", "passes_chave_media", "2.0"),
            ("Assistências (média)", "assistencias_media", "1.0"),
            ("Conversão de finalizações (%)", "conversao", "10.0"),
            ("Jogos sem sofrer gols (%)", "clean_sheets_pct", "30.0"),
            ("Desvio padrão dos pontos", "desvio_pontos", "1.0"),
            ("Desvio padrão gols marcados", "desvio_gols_pro", "1.2"),
            ("Desvio padrão gols sofridos", "desvio_gols_sofridos", "1.1"),
            ("Pontos após sair atrás (média)", "pontos_pos_desvantagem_media", "0.5"),
            ("Gols nos últimos 15 min (média)", "gols_ultimos_15min_media", "0.3"),
            ("Pontos após derrota (média)", "pontos_apos_derrota_media", "1.0"),
            ("Diferença aprovação casa-fora (%)", "diff_aprov_casa_fora", "10.0"),
            ("Aproveitamento viradas a favor (%)", "aprov_viradas_favor", "20.0"),
            ("Aproveitamento viradas contra (%)", "aprov_viradas_contra", "15.0"),
        ]
        for label, key, default in metricas_ovrall_labels:
            vc, vf = metrica_lado_a_lado(label, f"casa_{key}", f"fora_{key}", default)
            ovrall_casa[key] = vc
            ovrall_fora[key] = vf
    else:
        st.markdown("Cole os valores para **todas as métricas OVRall** separados por vírgula. A ordem é:")
        st.markdown("`" + ", ".join(METRICAS_OVRALL) + "`")
        col_lote1, col_lote2 = st.columns(2)
        with col_lote1:
            st.markdown("**Time da casa**")
            texto_lote_casa = st.text_area("Cole os valores do time da casa (23 números)", height=100, key="lote_casa_ovr")
            if st.button("Preencher métricas da casa"):
                partes = [x.strip() for x in texto_lote_casa.split(',')]
                if len(partes) == len(METRICAS_OVRALL):
                    for i, key in enumerate(METRICAS_OVRALL):
                        ovrall_casa[key] = para_float(partes[i])
                    st.success("Métricas da casa preenchidas!")
                else:
                    st.error(f"Precisa de {len(METRICAS_OVRALL)} valores, mas foram fornecidos {len(partes)}.")
        with col_lote2:
            st.markdown("**Time da fora**")
            texto_lote_fora = st.text_area("Cole os valores do time da fora (23 números)", height=100, key="lote_fora_ovr")
            if st.button("Preencher métricas da fora"):
                partes = [x.strip() for x in texto_lote_fora.split(',')]
                if len(partes) == len(METRICAS_OVRALL):
                    for i, key in enumerate(METRICAS_OVRALL):
                        ovrall_fora[key] = para_float(partes[i])
                    st.success("Métricas da fora preenchidas!")
                else:
                    st.error(f"Precisa de {len(METRICAS_OVRALL)} valores, mas foram fornecidos {len(partes)}.")

    st.divider()
    st.subheader("🧠 IC – Fatores Contextuais")
    modo_ic = st.radio("Modo de preenchimento", ["Manual", "Preencher em lote"], key="modo_ic")
    
    ic_casa = {}
    ic_fora = {}
    
    if modo_ic == "Manual":
        metricas_ic_labels = [
            ("Confronto direto (%)", "confronto_direto", "50.0"),
            ("Mesmo escalão (%)", "mesmo_escalao", "50.0"),
            ("Contra escalão adversário (%)", "contra_escalao_adversario", "50.0"),
            ("Fator casa (%)", "fator_casa", "50.0"),
            ("Odd (opcional)", "odds", "0.0"),
        ]
        for label, key, default in metricas_ic_labels:
            vc, vf = metrica_lado_a_lado(label, f"casa_{key}", f"fora_{key}", default)
            ic_casa[key] = vc
            ic_fora[key] = vf
    else:
        st.markdown("Cole os valores para **todas as métricas IC** separados por vírgula. A ordem é:")
        st.markdown("`" + ", ".join(METRICAS_IC) + "`")
        col_lote1, col_lote2 = st.columns(2)
        with col_lote1:
            st.markdown("**Time da casa**")
            texto_lote_casa_ic = st.text_area("Cole os valores do time da casa (5 números)", height=100, key="lote_casa_ic")
            if st.button("Preencher métricas IC da casa"):
                partes = [x.strip() for x in texto_lote_casa_ic.split(',')]
                if len(partes) == len(METRICAS_IC):
                    for i, key in enumerate(METRICAS_IC):
                        ic_casa[key] = para_float(partes[i])
                    st.success("Métricas IC da casa preenchidas!")
                else:
                    st.error(f"Precisa de {len(METRICAS_IC)} valores, mas foram fornecidos {len(partes)}.")
        with col_lote2:
            st.markdown("**Time da fora**")
            texto_lote_fora_ic = st.text_area("Cole os valores do time da fora (5 números)", height=100, key="lote_fora_ic")
            if st.button("Preencher métricas IC da fora"):
                partes = [x.strip() for x in texto_lote_fora_ic.split(',')]
                if len(partes) == len(METRICAS_IC):
                    for i, key in enumerate(METRICAS_IC):
                        ic_fora[key] = para_float(partes[i])
                    st.success("Métricas IC da fora preenchidas!")
                else:
                    st.error(f"Precisa de {len(METRICAS_IC)} valores, mas foram fornecidos {len(partes)}.")

    st.divider()
    if st.button("Calcular MyPredict Manual"):
        # --- Montar recortes IMA ---
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

        # OVRall
        dados_liga = {k: [ovrall_casa.get(k, 0) or 0, ovrall_fora.get(k, 0) or 0] for k in set(ovrall_casa) | set(ovrall_fora)}
        ovrall_val_casa = calcular_ovrall(ovrall_casa, dados_liga)
        ovrall_val_fora = calcular_ovrall(ovrall_fora, dados_liga)

        # IC
        ic_val_casa = calcular_ic(ic_casa)
        ic_val_fora = calcular_ic(ic_fora)

        # MPV
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
