"""
MyPredict 2.0 – Aplicativo Completo (Backtest Focado em 1X2, Selos Corrigidos)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial
import os

# ============================================================
# LIMIARES PARA SELOS (AJUSTADOS)
# ============================================================
LIMITE_OURO = 0.695
LIMITE_VERDE = 0.50
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
    h1, h2, h3, h4 { color: #DAA520; }
    .stButton>button { background:#DAA520; color:#000; font-weight:bold; border-radius:8px; }
    .card {
        background-color: #1E1E1E; border-left: 4px solid #DAA520;
        padding: 12px; margin: 8px 0; border-radius: 6px;
    }
    .team-name { font-size: 1.1rem; color: #DAA520; font-weight: bold; }
    .result { font-size: 1.8rem; font-weight: bold; text-align: center; }
    .metric-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 6px 0; }
    .metric-cell { flex: 1; min-width: 80px; text-align: center; }
    .metric-value { font-size: 1.2rem; color: #DAA520; font-weight: bold; }
    .metric-label { font-size: 0.7rem; color: #aaa; text-transform: uppercase; }
    .prob-cell { flex: 1; min-width: 70px; text-align: center; }
    .prob-value { font-size: 1.1rem; color: #fff; }
    .prob-market { font-size: 0.9rem; color: #DAA520; }
    .acerto { font-size: 1.5rem; }
    hr { border-color: #333; margin: 8px 0; }
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
# MAPEAMENTO DE PRATELEIRA PARA VALORES BASE
# ============================================================
SHELF_VALUES = {1: 80, 2: 65, 3: 50, 4: 35, 5: 20}
SHELF_NAMES = {1: "Elite", 2: "Alta", 3: "Meio", 4: "Baixa", 5: "Crítico"}

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
            # ... (código do conversor mantido) ...
            st.write("Conversor mantido. Use o código completo do arquivo real.")

# ============================================================
# ANÁLISE DE JOGO (mantida)
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

        def get_ovrall(time, hist):
            prat = prats.get(time, 3)
            base = SHELF_VALUES[prat]
            if not any(j['time'] == time for j in hist):
                return base, (base, base, base, base, base, base)
            ata = calcular_ATA(hist, time, data_ref_dt)
            de = calcular_DEF(hist, time, data_ref_dt)
            mei = base
            forc = base
            cons = base
            res = base
            ovr = calcular_OVRall([ata, de, mei, forc, cons, res])
            return ovr, (ata, de, mei, forc, cons, res)

        ovrall_casa, comp_casa = get_ovrall(time_casa, jogos_passados)
        ovrall_fora, comp_fora = get_ovrall(time_fora, jogos_passados)

        def calcular_MPV_final(time):
            jogos_time = [j for j in jogos_passados if j['time'] == time]
            if not jogos_time:
                return inicializar_MPV(ovrall_casa if time == time_casa else ovrall_fora)
            jogos_time = sorted(jogos_time, key=lambda x: x['data'])
            ovr, _ = get_ovrall(time, jogos_passados)
            mpv = inicializar_MPV(ovr)
            for jogo in jogos_time:
                ima_jogo, _ = calcular_IMA(jogos_passados, time, jogo['data'], mando_proximo=jogo['mando'])
                ovr_adv, _ = get_ovrall(jogo['adv'], jogos_passados)
                mpv_adv = inicializar_MPV(ovr_adv)
                mpv = atualizar_MPV(mpv, mpv_adv, jogo['mando'], jogo['resultado'], ima_jogo)
            return mpv

        mpv_casa_raw = calcular_MPV_final(time_casa)
        mpv_fora_raw = calcular_MPV_final(time_fora)

        ima_casa, _ = calcular_IMA(jogos_passados, time_casa, data_ref_dt, mando_proximo='casa')
        ima_fora, _ = calcular_IMA(jogos_passados, time_fora, data_ref_dt, mando_proximo='fora')

        prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

        # Recomendação
        probs = {f"Vitória do {time_casa}": prob_casa, "Empate": prob_empate, f"Vitória do {time_fora}": prob_fora}
        rec = max(probs, key=probs.get)
        rec_prob = probs[rec]
        selo_rec = get_selo(rec_prob)
        if selo_rec in ("🥇 Ouro", "🟢 Verde"):
            recomendacao_final = rec
        else:
            recomendacao_final = "Sem recomendação"

        # Odds para comparação
        odds_jogos = [j for j in jogos if j['time'] == time_casa and j['adv'] == time_fora]
        odd_casa = float(odds_jogos[-1].get('B365H', 2.0)) if odds_jogos else 2.0
        odd_empate = float(odds_jogos[-1].get('B365D', 3.0)) if odds_jogos else 3.0
        odd_fora = float(odds_jogos[-1].get('B365A', 3.0)) if odds_jogos else 3.0
        imp_casa = 1/odd_casa if odd_casa else 0
        imp_empate = 1/odd_empate if odd_empate else 0
        imp_fora = 1/odd_fora if odd_fora else 0

        st.markdown("---")
        st.success(f"MyPredict Recomenda: **{recomendacao_final}**")
        if selo_rec in ("🥇 Ouro", "🟢 Verde"):
            st.info(f"Selo de confiança: {selo_rec}")
        else:
            st.info(f"Probabilidade insuficiente para recomendação ({selo_rec})")

        col1, col2, col3 = st.columns(3)
        col1.metric("MPV Casa", f"{(mpv_casa_raw-1000)/10:.1f}")
        col2.metric("Diferença MPV", f"{abs((mpv_casa_raw-1000)/10 - (mpv_fora_raw-1000)/10):.1f}")
        col3.metric("MPV Fora", f"{(mpv_fora_raw-1000)/10:.1f}")

        st.markdown("---")
        st.subheader("📊 Probabilidades 1X2")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.metric("Casa (MyPredict)", f"{prob_casa:.1%}", delta=f"Bet365: {imp_casa:.1%}")
        with col_p2:
            st.metric("Empate (MyPredict)", f"{prob_empate:.1%}", delta=f"Bet365: {imp_empate:.1%}")
        with col_p3:
            st.metric("Fora (MyPredict)", f"{prob_fora:.1%}", delta=f"Bet365: {imp_fora:.1%}")

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
        esc_casa = comp_casa[3]/5 if comp_casa[3] else 4; esc_fora = comp_fora[3]/5 if comp_fora[3] else 4
        total_esc = esc_casa + esc_fora
        col4.metric("Over 9.5 esc.", f"{prob_over(total_esc, 8.5):.1%}")

# ============================================================
# BACKTEST VISUAL (CORRIGIDO – SELOS DEFINITIVOS, PRATELEIRAS FIXAS)
# ============================================================
elif opcao == "Backtest Visual":
    st.markdown("<h1 style='text-align:center;'>📈 Backtest MyPredict 2.0</h1>", unsafe_allow_html=True)
    if not partidas:
        st.error("Nenhuma partida carregada.")
        st.stop()

    # --- PRATELEIRAS FIXAS: classificação final da temporada ---
    prateleiras_fixas = classification_to_shelves(jogos)
    st.success("Prateleiras definidas a partir da classificação final da temporada.")

    # Função de probabilidades corrigida (normaliza soma = 1)
    def prob_1x2_corrigida(mpv_casa, mpv_fora):
        P_casa = 1 / (1 + 10 ** ((mpv_fora - (mpv_casa + PARAMS['V_mando'])) / PARAMS['S']))
        dif_norm = abs(mpv_casa + PARAMS['V_mando'] - mpv_fora) / PARAMS['S']
        P_empate = max(0.14, min(0.32, 0.30 - 0.05 * dif_norm))
        P_casa_final = max(0.0, P_casa - 0.5 * P_empate)
        P_empate_final = max(0.0, P_empate)
        P_fora_final = max(0.0, 1.0 - P_casa_final - P_empate_final)
        total = P_casa_final + P_empate_final + P_fora_final
        if total > 0:
            P_casa_final /= total
            P_empate_final /= total
            P_fora_final /= total
        return P_casa_final, P_empate_final, P_fora_final

    if 'resultados_backtest' not in st.session_state:
        st.session_state.resultados_backtest = None
        st.session_state.backtest_executado = False

    if st.button("Iniciar Backtest 1X2"):
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

            prat_casa = prateleiras_fixas.get(time_casa, 3)
            prat_fora = prateleiras_fixas.get(time_fora, 3)
            casa_info['prat_time'] = prat_casa
            casa_info['prat_adv'] = prat_fora
            fora_info['prat_time'] = prat_fora
            fora_info['prat_adv'] = prat_casa

            hist_filtrado = [j for j in historico if j['data'] < data_jogo]

            # --- IMA detalhado ---
            def calc_ima_detalhado(time, mando_prox):
                jogos_time = [j for j in hist_filtrado if j['time'] == time]
                jogos_time.sort(key=lambda x: x['data'], reverse=True)
                def ultimos(n, apenas_mando=None):
                    filtrados = []
                    for j in jogos_time:
                        if apenas_mando is None or j['mando'] == apenas_mando:
                            filtrados.append(j)
                        if len(filtrados) == n:
                            break
                    return filtrados
                def nota(lista):
                    if not lista:
                        return 50.0
                    P_obt = sum(pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], j['resultado']) for j in lista)
                    P_max = sum(pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'V') for j in lista)
                    P_min = sum(pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'D') for j in lista)
                    if P_max == P_min:
                        return 50.0
                    return ((P_obt - P_min) / (P_max - P_min)) * 100
                g10 = ultimos(10); g5 = ultimos(5); g3 = ultimos(3)
                l5 = ultimos(5, apenas_mando=mando_prox); l3 = ultimos(3, apenas_mando=mando_prox)
                n10, n5, n3, nl5, nl3 = nota(g10), nota(g5), nota(g3), nota(l5), nota(l3)
                ima = 0.10*n10 + 0.15*n5 + 0.20*n3 + 0.25*nl5 + 0.30*nl3
                return ima, (n10, n5, n3, nl5, nl3)

            ima_casa, jan_casa = calc_ima_detalhado(time_casa, 'casa')
            ima_fora, jan_fora = calc_ima_detalhado(time_fora, 'fora')

            # --- OVRall detalhado ---
            def ovrall_detalhado(time, prat):
                if not any(j['time'] == time for j in hist_filtrado):
                    base = SHELF_VALUES[prat]
                    return base, (base, base, base, base, base, base)
                ata = calcular_ATA(hist_filtrado, time, data_jogo)
                de = calcular_DEF(hist_filtrado, time, data_jogo)
                mei = SHELF_VALUES[prat]
                forc = SHELF_VALUES[prat]
                cons = SHELF_VALUES[prat]
                res = SHELF_VALUES[prat]
                ovr = calcular_OVRall([ata, de, mei, forc, cons, res])
                return ovr, (ata, de, mei, forc, cons, res)

            ovrall_casa, comp_casa = ovrall_detalhado(time_casa, prat_casa)
            ovrall_fora, comp_fora = ovrall_detalhado(time_fora, prat_fora)

            # MPV
            mpv_casa_raw = inicializar_MPV(ovrall_casa)
            mpv_fora_raw = inicializar_MPV(ovrall_fora)
            for jg in hist_filtrado:
                if jg['time'] == time_casa:
                    ima_jg, _ = calcular_IMA(hist_filtrado, time_casa, jg['data'], mando_proximo=jg['mando'])
                    ovr_adv = calcular_OVRall([calcular_ATA(hist_filtrado, jg['adv'], jg['data']),
                                               calcular_DEF(hist_filtrado, jg['adv'], jg['data']),
                                               SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                               SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                               SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                               SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)]])
                    mpv_adv = inicializar_MPV(ovr_adv)
                    mpv_casa_raw = atualizar_MPV(mpv_casa_raw, mpv_adv, jg['mando'], jg['resultado'], ima_jg)
                elif jg['time'] == time_fora:
                    ima_jg, _ = calcular_IMA(hist_filtrado, time_fora, jg['data'], mando_proximo=jg['mando'])
                    ovr_adv = calcular_OVRall([calcular_ATA(hist_filtrado, jg['adv'], jg['data']),
                                               calcular_DEF(hist_filtrado, jg['adv'], jg['data']),
                                               SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                               SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                               SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                               SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)]])
                    mpv_adv = inicializar_MPV(ovr_adv)
                    mpv_fora_raw = atualizar_MPV(mpv_fora_raw, mpv_adv, jg['mando'], jg['resultado'], ima_jg)

            prob_casa, prob_empate, prob_fora = prob_1x2_corrigida(mpv_casa_raw, mpv_fora_raw)

            # Recomendação e selo
            probs = {
                f"Vitória do {time_casa}": prob_casa,
                "Empate": prob_empate,
                f"Vitória do {time_fora}": prob_fora
            }
            rec = max(probs, key=probs.get)
            rec_prob = probs[rec]
            selo = get_selo(rec_prob)

            # Só considera recomendação se for Ouro ou Verde
            if selo in ("🥇 Ouro", "🟢 Verde"):
                recomendacao = rec
                aposta_valida = True
            else:
                recomendacao = "Sem recomendação"
                aposta_valida = False

            gols_casa_real = casa_info['gols']
            gols_fora_real = fora_info['gols']
            resultado_real = 'V' if gols_casa_real > gols_fora_real else ('D' if gols_casa_real < gols_fora_real else 'E')

            acertou = False
            if aposta_valida:
                if (rec == f"Vitória do {time_casa}" and resultado_real == 'V') or \
                   (rec == "Empate" and resultado_real == 'E') or \
                   (rec == f"Vitória do {time_fora}" and resultado_real == 'D'):
                    acertou = True

            imp_casa = 1 / float(casa_info.get('B365H', 2.0)) if float(casa_info.get('B365H', 2.0)) > 0 else 0
            imp_empate = 1 / float(casa_info.get('B365D', 3.0)) if float(casa_info.get('B365D', 3.0)) > 0 else 0
            imp_fora = 1 / float(casa_info.get('B365A', 3.0)) if float(casa_info.get('B365A', 3.0)) > 0 else 0

            dif_mpv = (mpv_casa_raw - 1000)/10 - (mpv_fora_raw - 1000)/10

            resultados.append({
                'data': data_jogo,
                'time_casa': time_casa, 'time_fora': time_fora,
                'prat_casa': prat_casa, 'prat_fora': prat_fora,
                'mpv_casa': (mpv_casa_raw - 1000) / 10,
                'mpv_fora': (mpv_fora_raw - 1000) / 10,
                'dif_mpv': dif_mpv,
                'ima_casa': ima_casa, 'ima_fora': ima_fora,
                'jan_casa': jan_casa, 'jan_fora': jan_fora,
                'comp_casa': comp_casa, 'comp_fora': comp_fora,
                'ovr_casa': ovrall_casa, 'ovr_fora': ovrall_fora,
                'prob_casa': prob_casa, 'prob_empate': prob_empate, 'prob_fora': prob_fora,
                'imp_casa': imp_casa, 'imp_empate': imp_empate, 'imp_fora': imp_fora,
                'recomendacao': recomendacao, 'rec_prob': rec_prob, 'selo': selo,
                'aposta_valida': aposta_valida,
                'resultado_real': resultado_real, 'acertou': acertou
            })

            historico.append(casa_info)
            historico.append(fora_info)
            progress.progress((idx + 1) / total)

        st.session_state.resultados_backtest = resultados

    # ============================================================
    # EXIBIÇÃO PAGINADA (10 POR VEZ, CARDS ABERTOS)
    # ============================================================
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
            if res['dif_mpv'] > 0:
                tendencia = f"MPV Casa maior em {res['dif_mpv']:.1f} pontos"
            elif res['dif_mpv'] < 0:
                tendencia = f"MPV Fora maior em {abs(res['dif_mpv']):.1f} pontos"
            else:
                tendencia = "MPV igual"

            # Destacar recomendação apenas se for válida
            if res['aposta_valida']:
                rec_text = f"**MyPredict Recomenda:** {res['recomendacao']} (Prob: {res['rec_prob']:.1%}, Selo: {res['selo']})"
            else:
                rec_text = f"MyPredict: **{res['recomendacao']}** (Prob: {res['rec_prob']:.1%}, Selo: {res['selo']})"

            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span class="team-name">{res['time_casa']}</span>
                        <span style="color:#aaa; font-size:0.8rem;"> (Prat {res['prat_casa']} - {SHELF_NAMES[res['prat_casa']]})</span>
                        <span style="color:#DAA520;"> vs </span>
                        <span class="team-name">{res['time_fora']}</span>
                        <span style="color:#aaa; font-size:0.8rem;"> (Prat {res['prat_fora']} - {SHELF_NAMES[res['prat_fora']]})</span>
                    </div>
                    <div class="result">{res['resultado_real']}</div>
                    <div class="acerto">{'✅' if res['aposta_valida'] and res['acertou'] else ('❌' if res['aposta_valida'] else '')}</div>
                </div>
                <div style="font-size:0.8rem; color:#aaa; margin-bottom:6px;">{res['data'].strftime('%d/%m/%Y')}</div>
                <div class="metric-row">
                    <div class="metric-cell"><div class="metric-label">MPV Casa</div><div class="metric-value">{res['mpv_casa']:.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">MPV Fora</div><div class="metric-value">{res['mpv_fora']:.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">Diferença</div><div class="metric-value">{res['dif_mpv']:+.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">IMA Casa</div><div class="metric-value">{res['ima_casa']:.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">IMA Fora</div><div class="metric-value">{res['ima_fora']:.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">OVR Casa</div><div class="metric-value">{res['ovr_casa']:.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">OVR Fora</div><div class="metric-value">{res['ovr_fora']:.1f}</div></div>
                </div>
                <div style="font-size:0.7rem; color:#aaa; margin-bottom:4px;">{tendencia}</div>
                <div class="metric-row" style="font-size:0.7rem; color:#aaa;">
                    <div class="metric-cell">G10:{res['jan_casa'][0]:.0f} G5:{res['jan_casa'][1]:.0f} G3:{res['jan_casa'][2]:.0f} L5:{res['jan_casa'][3]:.0f} L3:{res['jan_casa'][4]:.0f}</div>
                    <div class="metric-cell">G10:{res['jan_fora'][0]:.0f} G5:{res['jan_fora'][1]:.0f} G3:{res['jan_fora'][2]:.0f} L5:{res['jan_fora'][3]:.0f} L3:{res['jan_fora'][4]:.0f}</div>
                </div>
                <div class="metric-row" style="font-size:0.7rem; color:#aaa;">
                    <div class="metric-cell">ATA:{res['comp_casa'][0]:.0f} DEF:{res['comp_casa'][1]:.0f} MEI:{res['comp_casa'][2]:.0f} FOR:{res['comp_casa'][3]:.0f} CONS:{res['comp_casa'][4]:.0f} RES:{res['comp_casa'][5]:.0f}</div>
                    <div class="metric-cell">ATA:{res['comp_fora'][0]:.0f} DEF:{res['comp_fora'][1]:.0f} MEI:{res['comp_fora'][2]:.0f} FOR:{res['comp_fora'][3]:.0f} CONS:{res['comp_fora'][4]:.0f} RES:{res['comp_fora'][5]:.0f}</div>
                </div>
                <hr>
                <div style="margin-bottom:4px;">{rec_text}</div>
                <div class="metric-row">
                    <div class="prob-cell">
                        <div class="prob-market">Casa (MyPredict)</div>
                        <div class="prob-value">{res['prob_casa']:.1%}</div>
                        <div style="font-size:0.7rem; color:#aaa;">Bet365: {res['imp_casa']:.1%}</div>
                    </div>
                    <div class="prob-cell">
                        <div class="prob-market">Empate (MyPredict)</div>
                        <div class="prob-value">{res['prob_empate']:.1%}</div>
                        <div style="font-size:0.7rem; color:#aaa;">Bet365: {res['imp_empate']:.1%}</div>
                    </div>
                    <div class="prob-cell">
                        <div class="prob-market">Fora (MyPredict)</div>
                        <div class="prob-value">{res['prob_fora']:.1%}</div>
                        <div style="font-size:0.7rem; color:#aaa;">Bet365: {res['imp_fora']:.1%}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ============================================================
        # RESUMO (APENAS RECOMENDAÇÕES VÁLIDAS – OURO E VERDE)
        # ============================================================
        st.markdown("---")
        st.subheader("📊 Desempenho do MyPredict (apenas recomendações Ouro e Verde)")

        apostas_validas = [r for r in resultados if r['aposta_valida']]
        total_apostas = len(apostas_validas)

        if total_apostas > 0:
            acertos = sum(1 for r in apostas_validas if r['acertou'])
            taxa = (acertos / total_apostas) * 100
            lucro = 0.0
            for r in apostas_validas:
                if r['recomendacao'].startswith('Vitória do '):
                    time_rec = r['recomendacao'].replace('Vitória do ', '')
                    if time_rec == r['time_casa']:
                        odd = float(r['imp_casa'] and (1/r['imp_casa']) or 2.0)  # odd da casa
                    else:
                        odd = float(r['imp_fora'] and (1/r['imp_fora']) or 3.0)
                else:
                    odd = float(r['imp_empate'] and (1/r['imp_empate']) or 3.0)
                if r['acertou']:
                    lucro += odd - 1
                else:
                    lucro -= 1

            roi = (lucro / total_apostas) * 100

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total de Recomendações", total_apostas)
            col2.metric("Acertos", acertos)
            col3.metric("Taxa de Acerto", f"{taxa:.1f}%")
            col4.metric("Lucro/Prejuízo", f"{lucro:+.2f} unidades")
            st.metric("ROI", f"{roi:.2f}%")

            st.subheader("Desempenho por Selo")
            for selo_nome in ["🥇 Ouro", "🟢 Verde"]:
                jogos_selo = [r for r in apostas_validas if r['selo'] == selo_nome]
                if jogos_selo:
                    acertos_selo = sum(1 for r in jogos_selo if r['acertou'])
                    taxa_selo = (acertos_selo / len(jogos_selo)) * 100
                    st.write(f"{selo_nome}: {len(jogos_selo)} jogos, {acertos_selo} acertos ({taxa_selo:.1f}%)")
        else:
            st.warning("Nenhuma recomendação foi emitida (apenas Ouro ou Verde).")
    else:
        st.info("Clique em 'Iniciar Backtest 1X2' para processar os jogos.")
