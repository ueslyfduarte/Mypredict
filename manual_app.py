# # manual_app.py — MyPredict 2.0 (Final com setas, selos e sem placeholders)
import streamlit as st
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

def para_float(valor_str):
    if valor_str is None or valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        return None

st.markdown("""
<style>
    .selo-dourado {
        background: linear-gradient(145deg, #ffd700, #b8860b);
        color: #0e1117;
        font-weight: 900;
        text-align: center;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 10px auto;
        font-size: 12px;
        box-shadow: 0 0 20px #ffd700;
    }
    .selo-verde {
        background: #00ff7f;
        color: #0e1117;
        font-weight: 700;
        text-align: center;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 5px;
    }
    .selo-amarelo {
        background: #ffaa00;
        color: #0e1117;
        font-weight: 700;
        text-align: center;
        border-radius: 20px;
        padding: 4px 12px;
        margin: 5px;
    }
    .seta-up { color: #00ff7f; font-size: 20px; }
    .seta-down { color: #ff4d4d; font-size: 20px; }
    .seta-neutral { color: #ffd700; font-size: 20px; }
</style>
""", unsafe_allow_html=True)

def indicador(prob):
    if prob is None:
        return "⬜", ""
    if prob >= 0.70:
        return "⬆️", "selo-dourado"
    elif prob >= 0.55:
        return "⬆️", "selo-verde"
    elif prob >= 0.45:
        return "➖", "selo-amarelo"
    else:
        return "⬇️", ""

def show():
    st.title("MyPredict 2.0 – Modo Manual")
    st.markdown("Preencha **todos** os campos abaixo. Só clique em **Calcular** quando os dados estiverem completos.")

    # ---------- TIMES ----------
    c1, c2 = st.columns(2)
    time_casa = c1.text_input("Time da Casa", "Flamengo")
    time_fora = c2.text_input("Time da Fora", "Palmeiras")

    # ---------- PRATELEIRAS ----------
    st.subheader("🏷 Projeção de Prateleiras")
    pos_casa = st.number_input("Posição do time da casa", 1, 20, 1)
    pos_fora = st.number_input("Posição do time da fora", 1, 20, 2)
    prat_casa = obter_prateleira(pos_casa)
    prat_fora = obter_prateleira(pos_fora)
    st.write(f"Casa: **{prat_casa}** – Fora: **{prat_fora}**")
    prateleiras = {time_casa: prat_casa, time_fora: prat_fora}

    # ---------- IMA (10 jogos cada) ----------
    st.subheader("📊 IMA – Últimos 10 jogos")
    st.markdown("Formato: `Resultado (V/E/D), Adversário, Mandante (S/N)` — uma linha por jogo")

    jogos_casa = []
    jogos_fora = []
    col_j1, col_j2 = st.columns(2)
    with col_j1:
        txt_casa = st.text_area("Time da casa", height=200, key="jogos_casa")
    with col_j2:
        txt_fora = st.text_area("Time da fora", height=200, key="jogos_fora")

    def parse_jogos(texto):
        jogos = []
        for linha in texto.strip().split('\n'):
            partes = [p.strip() for p in linha.split(',')]
            if len(partes) >= 3:
                res = partes[0]
                adv = partes[1]
                mand = partes[2].upper() == 'S'
                jogos.append({"resultado": res, "adversario": adv, "mandante": mand})
        return jogos

    jogos_casa = parse_jogos(txt_casa)
    jogos_fora = parse_jogos(txt_fora)

    for j in jogos_casa + jogos_fora:
        if j['adversario'] not in prateleiras:
            prateleiras[j['adversario']] = "Media"

    # ---------- OVRALL ----------
    st.subheader("📈 OVRall – Métricas da Temporada")
    st.markdown("Insira os valores abaixo. Deixe em branco se não souber (a métrica será ignorada). Use vírgula como separador decimal.")

    def metrica(label, key_casa, key_fora):
        c1, c2 = st.columns(2)
        vc = para_float(c1.text_input(label, key=f"{key_casa}_val"))
        vf = para_float(c2.text_input(label, key=f"{key_fora}_val"))
        return vc, vf

    ovrall_casa = {}
    ovrall_fora = {}

    metricas = [
        ("Gols marcados (média)", "gols_media"),
        ("Gols sofridos (média)", "gols_sofridos_media"),
        ("xG (média)", "xg_media"),
        ("xGA (média)", "xga_media"),
        ("Finalizações no alvo (média)", "finalizacoes_alvo_media"),
        ("Finalizações no alvo sofridas (média)", "finalizacoes_alvo_sofridas_media"),
        ("Chutes totais (média)", "chutes_media"),
        ("Desarmes + Interceptações (média)", "desarmes_intercep_media"),
        ("Posse de bola (%)", "posse_media"),
        ("Passes certos (%)", "passes_certos_pct"),
        ("Passes-chave (média)", "passes_chave_media"),
        ("Assistências (média)", "assistencias_media"),
        ("Conversão de finalizações (%)", "conversao"),
        ("Jogos sem sofrer gols (%)", "clean_sheets_pct"),
        ("Desvio padrão dos pontos", "desvio_pontos"),
        ("Desvio padrão gols marcados", "desvio_gols_pro"),
        ("Desvio padrão gols sofridos", "desvio_gols_sofridos"),
        ("Pontos após sair atrás (média)", "pontos_pos_desvantagem_media"),
        ("Gols nos últimos 15 min (média)", "gols_ultimos_15min_media"),
        ("Pontos após derrota (média)", "pontos_apos_derrota_media"),
        ("Diferença aprovação casa-fora (%)", "diff_aprov_casa_fora"),
        ("Aproveitamento viradas a favor (%)", "aprov_viradas_favor"),
        ("Aproveitamento viradas contra (%)", "aprov_viradas_contra"),
    ]

    for label, key in metricas:
        vc, vf = metrica(label, f"casa_{key}", f"fora_{key}")
        ovrall_casa[key] = vc
        ovrall_fora[key] = vf

    # ---------- IC ----------
    st.subheader("🧠 IC – Fatores Contextuais")
    ic_casa = {}
    ic_fora = {}
    metrica_ic = [
        ("Confronto direto (%)", "confronto_direto"),
        ("Mesmo escalão (%)", "mesmo_escalao"),
        ("Contra escalão adversário (%)", "contra_escalao_adversario"),
        ("Fator casa (%)", "fator_casa"),
        ("Odd", "odds"),
    ]
    for label, key in metrica_ic:
        vc, vf = metrica(label, f"ic_casa_{key}", f"ic_fora_{key}")
        ic_casa[key] = vc
        ic_fora[key] = vf

    # ---------- CÁLCULO ----------
    if st.button("Calcular MyPredict Manual"):
        if len(jogos_casa) < 10 or len(jogos_fora) < 10:
            st.error("São necessários exatamente 10 jogos para cada time.")
            st.stop()
        if ovrall_casa.get('gols_media') is None or ovrall_fora.get('gols_media') is None:
            st.error("É obrigatório informar a média de gols marcados de ambos os times.")
            st.stop()

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

        # Exibição com setas e selos
        st.subheader("📊 Resultados")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitória Casa", f"{p1:.1%}")
            seta, selo = indicador(p1)
            st.markdown(seta)
            if selo == "selo-dourado":
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
            elif selo == "selo-verde":
                st.markdown('<div class="selo-verde">FAVORITO</div>', unsafe_allow_html=True)
            elif selo == "selo-amarelo":
                st.markdown('<div class="selo-amarelo">EQUILIBRADO</div>', unsafe_allow_html=True)
        with col2:
            st.metric("Empate", f"{pX:.1%}")
            seta, selo = indicador(pX)
            st.markdown(seta)
        with col3:
            st.metric("Vitória Fora", f"{p2:.1%}")
            seta, selo = indicador(p2)
            st.markdown(seta)
            if selo == "selo-dourado":
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
            elif selo == "selo-verde":
                st.markdown('<div class="selo-verde">FAVORITO</div>', unsafe_allow_html=True)

        st.markdown("---")
        col4, col5 = st.columns(2)
        with col4:
            st.metric("Over 2.5 gols", f"{over25:.1%}" if over25 else "N/D")
            seta, selo = indicador(over25)
            st.markdown(seta)
            if over25 and over25 >= 0.70:
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
        with col5:
            st.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")
            seta, selo = indicador(btts)
            st.markdown(seta)
            if btts and btts >= 0.70:
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)

        st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")
        seta, _ = indicador(gol_ht)
        st.markdown(seta)

        st.metric("Over Escanteios", f"{esc:.1%}" if esc else "N/D")
        seta, _ = indicador(esc)
        st.markdown(seta)

        with st.expander("📊 Métricas detalhadas"):
            st.write(f"**{time_casa}** – IMA: {ima_casa:.1f}, OVRall: {ovrall_val_casa:.1f}, IC: {ic_val_casa:.1f}, MPV: {mpv_casa:.1f}")
            st.write(f"**{time_fora}** – IMA: {ima_fora:.1f}, OVRall: {ovrall_val_fora:.1f}, IC: {ic_val_fora:.1f}, MPV: {mpv_fora:.1f}")
