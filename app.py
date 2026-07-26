"""
MyPredict 2.0 - Aplicativo Completo com Menu Lateral
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import (
    calcular_IMA,
    calcular_ATA,
    calcular_DEF,
    calcular_MEI,
    calcular_FOR,
    calcular_CONS,
    calcular_RES,
    calcular_OVRall,
    inicializar_MPV,
    atualizar_MPV,
    probabilidades_1x2,
    calcular_edge,
    determinar_selo
)

# ============================================================
# CONFIGURAÇÃO VISUAL
# ============================================================
st.set_page_config(page_title="MyPredict 2.0", page_icon="⚽", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #111111; color: #FFFFFF; }
    h1, h2, h3 { color: #DAA520 !important; }
    .stButton>button {
        background-color: #DAA520; color: #000; border: none;
        font-weight: bold; padding: 0.5rem 2rem; border-radius: 8px;
    }
    .positivo { color: #00C853; font-weight: bold; }
    .negativo { color: #FF1744; font-weight: bold; }
    .mpv-destaque { font-size: 3rem; font-weight: bold; color: #DAA520; text-align: center; }
    .metrica-row:nth-child(odd) { background-color: #1E1E1E; }
    .metrica-row:nth-child(even) { background-color: #2A2A2A; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CARREGAR DADOS
# ============================================================
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("data/meus_jogos.csv", parse_dates=["data"])
        jogos = df.to_dict(orient="records")
        return jogos
    except FileNotFoundError:
        st.error("Arquivo 'data/meus_jogos.csv' não encontrado.")
        return []

jogos = carregar_dados()
if not jogos:
    st.stop()

times_disponiveis = sorted(list(set(j['time'] for j in jogos)))

# ============================================================
# MENU LATERAL
# ============================================================
st.sidebar.markdown("<h2 style='color: #DAA520;'>⚽ MyPredict 2.0</h2>", unsafe_allow_html=True)
opcao = st.sidebar.radio("Navegação", ["Análise de Jogo", "Backtest"])

# ============================================================
# PÁGINA 1: ANÁLISE DE JOGO
# ============================================================
if opcao == "Análise de Jogo":
    st.markdown("<h1 style='text-align: center;'>⚽ MyPredict 2.0</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #CCCCCC;'>Análise Preditiva com Método Próprio</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #DAA520; font-style: italic;'>\"O futebol é a coisa mais importante entre as coisas menos importantes.\" – Arrigo Sacchi</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        time_casa = st.selectbox("🏠 Time Mandante", times_disponiveis, index=0)
    with col2:
        st.markdown("<h2 style='text-align: center; color: #DAA520;'>VS</h2>", unsafe_allow_html=True)
    with col3:
        time_fora = st.selectbox("✈️ Time Visitante", times_disponiveis, index=min(1, len(times_disponiveis)-1))

    ultima_data = max(j['data'] for j in jogos)
    data_ref = st.date_input("📅 Data de referência", value=ultima_data)

    if st.button("⚡ Gerar MyPredict"):
        data_ref_dt = datetime.combine(data_ref, datetime.min.time())

        # ---------- FUNÇÃO MPV HISTÓRICO ----------
        def calcular_MPV_final(time, jogos, data_ref_dt):
            jogos_time = sorted([j for j in jogos if j['time'] == time and j['data'] <= data_ref_dt], key=lambda x: x['data'])
            if not jogos_time:
                return inicializar_MPV(50.0)
            ovrall = calcular_OVRall([calcular_ATA(jogos, time, data_ref_dt),
                                      calcular_DEF(jogos, time, data_ref_dt),
                                      calcular_MEI(jogos, time, data_ref_dt),
                                      calcular_FOR(jogos, time, data_ref_dt),
                                      calcular_CONS(jogos, time, data_ref_dt),
                                      calcular_RES(jogos, time, data_ref_dt)])
            mpv = inicializar_MPV(ovrall)
            for jogo in jogos_time:
                ima_jogo, _ = calcular_IMA(jogos, time, jogo['data'], mando_proximo=jogo['mando'])
                ovrall_adv = calcular_OVRall([calcular_ATA(jogos, jogo['adv'], jogo['data']),
                                              calcular_DEF(jogos, jogo['adv'], jogo['data']),
                                              calcular_MEI(jogos, jogo['adv'], jogo['data']),
                                              calcular_FOR(jogos, jogo['adv'], jogo['data']),
                                              calcular_CONS(jogos, jogo['adv'], jogo['data']),
                                              calcular_RES(jogos, jogo['adv'], jogo['data'])])
                mpv_adv = inicializar_MPV(ovrall_adv)
                mpv = atualizar_MPV(mpv, mpv_adv, jogo['mando'], jogo['resultado'], ima_jogo)
            return mpv

        # ---------- CÁLCULOS ----------
        ima_casa, _ = calcular_IMA(jogos, time_casa, data_ref_dt, mando_proximo='casa')
        ima_fora, _ = calcular_IMA(jogos, time_fora, data_ref_dt, mando_proximo='fora')

        ata_casa = calcular_ATA(jogos, time_casa, data_ref_dt)
        def_casa = calcular_DEF(jogos, time_casa, data_ref_dt)
        mei_casa = calcular_MEI(jogos, time_casa, data_ref_dt)
        for_casa = calcular_FOR(jogos, time_casa, data_ref_dt)
        cons_casa = calcular_CONS(jogos, time_casa, data_ref_dt)
        res_casa = calcular_RES(jogos, time_casa, data_ref_dt)
        ovrall_casa = calcular_OVRall([ata_casa, def_casa, mei_casa, for_casa, cons_casa, res_casa])

        ata_fora = calcular_ATA(jogos, time_fora, data_ref_dt)
        def_fora = calcular_DEF(jogos, time_fora, data_ref_dt)
        mei_fora = calcular_MEI(jogos, time_fora, data_ref_dt)
        for_fora = calcular_FOR(jogos, time_fora, data_ref_dt)
        cons_fora = calcular_CONS(jogos, time_fora, data_ref_dt)
        res_fora = calcular_RES(jogos, time_fora, data_ref_dt)
        ovrall_fora = calcular_OVRall([ata_fora, def_fora, mei_fora, for_fora, cons_fora, res_fora])

        mpv_casa_raw = calcular_MPV_final(time_casa, jogos, data_ref_dt)
        mpv_fora_raw = calcular_MPV_final(time_fora, jogos, data_ref_dt)
        prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

        odd_casa, odd_empate, odd_fora = 2.0, 3.0, 3.0
        edge_casa = calcular_edge(prob_casa, odd_casa)
        edge_empate = calcular_edge(prob_empate, odd_empate)
        edge_fora = calcular_edge(prob_fora, odd_fora)

        dif_mpv = abs(mpv_casa_raw + 75 - mpv_fora_raw)
        selo_casa = determinar_selo(edge_casa, dif_mpv, 10)
        selo_empate = determinar_selo(edge_empate, dif_mpv, 10)
        selo_fora = determinar_selo(edge_fora, dif_mpv, 10)

        mpv_casa = (mpv_casa_raw - 1000) / 10
        mpv_fora = (mpv_fora_raw - 1000) / 10

        # ---------- EXIBIÇÃO ----------
        st.markdown("---")
        st.markdown("### 🏆 Contexto na Liga")
        times_dict = {t: {'P': 0, 'J': 0} for t in times_disponiveis}
        for j in jogos:
            t = j['time']
            if j['resultado'] == 'V':
                times_dict[t]['P'] += 3
            elif j['resultado'] == 'E':
                times_dict[t]['P'] += 1
            times_dict[t]['J'] += 1
        tabela = [[t, s['J'], s['P']] for t, s in times_dict.items()]
        df_tab = pd.DataFrame(tabela, columns=["Time", "J", "Pts"]).sort_values("Pts", ascending=False)
        st.dataframe(df_tab, use_container_width=True)

        st.markdown("### 📈 Momento Atual (IMA)")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{time_casa}", f"{ima_casa:.1f}")
        with col2:
            st.metric(f"{time_fora}", f"{ima_fora:.1f}")

        st.markdown("### 🔍 Métricas Detalhadas")
        nomes = ["ATA", "DEF", "MEI", "FOR", "CONS", "RES", "OVRall"]
        v_casa = [ata_casa, def_casa, mei_casa, for_casa, cons_casa, res_casa, ovrall_casa]
        v_fora = [ata_fora, def_fora, mei_fora, for_fora, cons_fora, res_fora, ovrall_fora]
        for nome, vc, vf in zip(nomes, v_casa, v_fora):
            st.write(f"**{nome}**")
            col1, col2 = st.columns(2)
            with col1:
                st.progress(int(vc))
                st.write(f"{time_casa}: {vc:.1f}")
            with col2:
                st.progress(int(vf))
                st.write(f"{time_fora}: {vf:.1f}")

        st.markdown("### 💎 MyPredict Value (MPV)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='mpv-destaque'>{mpv_casa:.1f}</div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='mpv-destaque'>{mpv_fora:.1f}</div>", unsafe_allow_html=True)

        st.markdown("### 📝 Análise do Confronto")
        favorito = time_casa if prob_casa > prob_fora else time_fora
        st.write(f"Favorito: **{favorito}** ({max(prob_casa, prob_fora):.1%})")

        st.markdown("### 📊 Probabilidades e Valor")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Casa", f"{prob_casa:.1%}")
            st.write(f"Edge: {edge_casa:+.1%}")
            st.write(f"Selo: {selo_casa}")
        with col2:
            st.metric("Empate", f"{prob_empate:.1%}")
            st.write(f"Edge: {edge_empate:+.1%}")
            st.write(f"Selo: {selo_empate}")
        with col3:
            st.metric("Fora", f"{prob_fora:.1%}")
            st.write(f"Edge: {edge_fora:+.1%}")
            st.write(f"Selo: {selo_fora}")

# ============================================================
# PÁGINA 2: BACKTEST
# ============================================================
elif opcao == "Backtest":
    st.markdown("<h1 style='text-align: center;'>📈 Backtest MyPredict 2.0</h1>", unsafe_allow_html=True)

    if st.button("Executar Backtest"):
        jogos_ord = sorted(jogos, key=lambda x: x['data'])
        partidas = {}
        for j in jogos_ord:
            chave = (j['data'], j['time'], j['adv'])
            if chave not in partidas:
                partidas[chave] = {'casa': None, 'fora': None}
            if j['mando'] == 'casa':
                partidas[chave]['casa'] = j
            else:
                partidas[chave]['fora'] = j

        log = []
        for chave, jogo_dict in sorted(partidas.items(), key=lambda x: x[0][0]):
            data_jogo = chave[0]
            time_casa = chave[1]
            time_fora = chave[2]
            jogo_casa = jogo_dict['casa']
            data_ref = pd.to_datetime(data_jogo)
            jogos_passados = [j for j in jogos if j['data'] < data_ref]

            ovrall_casa = calcular_OVRall([calcular_ATA(jogos_passados, time_casa, data_ref),
                                           calcular_DEF(jogos_passados, time_casa, data_ref),
                                           calcular_MEI(jogos_passados, time_casa, data_ref),
                                           calcular_FOR(jogos_passados, time_casa, data_ref),
                                           calcular_CONS(jogos_passados, time_casa, data_ref),
                                           calcular_RES(jogos_passados, time_casa, data_ref)])
            ovrall_fora = calcular_OVRall([calcular_ATA(jogos_passados, time_fora, data_ref),
                                           calcular_DEF(jogos_passados, time_fora, data_ref),
                                           calcular_MEI(jogos_passados, time_fora, data_ref),
                                           calcular_FOR(jogos_passados, time_fora, data_ref),
                                           calcular_CONS(jogos_passados, time_fora, data_ref),
                                           calcular_RES(jogos_passados, time_fora, data_ref)])
            mpv_casa = inicializar_MPV(ovrall_casa)
            mpv_fora = inicializar_MPV(ovrall_fora)
            prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa, mpv_fora)
            resultado_real = jogo_casa['resultado']

            log.append({
                'Data': data_jogo.strftime('%Y-%m-%d') if hasattr(data_jogo, 'strftime') else str(data_jogo),
                'Casa': time_casa,
                'Fora': time_fora,
                'Prob. Casa': f"{prob_casa:.1%}",
                'Prob. Empate': f"{prob_empate:.1%}",
                'Prob. Fora': f"{prob_fora:.1%}",
                'Resultado': resultado_real
            })

        df_log = pd.DataFrame(log)
        st.dataframe(df_log, use_container_width=True)
        st.success(f"Backtest concluído para {len(log)} partidas.")
