"""
MyPredict 2.0 – Aplicativo Completo (Parte 1: Conversor, Análise de Jogo, Setup)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial
import os

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
    .card { background-color: #1E1E1E; border-left: 4px solid #DAA520; padding: 15px; margin: 10px 0; border-radius: 8px; }
    .card-header { display: flex; justify-content: space-between; align-items: center; }
    .team-name { font-size: 1.2rem; color: #DAA520; }
    .score { font-size: 2rem; font-weight: bold; color: #fff; }
    .metric-row { display: flex; justify-content: space-between; margin: 8px 0; }
    .metric-item { text-align: center; flex: 1; }
    .metric-value { font-size: 1.5rem; color: #DAA520; }
    .metric-label { font-size: 0.8rem; color: #aaa; }
    .acerto { font-size: 2rem; }
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
# CONVERSOR
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
            dfs = []
            for arquivo in arquivos_raw:
                caminho = os.path.join(raw_path, arquivo)
                try:
                    df_temp = pd.read_csv(caminho, header=None, skiprows=1, encoding='utf-8-sig', sep=None, engine='python')
                    dfs.append(df_temp)
                except Exception as e:
                    st.error(f"Erro ao ler {arquivo}: {e}")
            if not dfs:
                st.stop()
            df = pd.concat(dfs, ignore_index=True)
            COL_DATE = 1; COL_HOME = 3; COL_AWAY = 4; COL_FTHG = 5; COL_FTAG = 6; COL_FTR = 7
            COL_HS = 12; COL_AS = 13; COL_HST = 14; COL_AST = 15; COL_HF = 16; COL_AF = 17
            COL_HC = 18; COL_AC = 19; COL_HY = 20; COL_AY = 21; COL_HR = 22; COL_AR = 23
            COL_B365H = 24; COL_B365D = 25; COL_B365A = 26

            linhas = []
            for _, jogo in df.iterrows():
                try:
                    data_str = str(jogo.iloc[COL_DATE]).split(' ')[0]
                    data = pd.to_datetime(data_str, format='%d/%m/%Y', exact=False).strftime('%Y-%m-%d')
                    home = str(jogo.iloc[COL_HOME]).strip(); away = str(jogo.iloc[COL_AWAY]).strip()
                    fthg = int(jogo.iloc[COL_FTHG]); ftag = int(jogo.iloc[COL_FTAG]); ftr = str(jogo.iloc[COL_FTR]).strip()
                    def res_casa(r): return 'V' if r == 'H' else ('D' if r == 'A' else 'E')
                    def res_fora(r): return 'V' if r == 'A' else ('D' if r == 'H' else 'E')
                    hst = float(jogo.iloc[COL_HST]) if not pd.isna(jogo.iloc[COL_HST]) else 0
                    ast = float(jogo.iloc[COL_AST]) if not pd.isna(jogo.iloc[COL_AST]) else 0
                    hs  = float(jogo.iloc[COL_HS]) if not pd.isna(jogo.iloc[COL_HS]) else 0
                    as_ = float(jogo.iloc[COL_AS]) if not pd.isna(jogo.iloc[COL_AS]) else 0
                    hc  = float(jogo.iloc[COL_HC]) if not pd.isna(jogo.iloc[COL_HC]) else 0
                    ac  = float(jogo.iloc[COL_AC]) if not pd.isna(jogo.iloc[COL_AC]) else 0
                    hf  = float(jogo.iloc[COL_HF]) if not pd.isna(jogo.iloc[COL_HF]) else 0
                    af  = float(jogo.iloc[COL_AF]) if not pd.isna(jogo.iloc[COL_AF]) else 0
                    hy  = int(jogo.iloc[COL_HY]) if not pd.isna(jogo.iloc[COL_HY]) else 0
                    ay  = int(jogo.iloc[COL_AY]) if not pd.isna(jogo.iloc[COL_AY]) else 0
                    hr  = int(jogo.iloc[COL_HR]) if not pd.isna(jogo.iloc[COL_HR]) else 0
                    ar  = int(jogo.iloc[COL_AR]) if not pd.isna(jogo.iloc[COL_AR]) else 0
                    b365h = float(jogo.iloc[COL_B365H]) if not pd.isna(jogo.iloc[COL_B365H]) else 2.0
                    b365d = float(jogo.iloc[COL_B365D]) if not pd.isna(jogo.iloc[COL_B365D]) else 3.0
                    b365a = float(jogo.iloc[COL_B365A]) if not pd.isna(jogo.iloc[COL_B365A]) else 3.0
                except Exception:
                    continue
                linhas.append({
                    'data': data, 'time': home, 'adv': away, 'mando': 'casa',
                    'resultado': res_casa(ftr), 'gols': fthg, 'gols_sofridos': ftag,
                    'prat_time': 3, 'prat_adv': 3,
                    'finalizacoes_alvo': hst, 'finalizacoes_totais': hs,
                    'escanteios': hc, 'faltas_sofridas': af, 'faltas_cometidas': hf,
                    'cartoes_amarelos': hy, 'cartoes_vermelhos': hr,
                    'B365H': b365h, 'B365D': b365d, 'B365A': b365a
                })
                linhas.append({
                    'data': data, 'time': away, 'adv': home, 'mando': 'fora',
                    'resultado': res_fora(ftr), 'gols': ftag, 'gols_sofridos': fthg,
                    'prat_time': 3, 'prat_adv': 3,
                    'finalizacoes_alvo': ast, 'finalizacoes_totais': as_,
                    'escanteios': ac, 'faltas_sofridas': hf, 'faltas_cometidas': af,
                    'cartoes_amarelos': ay, 'cartoes_vermelhos': ar,
                    'B365H': b365h, 'B365D': b365d, 'B365A': b365a
                })
            if linhas:
                df_final = pd.DataFrame(linhas)
                st.success(f"Conversão concluída! {len(df_final)} linhas.")
                st.download_button("📥 Baixar meus_jogos.csv", df_final.to_csv(index=False), file_name="meus_jogos.csv")
            else:
                st.error("Nenhuma linha convertida.")

# ============================================================
# ANÁLISE DE JOGO (MANTIDA)
# ============================================================
elif opcao == "Análise de Jogo":
    if not jogos:
        st.warning("Sem dados.")
        st.stop()
    times_disponiveis = sorted(set(j['time'] for j in jogos))
    # Prateleiras pela classificação da temporada completa (para análise)
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
        if ('Dourado' in selo_casa or 'Verde' in selo_casa) and edge_casa > 0:
            rec = f"Vitória {time_casa}"; rec_prob = prob_casa; rec_selo = selo_casa
        elif ('Dourado' in selo_empate or 'Verde' in selo_empate) and edge_empate > 0:
            rec = "Empate"; rec_prob = prob_empate; rec_selo = selo_empate
        elif ('Dourado' in selo_fora or 'Verde' in selo_fora) and edge_fora > 0:
            rec = f"Vitória {time_fora}"; rec_prob = prob_fora; rec_selo = selo_fora

        st.markdown("---")
        if rec:
            st.markdown(f"""<div class="recomendacao"><h3 style="color:#DAA520;">MyPredict Recomenda</h3><p style="font-size:1.5rem;">{rec}</p><p>Probabilidade: {rec_prob:.1%}</p><p>Selo: {rec_selo}</p></div>""", unsafe_allow_html=True)
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
# BACKTEST VISUAL (CORRIGIDO – SEM EDGE NA RECOMENDAÇÃO, MPV DESTACADO)
# ============================================================
elif opcao == "Backtest Visual":
    st.markdown("<h1 style='text-align:center;'>📈 Backtest MyPredict 2.0</h1>", unsafe_allow_html=True)
    if not partidas:
        st.error("Nenhuma partida carregada.")
        st.stop()

    # --- 1. Prateleiras fixas (classificação da temporada anterior) ---
    todas_datas = sorted([p['data'] for p in partidas])
    data_inicio_temporada = todas_datas[0]
    jogos_anteriores = [j for j in jogos if j['data'] < data_inicio_temporada]
    if len(jogos_anteriores) > 0:
        prateleiras_fixas = classification_to_shelves(jogos_anteriores)
        st.info("Prateleiras definidas a partir da temporada anterior.")
    else:
        prateleiras_fixas = classification_to_shelves(jogos)
        st.warning("Sem temporada anterior. Prateleiras definidas pela classificação geral.")

    st.write("Prateleiras fixas:")
    st.write({t: f"Prateleira {p}" for t, p in prateleiras_fixas.items()})

    # --- 2. Simulação ---
    if st.button("Iniciar Backtest Completo"):
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

            # Prateleiras fixas
            casa_info['prat_time'] = prateleiras_fixas.get(time_casa, 3)
            casa_info['prat_adv'] = prateleiras_fixas.get(time_fora, 3)
            fora_info['prat_time'] = prateleiras_fixas.get(time_fora, 3)
            fora_info['prat_adv'] = prateleiras_fixas.get(time_casa, 3)

            hist_filtrado = [j for j in historico if j['data'] < data_jogo]

            # IMA
            ima_casa, desvio_casa = calcular_IMA(hist_filtrado, time_casa, data_jogo, mando_proximo='casa')
            ima_fora, desvio_fora = calcular_IMA(hist_filtrado, time_fora, data_jogo, mando_proximo='fora')
            desvio_medio = (desvio_casa + desvio_fora) / 2

            # OVRall
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

            # MPV
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

            # Recomendação APENAS pelo selo (sem Edge > 0)
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

            acertou = False
            if recomendacao:
                if (recomendacao == f"Vitória {time_casa}" and resultado_real == 'V') or \
                   (recomendacao == "Empate" and resultado_real == 'E') or \
                   (recomendacao == f"Vitória {time_fora}" and resultado_real == 'D'):
                    acertou = True

            # Mercados adicionais
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

        # --- 3. Exibição dos Cards ---
        st.markdown("---")
        st.subheader("📋 Resultados das Partidas")
        for res in resultados:
            # Barra de MPV comparativa
            total_mpv = res['mpv_casa'] + res['mpv_fora']
            if total_mpv == 0:
                perc_casa = 50
                perc_fora = 50
            else:
                perc_casa = (res['mpv_casa'] / total_mpv) * 100
                perc_fora = 100 - perc_casa

            mpv_bar_html = f"""
            <div style="display:flex; align-items:center; margin:10px 0;">
                <span style="width:100px; color:#DAA520; font-weight:bold;">{res['time_casa']} ({res['mpv_casa']:.1f})</span>
                <div style="flex:1; background:#333; height:20px; border-radius:10px; overflow:hidden; display:flex;">
                    <div style="width:{perc_casa}%; background:#DAA520; height:100%;"></div>
                    <div style="width:{perc_fora}%; background:#888; height:100%;"></div>
                </div>
                <span style="width:100px; text-align:right; color:#DAA520; font-weight:bold;">({res['mpv_fora']:.1f}) {res['time_fora']}</span>
            </div>
            """

            with st.container():
                st.markdown(f"""
                <div class="card">
                    <div class="card-header">
                        <div>
                            <span class="team-name">{res['time_casa']} vs {res['time_fora']}</span><br>
                            <small>{res['data'].strftime('%d/%m/%Y')}</small>
                        </div>
                        <div class="score">{res['resultado_real']}</div>
                        <div class="acerto">{'✅' if res['recomendacao'] and res['acertou'] else ('❌' if res['recomendacao'] else '')}</div>
                    </div>
                    <!-- Comparação MPV em destaque -->
                    {mpv_bar_html}
                    <!-- Métricas principais -->
                    <div class="metric-row">
                        <div class="metric-item"><div class="metric-label">IMA Casa</div><div class="metric-value">{res['ima_casa']:.1f}</div></div>
                        <div class="metric-item"><div class="metric-label">IMA Fora</div><div class="metric-value">{res['ima_fora']:.1f}</div></div>
                        <div class="metric-item"><div class="metric-label">OVR Casa</div><div class="metric-value">{res['ovr_casa']:.1f}</div></div>
                        <div class="metric-item"><div class="metric-label">OVR Fora</div><div class="metric-value">{res['ovr_fora']:.1f}</div></div>
                    </div>
                    <!-- Probabilidades 1X2 (MyPredict vs Bet365) -->
                    <div class="metric-row">
                        <div class="metric-item">
                            <div class="metric-label">Casa (MyPredict)</div>
                            <div class="metric-value">{res['prob_casa']:.1%}</div>
                            <small>Bet365: {res['imp_casa']:.1%}</small>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Empate (MyPredict)</div>
                            <div class="metric-value">{res['prob_empate']:.1%}</div>
                            <small>Bet365: {res['imp_empate']:.1%}</small>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Fora (MyPredict)</div>
                            <div class="metric-value">{res['prob_fora']:.1%}</div>
                            <small>Bet365: {res['imp_fora']:.1%}</small>
                        </div>
                    </div>
                    <!-- Edge e Selos -->
                    <div class="metric-row">
                        <div class="metric-item"><div class="metric-label">Edge Casa</div><div class="metric-value">{res['edge_casa']:+.1%}</div><small>{res['selo_casa']}</small></div>
                        <div class="metric-item"><div class="metric-label">Edge Empate</div><div class="metric-value">{res['edge_empate']:+.1%}</div><small>{res['selo_empate']}</small></div>
                        <div class="metric-item"><div class="metric-label">Edge Fora</div><div class="metric-value">{res['edge_fora']:+.1%}</div><small>{res['selo_fora']}</small></div>
                    </div>
                    <!-- Recomendação -->
                    <div style="margin-top:10px;">
                        <strong>MyPredict Recomenda:</strong>
                        {f"{res['recomendacao']} (Prob: {res['rec_prob']:.1%}, Selo: {res['rec_selo']})" if res['recomendacao'] else "Nenhuma"}
                    </div>
                    <!-- Outros mercados -->
                    <div class="metric-row" style="margin-top:10px;">
                        <div class="metric-item"><div class="metric-label">Over 1.5 (MYP)</div><div class="metric-value">{res['over15_prob']:.1%}</div><small>{'✅' if res['over15_real'] else '❌'}</small></div>
                        <div class="metric-item"><div class="metric-label">Over 2.5 (MYP)</div><div class="metric-value">{res['over25_prob']:.1%}</div><small>{'✅' if res['over25_real'] else '❌'}</small></div>
                        <div class="metric-item"><div class="metric-label">BTTS (MYP)</div><div class="metric-value">{res['btts_prob']:.1%}</div><small>{'✅' if res['btts_real'] else '❌'}</small></div>
                        <div class="metric-item"><div class="metric-label">Esc. >9.5 (MYP)</div><div class="metric-value">{res['esc_prob']:.1%}</div><small>{'✅' if res['esc_real'] else '❌'}</small></div>
                    </div>
                    <div class="metric-row">
                        <div class="metric-item"><div class="metric-label">HT Over 0.5 (MYP)</div><div class="metric-value">{res['ht_over05_prob']:.1%}</div></div>
                        <div class="metric-item"><div class="metric-label">HT Over 1.5 (MYP)</div><div class="metric-value">{res['ht_over15_prob']:.1%}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # --- 4. Resumo Geral ---
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
