"""
MyPredict 2.0 - Aplicativo Completo (Conversor com Diagnóstico)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial
import os
import re

# ============================================================
# CONFIGURAÇÃO
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
# CARREGAR DADOS PROCESSADOS
# ============================================================
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("data/meus_jogos.csv", parse_dates=["data"])
        return df.to_dict(orient="records")
    except FileNotFoundError:
        return []

jogos = carregar_dados()

# ============================================================
# MENU LATERAL
# ============================================================
st.sidebar.markdown("<h2 style='color:#DAA520;'>⚽ MyPredict 2.0</h2>", unsafe_allow_html=True)
opcao = st.sidebar.radio("Modo", ["Análise de Jogo", "Backtest", "Converter Dados Brutos"])

# ============================================================
# CONVERSOR ROBUSTO COM DIAGNÓSTICO
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
                    # Lê o CSV sem forçar colunas, detectando separador
                    df_temp = pd.read_csv(caminho, encoding='utf-8-sig', sep=None, engine='python')
                    # Remove espaços dos nomes das colunas
                    df_temp.columns = df_temp.columns.str.strip()
                    dfs.append(df_temp)
                except Exception as e:
                    st.error(f"Erro ao ler {arquivo}: {e}")

            if not dfs:
                st.stop()

            df = pd.concat(dfs, ignore_index=True)

            # Mostrar colunas disponíveis
            st.write("Colunas encontradas no CSV original:", list(df.columns))

            # Função para encontrar coluna por palavras-chave (regex)
            def find_col(patterns):
                for col in df.columns:
                    col_lower = col.lower()
                    for pat in patterns:
                        if re.search(pat, col_lower):
                            return col
                return None

            # Mapeamento necessário com expressões regulares flexíveis
            col_date = find_col([r'date', r'dia', r'data'])
            col_home = find_col([r'hometeam', r'home', r'ht', r'casa', r'mandante'])
            col_away = find_col([r'awayteam', r'away', r'at', r'fora', r'visitante'])
            col_ftr = find_col([r'ftr', r'result', r'resultado'])
            col_fthg = find_col([r'fthg', r'homegoals', r'hg', r'golsmandante'])
            col_ftag = find_col([r'ftag', r'awaygoals', r'ag', r'golsvisitante'])
            col_hs = find_col([r'hs', r'homeshots', r'chutesmandante'])
            col_as_ = find_col([r'as', r'awayshots', r'chutesvisitante'])
            col_hst = find_col([r'hst', r'homeshotsontarget', r'shotsonmandante'])
            col_ast = find_col([r'ast', r'awayshotsontarget', r'shotsonvisitante'])
            col_hf = find_col([r'hf', r'homefouls', r'faltasmandante'])
            col_af = find_col([r'af', r'awayfouls', r'faltasvisitante'])
            col_hc = find_col([r'hc', r'homecorners', r'escanteiosmandante'])
            col_ac = find_col([r'ac', r'awaycorners', r'escanteiosvisitante'])
            col_hy = find_col([r'hy', r'homeyellow', r'amarelosmandante'])
            col_ay = find_col([r'ay', r'awayyellow', r'amarelosvisitante'])
            col_hr = find_col([r'hr', r'homered', r'vermelhosmandante'])
            col_ar = find_col([r'ar', r'awayred', r'vermelhosvisitante'])
            col_b365h = find_col([r'b365h', r'bet365h'])
            col_b365d = find_col([r'b365d', r'bet365d'])
            col_b365a = find_col([r'b365a', r'bet365a'])

            # Verifica se todas as colunas essenciais foram encontradas
            erros = []
            if not col_date: erros.append("Data (Date)")
            if not col_home: erros.append("Time Mandante (HomeTeam)")
            if not col_away: erros.append("Time Visitante (AwayTeam)")
            if not col_ftr: erros.append("Resultado (FTR)")
            if not col_fthg: erros.append("Gols Mandante (FTHG)")
            if not col_ftag: erros.append("Gols Visitante (FTAG)")

            if erros:
                st.error(f"Colunas essenciais não encontradas: {', '.join(erros)}.")
                st.stop()

            # Converter data
            try:
                df[col_date] = df[col_date].astype(str).str.split(' ').str[0]
                df[col_date] = pd.to_datetime(df[col_date], format='%d/%m/%Y', exact=False).dt.strftime('%Y-%m-%d')
            except Exception as e:
                st.error(f"Erro ao processar datas: {e}")
                st.stop()

            # Funções de resultado
            def res_casa(r):
                return 'V' if r == 'H' else ('D' if r == 'A' else 'E')
            def res_fora(r):
                return 'V' if r == 'A' else ('D' if r == 'H' else 'E')

            linhas = []
            for _, jogo in df.iterrows():
                try:
                    fthg = int(jogo[col_fthg])
                    ftag = int(jogo[col_ftag])
                    hst = float(jogo.get(col_hst, 0)) if col_hst else 0.0
                    ast = float(jogo.get(col_ast, 0)) if col_ast else 0.0
                    hs  = float(jogo.get(col_hs, 0)) if col_hs else 0.0
                    as_ = float(jogo.get(col_as_, 0)) if col_as_ else 0.0
                    hc  = float(jogo.get(col_hc, 0)) if col_hc else 0.0
                    ac  = float(jogo.get(col_ac, 0)) if col_ac else 0.0
                    hf  = float(jogo.get(col_hf, 0)) if col_hf else 0.0
                    af  = float(jogo.get(col_af, 0)) if col_af else 0.0
                    hy  = int(jogo.get(col_hy, 0)) if col_hy else 0
                    ay  = int(jogo.get(col_ay, 0)) if col_ay else 0
                    hr  = int(jogo.get(col_hr, 0)) if col_hr else 0
                    ar  = int(jogo.get(col_ar, 0)) if col_ar else 0
                    b365h = float(jogo.get(col_b365h, 2.0)) if col_b365h else 2.0
                    b365d = float(jogo.get(col_b365d, 3.0)) if col_b365d else 3.0
                    b365a = float(jogo.get(col_b365a, 3.0)) if col_b365a else 3.0
                except Exception as e:
                    st.warning(f"Erro em uma linha: {e}")
                    continue

                mandante = {
                    'data': jogo[col_date],
                    'time': jogo[col_home],
                    'adv': jogo[col_away],
                    'mando': 'casa',
                    'resultado': res_casa(jogo[col_ftr]),
                    'gols': fthg,
                    'gols_sofridos': ftag,
                    'prat_time': 3, 'prat_adv': 3,
                    'finalizacoes_alvo': hst,
                    'finalizacoes_totais': hs,
                    'escanteios': hc,
                    'faltas_sofridas': af,
                    'faltas_cometidas': hf,
                    'cartoes_amarelos': hy,
                    'cartoes_vermelhos': hr,
                    'B365H': b365h, 'B365D': b365d, 'B365A': b365a
                }
                visitante = {
                    'data': jogo[col_date],
                    'time': jogo[col_away],
                    'adv': jogo[col_home],
                    'mando': 'fora',
                    'resultado': res_fora(jogo[col_ftr]),
                    'gols': ftag,
                    'gols_sofridos': fthg,
                    'prat_time': 3, 'prat_adv': 3,
                    'finalizacoes_alvo': ast,
                    'finalizacoes_totais': as_,
                    'escanteios': ac,
                    'faltas_sofridas': hf,
                    'faltas_cometidas': af,
                    'cartoes_amarelos': ay,
                    'cartoes_vermelhos': ar,
                    'B365H': b365h, 'B365D': b365d, 'B365A': b365a
                }
                linhas.append(mandante)
                linhas.append(visitante)

            if linhas:
                df_final = pd.DataFrame(linhas)
                st.success(f"Conversão concluída! {len(df_final)} linhas geradas.")
                st.dataframe(df_final.head(10))
                csv_exportado = df_final.to_csv(index=False)
                st.download_button("📥 Baixar meus_jogos.csv", csv_exportado, file_name="meus_jogos.csv")
                st.info("Após baixar, substitua o arquivo `data/meus_jogos.csv` no GitHub pelo novo conteúdo.")
            else:
                st.error("Nenhuma linha foi convertida. Verifique o conteúdo dos CSVs.")

# ============================================================
# ANÁLISE DE JOGO
# ============================================================
elif opcao == "Análise de Jogo":
    if not jogos:
        st.warning("Arquivo 'data/meus_jogos.csv' não encontrado. Execute a conversão primeiro.")
        st.stop()
    
    times_disponiveis = sorted(set(j['time'] for j in jogos))
    
    # Atribuir prateleiras
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
            st.subheader(time_casa)
            st.metric("MPV", f"{mpv_casa:.1f}")
            st.metric("IMA", f"{ima_casa:.1f}")
            st.metric("OVRall", f"{ovrall_casa:.1f}")
            st.caption(f"ATA: {ata_casa:.1f} | DEF: {def_casa:.1f} | MEI: {mei_casa:.1f} | FOR: {for_casa:.1f}")
        with col2:
            st.markdown("<h2 style='text-align:center; color:#DAA520;'>VS</h2>", unsafe_allow_html=True)
        with col3:
            st.subheader(time_fora)
            st.metric("MPV", f"{mpv_fora:.1f}")
            st.metric("IMA", f"{ima_fora:.1f}")
            st.metric("OVRall", f"{ovrall_fora:.1f}")
            st.caption(f"ATA: {ata_fora:.1f} | DEF: {def_fora:.1f} | MEI: {mei_fora:.1f} | FOR: {for_fora:.1f}")
        
        st.markdown("---")
        st.subheader("📊 Probabilidades 1X2")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Casa", f"{prob_casa:.1%}")
            st.metric("Edge", f"{edge_casa:+.1%}")
            st.caption(f"Selo: {selo_casa}")
        with col2:
            st.metric("Empate", f"{prob_empate:.1%}")
            st.metric("Edge", f"{edge_empate:+.1%}")
            st.caption(f"Selo: {selo_empate}")
        with col3:
            st.metric("Fora", f"{prob_fora:.1%}")
            st.metric("Edge", f"{edge_fora:+.1%}")
            st.caption(f"Selo: {selo_fora}")
        
        st.markdown("---")
        st.subheader("🎯 Mercados Adicionais")
        def media_gols(time, tipo):
            jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref_dt][-10:]
            if not jogos_time: return 1.0
            return sum(j.get('gols', 0) if tipo == 'marcados' else j.get('gols_sofridos', 0) for j in jogos_time)/len(jogos_time)
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

# ============================================================
# BACKTEST
# ============================================================
elif opcao == "Backtest":
    if not jogos:
        st.warning("Nenhum dado disponível. Faça a conversão primeiro.")
        st.stop()
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
            jogo_fora = jogo_dict['fora']
            if not jogo_casa or not jogo_fora:
                continue
            data_ref = pd.to_datetime(data_jogo)
            jogos_passados = [j for j in jogos if j['data'] < data_ref]
            
            ata_casa = calcular_ATA(jogos_passados, time_casa, data_ref)
            def_casa = calcular_DEF(jogos_passados, time_casa, data_ref)
            ata_fora = calcular_ATA(jogos_passados, time_fora, data_ref)
            def_fora = calcular_DEF(jogos_passados, time_fora, data_ref)
            
            def media_gols(time, tipo):
                jogos_time = [j for j in jogos_passados if j['time'] == time][-10:]
                if not jogos_time: return 1.0
                if tipo == 'marcados':
                    return sum(j.get('gols', 0) for j in jogos_time) / len(jogos_time)
                else:
                    return sum(j.get('gols_sofridos', 0) for j in jogos_time) / len(jogos_time)
            
            gols_casa = media_gols(time_casa, 'marcados')
            sofridos_fora = media_gols(time_fora, 'sofridos')
            gols_fora = media_gols(time_fora, 'marcados')
            sofridos_casa = media_gols(time_casa, 'sofridos')
            media_total = (gols_casa + sofridos_fora)/2 + (gols_fora + sofridos_casa)/2
            
            prob_over25 = prob_over(media_total, 2.5)
            prob_bt = prob_btts(ata_casa, def_fora, ata_fora, def_casa)
            
            total_gols = jogo_casa.get('gols', 0) + jogo_casa.get('gols_sofridos', 0)
            over25_real = total_gols > 2.5
            btts_real = (jogo_casa.get('gols', 0) > 0 and jogo_casa.get('gols_sofridos', 0) > 0)
            
            log.append({
                'Data': str(data_jogo)[:10],
                'Casa': time_casa,
                'Fora': time_fora,
                'Prob Over 2.5': f"{prob_over25:.1%}",
                'Over 2.5 Real': 'Sim' if over25_real else 'Não',
                'Prob BTTS': f"{prob_bt:.1%}",
                'BTTS Real': 'Sim' if btts_real else 'Não'
            })
        
        if log:
            df_log = pd.DataFrame(log)
            st.dataframe(df_log, use_container_width=True)
            st.success(f"Backtest concluído para {len(log)} partidas.")
