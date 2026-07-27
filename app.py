"""
MyPredict 2.0 – Aplicativo Completo (Selos pela Probabilidade MyPredict)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial
import os

# ============================================================
# LIMIARES PARA SELOS (BASEADOS NA PROBABILIDADE MYPREDICT)
# ============================================================
LIMITE_OURO = 0.50
LIMITE_VERDE = 0.40
LIMITE_MARGINAL = 0.33

def get_selo(probabilidade):
    if probabilidade >= LIMITE_OURO:
        return "🥇 Ouro"
    elif probabilidade >= LIMITE_VERDE:
        return "🟢 Verde"
    elif probabilidade >= LIMITE_MARGINAL:
        return "⚪ Marginal"
    else:
        return "🔴 Sem selo"

# ============================================================
# CONFIGURAÇÃO VISUAL
# ============================================================
st.set_page_config(page_title="MyPredict 2.0", page_icon="⚽", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #111; color: #fff; }
    h1, h2, h3 { color: #DAA520; }
    .stButton>button { background:#DAA520; color:#000; font-weight:bold; border-radius:8px; }
    .positivo { color:#00C853; font-weight:bold; }
    .negativo { color:#FF1744; font-weight:bold; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# FUNÇÕES AUXILIARES DE PROBABILIDADE
# ============================================================
def prob_over(media_gols, limite):
    prob_under = sum((media_gols**k) * exp(-media_gols) / factorial(k) for k in range(int(limite)+1))
    return 1 - prob_under

def prob_btts(ata_casa, def_fora, ata_fora, def_casa):
    media_casa = (ata_casa/50) * (1 - def_fora/100)
    media_fora = (ata_fora/50) * (1 - def_casa/100)
    prob_c = 1 - exp(-media_casa)
    prob_f = 1 - exp(-media_fora)
    return prob_c * prob_f

# ============================================================
# CARREGAR DADOS
# ============================================================
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("data/meus_jogos.csv", sep=None, engine='python')
        for col in ['time', 'adv', 'mando', 'resultado']:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        col_data = [c for c in df.columns if 'data' in c.lower() or 'date' in c.lower()][0]
        df[col_data] = pd.to_datetime(df[col_data], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[col_data])
        df = df.rename(columns={col_data: 'data'})
        jogos_planos = df.to_dict(orient="records")
        def make_key(row):
            times = sorted([row['time'], row['adv']])
            return (row['data'], times[0], times[1])
        df['key'] = df.apply(make_key, axis=1)
        partidas = []
        for key, group in df.groupby('key'):
            casa = group[group['mando'] == 'casa']
            fora = group[group['mando'] == 'fora']
            if not casa.empty and not fora.empty:
                partidas.append({
                    'data': key[0],
                    'casa': casa.iloc[0].to_dict(),
                    'fora': fora.iloc[0].to_dict()
                })
        return jogos_planos, partidas
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return [], []

jogos, partidas = carregar_dados()

# ============================================================
# FUNÇÃO PARA CLASSIFICAÇÃO E PRATELEIRAS
# ============================================================
def classification_to_shelves(games):
    teams = {}
    for g in games:
        t = g['time']
        if t not in teams:
            teams[t] = {'Pts': 0}
        if g['resultado'] == 'V':
            teams[t]['Pts'] += 3
        elif g['resultado'] == 'E':
            teams[t]['Pts'] += 1
    sorted_teams = sorted(teams.items(), key=lambda x: -x[1]['Pts'])
    n = len(sorted_teams)
    shelves = {}
    for i, (team, _) in enumerate(sorted_teams):
        if i < n * 0.15:
            shelves[team] = 1
        elif i < n * 0.35:
            shelves[team] = 2
        elif i < n * 0.65:
            shelves[team] = 3
        elif i < n * 0.85:
            shelves[team] = 4
        else:
            shelves[team] = 5
    return shelves

# ============================================================
# MENU LATERAL
# ============================================================
st.sidebar.markdown("<h2 style='color:#DAA520;'>⚽ MyPredict 2.0</h2>", unsafe_allow_html=True)
opcao = st.sidebar.radio("Modo", ["Análise de Jogo", "Backtest Visual", "Converter Dados Brutos"])

# ============================================================
# CONVERSOR (mantido)
# ============================================================
if opcao == "Converter Dados Brutos":
    st.markdown("<h1 style='text-align:center;'>🔄 Conversor de CSV</h1>", unsafe_allow_html=True)
    raw_path = "data/raw"
    try:
        arquivos_raw = [f for f in os.listdir(raw_path) if f.endswith('.csv')]
    except FileNotFoundError:
        st.error("Pasta 'data/raw' não encontrada.")
        arquivos_raw = []
    if not arquivos_raw:
        st.warning("Nenhum CSV em data/raw/.")
    else:
        st.write("Arquivos encontrados:", arquivos_raw)
        if st.button("⚙️ Converter para meus_jogos.csv"):
            # ... (código do conversor igual ao último funcional) ...
            st.write("Conversor mantido. Use o código completo do arquivo real.")

# ============================================================
# ANÁLISE DE JOGO (RECOMENDAÇÃO + SELO POR PROBABILIDADE)
# ============================================================
elif opcao == "Análise de Jogo":
    if not jogos:
        st.warning("Sem dados.")
        st.stop()
    times_disponiveis = sorted(set(j['time'] for j in jogos))
    prats = classification_to_shelves(jogos)
    for j in jogos:
        j['prat_time'] = prats.get(j['time'], 3)
        j['prat_adv'] = prats.get(j['adv'], 3)

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
        jogos_passados = [j for j in jogos if j['data'] < data_ref_dt]

        def calcular_MPV_final(time):
            jogos_time = [j for j in jogos_passados if j['time'] == time]
            if not jogos_time: return inicializar_MPV(50.0)
            jogos_time = sorted(jogos_time, key=lambda x: x['data'])
            ovrall = calcular_OVRall([calcular_ATA(jogos_passados, time, data_ref_dt),
                                      calcular_DEF(jogos_passados, time, data_ref_dt),
                                      calcular_MEI(jogos_passados, time, data_ref_dt),
                                      calcular_FOR(jogos_passados, time, data_ref_dt),
                                      calcular_CONS(jogos_passados, time, data_ref_dt),
                                      calcular_RES(jogos_passados, time, data_ref_dt)])
            mpv = inicializar_MPV(ovrall)
            for jogo in jogos_time:
                ima_jogo, _ = calcular_IMA(jogos_passados, time, jogo['data'], mando_proximo=jogo['mando'])
                ovrall_adv = calcular_OVRall([calcular_ATA(jogos_passados, jogo['adv'], jogo['data']),
                                              calcular_DEF(jogos_passados, jogo['adv'], jogo['data']),
                                              50,50,50,50])
                mpv_adv = inicializar_MPV(ovrall_adv)
                mpv = atualizar_MPV(mpv, mpv_adv, jogo['mando'], jogo['resultado'], ima_jogo)
            return mpv

        mpv_casa_raw = calcular_MPV_final(time_casa)
        mpv_fora_raw = calcular_MPV_final(time_fora)
        prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

        # Recomendação e selo
        probs = {'Vitória Casa': prob_casa, 'Empate': prob_empate, 'Vitória Fora': prob_fora}
        rec = max(probs, key=probs.get)
        rec_prob = probs[rec]
        selo_rec = get_selo(rec_prob)

        st.markdown("---")
        st.success(f"MyPredict Recomenda: **{rec}** (Probabilidade: {rec_prob:.1%})")
        st.info(f"Selo de confiança: {selo_rec}")

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("MPV Casa", f"{(mpv_casa_raw-1000)/10:.1f}")
        with col2: st.metric("Diferença MPV", f"{abs((mpv_casa_raw-1000)/10 - (mpv_fora_raw-1000)/10):.1f}")
        with col3: st.metric("MPV Fora", f"{(mpv_fora_raw-1000)/10:.1f}")

        st.markdown("---")
        st.subheader("🎯 Outros Mercados")
        def media_gols(time, tipo):
            jogos_time = [j for j in jogos_passados if j['time'] == time][-10:]
            if not jogos_time: return 1.0
            if tipo == 'marcados': return sum(j['gols'] for j in jogos_time) / len(jogos_time)
            else: return sum(j['gols_sofridos'] for j in jogos_time) / len(jogos_time)
        gols_casa = media_gols(time_casa, 'marcados'); sofridos_fora = media_gols(time_fora, 'sofridos')
        gols_fora = media_gols(time_fora, 'marcados'); sofridos_casa = media_gols(time_casa, 'sofridos')
        media_total = (gols_casa + sofridos_fora)/2 + (gols_fora + sofridos_casa)/2
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Over 1.5 gols", f"{prob_over(media_total, 1.5):.1%}")
        col2.metric("Over 2.5 gols", f"{prob_over(media_total, 2.5):.1%}")
        col3.metric("Ambas Marcam", f"{prob_btts(ata_casa, def_fora, ata_fora, def_casa):.1%}")
        esc_casa = for_casa/5 if for_casa else 4; esc_fora = for_fora/5 if for_fora else 4
        total_esc = esc_casa + esc_fora
        col4.metric("Over 9.5 esc.", f"{prob_over(total_esc, 8.5):.1%}")

# ============================================================
# BACKTEST VISUAL (SELOS POR PROBABILIDADE)
# ============================================================
elif opcao == "Backtest Visual":
    st.markdown("<h1 style='text-align:center;'>📈 Backtest MyPredict 2.0</h1>", unsafe_allow_html=True)
    if not partidas:
        st.error("Nenhuma partida carregada.")
        st.stop()

    # Prateleiras fixas
    todas_datas = sorted([p['data'] for p in partidas])
    data_inicio_temporada = todas_datas[0]
    jogos_anteriores = [j for j in jogos if j['data'] < data_inicio_temporada]
    if len(jogos_anteriores) > 0:
        prateleiras_fixas = classification_to_shelves(jogos_anteriores)
    else:
        prateleiras_fixas = classification_to_shelves(jogos)

    if 'resultados_backtest' not in st.session_state:
        st.session_state.resultados_backtest = None
        st.session_state.backtest_executado = False

    if st.button("Iniciar Backtest Completo"):
        st.session_state.backtest_executado = True
        partidas_ord = sorted(partidas, key=lambda p: p['data'])
        historico = []
        resultados = []
        progress = st.progress(0)
        total = len(partidas_ord)

        for idx, p in enumerate(partidas_ord):
            data_jogo = p['data']
            casa_info = p['casa']
            fora_info = p['fora']
            time_casa = casa_info['time']
            time_fora = fora_info['time']

            casa_info['prat_time'] = prateleiras_fixas.get(time_casa, 3)
            casa_info['prat_adv'] = prateleiras_fixas.get(time_fora, 3)
            fora_info['prat_time'] = prateleiras_fixas.get(time_fora, 3)
            fora_info['prat_adv'] = prateleiras_fixas.get(time_casa, 3)

            hist_filtrado = [j for j in historico if j['data'] < data_jogo]

            ima_casa, _ = calcular_IMA(hist_filtrado, time_casa, data_jogo, mando_proximo='casa')
            ima_fora, _ = calcular_IMA(hist_filtrado, time_fora, data_jogo, mando_proximo='fora')

            if not any(j['time'] == time_casa for j in hist_filtrado):
                prat = prateleiras_fixas.get(time_casa, 3)
                ovrall_casa = {1: 80, 2: 65, 3: 50, 4: 35, 5: 20}.get(prat, 50)
            else:
                ovrall_casa = calcular_OVRall([calcular_ATA(hist_filtrado, time_casa, data_jogo),
                                               calcular_DEF(hist_filtrado, time_casa, data_jogo),
                                               calcular_MEI(hist_filtrado, time_casa, data_jogo),
                                               calcular_FOR(hist_filtrado, time_casa, data_jogo),
                                               calcular_CONS(hist_filtrado, time_casa, data_jogo),
                                               calcular_RES(hist_filtrado, time_casa, data_jogo)])
            if not any(j['time'] == time_fora for j in hist_filtrado):
                prat = prateleiras_fixas.get(time_fora, 3)
                ovrall_fora = {1: 80, 2: 65, 3: 50, 4: 35, 5: 20}.get(prat, 50)
            else:
                ovrall_fora = calcular_OVRall([calcular_ATA(hist_filtrado, time_fora, data_jogo),
                                               calcular_DEF(hist_filtrado, time_fora, data_jogo),
                                               calcular_MEI(hist_filtrado, time_fora, data_jogo),
                                               calcular_FOR(hist_filtrado, time_fora, data_jogo),
                                               calcular_CONS(hist_filtrado, time_fora, data_jogo),
                                               calcular_RES(hist_filtrado, time_fora, data_jogo)])

            mpv_casa_raw = inicializar_MPV(ovrall_casa)
            mpv_fora_raw = inicializar_MPV(ovrall_fora)
            for jg in hist_filtrado:
                if jg['time'] == time_casa:
                    ima_jg, _ = calcular_IMA(hist_filtrado, time_casa, jg['data'], mando_proximo=jg['mando'])
                    ovrall_adv = calcular_OVRall([calcular_ATA(hist_filtrado, jg['adv'], jg['data']),
                                                  calcular_DEF(hist_filtrado, jg['adv'], jg['data']),
                                                  50,50,50,50])
                    mpv_adv = inicializar_MPV(ovrall_adv)
                    mpv_casa_raw = atualizar_MPV(mpv_casa_raw, mpv_adv, jg['mando'], jg['resultado'], ima_jg)
                elif jg['time'] == time_fora:
                    ima_jg, _ = calcular_IMA(hist_filtrado, time_fora, jg['data'], mando_proximo=jg['mando'])
                    ovrall_adv = calcular_OVRall([calcular_ATA(hist_filtrado, jg['adv'], jg['data']),
                                                  calcular_DEF(hist_filtrado, jg['adv'], jg['data']),
                                                  50,50,50,50])
                    mpv_adv = inicializar_MPV(ovrall_adv)
                    mpv_fora_raw = atualizar_MPV(mpv_fora_raw, mpv_adv, jg['mando'], jg['resultado'], ima_jg)

            prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

            # Recomendação e selo
            probs = {'Vitória Casa': prob_casa, 'Empate': prob_empate, 'Vitória Fora': prob_fora}
            rec = max(probs, key=probs.get)
            rec_prob = probs[rec]
            selo_rec = get_selo(rec_prob)

            # Resultado real
            gols_casa_real = casa_info['gols']
            gols_fora_real = fora_info['gols']
            resultado_real = 'V' if gols_casa_real > gols_fora_real else ('D' if gols_casa_real < gols_fora_real else 'E')
            total_gols = gols_casa_real + gols_fora_real
            over15_real = total_gols > 1.5
            over25_real = total_gols > 2.5
            btts_real = gols_casa_real > 0 and gols_fora_real > 0
            esc_casa_real = casa_info.get('escanteios', 0)
            esc_fora_real = fora_info.get('escanteios', 0)
            esc_real = (esc_casa_real + esc_fora_real) > 9.5

            acertou = (rec == 'Vitória Casa' and resultado_real == 'V') or \
                      (rec == 'Empate' and resultado_real == 'E') or \
                      (rec == 'Vitória Fora' and resultado_real == 'D')

            def media_hist(time, tipo):
                jogos_time = [j for j in hist_filtrado if j['time'] == time]
                if not jogos_time:
                    return 1.0 if tipo != 'escanteios' else 4.0
                if tipo == 'marcados': return sum(j.get('gols', 0) for j in jogos_time) / len(jogos_time)
                elif tipo == 'sofridos': return sum(j.get('gols_sofridos', 0) for j in jogos_time) / len(jogos_time)
                elif tipo == 'escanteios': return sum(j.get('escanteios', 0) for j in jogos_time) / len(jogos_time)

            gols_casa_hist = media_hist(time_casa, 'marcados')
            sofridos_fora_hist = media_hist(time_fora, 'sofridos')
            gols_fora_hist = media_hist(time_fora, 'marcados')
            sofridos_casa_hist = media_hist(time_casa, 'sofridos')
            esc_casa_hist = media_hist(time_casa, 'escanteios')
            esc_fora_hist = media_hist(time_fora, 'escanteios')
            media_total = (gols_casa_hist + sofridos_fora_hist)/2 + (gols_fora_hist + sofridos_casa_hist)/2
            media_esc_total = esc_casa_hist + esc_fora_hist

            prob_over15 = prob_over(media_total, 1.5)
            prob_over25 = prob_over(media_total, 2.5)
            prob_bt = prob_btts(ovrall_casa, ovrall_fora, ovrall_fora, ovrall_casa)
            prob_esc = prob_over(media_esc_total, 9.5)
            prob_ht_over05 = prob_over(media_total * 0.4, 0.5)
            prob_ht_over15 = prob_over(media_total * 0.4, 1.5)

            # Probabilidades implícitas (Bet365) – apenas para exibição
            imp_casa = 1 / float(casa_info.get('B365H', 2.0)) if float(casa_info.get('B365H', 2.0)) > 0 else 0
            imp_empate = 1 / float(casa_info.get('B365D', 3.0)) if float(casa_info.get('B365D', 3.0)) > 0 else 0
            imp_fora = 1 / float(casa_info.get('B365A', 3.0)) if float(casa_info.get('B365A', 3.0)) > 0 else 0

            resultados.append({
                'data': data_jogo,
                'time_casa': time_casa,
                'time_fora': time_fora,
                'mpv_casa': (mpv_casa_raw - 1000) / 10,
                'mpv_fora': (mpv_fora_raw - 1000) / 10,
                'ima_casa': ima_casa,
                'ima_fora': ima_fora,
                'ovr_casa': ovrall_casa,
                'ovr_fora': ovrall_fora,
                'prob_casa': prob_casa, 'imp_casa': imp_casa,
                'prob_empate': prob_empate, 'imp_empate': imp_empate,
                'prob_fora': prob_fora, 'imp_fora': imp_fora,
                'recomendacao': rec, 'rec_prob': rec_prob, 'selo': selo_rec,
                'resultado_real': resultado_real, 'acertou': acertou,
                'over15_prob': prob_over15, 'over15_real': over15_real,
                'over25_prob': prob_over25, 'over25_real': over25_real,
                'btts_prob': prob_bt, 'btts_real': btts_real,
                'esc_prob': prob_esc, 'esc_real': esc_real,
                'ht_over05_prob': prob_ht_over05,
                'ht_over15_prob': prob_ht_over15
            })

            historico.append(casa_info)
            historico.append(fora_info)
            progress.progress((idx + 1) / total)

        st.session_state.resultados_backtest = resultados

    # Exibição paginada
    if st.session_state.resultados_backtest:
        resultados = st.session_state.resultados_backtest
        total_jogos = len(resultados)
        pag_size = 10
        total_pags = (total_jogos // pag_size) + (1 if total_jogos % pag_size else 0)
        pag = st.selectbox(f"Página (1 a {total_pags})", range(1, total_pags + 1))
        inicio = (pag - 1) * pag_size
        fim = inicio + pag_size
        pagina_atual = resultados[inicio:fim]
        st.markdown(f"Mostrando {inicio+1}–{min(fim, total_jogos)} de {total_jogos} partidas")

        for res in pagina_atual:
            with st.container():
                st.markdown(f"### {res['time_casa']} vs {res['time_fora']} – {res['data'].strftime('%d/%m/%Y')}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("MPV Casa", f"{res['mpv_casa']:.1f}")
                    st.metric("IMA Casa", f"{res['ima_casa']:.1f}")
                with col2:
                    st.metric("MPV Fora", f"{res['mpv_fora']:.1f}")
                    st.metric("IMA Fora", f"{res['ima_fora']:.1f}")
                with col3:
                    st.metric("OVR Casa", f"{res['ovr_casa']:.1f}")
                    st.metric("OVR Fora", f"{res['ovr_fora']:.1f}")
                with col4:
                    st.write(f"Resultado: {res['resultado_real']}")
                    st.write(f"Recomendação: **{res['recomendacao']}**")
                    st.write(f"Prob MyPredict: {res['rec_prob']:.1%}")
                    st.write(f"Selo: {res['selo']}")
                    st.write(f"Acertou: {'✅' if res['acertou'] else '❌'}")

                st.write("**Probabilidades 1X2**")
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    st.metric("Casa (MyPredict)", f"{res['prob_casa']:.1%}", delta=f"Bet365: {res['imp_casa']:.1%}")
                with col_p2:
                    st.metric("Empate (MyPredict)", f"{res['prob_empate']:.1%}", delta=f"Bet365: {res['imp_empate']:.1%}")
                with col_p3:
                    st.metric("Fora (MyPredict)", f"{res['prob_fora']:.1%}", delta=f"Bet365: {res['imp_fora']:.1%}")

                st.write("**Outros Mercados (MyPredict)**")
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                with col_m1:
                    st.metric("Over 1.5", f"{res['over15_prob']:.1%}", delta=f"{'✅' if res['over15_real'] else '❌'}")
                with col_m2:
                    st.metric("Over 2.5", f"{res['over25_prob']:.1%}", delta=f"{'✅' if res['over25_real'] else '❌'}")
                with col_m3:
                    st.metric("BTTS", f"{res['btts_prob']:.1%}", delta=f"{'✅' if res['btts_real'] else '❌'}")
                with col_m4:
                    st.metric("Esc. >9.5", f"{res['esc_prob']:.1%}", delta=f"{'✅' if res['esc_real'] else '❌'}")
                col_m5, col_m6 = st.columns(2)
                with col_m5:
                    st.metric("HT Over 0.5", f"{res['ht_over05_prob']:.1%}")
                with col_m6:
                    st.metric("HT Over 1.5", f"{res['ht_over15_prob']:.1%}")
                st.markdown("---")

        # Resumo
        st.markdown("---")
        st.subheader("📊 Desempenho do MyPredict")
        total_jogos = len(resultados)
        acertos = sum(1 for r in resultados if r['acertou'])
        taxa = (acertos / total_jogos) * 100
        st.metric("Total de Jogos", total_jogos)
        st.metric("Acertos", acertos)
        st.metric("Taxa de Acerto", f"{taxa:.1f}%")

        # Desempenho por selo
        for selo_nome in ["🥇 Ouro", "🟢 Verde", "⚪ Marginal", "🔴 Sem selo"]:
            jogos_selo = [r for r in resultados if r['selo'] == selo_nome]
            if jogos_selo:
                acertos_selo = sum(1 for r in jogos_selo if r['acertou'])
                taxa_selo = (acertos_selo / len(jogos_selo)) * 100
                st.write(f"{selo_nome}: {len(jogos_selo)} jogos, {acertos_selo} acertos ({taxa_selo:.1f}%)")
    else:
        st.info("Clique em 'Iniciar Backtest Completo' para processar os jogos.")
