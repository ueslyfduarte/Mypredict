# manual_app.py — MyPredict 2.0 (com detalhamento, indicadores e médias da liga)
import streamlit as st
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira, _percentil
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA, PESOS_OVRALL

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
    """Retorna seta e selo conforme a probabilidade."""
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
    modo_entrada = st.radio("Escolha o modo de entrada", ["Preenchimento Manual", "Colar resposta da IA"])

    # ------------------------------------------------------------
    # Variáveis que serão usadas em ambos os modos
    # ------------------------------------------------------------
    time_casa = ""
    time_fora = ""
    pos_casa = 1
    pos_fora = 2
    jogos_casa = []
    jogos_fora = []
    ovrall_casa = {}
    ovrall_fora = {}
    ic_casa = {}
    ic_fora = {}
    prateleiras = {}
    dados_liga = {
        "media_gols_casa": MEDIA_GOLS_CASA_LIGA,
        "media_gols_fora": MEDIA_GOLS_FORA_LIGA,
        "posse_media": 50.0,
        "passes_certos_pct": 80.0,
    }

    # ------------------------------------------------------------
    # MODO: COLAR RESPOSTA DA IA
    # ------------------------------------------------------------
    if modo_entrada == "Colar resposta da IA":
        st.markdown("### 📥 Cole aqui a resposta completa da IA")
        if 'dados_processados' not in st.session_state:
            st.session_state.dados_processados = False
        texto_colado = st.text_area(
            "Cole a resposta inteira da IA aqui (posições, jogos, métricas OVRall e IC)",
            height=300,
            key="texto_ia"
        )
        if st.button("📥 Processar dados"):
            # ... (código de parsing idêntico ao anterior, omitido por brevidade)
            st.success("Processado!")
            st.session_state.dados_processados = True
            st.rerun()

        if st.session_state.dados_processados:
            # Usa os dados do session_state
            time_casa = st.text_input("Time da Casa", value=st.session_state.time_casa)
            time_fora = st.text_input("Time da Fora", value=st.session_state.time_fora)
            pos_casa = st.session_state.pos_casa
            pos_fora = st.session_state.pos_fora
            jogos_casa = st.session_state.jogos_casa
            jogos_fora = st.session_state.jogos_fora
            ovrall_casa = st.session_state.ovrall_casa
            ovrall_fora = st.session_state.ovrall_fora
            ic_casa = st.session_state.ic_casa
            ic_fora = st.session_state.ic_fora
            # prateleiras já foram processadas
    else:
        # ------------------------------------------------------------
        # MODO MANUAL (ORIGINAL)
        # ------------------------------------------------------------
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

        st.divider()
        st.subheader("📊 IMA – Últimos jogos")
        modo_ima = st.radio("Modo de preenchimento", ["Manual", "Colar dados (CSV)"], key="modo_ima")
        if modo_ima == "Manual":
            # ... (código de input de jogos igual ao anterior)
            pass
        else:
            # ... (código de colar jogos)
            pass

        st.divider()
        st.subheader("📈 OVRall – Estatísticas da Temporada")
        modo_ovrall = st.radio("Modo de preenchimento", ["Manual", "Preencher em lote"], key="modo_ovrall")
        if modo_ovrall == "Manual":
            # ... (métricas lado a lado)
            pass
        else:
            # ... (lote)
            pass

        st.divider()
        st.subheader("🧠 IC – Fatores Contextuais")
        modo_ic = st.radio("Modo de preenchimento", ["Manual", "Preencher em lote"], key="modo_ic")
        if modo_ic == "Manual":
            # ...
            pass
        else:
            # ...
            pass

    # ------------------------------------------------------------
    # MÉDIAS DA LIGA (comum a ambos os modos)
    # ------------------------------------------------------------
    st.divider()
    st.subheader("📊 Médias da Liga (para normalização)")
    col_liga1, col_liga2 = st.columns(2)
    with col_liga1:
        media_gols_casa = st.number_input("Média de gols (casa)", value=MEDIA_GOLS_CASA_LIGA)
        media_posse = st.slider("Posse média (%)", 0, 100, 50)
    with col_liga2:
        media_gols_fora = st.number_input("Média de gols (fora)", value=MEDIA_GOLS_FORA_LIGA)
        media_passes = st.slider("Passes certos médio (%)", 0, 100, 80)

    # Atualiza o dicionário de dados da liga
    dados_liga = {
        "media_gols_casa": media_gols_casa,
        "media_gols_fora": media_gols_fora,
        "posse_media": media_posse,
        "passes_certos_pct": media_passes,
        # Adicionamos os valores do próprio time para referência
        "gols_media": [ovrall_casa.get('gols_media', 0) or 0, ovrall_fora.get('gols_media', 0) or 0],
        "gols_sofridos_media": [ovrall_casa.get('gols_sofridos_media', 0) or 0, ovrall_fora.get('gols_sofridos_media', 0) or 0],
        "xg_media": [ovrall_casa.get('xg_media', 0) or 0, ovrall_fora.get('xg_media', 0) or 0],
        "xga_media": [ovrall_casa.get('xga_media', 0) or 0, ovrall_fora.get('xga_media', 0) or 0],
        "finalizacoes_alvo_media": [ovrall_casa.get('finalizacoes_alvo_media', 0) or 0, ovrall_fora.get('finalizacoes_alvo_media', 0) or 0],
        "finalizacoes_alvo_sofridas_media": [ovrall_casa.get('finalizacoes_alvo_sofridas_media', 0) or 0, ovrall_fora.get('finalizacoes_alvo_sofridas_media', 0) or 0],
        "chutes_media": [ovrall_casa.get('chutes_media', 0) or 0, ovrall_fora.get('chutes_media', 0) or 0],
        "desarmes_intercep_media": [ovrall_casa.get('desarmes_intercep_media', 0) or 0, ovrall_fora.get('desarmes_intercep_media', 0) or 0],
        "posse_media_lista": [ovrall_casa.get('posse_media', 0) or 0, ovrall_fora.get('posse_media', 0) or 0],
        "passes_certos_pct_lista": [ovrall_casa.get('passes_certos_pct', 0) or 0, ovrall_fora.get('passes_certos_pct', 0) or 0],
        "passes_chave_media": [ovrall_casa.get('passes_chave_media', 0) or 0, ovrall_fora.get('passes_chave_media', 0) or 0],
        "assistencias_media": [ovrall_casa.get('assistencias_media', 0) or 0, ovrall_fora.get('assistencias_media', 0) or 0],
        "conversao": [ovrall_casa.get('conversao', 0) or 0, ovrall_fora.get('conversao', 0) or 0],
        "clean_sheets_pct": [ovrall_casa.get('clean_sheets_pct', 0) or 0, ovrall_fora.get('clean_sheets_pct', 0) or 0],
        "desvio_pontos": [ovrall_casa.get('desvio_pontos', 0) or 0, ovrall_fora.get('desvio_pontos', 0) or 0],
        "desvio_gols_pro": [ovrall_casa.get('desvio_gols_pro', 0) or 0, ovrall_fora.get('desvio_gols_pro', 0) or 0],
        "desvio_gols_sofridos": [ovrall_casa.get('desvio_gols_sofridos', 0) or 0, ovrall_fora.get('desvio_gols_sofridos', 0) or 0],
        "pontos_pos_desvantagem_media": [ovrall_casa.get('pontos_pos_desvantagem_media', 0) or 0, ovrall_fora.get('pontos_pos_desvantagem_media', 0) or 0],
        "gols_ultimos_15min_media": [ovrall_casa.get('gols_ultimos_15min_media', 0) or 0, ovrall_fora.get('gols_ultimos_15min_media', 0) or 0],
        "pontos_apos_derrota_media": [ovrall_casa.get('pontos_apos_derrota_media', 0) or 0, ovrall_fora.get('pontos_apos_derrota_media', 0) or 0],
        "diff_aprov_casa_fora": [ovrall_casa.get('diff_aprov_casa_fora', 0) or 0, ovrall_fora.get('diff_aprov_casa_fora', 0) or 0],
        "aprov_viradas_favor": [ovrall_casa.get('aprov_viradas_favor', 0) or 0, ovrall_fora.get('aprov_viradas_favor', 0) or 0],
        "aprov_viradas_contra": [ovrall_casa.get('aprov_viradas_contra', 0) or 0, ovrall_fora.get('aprov_viradas_contra', 0) or 0],
    }

    # ------------------------------------------------------------
    # Prateleiras (com ajuste)
    # ------------------------------------------------------------
    prat_casa = obter_prateleira(pos_casa)
    prat_fora = obter_prateleira(pos_fora)
    prateleiras = {time_casa: prat_casa, time_fora: prat_fora}
    for jogo in jogos_casa + jogos_fora:
        if jogo['adversario'] not in prateleiras:
            prateleiras[jogo['adversario']] = "Media"

    with st.expander("Ajustar prateleiras dos adversários"):
        adversarios = sorted(set(j['adversario'] for j in jogos_casa + jogos_fora if j['adversario'] not in [time_casa, time_fora]))
        for adv in adversarios:
            prateleiras[adv] = st.selectbox(
                f"Prateleira de {adv}",
                ["Elite", "Alta", "Media", "Baixa", "Critica"],
                index=["Elite", "Alta", "Media", "Baixa", "Critica"].index(prateleiras[adv]),
                key=f"prat_{adv}"
            )

    # ------------------------------------------------------------
    # Cálculo
    # ------------------------------------------------------------
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
                                        media_gols_casa)
        gols_esp_fora = _gols_esperados(ovrall_fora.get('gols_media') or 1.5,
                                        ovrall_casa.get('gols_sofridos_media') or 1.0,
                                        media_gols_fora)
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

        # ------------------------------------------------------------
        # Exibição dos resultados com indicadores
        # ------------------------------------------------------------
        st.subheader("📊 Resultados")
        col1, col2, col3 = st.columns(3)
        seta1, selo1 = indicador(p1)
        setaX, seloX = indicador(pX)
        seta2, selo2 = indicador(p2)

        with col1:
            st.metric("Vitória Casa", f"{p1:.1%}")
            st.markdown(f"{seta1}")
            if selo1 == "selo-dourado":
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
            elif selo1 == "selo-verde":
                st.markdown('<div class="selo-verde">FAVORITO</div>', unsafe_allow_html=True)
        with col2:
            st.metric("Empate", f"{pX:.1%}")
            st.markdown(f"{setaX}")
        with col3:
            st.metric("Vitória Fora", f"{p2:.1%}")
            st.markdown(f"{seta2}")
            if selo2 == "selo-dourado":
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)

        st.divider()
        col4, col5 = st.columns(2)
        seta_o25, _ = indicador(over25)
        seta_btts, _ = indicador(btts)
        seta_ht, _ = indicador(gol_ht)
        seta_esc, _ = indicador(esc)

        with col4:
            st.metric("Over 2.5 gols", f"{over25:.1%}" if over25 else "N/D")
            st.markdown(seta_o25)
            if over25 and over25 >= 0.70:
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
        with col5:
            st.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")
            st.markdown(seta_btts)
            if btts and btts >= 0.70:
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)

        st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")
        st.markdown(seta_ht)
        st.metric("Over Escanteios", f"{esc:.1%}" if esc else "N/D")
        st.markdown(seta_esc)

        # Detalhamento completo
        with st.expander("🔍 Detalhamento dos Cálculos"):
            # IMA
            st.markdown("**IMA (Índice de Momento Atual)**")
            st.write(f"{time_casa}: {ima_casa:.1f}")
            st.write(f"{time_fora}: {ima_fora:.1f}")

            # OVRall
            st.markdown("**OVRall (Força Geral)**")
            # Recalculamos as dimensões para mostrar
            dims = {
                'Ataque': [('gols_media', False), ('xg_media', False), ('finalizacoes_alvo_media', False), ('conversao', False)],
                'Defesa': [('gols_sofridos_media', True), ('xga_media', True), ('finalizacoes_alvo_sofridas_media', True), ('desarmes_intercep_media', False)],
                'MeioCampo': [('posse_media', False), ('passes_certos_pct', False), ('passes_chave_media', False), ('assistencias_media', False), ('chutes_media', False)],
                'Consistencia': [('desvio_pontos', True), ('desvio_gols_pro', True), ('desvio_gols_sofridos', True), ('clean_sheets_pct', False)],
                'Resiliencia': [('pontos_pos_desvantagem_media', False), ('gols_ultimos_15min_media', False), ('pontos_apos_derrota_media', False), ('diff_aprov_casa_fora', True), ('aprov_viradas_favor', False), ('aprov_viradas_contra', True)],
            }
            for nome, dim in [("Casa", ovrall_casa), ("Fora", ovrall_fora)]:
                st.markdown(f"**{nome}**")
                for dimensao, indicadores in dims.items():
                    notas = []
                    for ind, menor in indicadores:
                        val = dim.get(ind)
                        if val is not None:
                            # Percentil aproximado (comparando com o outro time e médias da liga)
                            ref = dados_liga.get(ind, [0])
                            if isinstance(ref, list):
                                nota = _percentil(val, ref, menor)
                            else:
                                nota = val
                            notas.append(nota)
                    if notas:
                        nota_dimensao = sum(notas) / len(notas)
                        st.write(f"{dimensao}: {nota_dimensao:.1f}")

            # IC
            st.markdown("**IC (Índice de Contexto)**")
            st.write(f"Casa: {ic_val_casa:.1f}, Fora: {ic_val_fora:.1f}")

            # MPV
            st.markdown("**MPV (MyPredict Value)**")
            st.write(f"Casa: {mpv_casa:.1f}, Fora: {mpv_fora:.1f}")
