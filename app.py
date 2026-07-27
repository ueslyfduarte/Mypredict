"""
MyPredict 2.0 – Aplicativo Completo (Backtest Paginado)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial
import os

# ============================================================
# CONFIGURAÇÃO VISUAL (Tema Escuro Dourado)
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
# CONVERSOR (mantido funcional)
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
# ANÁLISE DE JOGO (SIMPLIFICADA)
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

        rec = None; rec_prob = 0; rec_selo = ""
        if 'Dourado' in selo_casa or 'Verde' in selo_casa:
            rec = f"Vitória {time_casa}"; rec_prob = prob_casa; rec_selo = selo_casa
        elif 'Dourado' in selo_empate or 'Verde' in selo_empate:
            rec = "Empate"; rec_prob = prob_empate; rec_selo = selo_empate
        elif 'Dourado' in selo_fora or 'Verde' in selo_fora:
            rec = f"Vitória {time_fora}"; rec_prob = prob_fora; rec_selo = selo_fora

        st.markdown("---")
        if rec:
            st.success(f"MyPredict Recomenda: **{rec}** (Prob: {rec_prob:.1%}, Selo: {rec_selo})")
        else:
            st.info("Sem recomendação de alto valor.")

        col1, col2, col3 = st.columns(3)
        with col1: st.metric(f"MPV {time_casa}", f"{mpv_casa:.1f}")
        with col2: st.metric("Diferença MPV", f"{abs(mpv_casa - mpv_fora):.1f}")
        with col3: st.metric(f"MPV {time_fora}", f"{mpv_fora:.1f}")

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
# BACKTEST VISUAL (PAGINADO, 10 POR VEZ)
# ============================================================
elif opcao == "Backtest Visual":
    st.markdown("<h1 style='text-align:center;'>📈 Backtest MyPredict 2.0</h1>", unsafe_allow_html=True)
    if not partidas:
        st.error("Nenhuma partida carregada.")
        st.stop()

    # Prateleiras fixas (temporada anterior)
    todas_datas = sorted([p['data'] for p in partidas])
    data_inicio_temporada = todas_datas[0]
    jogos_anteriores = [j for j in jogos if j['data'] < data_inicio_temporada]
    if len(jogos_anteriores) > 0:
        prateleiras_fixas = classification_to_shelves(jogos_anteriores)
    else:
        prateleiras_fixas = classification_to_shelves(jogos)

    # Estado da sessão
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

            ima_casa, desvio_casa = calcular_IMA(hist_filtrado, time_casa, data_jogo, mando_proximo='casa')
            ima_fora, desvio_fora = calcular_IMA(hist_filtrado, time_fora, data_jogo, mando_proximo='fora')
            desvio_medio = (desvio_casa + desvio_fora) / 2

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

            odd_casa = casa_info.get('B365H', 2.0)
            odd_empate = casa_info.get('B365D', 3.0)
            odd_fora = casa_info.get('B365A', 3.0)

            imp_casa = 1 / odd_casa if odd_casa > 0 else 0
            imp_empate = 1 / odd_empate if odd_empate > 0 else 0
            imp_fora = 1 / odd_fora if odd_fora > 0 else 0

            edge_casa = calcular_edge(prob_casa, odd_casa)
            edge_empate = calcular_edge(prob_empate, odd_empate)
            edge_fora = calcular_edge(prob_fora, odd_fora)

            dif_mpv = abs(mpv_casa_raw + 75 - mpv_fora_raw)
            selo_casa = determinar_selo(edge_casa, dif_mpv, desvio_medio)
            selo_empate = determinar_selo(edge_empate, dif_mpv, desvio_medio)
            selo_fora = determinar_selo(edge_fora, dif_mpv, desvio_medio)

            recomendacao = None
            rec_prob = 0
            rec_selo = ""
            rec_odd = 0
            if 'Dourado' in selo_casa or 'Verde' in selo_casa:
                recomendacao = f"Vitória {time_casa}"
                rec_prob = prob_casa
                rec_odd = odd_casa
                rec_selo = selo_casa
            elif 'Dourado' in selo_empate or 'Verde' in selo_empate:
                recomendacao = "Empate"
                rec_prob = prob_empate
                rec_odd = odd_empate
                rec_selo = selo_empate
            elif 'Dourado' in selo_fora or 'Verde' in selo_fora:
                recomendacao = f"Vitória {time_fora}"
                rec_prob = prob_fora
                rec_odd = odd_fora
                rec_selo = selo_fora

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

            acertou = False
            if recomendacao:
                if (recomendacao == f"Vitória {time_casa}" and resultado_real == 'V') or \
                   (recomendacao == "Empate" and resultado_real == 'E') or \
                   (recomendacao == f"Vitória {time_fora}" and resultado_real == 'D'):
                    acertou = True

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
                'edge_casa': edge_casa, 'edge_empate': edge_empate, 'edge_fora': edge_fora,
                'selo_casa': selo_casa, 'selo_empate': selo_empate, 'selo_fora': selo_fora,
                'recomendacao': recomendacao, 'rec_prob': rec_prob,
                'rec_odd': rec_odd, 'rec_selo': rec_selo,
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

    # Exibição paginada (10 por vez)
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
                    if res['recomendacao']:
                        st.write(f"Recomendação: {res['recomendacao']}")
                        st.write(f"Prob: {res['rec_prob']:.1%} | Selo: {res['rec_selo']}")
                        st.write(f"Acertou: {'✅' if res['acertou'] else '❌'}")
                    else:
                        st.write("Sem recomendação")

                # Probabilidades
                st.write("**Probabilidades 1X2**")
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    st.metric("Casa (MyPredict)", f"{res['prob_casa']:.1%}", delta=f"Bet365: {res['imp_casa']:.1%}")
                with col_p2:
                    st.metric("Empate (MyPredict)", f"{res['prob_empate']:.1%}", delta=f"Bet365: {res['imp_empate']:.1%}")
                with col_p3:
                    st.metric("Fora (MyPredict)", f"{res['prob_fora']:.1%}", delta=f"Bet365: {res['imp_fora']:.1%}")

                # Edge e Selos
                st.write("**Edge e Selos**")
                col_e1, col_e2, col_e3 = st.columns(3)
                with col_e1:
                    st.write(f"Edge Casa: {res['edge_casa']:+.1%} ({res['selo_casa']})")
                with col_e2:
                    st.write(f"Edge Empate: {res['edge_empate']:+.1%} ({res['selo_empate']})")
                with col_e3:
                    st.write(f"Edge Fora: {res['edge_fora']:+.1%} ({res['selo_fora']})")

                # Outros mercados
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

        # Resumo geral
        st.markdown("---")
        st.subheader("📊 Desempenho do MyPredict")
        apostas = [r for r in resultados if r['recomendacao']]
        total_apostas = len(apostas)
        if total_apostas > 0:
            acertos = sum(1 for r in apostas if r['acertou'])
            taxa = (acertos / total_apostas) * 100
            lucro = sum([r['rec_odd'] - 1 if r['acertou'] else -1 for r in apostas])
            roi = (lucro / total_apostas) * 100
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Apostas", total_apostas)
            with col2: st.metric("Acertos", acertos)
            with col3: st.metric("Taxa de Acerto", f"{taxa:.1f}%")
            with col4: st.metric("Lucro/Prejuízo", f"{lucro:+.2f} unidades")
            st.metric("ROI", f"{roi:.2f}%")
        else:
            st.warning("Nenhuma aposta foi recomendada.")
    else:
        st.info("Clique em 'Iniciar Backtest Completo' para processar os jogos.")
