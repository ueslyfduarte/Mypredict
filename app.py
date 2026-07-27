"""
MyPredict 2.0 – Simulação Interativa com FÓRMULAS EXPLÍCITAS
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial
import os

# ============================================================
# LIMIARES PARA SELOS
# ============================================================
LIMITE_OURO = 0.695
LIMITE_VERDE = 0.50
LIMITE_MARGINAL = 0.33

def get_selo(probabilidade):
    if probabilidade >= LIMITE_OURO: return "🥇 Ouro"
    elif probabilidade >= LIMITE_VERDE: return "🟢 Verde"
    elif probabilidade >= LIMITE_MARGINAL: return "⚪ Marginal"
    else: return "🔴 Sem selo"

# ============================================================
# CONFIGURAÇÃO VISUAL
# ============================================================
st.set_page_config(page_title="MyPredict 2.0", page_icon="⚽", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #111; color: #fff; }
    h1, h2, h3, h4 { color: #DAA520; }
    .stButton>button { background:#DAA520; color:#000; font-weight:bold; border-radius:8px; }
    .card { background-color: #1E1E1E; border-left: 4px solid #DAA520; padding: 12px; margin: 8px 0; border-radius: 6px; }
    .team-name { font-size: 1.2rem; color: #DAA520; font-weight: bold; }
    .result { font-size: 2rem; font-weight: bold; text-align: center; }
    .metric-row { display: flex; flex-wrap: wrap; gap: 10px; margin: 8px 0; }
    .metric-cell { flex: 1; min-width: 90px; text-align: center; }
    .metric-value { font-size: 1.3rem; color: #DAA520; font-weight: bold; }
    .metric-label { font-size: 0.7rem; color: #aaa; text-transform: uppercase; }
    .prob-cell { flex: 1; min-width: 80px; text-align: center; }
    .prob-value { font-size: 1.2rem; color: #fff; }
    .prob-market { font-size: 0.9rem; color: #DAA520; }
    .acerto { font-size: 2rem; }
    hr { border-color: #333; margin: 8px 0; }
    .formula { background-color: #2A2A2A; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 0.8rem; margin: 4px 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CARREGAR DADOS
# ============================================================
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("data/meus_jogos.csv", sep=None, engine='python')
        for col in ['time', 'adv', 'mando', 'resultado']:
            if col in df.columns: df[col] = df[col].astype(str).str.strip()
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
                partidas.append({'data': key[0], 'casa': casa.iloc[0].to_dict(), 'fora': fora.iloc[0].to_dict()})
        return jogos_planos, partidas
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return [], []

jogos, partidas = carregar_dados()

# ============================================================
# PRATELEIRAS E OVRall INICIAL (MENOR ODD DA TEMPORADA)
# ============================================================
def compute_initial_shelves_and_ovrall(jogos):
    min_odds = {}
    for j in jogos:
        time = j['time']
        odd = float(j.get('B365H', 3.0)) if j['mando'] == 'casa' else float(j.get('B365A', 3.0))
        if time not in min_odds or odd < min_odds[time]: min_odds[time] = odd
    sorted_teams = sorted(min_odds, key=lambda t: min_odds[t])
    n = len(sorted_teams)
    shelves, ovrall_ini = {}, {}
    for i, t in enumerate(sorted_teams):
        if i < n*0.15: shelves[t] = 1
        elif i < n*0.35: shelves[t] = 2
        elif i < n*0.65: shelves[t] = 3
        elif i < n*0.85: shelves[t] = 4
        else: shelves[t] = 5
        ovrall_ini[t] = max(0, min(100, 100 - (min_odds[t] - 1.0) * 25))
    for t in set(j['time'] for j in jogos):
        if t not in shelves: shelves[t] = 3; ovrall_ini[t] = 50.0
    return shelves, ovrall_ini

PRATELEIRAS, OVRALL_INICIAL = compute_initial_shelves_and_ovrall(jogos)
SHELF_NAMES = {1: "Elite", 2: "Alta", 3: "Meio", 4: "Baixa", 5: "Crítico"}

# ============================================================
# MENU LATERAL
# ============================================================
st.sidebar.markdown("<h2 style='color:#DAA520;'>⚽ MyPredict 2.0</h2>", unsafe_allow_html=True)
opcao = st.sidebar.radio("Modo", ["Análise de Jogo", "Simulação Passo a Passo", "Converter Dados Brutos"])

# ============================================================
# CONVERSOR (mantido)
# ============================================================
if opcao == "Converter Dados Brutos":
    st.markdown("<h1 style='text-align:center;'>🔄 Conversor de CSV</h1>", unsafe_allow_html=True)
    # ... (código do conversor) ...
    st.write("Conversor mantido.")

# ============================================================
# ANÁLISE DE JOGO (mantida)
# ============================================================
elif opcao == "Análise de Jogo":
    if not jogos: st.warning("Sem dados."); st.stop()
    # ... (código da análise de jogo) ...
    st.write("Análise de Jogo mantida.")

# ============================================================
# SIMULAÇÃO PASSO A PASSO COM FÓRMULAS
# ============================================================
elif opcao == "Simulação Passo a Passo":
    st.markdown("<h1 style='text-align:center;'>📈 Simulação MyPredict 2.0 – Passo a Passo (Fórmulas Visíveis)</h1>", unsafe_allow_html=True)
    if not partidas: st.error("Nenhuma partida carregada."); st.stop()

    st.success("Prateleiras e OVRall inicial definidos pelas odds de toda a temporada.")
    st.write("Prateleiras fixas:", {t: f"{s} ({SHELF_NAMES[s]})" for t, s in PRATELEIRAS.items()})

    if st.button("▶️ Iniciar Simulação Detalhada"):
        partidas_ord = sorted(partidas, key=lambda p: p['data'])
        historico = []
        banca = 100.0
        stake = 10.0
        resultados = []
        mpv_atual = {t: inicializar_MPV(OVRALL_INICIAL[t]) for t in PRATELEIRAS}
        progress = st.progress(0)

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

            # --- IMA COM FÓRMULAS ---
            def ima_detalhado(time, mando_prox):
                jogos_time = [j for j in hist_filtrado if j['time'] == time]
                jogos_time.sort(key=lambda x: x['data'], reverse=True)
                def ultimos(n, apenas_mando=None):
                    filtrados = []
                    for j in jogos_time:
                        if apenas_mando is None or j['mando'] == apenas_mando: filtrados.append(j)
                        if len(filtrados) == n: break
                    return filtrados
                def nota(lista):
                    if not lista: return 50.0, 0, 0, 0
                    P_obt = sum(pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], j['resultado']) for j in lista)
                    P_max = sum(pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'V') for j in lista)
                    P_min = sum(pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'D') for j in lista)
                    if P_max == P_min: return 50.0, P_obt, P_max, P_min
                    return ((P_obt - P_min) / (P_max - P_min)) * 100, P_obt, P_max, P_min
                g10, g5, g3 = ultimos(10), ultimos(5), ultimos(3)
                l5 = ultimos(5, apenas_mando=mando_prox)
                l3 = ultimos(3, apenas_mando=mando_prox)
                n10, p10_obt, p10_max, p10_min = nota(g10)
                n5, p5_obt, p5_max, p5_min = nota(g5)
                n3, p3_obt, p3_max, p3_min = nota(g3)
                nl5, pl5_obt, pl5_max, pl5_min = nota(l5)
                nl3, pl3_obt, pl3_max, pl3_min = nota(l3)
                ima = 0.10*n10 + 0.15*n5 + 0.20*n3 + 0.25*nl5 + 0.30*nl3
                return ima, (n10, n5, n3, nl5, nl3), ((p10_obt, p10_max, p10_min), (p5_obt, p5_max, p5_min), (p3_obt, p3_max, p3_min), (pl5_obt, pl5_max, pl5_min), (pl3_obt, pl3_max, pl3_min))

            ima_casa, notas_casa, detalhes_casa = ima_detalhado(time_casa, 'casa')
            ima_fora, notas_fora, detalhes_fora = ima_detalhado(time_fora, 'fora')
            ima_casa = max(0.0, min(100.0, ima_casa))
            ima_fora = max(0.0, min(100.0, ima_fora))

            # --- OVRall COM COMPONENTES ---
            def ovrall_detalhado(time, prat):
                if not any(j['time'] == time for j in hist_filtrado):
                    base = OVRALL_INICIAL[time]
                    return base, (base, base, base, base, base, base)
                ata = calcular_ATA(hist_filtrado, time, data_jogo)
                de = calcular_DEF(hist_filtrado, time, data_jogo)
                mei = calcular_MEI(hist_filtrado, time, data_jogo)
                forc = calcular_FOR(hist_filtrado, time, data_jogo)
                cons = calcular_CONS(hist_filtrado, time, data_jogo)
                res = calcular_RES(hist_filtrado, time, data_jogo)
                ovr = calcular_OVRall([ata, de, mei, forc, cons, res])
                return ovr, (ata, de, mei, forc, cons, res)

            ovrall_casa, comp_casa = ovrall_detalhado(time_casa, prat_casa)
            ovrall_fora, comp_fora = ovrall_detalhado(time_fora, prat_fora)

            # --- MPV ---
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

            gols_casa_real = casa_info['gols']
            gols_fora_real = fora_info['gols']
            resultado_real = 'V' if gols_casa_real > gols_fora_real else ('D' if gols_casa_real < gols_fora_real else 'E')

            # Atualiza MPV
            k_casa = PARAMS['K']['normal'] if 40 <= ima_casa <= 60 else (PARAMS['K']['atencao'] if 25 <= ima_casa < 40 or 60 < ima_casa <= 75 else PARAMS['K']['alerta'])
            k_fora = PARAMS['K']['normal'] if 40 <= ima_fora <= 60 else (PARAMS['K']['atencao'] if 25 <= ima_fora < 40 or 60 < ima_fora <= 75 else PARAMS['K']['alerta'])
            mpv_atual[time_casa] = atualizar_MPV(mpv_casa_raw, mpv_fora_raw, 'casa', resultado_real, ima_casa)
            mpv_atual[time_fora] = atualizar_MPV(mpv_fora_raw, mpv_casa_raw, 'fora',
                                                  'V' if resultado_real == 'D' else ('D' if resultado_real == 'V' else 'E'),
                                                  ima_fora)

            # Lucro
            odd_utilizada = None; lucro_partida = 0.0
            if aposta_valida:
                if rec.startswith('Vitória do '):
                    time_rec = rec.replace('Vitória do ', '')
                    odd_utilizada = float(casa_info.get('B365H', 2.0)) if time_rec == time_casa else float(casa_info.get('B365A', 3.0))
                else: odd_utilizada = float(casa_info.get('B365D', 3.0))
                if (rec == f"Vitória do {time_casa}" and resultado_real == 'V') or \
                   (rec == "Empate" and resultado_real == 'E') or \
                   (rec == f"Vitória do {time_fora}" and resultado_real == 'D'):
                    lucro_partida = stake * (odd_utilizada - 1)
                else: lucro_partida = -stake
                banca += lucro_partida

            imp_casa = 1 / float(casa_info.get('B365H', 2.0)) if float(casa_info.get('B365H', 2.0)) > 0 else 0
            imp_empate = 1 / float(casa_info.get('B365D', 3.0)) if float(casa_info.get('B365D', 3.0)) > 0 else 0
            imp_fora = 1 / float(casa_info.get('B365A', 3.0)) if float(casa_info.get('B365A', 3.0)) > 0 else 0

            # Exibição detalhada
            with st.container():
                st.markdown(f"### {time_casa} vs {time_fora} – {data_jogo.strftime('%d/%m/%Y')}")
                st.markdown(f"**Prateleiras:** {time_casa} ({SHELF_NAMES[prat_casa]}) | {time_fora} ({SHELF_NAMES[prat_fora]})")

                with st.expander("📊 IMA – Índice de Momento Atual (Fórmula: (P_obt - P_min)/(P_max - P_min)*100)"):
                    for lado, notas, det in [("Casa", notas_casa, detalhes_casa), ("Fora", notas_fora, detalhes_fora)]:
                        st.write(f"**{lado}**")
                        janelas = ["G10", "G5", "G3", "L5", "L3"]
                        for i, nome in enumerate(janelas):
                            st.markdown(f"- {nome}: Nota={notas[i]:.1f} | P_obt={det[i][0]:.1f} P_max={det[i][1]:.1f} P_min={det[i][2]:.1f}")
                        st.write(f"IMA {lado} = 0.10*G10 + 0.15*G5 + 0.20*G3 + 0.25*L5 + 0.30*L3 = {notas[0]*0.1 + notas[1]*0.15 + notas[2]*0.20 + notas[3]*0.25 + notas[4]*0.30:.1f}")

                with st.expander("💪 OVRall – Força Geral (Pesos: ATA 25% DEF 25% MEI 20% FOR 15% CONS 10% RES 5%)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{time_casa}**")
                        st.write(f"ATA={comp_casa[0]:.1f} DEF={comp_casa[1]:.1f} MEI={comp_casa[2]:.1f} FOR={comp_casa[3]:.1f} CONS={comp_casa[4]:.1f} RES={comp_casa[5]:.1f}")
                    with col2:
                        st.write(f"**{time_fora}**")
                        st.write(f"ATA={comp_fora[0]:.1f} DEF={comp_fora[1]:.1f} MEI={comp_fora[2]:.1f} FOR={comp_fora[3]:.1f} CONS={comp_fora[4]:.1f} RES={comp_fora[5]:.1f}")

                with st.expander("⭐ MPV – MyPredict Value (Escala 0-100, Fórmula Elo com K dinâmico)"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("MPV Casa", f"{(mpv_casa_raw-1000)/10:.1f}")
                        st.caption(f"K = {k_casa} (IMA={ima_casa:.1f})")
                    with col2:
                        st.metric("MPV Fora", f"{(mpv_fora_raw-1000)/10:.1f}")
                        st.caption(f"K = {k_fora} (IMA={ima_fora:.1f})")
                    dif_mpv = (mpv_casa_raw - mpv_fora_raw) / 10
                    st.write(f"Diferença MPV: {dif_mpv:+.1f}")

                with st.expander("📈 Probabilidades 1X2 (Fórmula Elo + Heurística de Empate)"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Casa (MYP)", f"{prob_casa:.1%}", delta=f"Bet365: {imp_casa:.1%}")
                    col2.metric("Empate (MYP)", f"{prob_empate:.1%}", delta=f"Bet365: {imp_empate:.1%}")
                    col3.metric("Fora (MYP)", f"{prob_fora:.1%}", delta=f"Bet365: {imp_fora:.1%}")
                    st.latex(r"P_{mandante} = \frac{1}{1 + 10^{(MPV_{visitante} - (MPV_{mandante} + V_{mando})) / S}}")
                    st.latex(r"P_{empate} = \max(0.14, \min(0.32, 0.30 - 0.05 \times \frac{|MPV_{mandante} + V_{mando} - MPV_{visitante}|}{S}))")

                st.markdown("---")
                st.markdown(f"**🎯 Recomendação MyPredict:** {recomendacao} (Prob: {rec_prob:.1%}, Selo: {selo})")
                st.markdown(f"**Resultado Real:** {resultado_real} | {'✅ ACERTOU' if aposta_valida and lucro_partida > 0 else ('❌ ERROU' if aposta_valida else '')}")
                st.markdown(f"**Lucro:** R$ {lucro_partida:+.2f} | **Banca:** R$ {banca:.2f}")

            resultados.append({'aposta_valida': aposta_valida, 'acertou': (aposta_valida and lucro_partida > 0), 'lucro_partida': lucro_partida, 'banca_apos': banca})
            historico.append(casa_info)
            historico.append(fora_info)
            progress.progress((idx + 1) / len(partidas_ord))

        # Resumo final
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
