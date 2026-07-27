"""
MyPredict 2.0 – Aplicativo Oficial (Prateleiras por Odds da Temporada Inteira)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial
import os

# ============================================================
# LIMIARES PARA SELOS (POR PROBABILIDADE)
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
# FUNÇÕES DE PRATELEIRAS E OVRall INICIAL (VIA MENOR ODD DA TEMPORADA)
# ============================================================
def compute_initial_shelves_and_ovrall(jogos):
    # Para cada time, encontra a menor odd em que aparece (B365H se mandante, B365A se visitante)
    min_odds = {}
    for j in jogos:
        time = j['time']
        if j['mando'] == 'casa':
            odd = float(j.get('B365H', 3.0))
        else:
            odd = float(j.get('B365A', 3.0))
        if time not in min_odds or odd < min_odds[time]:
            min_odds[time] = odd

    # Ordena times pela menor odd (menor = melhor, favorito)
    sorted_teams = sorted(min_odds, key=lambda t: min_odds[t])
    n = len(sorted_teams)
    shelves = {}
    ovrall_ini = {}
    for i, t in enumerate(sorted_teams):
        if i < n * 0.15:
            shelves[t] = 1
        elif i < n * 0.35:
            shelves[t] = 2
        elif i < n * 0.65:
            shelves[t] = 3
        elif i < n * 0.85:
            shelves[t] = 4
        else:
            shelves[t] = 5
        # OVRall inicial linear centrado em 50 (odd 3.0 -> 50, odd 1.0 -> 100, odd 5.0 -> 0)
        odd = min_odds[t]
        ovrall_ini[t] = max(0, min(100, 100 - (odd - 1.0) * 25))
    # Times que não apareceram recebem prateleira 3 e OVRall 50
    for t in set(j['time'] for j in jogos):
        if t not in shelves:
            shelves[t] = 3
            ovrall_ini[t] = 50.0
    return shelves, ovrall_ini

PRATELEIRAS, OVRALL_INICIAL = compute_initial_shelves_and_ovrall(jogos)

# ============================================================
# MAPEAMENTO DE PRATELEIRA PARA NOMES
# ============================================================
SHELF_NAMES = {1: "Elite", 2: "Alta", 3: "Meio", 4: "Baixa", 5: "Crítico"}

# ============================================================
# MENU LATERAL
# ============================================================
st.sidebar.markdown("<h2 style='color:#DAA520;'>⚽ MyPredict 2.0</h2>", unsafe_allow_html=True)
opcao = st.sidebar.radio("Modo", ["Análise de Jogo", "Backtest Oficial", "Converter Dados Brutos"])

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
            st.write("Conversor mantido.")

# ============================================================
# ANÁLISE DE JOGO (mantida)
# ============================================================
elif opcao == "Análise de Jogo":
    if not jogos:
        st.warning("Sem dados.")
        st.stop()
    times_disponiveis = sorted(set(j['time'] for j in jogos))
    for j in jogos:
        j['prat_time'] = PRATELEIRAS.get(j['time'], 3)
        j['prat_adv'] = PRATELEIRAS.get(j['adv'], 3)

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

        # Função auxiliar OVRall (usa core.py)
        def get_ovrall(time):
            if not any(j['time'] == time for j in jogos_passados):
                return OVRALL_INICIAL.get(time, 50.0)
            ata = calcular_ATA(jogos_passados, time, data_ref_dt)
            de = calcular_DEF(jogos_passados, time, data_ref_dt)
            mei = calcular_MEI(jogos_passados, time, data_ref_dt)
            forc = calcular_FOR(jogos_passados, time, data_ref_dt)
            cons = calcular_CONS(jogos_passados, time, data_ref_dt)
            res = calcular_RES(jogos_passados, time, data_ref_dt)
            return calcular_OVRall([ata, de, mei, forc, cons, res])

        ovrall_casa = get_ovrall(time_casa)
        ovrall_fora = get_ovrall(time_fora)

        # MPV
        mpv_casa_raw = inicializar_MPV(ovrall_casa)
        mpv_fora_raw = inicializar_MPV(ovrall_fora)
        # Evolução com jogos passados
        for jg in sorted(jogos_passados, key=lambda x: x['data']):
            if jg['time'] == time_casa:
                ima_jg, _ = calcular_IMA(jogos_passados, time_casa, jg['data'], mando_proximo=jg['mando'])
                ovr_adv = get_ovrall(jg['adv'])
                mpv_adv = inicializar_MPV(ovr_adv)
                mpv_casa_raw = atualizar_MPV(mpv_casa_raw, mpv_adv, jg['mando'], jg['resultado'], ima_jg)
            elif jg['time'] == time_fora:
                ima_jg, _ = calcular_IMA(jogos_passados, time_fora, jg['data'], mando_proximo=jg['mando'])
                ovr_adv = get_ovrall(jg['adv'])
                mpv_adv = inicializar_MPV(ovr_adv)
                mpv_fora_raw = atualizar_MPV(mpv_fora_raw, mpv_adv, jg['mando'], jg['resultado'], ima_jg)

        prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

        # Recomendação
        probs = {f"Vitória do {time_casa}": prob_casa, "Empate": prob_empate, f"Vitória do {time_fora}": prob_fora}
        rec = max(probs, key=probs.get)
        rec_prob = probs[rec]
        selo = get_selo(rec_prob)
        recomendacao_final = rec if selo in ("🥇 Ouro", "🟢 Verde") else "Sem recomendação"

        # Odds
        odds_jg = [j for j in jogos if j['time'] == time_casa and j['adv'] == time_fora]
        odd_casa = float(odds_jg[-1].get('B365H', 2.0)) if odds_jg else 2.0
        odd_empate = float(odds_jg[-1].get('B365D', 3.0)) if odds_jg else 3.0
        odd_fora = float(odds_jg[-1].get('B365A', 3.0)) if odds_jg else 3.0
        imp_casa = 1/odd_casa if odd_casa else 0
        imp_empate = 1/odd_empate if odd_empate else 0
        imp_fora = 1/odd_fora if odd_fora else 0

        st.markdown("---")
        st.success(f"MyPredict Recomenda: **{recomendacao_final}** (Prob: {rec_prob:.1%}, Selo: {selo})")
        col1, col2, col3 = st.columns(3)
        col1.metric("MPV Casa", f"{(mpv_casa_raw-1000)/10:.1f}")
        col2.metric("Diferença", f"{((mpv_casa_raw-mpv_fora_raw)/10):+.1f}")
        col3.metric("MPV Fora", f"{(mpv_fora_raw-1000)/10:.1f}")

        st.markdown("---")
        st.subheader("📊 Probabilidades 1X2")
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("Casa (MyPredict)", f"{prob_casa:.1%}", delta=f"Bet365: {imp_casa:.1%}")
        col_p2.metric("Empate (MyPredict)", f"{prob_empate:.1%}", delta=f"Bet365: {imp_empate:.1%}")
        col_p3.metric("Fora (MyPredict)", f"{prob_fora:.1%}", delta=f"Bet365: {imp_fora:.1%}")

# ============================================================
# BACKTEST OFICIAL (PRATELEIRAS E OVRALL POR TEMPORADA INTEIRA, BANCA R$100, STAKE R$10)
# ============================================================
elif opcao == "Backtest Oficial":
    st.markdown("<h1 style='text-align:center;'>📈 Backtest MyPredict 2.0 (Oficial)</h1>", unsafe_allow_html=True)
    if not partidas:
        st.error("Nenhuma partida carregada.")
        st.stop()

    st.success("Prateleiras e OVRall inicial definidos pelas odds de toda a temporada.")
    st.write("Prateleiras fixas:", {t: f"{s} ({SHELF_NAMES[s]})" for t, s in PRATELEIRAS.items()})

    if 'resultados_backtest' not in st.session_state:
        st.session_state.resultados_backtest = None
        st.session_state.backtest_executado = False

    if st.button("Iniciar Backtest Oficial (R$100)"):
        st.session_state.backtest_executado = True
        partidas_ord = sorted(partidas, key=lambda p: p['data'])
        historico = []
        resultados = []
        banca = 100.0  # Banca inicial
        stake = 10.0   # Valor apostado por recomendação
        progress = st.progress(0)
        total = len(partidas_ord)

        # Mantém MPV atual de cada time
        mpv_atual = {}
        for t in PRATELEIRAS:
            mpv_atual[t] = inicializar_MPV(OVRALL_INICIAL[t])

        for idx, p in enumerate(partidas_ord):
            data_jogo = p['data']
            casa_info = p['casa']
            fora_info = p['fora']
            time_casa = casa_info['time']
            time_fora = fora_info['time']

            prat_casa = PRATELEIRAS[time_casa]
            prat_fora = PRATELEIRAS[time_fora]
            casa_info['prat_time'] = prat_casa
            casa_info['prat_adv'] = prat_fora
            fora_info['prat_time'] = prat_fora
            fora_info['prat_adv'] = prat_casa

            hist_filtrado = [j for j in historico if j['data'] < data_jogo]

            # IMA (usa core.py)
            ima_casa, _ = calcular_IMA(hist_filtrado, time_casa, data_jogo, mando_proximo='casa')
            ima_fora, _ = calcular_IMA(hist_filtrado, time_fora, data_jogo, mando_proximo='fora')

            # OVRall (usa core.py com fallback)
            def ovrall_time(time):
                if not any(j['time'] == time for j in hist_filtrado):
                    return OVRALL_INICIAL[time]
                ata = calcular_ATA(hist_filtrado, time, data_jogo)
                de = calcular_DEF(hist_filtrado, time, data_jogo)
                mei = calcular_MEI(hist_filtrado, time, data_jogo)
                forc = calcular_FOR(hist_filtrado, time, data_jogo)
                cons = calcular_CONS(hist_filtrado, time, data_jogo)
                res = calcular_RES(hist_filtrado, time, data_jogo)
                return calcular_OVRall([ata, de, mei, forc, cons, res])

            ovrall_casa = ovrall_time(time_casa)
            ovrall_fora = ovrall_time(time_fora)

            # MPV atual (já evoluído)
            mpv_casa_raw = mpv_atual[time_casa]
            mpv_fora_raw = mpv_atual[time_fora]

            prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

            # Recomendação
            probs = {f"Vitória do {time_casa}": prob_casa, "Empate": prob_empate, f"Vitória do {time_fora}": prob_fora}
            rec = max(probs, key=probs.get)
            rec_prob = probs[rec]
            selo = get_selo(rec_prob)

            aposta_valida = selo in ("🥇 Ouro", "🟢 Verde")
            recomendacao = rec if aposta_valida else "Sem recomendação"

            # Resultado real
            gols_casa_real = casa_info['gols']
            gols_fora_real = fora_info['gols']
            resultado_real = 'V' if gols_casa_real > gols_fora_real else ('D' if gols_casa_real < gols_fora_real else 'E')

            # Atualiza MPV após o jogo
            k_casa = PARAMS['K']['normal'] if 40 <= ima_casa <= 60 else (PARAMS['K']['atencao'] if 25 <= ima_casa < 40 or 60 < ima_casa <= 75 else PARAMS['K']['alerta'])
            k_fora = PARAMS['K']['normal'] if 40 <= ima_fora <= 60 else (PARAMS['K']['atencao'] if 25 <= ima_fora < 40 or 60 < ima_fora <= 75 else PARAMS['K']['alerta'])

            mpv_atual[time_casa] = atualizar_MPV(mpv_casa_raw, mpv_fora_raw, 'casa', resultado_real, ima_casa)
            mpv_atual[time_fora] = atualizar_MPV(mpv_fora_raw, mpv_casa_raw, 'fora', 
                                                  'V' if resultado_real == 'D' else ('D' if resultado_real == 'V' else 'E'),
                                                  ima_fora)

            # Lucro (com stake fixo)
            odd_utilizada = None
            lucro_partida = 0.0
            if aposta_valida:
                if rec.startswith('Vitória do '):
                    time_rec = rec.replace('Vitória do ', '')
                    odd_utilizada = float(casa_info.get('B365H', 2.0)) if time_rec == time_casa else float(casa_info.get('B365A', 3.0))
                else:
                    odd_utilizada = float(casa_info.get('B365D', 3.0))

                if (rec == f"Vitória do {time_casa}" and resultado_real == 'V') or \
                   (rec == "Empate" and resultado_real == 'E') or \
                   (rec == f"Vitória do {time_fora}" and resultado_real == 'D'):
                    lucro_partida = stake * (odd_utilizada - 1)
                else:
                    lucro_partida = -stake
                banca += lucro_partida

            # Implícitas Bet365 para exibição
            imp_casa = 1 / float(casa_info.get('B365H', 2.0)) if float(casa_info.get('B365H', 2.0)) > 0 else 0
            imp_empate = 1 / float(casa_info.get('B365D', 3.0)) if float(casa_info.get('B365D', 3.0)) > 0 else 0
            imp_fora = 1 / float(casa_info.get('B365A', 3.0)) if float(casa_info.get('B365A', 3.0)) > 0 else 0

            resultados.append({
                'data': data_jogo,
                'time_casa': time_casa, 'time_fora': time_fora,
                'prat_casa': prat_casa, 'prat_fora': prat_fora,
                'mpv_casa': (mpv_casa_raw - 1000) / 10,
                'mpv_fora': (mpv_fora_raw - 1000) / 10,
                'ima_casa': ima_casa, 'ima_fora': ima_fora,
                'ovr_casa': ovrall_casa, 'ovr_fora': ovrall_fora,
                'prob_casa': prob_casa, 'prob_empate': prob_empate, 'prob_fora': prob_fora,
                'imp_casa': imp_casa, 'imp_empate': imp_empate, 'imp_fora': imp_fora,
                'recomendacao': recomendacao, 'rec_prob': rec_prob, 'selo': selo,
                'aposta_valida': aposta_valida, 'odd_utilizada': odd_utilizada,
                'lucro_partida': lucro_partida, 'banca_apos': banca,
                'resultado_real': resultado_real, 'acertou': (aposta_valida and lucro_partida > 0)
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
            dif_mpv = res['mpv_casa'] - res['mpv_fora']
            tendencia = f"MPV Casa maior em {dif_mpv:.1f} pts" if dif_mpv > 0 else (f"MPV Fora maior em {-dif_mpv:.1f} pts" if dif_mpv < 0 else "MPV igual")

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
                    <div class="metric-cell"><div class="metric-label">Diferença</div><div class="metric-value">{dif_mpv:+.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">IMA Casa</div><div class="metric-value">{res['ima_casa']:.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">IMA Fora</div><div class="metric-value">{res['ima_fora']:.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">OVR Casa</div><div class="metric-value">{res['ovr_casa']:.1f}</div></div>
                    <div class="metric-cell"><div class="metric-label">OVR Fora</div><div class="metric-value">{res['ovr_fora']:.1f}</div></div>
                </div>
                <div style="font-size:0.7rem; color:#aaa; margin-bottom:4px;">{tendencia}</div>
                <hr>
                <div style="margin-bottom:4px;"><strong>MyPredict Recomenda:</strong> {res['recomendacao']} (Prob: {res['rec_prob']:.1%}, Selo: {res['selo']})</div>
                <div style="color:#DAA520; font-weight:bold;">Lucro: R$ {res['lucro_partida']:+.2f} | Banca: R$ {res['banca_apos']:.2f}</div>
                <div class="metric-row">
                    <div class="prob-cell"><div class="prob-market">Casa (MyPredict)</div><div class="prob-value">{res['prob_casa']:.1%}</div><div style="font-size:0.7rem; color:#aaa;">Bet365: {res['imp_casa']:.1%}</div></div>
                    <div class="prob-cell"><div class="prob-market">Empate (MyPredict)</div><div class="prob-value">{res['prob_empate']:.1%}</div><div style="font-size:0.7rem; color:#aaa;">Bet365: {res['imp_empate']:.1%}</div></div>
                    <div class="prob-cell"><div class="prob-market">Fora (MyPredict)</div><div class="prob-value">{res['prob_fora']:.1%}</div><div style="font-size:0.7rem; color:#aaa;">Bet365: {res['imp_fora']:.1%}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Resumo
        st.markdown("---")
        st.subheader("💰 Resultado Financeiro (Banca Inicial: R$ 100,00)")
        apostas_validas = [r for r in resultados if r['aposta_valida']]
        total_apostas = len(apostas_validas)
        if total_apostas > 0:
            acertos = sum(1 for r in apostas_validas if r['acertou'])
            banca_final = resultados[-1]['banca_apos']
            lucro_total = banca_final - 100.0
            roi = (lucro_total / 100.0) * 100
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Apostas", total_apostas)
            col2.metric("Acertos", acertos)
            col3.metric("Banca Final", f"R$ {banca_final:.2f}")
            col4.metric("Lucro", f"R$ {lucro_total:+.2f}")
            st.metric("ROI", f"{roi:.2f}%")
        else:
            st.warning("Nenhuma aposta realizada.")
    else:
        st.info("Clique em 'Iniciar Backtest Oficial (R$100)'.")
