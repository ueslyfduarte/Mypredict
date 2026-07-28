# manual_app.py — MyPredict 2.0 (entrada única via prompt)
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

def show():
    st.title("MyPredict 2.0 – Modo Manual")
    st.markdown("### 📥 Cole aqui a resposta completa da IA")

    # Inicializar estados na sessão
    if 'dados_processados' not in st.session_state:
        st.session_state.dados_processados = False
    if 'jogos_casa' not in st.session_state:
        st.session_state.jogos_casa = []
        st.session_state.jogos_fora = []
        st.session_state.ovrall_casa = {}
        st.session_state.ovrall_fora = {}
        st.session_state.ic_casa = {}
        st.session_state.ic_fora = {}
        st.session_state.time_casa = ""
        st.session_state.time_fora = ""
        st.session_state.pos_casa = 1
        st.session_state.pos_fora = 2
        st.session_state.prateleiras = {}

    texto_colado = st.text_area(
        "Cole a resposta inteira da IA aqui (posições, jogos, métricas OVRall e IC)",
        height=300,
        key="texto_ia"
    )

    if st.button("📥 Processar dados"):
        # Parse do texto
        linhas = texto_colado.strip().split('\n')
        secao = None
        jogos_temp_casa = []
        jogos_temp_fora = []
        ovrall_casa = {}
        ovrall_fora = {}
        ic_casa = {}
        ic_fora = {}
        pos_casa = 1
        pos_fora = 2
        time_casa = ""
        time_fora = ""
        prateleiras_extra = {}

        for linha in linhas:
            linha = linha.strip()
            if not linha:
                continue

            # Detecta seções
            if linha.startswith("1. Posições:"):
                secao = "posicoes"
                continue
            elif linha.startswith("2. Últimos 10 jogos do time da casa"):
                secao = "jogos_casa"
                continue
            elif linha.startswith("3. Últimos 10 jogos do time da fora"):
                secao = "jogos_fora"
                continue
            elif linha.startswith("4. Métricas OVRall do time da casa"):
                secao = "ovrall_casa"
                continue
            elif linha.startswith("5. Métricas OVRall do time da fora"):
                secao = "ovrall_fora"
                continue
            elif linha.startswith("6. Métricas IC do time da casa"):
                secao = "ic_casa"
                continue
            elif linha.startswith("7. Métricas IC do time da fora"):
                secao = "ic_fora"
                continue
            elif linha.startswith("8.") or linha.startswith("Adversário"):
                secao = "prateleiras"
                continue

            if secao == "posicoes":
                if linha.startswith("Casa:"):
                    try:
                        pos_casa = int(linha.split(":")[1].strip())
                    except:
                        pass
                elif linha.startswith("Fora:"):
                    try:
                        pos_fora = int(linha.split(":")[1].strip())
                    except:
                        pass
            elif secao == "jogos_casa":
                partes = [p.strip() for p in linha.split(',')]
                if len(partes) >= 3:
                    res = partes[0]
                    adv = partes[1]
                    mand = partes[2].upper() == 'S'
                    jogos_temp_casa.append({"resultado": res, "adversario": adv, "mandante": mand})
            elif secao == "jogos_fora":
                partes = [p.strip() for p in linha.split(',')]
                if len(partes) >= 3:
                    res = partes[0]
                    adv = partes[1]
                    mand = partes[2].upper() == 'S'
                    jogos_temp_fora.append({"resultado": res, "adversario": adv, "mandante": mand})
            elif secao == "ovrall_casa":
                partes = [x.strip() for x in linha.split(',')]
                if len(partes) == len(METRICAS_OVRALL):
                    for i, key in enumerate(METRICAS_OVRALL):
                        ovrall_casa[key] = para_float(partes[i])
            elif secao == "ovrall_fora":
                partes = [x.strip() for x in linha.split(',')]
                if len(partes) == len(METRICAS_OVRALL):
                    for i, key in enumerate(METRICAS_OVRALL):
                        ovrall_fora[key] = para_float(partes[i])
            elif secao == "ic_casa":
                partes = [x.strip() for x in linha.split(',')]
                if len(partes) == len(METRICAS_IC):
                    for i, key in enumerate(METRICAS_IC):
                        ic_casa[key] = para_float(partes[i])
            elif secao == "ic_fora":
                partes = [x.strip() for x in linha.split(',')]
                if len(partes) == len(METRICAS_IC):
                    for i, key in enumerate(METRICAS_IC):
                        ic_fora[key] = para_float(partes[i])
            elif secao == "prateleiras":
                if ':' in linha:
                    adv, prat = linha.split(':', 1)
                    prateleiras_extra[adv.strip()] = prat.strip()

        # Salvar no session_state
        st.session_state.jogos_casa = jogos_temp_casa
        st.session_state.jogos_fora = jogos_temp_fora
        st.session_state.ovrall_casa = ovrall_casa
        st.session_state.ovrall_fora = ovrall_fora
        st.session_state.ic_casa = ic_casa
        st.session_state.ic_fora = ic_fora
        st.session_state.pos_casa = pos_casa
        st.session_state.pos_fora = pos_fora
        st.session_state.prateleiras_extra = prateleiras_extra
        st.session_state.dados_processados = True
        st.success("Dados processados com sucesso!")
        st.rerun()

    # Se já processou, mostra os dados e permite ajustes
    if st.session_state.dados_processados:
        st.success("Dados carregados! Ajuste as prateleiras se necessário e clique em Calcular.")

        # Times
        col1, col2 = st.columns(2)
        with col1:
            time_casa = st.text_input("Time da Casa", value=st.session_state.get("time_casa", "Flamengo"))
        with col2:
            time_fora = st.text_input("Time da Fora", value=st.session_state.get("time_fora", "Palmeiras"))

        # Prateleiras
        pos_casa = st.session_state.pos_casa
        pos_fora = st.session_state.pos_fora
        prat_casa = obter_prateleira(pos_casa)
        prat_fora = obter_prateleira(pos_fora)
        st.write(f"Casa: **{prat_casa}** – Fora: **{prat_fora}**")
        prateleiras = {time_casa: prat_casa, time_fora: prat_fora}

        # Adicionar prateleiras dos adversários (padrão Média)
        for jogo in st.session_state.jogos_casa + st.session_state.jogos_fora:
            if jogo['adversario'] not in prateleiras:
                prateleiras[jogo['adversario']] = "Media"

        # Aplicar as prateleiras extras vindas do prompt
        for adv, prat in st.session_state.prateleiras_extra.items():
            if adv in prateleiras:
                prateleiras[adv] = prat

        # Ajustar prateleiras
        with st.expander("Ajustar prateleiras dos adversários"):
            adversarios = sorted(set(j['adversario'] for j in st.session_state.jogos_casa + st.session_state.jogos_fora if j['adversario'] not in [time_casa, time_fora]))
            for adv in adversarios:
                prateleiras[adv] = st.selectbox(
                    f"Prateleira de {adv}",
                    ["Elite", "Alta", "Media", "Baixa", "Critica"],
                    index=["Elite", "Alta", "Media", "Baixa", "Critica"].index(prateleiras[adv]),
                    key=f"prat_{adv}"
                )

        st.divider()
        if st.button("Calcular MyPredict Manual"):
            jogos_casa = st.session_state.jogos_casa
            jogos_fora = st.session_state.jogos_fora
            ovrall_casa = st.session_state.ovrall_casa
            ovrall_fora = st.session_state.ovrall_fora
            ic_casa = st.session_state.ic_casa
            ic_fora = st.session_state.ic_fora

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
