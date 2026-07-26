"""
MyPredict 2.0 - Aplicativo Completo com Dados Reais
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial

# Configuração visual
st.set_page_config(page_title="MyPredict 2.0", page_icon="⚽", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #111; color: #fff; }
    h1, h2, h3 { color: #DAA520; }
    .stButton>button { background:#DAA520; color:#000; font-weight:bold; border-radius:8px; }
    .positivo { color:#00C853; font-weight:bold; }
    .negativo { color:#FF1744; font-weight:bold; }
    .mpv-destaque { font-size:3rem; color:#DAA520; text-align:center; }
</style>
""", unsafe_allow_html=True)

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

# Atribuir prateleiras com base nas odds (menor odd = melhor)
odds_por_time = {}
for j in jogos:
    if j['time'] not in odds_por_time:
        try:
            odd = float(j.get('B365H', 3.0)) if j['mando'] == 'casa' else float(j.get('B365A', 3.0))
            odds_por_time[j['time']] = odd
        except:
            odds_por_time[j['time']] = 3.0
times_ordenados = sorted(odds_por_time, key=lambda t: odds_por_time[t])
prateleiras = {}
n = len(times_ordenados)
for i, t in enumerate(times_ordenados):
    if i < n*0.15: prateleiras[t] = 1
    elif i < n*0.35: prateleiras[t] = 2
    elif i < n*0.65: prateleiras[t] = 3
    elif i < n*0.85: prateleiras[t] = 4
    else: prateleiras[t] = 5
for j in jogos:
    j['prat_time'] = prateleiras.get(j['time'], 3)
    j['prat_adv'] = prateleiras.get(j['adv'], 3)

times_disponiveis = sorted(set(j['time'] for j in jogos))

# Funções auxiliares de mercados
def prob_over(media_gols, limite):
    prob_under = sum((media_gols**k) * exp(-media_gols) / factorial(k) for k in range(int(limite)+1))
    return 1 - prob_under

def prob_btts(ata_casa, def_fora, ata_fora, def_casa):
    media_casa = (ata_casa/50) * (1 - def_fora/100)
    media_fora = (ata_fora/50) * (1 - def_casa/100)
    prob_c = 1 - exp(-media_casa)
    prob_f = 1 - exp(-media_fora)
    return prob_c * prob_f

# Menu
st.sidebar.markdown("<h2 style='color:#DAA520;'>⚽ MyPredict 2.0</h2>", unsafe_allow_html=True)
opcao = st.sidebar.radio("Modo", ["Análise de Jogo", "Backtest"])

if opcao == "Análise de Jogo":
    st.markdown("<h1 style='text-align:center;'>⚽ MyPredict 2.0</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#DAA520;'>\"O futebol é a coisa mais importante entre as menos importantes.\" – Arrigo Sacchi</p>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2, col3 = st.columns([2,1,2])
    with col1:
        time_casa = st.selectbox("🏠 Mandante", times_disponiveis)
    with col2:
        st.markdown("<h2 style='text-align:center; color:#DAA520;'>VS</h2>", unsafe_allow_html=True)
    with col3:
        time_fora = st.selectbox("✈️ Visitante", times_disponiveis, index=1)
    data_ref = st.date_input("📅 Data de referência", value=max(j['data'] for j in jogos))

    if st.button("⚡ Gerar MyPredict"):
        data_ref_dt = datetime.combine(data_ref, datetime.min.time())

        def calcular_MPV_final(time):
            jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref_dt]
            if not jogos_time:
                return inicializar_MPV(50.0)
            ovrall = calcular_OVRall([calcular_ATA(jogos, time, data_ref_dt),
                                      calcular_DEF(jogos, time, data_ref_dt),
                                      calcular_MEI(jogos, time, data_ref_dt),
                                      calcular_FOR(jogos, time, data_ref_dt),
                                      calcular_CONS(jogos, time, data_ref_dt),
                                      calcular_RES(jogos, time, data_ref_dt)])
            mpv = inicializar_MPV(ovrall)
            for jogo in sorted(jogos_time, key=lambda x: x['data']):
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

        ima_casa, _ = calcular_IMA(jogos, time_casa, data_ref_dt, 'casa')
        ima_fora, _ = calcular_IMA(jogos, time_fora, data_ref_dt, 'fora')
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

        mpv_casa_raw = calcular_MPV_final(time_casa)
        mpv_fora_raw = calcular_MPV_final(time_fora)
        prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

        # Odds reais (último jogo entre eles ou estimativa)
        odds_jogos = [j for j in jogos if j['time'] == time_casa and j['adv'] == time_fora]
        odd_casa = float(odds_jogos[-1].get('B365H', 2.0)) if odds_jogos else 2.0
        odd_empate = float(odds_jogos[-1].get('B365D', 3.0)) if odds_jogos else 3.0
        odd_fora = float(odds_jogos[-1].get('B365A', 3.0)) if odds_jogos else 3.0

        edge_casa = calcular_edge(prob_casa, odd_casa)
        edge_empate = calcular_edge(prob_empate, odd_empate)
        edge_fora = calcular_edge(prob_fora, odd_fora)
        dif_mpv = abs(mpv_casa_raw + 75 - mpv_fora_raw)
        selo_casa = determinar_selo(edge_casa, dif_mpv, 10)
        selo_empate = determinar_selo(edge_empate, dif_mpv, 10)
        selo_fora = determinar_selo(edge_fora, dif_mpv, 10)

        mpv_casa = (mpv_casa_raw - 1000) / 10
        mpv_fora = (mpv_fora_raw - 1000) / 10

        st.markdown("---")
        col1, col2, col3 = st.columns([2,1,2])
        with col1:
            st.markdown(f"### {time_casa}")
            st.metric("MPV", f"{mpv_casa:.1f}")
            st.metric("IMA", f"{ima_casa:.1f}")
            st.metric("OVRall", f"{ovrall_casa:.1f}")
        with col2:
            st.markdown("<h2 style='text-align:center; color:#DAA520;'>VS</h2>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"### {time_fora}")
            st.metric("MPV", f"{mpv_fora:.1f}")
            st.metric("IMA", f"{ima_fora:.1f}")
            st.metric("OVRall", f"{ovrall_fora:.1f}")

        st.markdown("---")
        st.subheader("📊 Probabilidades 1X2")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Casa", f"{prob_casa:.1%}")
            st.metric("Edge", f"{edge_casa:+.1%}")
            st.write(f"Selo: {selo_casa}")
        with col2:
            st.metric("Empate", f"{prob_empate:.1%}")
            st.metric("Edge", f"{edge_empate:+.1%}")
            st.write(f"Selo: {selo_empate}")
        with col3:
            st.metric("Fora", f"{prob_fora:.1%}")
            st.metric("Edge", f"{edge_fora:+.1%}")
            st.write(f"Selo: {selo_fora}")

        st.markdown("---")
        st.subheader("🎯 Mercados Adicionais")
        def media_gols(time, tipo):
            jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref_dt][-10:]
            if not jogos_time: return 1.0
            return sum(j['gols'] if tipo == 'marcados' else j['gols_sofridos'] for j in jogos_time)/len(jogos_time)
        gols_casa = media_gols(time_casa, 'marcados')
        gols_fora = media_gols(time_fora, 'marcados')
        sofridos_casa = media_gols(time_casa, 'sofridos')
        sofridos_fora = media_gols(time_fora, 'sofridos')
        media_total = (gols_casa + sofridos_fora)/2 + (gols_fora + sofridos_casa)/2
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Over 1.5 gols", f"{prob_over(media_total, 1.5):.1%}")
        col2.metric("Over 2.5 gols", f"{prob_over(media_total, 2.5):.1%}")
        col3.metric("Ambas Marcam", f"{prob_btts(ata_casa, def_fora, ata_fora, def_casa):.1%}")
        esc_casa = for_casa/5
        esc_fora = for_fora/5
        total_esc = esc_casa + esc_fora
        col4.metric("Over 9.5 esc.", f"{prob_over(total_esc, 8.5):.1%}")

elif opcao == "Backtest":
    st.markdown("<h1 style='text-align:center;'>📈 Backtest MyPredict 2.0</h1>", unsafe_allow_html=True)
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

            ata_casa = calcular_ATA(jogos_passados, time_casa, data_ref)
            def_casa = calcular_DEF(jogos_passados, time_casa, data_ref)
            ata_fora = calcular_ATA(jogos_passados, time_fora, data_ref)
            def_fora = calcular_DEF(jogos_passados, time_fora, data_ref)

            def media_gols(time, tipo):
                jogos_time = [j for j in jogos_passados if j['time'] == time][-10:]
                if not jogos_time: return 1.0
                return sum(j['gols'] if tipo == 'marcados' else j['gols_sofridos'] for j in jogos_time)/len(jogos_time)

            gols_casa = media_gols(time_casa, 'marcados')
            sofridos_fora = media_gols(time_fora, 'sofridos')
            gols_fora = media_gols(time_fora, 'marcados')
            sofridos_casa = media_gols(time_casa, 'sofridos')
            media_total = (gols_casa + sofridos_fora)/2 + (gols_fora + sofridos_casa)/2

            prob_over25 = prob_over(media_total, 2.5)
            prob_bt = prob_btts(ata_casa, def_fora, ata_fora, def_casa)

            total_gols = jogo_casa['gols'] + jogo_casa['gols_sofridos']
            over25_real = total_gols > 2.5
            btts_real = (jogo_casa['gols'] > 0 and jogo_casa['gols_sofridos'] > 0)

            log.append({
                'Data': data_jogo.strftime('%Y-%m-%d') if hasattr(data_jogo,'strftime') else str(data_jogo),
                'Casa': time_casa,
                'Fora': time_fora,
                'Prob Over 2.5': f"{prob_over25:.1%}",
                'Over 2.5 Real': 'Sim' if over25_real else 'Não',
                'Prob BTTS': f"{prob_bt:.1%}",
                'BTTS Real': 'Sim' if btts_real else 'Não'
            })

        df_log = pd.DataFrame(log)
        st.dataframe(df_log, use_container_width=True)
        st.success(f"Backtest concluído para {len(log)} partidas.")
