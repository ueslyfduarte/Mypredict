"""
MyPredict 2.0 - Aplicativo Completo com Backtest Realista (Prateleiras Fixas)
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
    .mpv-destaque { font-size:3rem; color:#DAA520; text-align:center; }
    .recomendacao { background-color: #1E1E1E; border-left: 4px solid #DAA520; padding: 10px; margin: 10px 0; border-radius: 5px; }
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
# MENU LATERAL
# ============================================================
st.sidebar.markdown("<h2 style='color:#DAA520;'>⚽ MyPredict 2.0</h2>", unsafe_allow_html=True)
opcao = st.sidebar.radio("Modo", ["Análise de Jogo", "Backtest Realista", "Converter Dados Brutos"])

# ============================================================
# CONVERSOR (mantido funcional)
# ============================================================
if opcao == "Converter Dados Brutos":
    st.markdown("<h1 style='text-align:center;'>🔄 Conversor de CSV</h1>", unsafe_allow_html=True)
    st.markdown("Converte os arquivos da pasta `data/raw/` para o formato MyPredict.")
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
                    home = str(jogo.iloc[COL_HOME]).strip()
                    away = str(jogo.iloc[COL_AWAY]).strip()
                    fthg = int(jogo.iloc[COL_FTHG])
                    ftag = int(jogo.iloc[COL_FTAG])
                    ftr = str(jogo.iloc[COL_FTR]).strip()
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
                st.success(f"MyPredict: Conversão concluída! {len(df_final)} linhas geradas.")
                st.dataframe(df_final.head(10))
                csv_exportado = df_final.to_csv(index=False)
                st.download_button("📥 Baixar meus_jogos.csv", csv_exportado, file_name="meus_jogos.csv")
                st.info("Após baixar, substitua o arquivo `data/meus_jogos.csv` no GitHub pelo novo conteúdo. Use Upload file para evitar corromper.")
            else:
                st.error("Nenhuma linha foi convertida.")

# ============================================================
# ANÁLISE DE JOGO (mantida)
# ============================================================
elif opcao == "Análise de Jogo":
    if not jogos:
        st.warning("Sem dados. Faça a conversão primeiro.")
        st.stop()
    times_disponiveis = sorted(set(j['time'] for j in jogos))
    # Prateleiras (usando odds médias como proxy)
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
            if not jogos_time:
                return inicializar_MPV(50.0)
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
            st.markdown(f"""
            <div class="recomendacao">
                <h3 style="color:#DAA520;">MyPredict Recomenda</h3>
                <p style="font-size:1.5rem;">{rec}</p>
                <p>Probabilidade: {rec_prob:.1%}</p>
                <p>Selo: {rec_selo}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Sem recomendação de alto valor para este jogo.")
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
        gols_casa = media_gols(time_casa, 'marcados')
        sofridos_fora = media_gols(time_fora, 'sofridos')
        gols_fora = media_gols(time_fora, 'marcados')
        sofridos_casa = media_gols(time_casa, 'sofridos')
        media_total = (gols_casa + sofridos_fora)/2 + (gols_fora + sofridos_casa)/2
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Over 1.5 gols", f"{prob_over(media_total, 1.5):.1%}")
        col2.metric("Over 2.5 gols", f"{prob_over(media_total, 2.5):.1%}")
        col3.metric("Ambas Marcam", f"{prob_btts(ata_casa, def_fora, ata_fora, def_casa):.1%}")
        esc_casa = for_casa/5 if for_casa else 4
        esc_fora = for_fora/5 if for_fora else 4
        total_esc = esc_casa + esc_fora
        col4.metric("Over 9.5 esc.", f"{prob_over(total_esc, 8.5):.1%}")

# ============================================================
# BACKTEST REALISTA CORRIGIDO
# ============================================================
elif opcao == "Backtest Realista":
    st.markdown("<h1 style='text-align:center;'>📈 Backtest MyPredict 2.0</h1>", unsafe_allow_html=True)
    if not partidas:
        st.error("Nenhuma partida carregada.")
        st.stop()
    st.write(f"Total de partidas: {len(partidas)}")

    # Definir prateleiras fixas baseadas nas odds iniciais
    odds_iniciais = {}
    for p in partidas:
        for info in [p['casa'], p['fora']]:
            time = info['time']
            if time not in odds_iniciais:
                try:
                    odd_casa = float(info.get('B365H', 3.0))
                    odd_fora = float(info.get('B365A', 3.0))
                    odds_iniciais[time] = min(odd_casa, odd_fora)
                except:
                    odds_iniciais[time] = 3.0
    times_ordenados = sorted(odds_iniciais, key=lambda t: odds_iniciais[t])
    n = len(times_ordenados)
    prateleiras_fixas = {}
    for i, t in enumerate(times_ordenados):
        if i < n * 0.15: prateleiras_fixas[t] = 1
        elif i < n * 0.35: prateleiras_fixas[t] = 2
        elif i < n * 0.65: prateleiras_fixas[t] = 3
        elif i < n * 0.85: prateleiras_fixas[t] = 4
        else: prateleiras_fixas[t] = 5
    st.write("Prateleiras fixas definidas (pré-temporada):")
    st.write({t: f"Prateleira {p}" for t, p in prateleiras_fixas.items()})

    if st.button("Iniciar Simulação Completa"):
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

            # Atribuir prateleiras fixas
            casa_info['prat_time'] = prateleiras_fixas[time_casa]
            casa_info['prat_adv'] = prateleiras_fixas[time_fora]
            fora_info['prat_time'] = prateleiras_fixas[time_fora]
            fora_info['prat_adv'] = prateleiras_fixas[time_casa]

            hist_filtrado = [j for j in historico if j['data'] < data_jogo]

            # IMA
            ima_casa, _ = calcular_IMA(hist_filtrado, time_casa, data_jogo, mando_proximo='casa')
            ima_fora, _ = calcular_IMA(hist_filtrado, time_fora, data_jogo, mando_proximo='fora')

            # OVRall
            ata_casa = calcular_ATA(hist_filtrado, time_casa, data_jogo)
            def_casa = calcular_DEF(hist_filtrado, time_casa, data_jogo)
            mei_casa = calcular_MEI(hist_filtrado, time_casa, data_jogo)
            for_casa = calcular_FOR(hist_filtrado, time_casa, data_jogo)
            cons_casa = calcular_CONS(hist_filtrado, time_casa, data_jogo)
            res_casa = calcular_RES(hist_filtrado, time_casa, data_jogo)
            ovrall_casa = calcular_OVRall([ata_casa, def_casa, mei_casa, for_casa, cons_casa, res_casa])

            ata_fora = calcular_ATA(hist_filtrado, time_fora, data_jogo)
            def_fora = calcular_DEF(hist_filtrado, time_fora, data_jogo)
            mei_fora = calcular_MEI(hist_filtrado, time_fora, data_jogo)
            for_fora = calcular_FOR(hist_filtrado, time_fora, data_jogo)
            cons_fora = calcular_CONS(hist_filtrado, time_fora, data_jogo)
            res_fora = calcular_RES(hist_filtrado, time_fora, data_jogo)
            ovrall_fora = calcular_OVRall([ata_fora, def_fora, mei_fora, for_fora, cons_fora, res_fora])

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

            # Probabilidades 1X2
            prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

            # Odds
            odd_casa = casa_info.get('B365H', 2.0)
            odd_empate = casa_info.get('B365D', 3.0)
            odd_fora = casa_info.get('B365A', 3.0)

            # Edge e Selos
            edge_casa = calcular_edge(prob_casa, odd_casa)
            edge_empate = calcular_edge(prob_empate, odd_empate)
            edge_fora = calcular_edge(prob_fora, odd_fora)
            dif_mpv = abs(mpv_casa_raw + 75 - mpv_fora_raw)
            desvio_ima = 10
            selo_casa = determinar_selo(edge_casa, dif_mpv, desvio_ima)
            selo_empate = determinar_selo(edge_empate, dif_mpv, desvio_ima)
            selo_fora = determinar_selo(edge_fora, dif_mpv, desvio_ima)

            # Recomendação
            recomendacao = None
            rec_prob = 0
            rec_odd = 0
            rec_selo = ""
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

            # Resultados reais
            gols_casa_real = casa_info['gols']
            gols_fora_real = fora_info['gols']
            resultado_real = 'V' if gols_casa_real > gols_fora_real else ('D' if gols_casa_real < gols_fora_real else 'E')
            total_gols = gols_casa_real + gols_fora_real
            over15_real = total_gols > 1.5
            over25_real = total_gols > 2.5
            btts_real = gols_casa_real > 0 and gols_fora_real > 0
            esc_casa_real = casa_info.get('escanteios', 0)
            esc_fora_real = fora_info.get('escanteios', 0)
            over9_5_esc_real = (esc_casa_real + esc_fora_real) > 9.5

            acertou = False
            if recomendacao:
                if (recomendacao == f"Vitória {time_casa}" and resultado_real == 'V') or \
                   (recomendacao == "Empate" and resultado_real == 'E') or \
                   (recomendacao == f"Vitória {time_fora}" and resultado_real == 'D'):
                    acertou = True

            # Médias históricas
            def media_hist(time, tipo):
                jogos_time = [j for j in hist_filtrado if j['time'] == time]
                if not jogos_time:
                    return 1.0 if tipo != 'escanteios' else 4.0
                if tipo == 'marcados':
                    return sum(j.get('gols', 0) for j in jogos_time) / len(jogos_time)
                elif tipo == 'sofridos':
                    return sum(j.get('gols_sofridos', 0) for j in jogos_time) / len(jogos_time)
                elif tipo == 'escanteios':
                    return sum(j.get('escanteios', 0) for j in jogos_time) / len(jogos_time)

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
            prob_bt = prob_btts(ata_casa, def_fora, ata_fora, def_casa)
            prob_over9_5_esc = prob_over(media_esc_total, 9.5)

            resultados.append({
                'Data': data_jogo.strftime('%Y-%m-%d'),
                'Mandante': time_casa,
                'Visitante': time_fora,
                'MyPredict Recomenda': recomendacao if recomendacao else 'Nenhuma',
                'Probabilidade': f"{rec_prob:.1%}" if recomendacao else '-',
                'Selo': rec_selo if recomendacao else '-',
                'Odd': f"{rec_odd:.2f}" if recomendacao else '-',
                'Resultado': resultado_real,
                'Acertou?': '✅' if recomendacao and acertou else ('❌' if recomendacao else '-'),
                'Over 1.5 Prob': f"{prob_over15:.1%}",
                'Over 1.5 Real': '✅' if over15_real else '❌',
                'Over 2.5 Prob': f"{prob_over25:.1%}",
                'Over 2.5 Real': '✅' if over25_real else '❌',
                'BTTS Prob': f"{prob_bt:.1%}",
                'BTTS Real': '✅' if btts_real else '❌',
                'Esc. >9.5 Prob': f"{prob_over9_5_esc:.1%}",
                'Esc. >9.5 Real': '✅' if over9_5_esc_real else '❌'
            })

            historico.append(casa_info)
            historico.append(fora_info)
            progress.progress((idx + 1) / total)

        if resultados:
            df_res = pd.DataFrame(resultados)
            st.dataframe(df_res, use_container_width=True)

            st.markdown("---")
            st.subheader("📊 Desempenho do MyPredict na Temporada")
            df_apostas = df_res[df_res['MyPredict Recomenda'] != 'Nenhuma']
            total_apostas = len(df_apostas)
            if total_apostas > 0:
                acertos = len(df_apostas[df_apostas['Acertou?'] == '✅'])
                taxa_acerto = (acertos / total_apostas) * 100
                lucro = sum([float(row['Odd']) - 1 if row['Acertou?'] == '✅' else -1 for _, row in df_apostas.iterrows()])
                roi = (lucro / total_apostas) * 100

                col1, col2, col3, col4 = st.columns(4)
                with col1: st.metric("Apostas MyPredict", total_apostas)
                with col2: st.metric("Acertos", acertos)
                with col3: st.metric("Taxa de Acerto", f"{taxa_acerto:.1f}%")
                with col4: st.metric("Lucro/Prejuízo", f"{lucro:+.2f} unidades")
                st.metric("ROI", f"{roi:.2f}%")
            else:
                st.warning("Nenhuma aposta foi recomendada. Os critérios de selo podem estar muito rigorosos. Ajuste os limiares em PARAMS.")
        else:
            st.error("Nenhum resultado gerado.")
