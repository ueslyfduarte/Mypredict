"""
MyPredict 2.0 – Aplicativo Completo com Recomendações Over 1.5 e BTTS
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial
import os

# ============================================================
# LIMIARES E CONFIGURAÇÕES
# ============================================================
LIMITE_OURO = 0.65
LIMITE_VERDE = 0.50
LIMITE_MARGINAL = 0.33
LIMITE_DUPLA_CHANCE = 0.70

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
# MAPEAMENTO DE PRATELEIRA PARA VALORES BASE (MEI, FOR, CONS, RES)
# ============================================================
SHELF_VALUES = {1: 80, 2: 65, 3: 50, 4: 35, 5: 20}

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
# ANÁLISE DE JOGO (RECOMENDAÇÕES COMPLETAS)
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
                return base
            ata = calcular_ATA(hist, time, data_ref_dt)
            de = calcular_DEF(hist, time, data_ref_dt)
            return calcular_OVRall([ata, de, base, base, base, base])

        ovrall_casa = get_ovrall(time_casa, jogos_passados)
        ovrall_fora = get_ovrall(time_fora, jogos_passados)

        def calcular_MPV_final(time):
            jogos_time = [j for j in jogos_passados if j['time'] == time]
            if not jogos_time:
                return inicializar_MPV(ovrall_casa if time == time_casa else ovrall_fora)
            jogos_time = sorted(jogos_time, key=lambda x: x['data'])
            ovrall = get_ovrall(time, jogos_passados)
            mpv = inicializar_MPV(ovrall)
            for jogo in jogos_time:
                ima_jogo, _ = calcular_IMA(jogos_passados, time, jogo['data'], mando_proximo=jogo['mando'])
                ovrall_adv = get_ovrall(jogo['adv'], jogos_passados)
                mpv_adv = inicializar_MPV(ovrall_adv)
                mpv = atualizar_MPV(mpv, mpv_adv, jogo['mando'], jogo['resultado'], ima_jogo)
            return mpv

        mpv_casa_raw = calcular_MPV_final(time_casa)
        mpv_fora_raw = calcular_MPV_final(time_fora)

        ima_casa, _ = calcular_IMA(jogos_passados, time_casa, data_ref_dt, mando_proximo='casa')
        ima_fora, _ = calcular_IMA(jogos_passados, time_fora, data_ref_dt, mando_proximo='fora')

        if ima_fora > 70:
            mpv_fora_raw += 50

        prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

        # Recomendação Resultado
        probs = [('Vitória Casa', prob_casa), ('Empate', prob_empate), ('Vitória Fora', prob_fora)]
        probs.sort(key=lambda x: x[1], reverse=True)
        maior, segunda = probs[0], probs[1]
        if maior[1] < 0.50 and (maior[1] - segunda[1]) < 0.05:
            rec = "Empate Técnico"
            rec_prob = prob_empate
        else:
            rec = maior[0]
            rec_prob = maior[1]
        selo_rec = get_selo(rec_prob)

        # Dupla chance
        dupla = None
        if prob_casa + prob_empate >= LIMITE_DUPLA_CHANCE:
            dupla = f"Dupla Chance Casa/Empate ({prob_casa + prob_empate:.1%})"
        elif prob_fora + prob_empate >= LIMITE_DUPLA_CHANCE:
            dupla = f"Dupla Chance Fora/Empate ({prob_fora + prob_empate:.1%})"

        # Médias para Over/BTTS
        def media_gols(time, tipo):
            jogos_time = [j for j in jogos_passados if j['time'] == time][-10:]
            if not jogos_time: return 1.0
            if tipo == 'marcados': return sum(j['gols'] for j in jogos_time) / len(jogos_time)
            else: return sum(j['gols_sofridos'] for j in jogos_time) / len(jogos_time)
        gols_casa = media_gols(time_casa, 'marcados'); sofridos_fora = media_gols(time_fora, 'sofridos')
        gols_fora = media_gols(time_fora, 'marcados'); sofridos_casa = media_gols(time_casa, 'sofridos')
        media_total = (gols_casa + sofridos_fora)/2 + (gols_fora + sofridos_casa)/2

        prob_over15 = prob_over(media_total, 1.5)
        prob_bt = prob_btts(ata_casa, def_fora, ata_fora, def_casa)

        # Recomendações Over 1.5 e BTTS
        rec_over15 = "Over 1.5" if prob_over15 >= 0.5 else "Under 1.5"
        rec_btts = "Sim" if prob_bt >= 0.5 else "Não"

        # Análise por prateleira
        prat_adv = prats.get(time_fora, 3)
        hist_prat = [j for j in jogos_passados if j['time'] == time_casa and prats.get(j['adv'], 3) == prat_adv]
        v = sum(1 for j in hist_prat if j['resultado'] == 'V')
        e = sum(1 for j in hist_prat if j['resultado'] == 'E')
        d = sum(1 for j in hist_prat if j['resultado'] == 'D')
        total_prat = len(hist_prat)
        analise_prat = f"Contra mesma prateleira ({prat_adv}): V:{v} E:{e} D:{d} ({(v/total_prat)*100:.1f}% vit.)" if total_prat > 0 else "Sem histórico contra essa prateleira."

        st.markdown("---")
        st.success(f"MyPredict Recomenda: **{rec}** (Probabilidade: {rec_prob:.1%})")
        st.info(f"Selo de confiança: {selo_rec}")
        if dupla:
            st.warning(f"🔄 {dupla}")

        col1, col2, col3 = st.columns(3)
        with col1: st.metric("MPV Casa", f"{(mpv_casa_raw-1000)/10:.1f}")
        with col2: st.metric("Diferença MPV", f"{abs((mpv_casa_raw-1000)/10 - (mpv_fora_raw-1000)/10):.1f}")
        with col3: st.metric("MPV Fora", f"{(mpv_fora_raw-1000)/10:.1f}")

        st.caption(analise_prat)

        st.markdown("---")
        st.subheader("🎯 Recomendações de Mercados")
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            st.metric("Over/Under 1.5 gols", f"{rec_over15} ({prob_over15:.1%})")
        with col_rec2:
            st.metric("Ambas Marcam", f"{rec_btts} ({prob_bt:.1%})")

        st.subheader("Outros Mercados")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Over 1.5 gols", f"{prob_over15:.1%}")
        col2.metric("Over 2.5 gols", f"{prob_over(media_total, 2.5):.1%}")
        col3.metric("Ambas Marcam", f"{prob_bt:.1%}")
        esc_casa = for_casa/5 if for_casa else 4; esc_fora = for_fora/5 if for_fora else 4
        total_esc = esc_casa + esc_fora
        col4.metric("Over 9.5 esc.", f"{prob_over(total_esc, 8.5):.1%}")

# ============================================================
# BACKTEST VISUAL (FOCO 1X2, EXIBIÇÃO DOS CÁLCULOS INTERNOS)
# ============================================================
elif opcao == "Backtest Visual":
    st.markdown("<h1 style='text-align:center;'>📈 Backtest MyPredict 2.0 – Análise 1X2</h1>", unsafe_allow_html=True)
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

            # --- IMA (com detalhamento das janelas) ---
            # Precisamos capturar as notas individuais. Para isso, replicamos parte da lógica do calcular_IMA.
            jogos_time_casa = [j for j in hist_filtrado if j['time'] == time_casa]
            jogos_time_fora = [j for j in hist_filtrado if j['time'] == time_fora]
            jogos_time_casa.sort(key=lambda x: x['data'], reverse=True)
            jogos_time_fora.sort(key=lambda x: x['data'], reverse=True)

            def ultimos(jogos_time, n, apenas_mando=None):
                filtrados = []
                for j in jogos_time:
                    if apenas_mando is None or j['mando'] == apenas_mando:
                        filtrados.append(j)
                    if len(filtrados) == n:
                        break
                return filtrados

            def nota_janela(jogos_janela):
                if not jogos_janela:
                    return 50.0
                P_obtida = P_max = P_min = 0.0
                for j in jogos_janela:
                    P_obtida += pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], j['resultado'])
                    P_max += pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'V')
                    P_min += pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'D')
                if P_max == P_min:
                    return 50.0
                return ((P_obtida - P_min) / (P_max - P_min)) * 100

            # Janelas Casa
            G10_casa = ultimos(jogos_time_casa, 10)
            G5_casa  = ultimos(jogos_time_casa, 5)
            G3_casa  = ultimos(jogos_time_casa, 3)
            L5_casa  = ultimos(jogos_time_casa, 5, apenas_mando='casa')
            L3_casa  = ultimos(jogos_time_casa, 3, apenas_mando='casa')
            n_G10_casa = nota_janela(G10_casa)
            n_G5_casa  = nota_janela(G5_casa)
            n_G3_casa  = nota_janela(G3_casa)
            n_L5_casa  = nota_janela(L5_casa)
            n_L3_casa  = nota_janela(L3_casa)
            ima_casa = (0.10 * n_G10_casa + 0.15 * n_G5_casa + 0.20 * n_G3_casa +
                        0.25 * n_L5_casa + 0.30 * n_L3_casa)

            # Janelas Fora
            G10_fora = ultimos(jogos_time_fora, 10)
            G5_fora  = ultimos(jogos_time_fora, 5)
            G3_fora  = ultimos(jogos_time_fora, 3)
            L5_fora  = ultimos(jogos_time_fora, 5, apenas_mando='fora')
            L3_fora  = ultimos(jogos_time_fora, 3, apenas_mando='fora')
            n_G10_fora = nota_janela(G10_fora)
            n_G5_fora  = nota_janela(G5_fora)
            n_G3_fora  = nota_janela(G3_fora)
            n_L5_fora  = nota_janela(L5_fora)
            n_L3_fora  = nota_janela(L3_fora)
            ima_fora = (0.10 * n_G10_fora + 0.15 * n_G5_fora + 0.20 * n_G3_fora +
                        0.25 * n_L5_fora + 0.30 * n_L3_fora)

            # --- OVRall (detalhado) ---
            def get_ovrall_detalhado(time, prat, hist):
                if not any(j['time'] == time for j in hist):
                    base = SHELF_VALUES[prat]
                    # Retorna componentes padrão baseados na prateleira
                    return base, base, base, base, base, base
                ata = calcular_ATA(hist, time, data_jogo)
                de = calcular_DEF(hist, time, data_jogo)
                mei = SHELF_VALUES[prat]  # placeholder fixo pela prateleira
                forc = SHELF_VALUES[prat]
                cons = SHELF_VALUES[prat]
                res = SHELF_VALUES[prat]
                return ata, de, mei, forc, cons, res

            ata_casa, def_casa, mei_casa, for_casa, cons_casa, res_casa = get_ovrall_detalhado(time_casa, prat_casa, hist_filtrado)
            ovrall_casa = calcular_OVRall([ata_casa, def_casa, mei_casa, for_casa, cons_casa, res_casa])

            ata_fora, def_fora, mei_fora, for_fora, cons_fora, res_fora = get_ovrall_detalhado(time_fora, prat_fora, hist_filtrado)
            ovrall_fora = calcular_OVRall([ata_fora, def_fora, mei_fora, for_fora, cons_fora, res_fora])

            # MPV
            mpv_casa_raw = inicializar_MPV(ovrall_casa)
            mpv_fora_raw = inicializar_MPV(ovrall_fora)
            # Evolução com jogos passados
            for jg in hist_filtrado:
                if jg['time'] == time_casa:
                    ima_jg, _ = calcular_IMA(hist_filtrado, time_casa, jg['data'], mando_proximo=jg['mando'])
                    ovrall_adv = calcular_OVRall([calcular_ATA(hist_filtrado, jg['adv'], jg['data']),
                                                  calcular_DEF(hist_filtrado, jg['adv'], jg['data']),
                                                  SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                                  SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                                  SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                                  SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)]])
                    mpv_adv = inicializar_MPV(ovrall_adv)
                    mpv_casa_raw = atualizar_MPV(mpv_casa_raw, mpv_adv, jg['mando'], jg['resultado'], ima_jg)
                elif jg['time'] == time_fora:
                    ima_jg, _ = calcular_IMA(hist_filtrado, time_fora, jg['data'], mando_proximo=jg['mando'])
                    ovrall_adv = calcular_OVRall([calcular_ATA(hist_filtrado, jg['adv'], jg['data']),
                                                  calcular_DEF(hist_filtrado, jg['adv'], jg['data']),
                                                  SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                                  SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                                  SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)],
                                                  SHELF_VALUES[prateleiras_fixas.get(jg['adv'], 3)]])
                    mpv_adv = inicializar_MPV(ovrall_adv)
                    mpv_fora_raw = atualizar_MPV(mpv_fora_raw, mpv_adv, jg['mando'], jg['resultado'], ima_jg)

            # Bônus IMA fora alto
            if ima_fora > 70:
                mpv_fora_raw += 50

            prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

            # Recomendação
            probs = {'Vitória Casa': prob_casa, 'Empate': prob_empate, 'Vitória Fora': prob_fora}
            rec = max(probs, key=probs.get)
            rec_prob = probs[rec]
            selo = get_selo(rec_prob)

            # Resultado real
            gols_casa_real = casa_info['gols']
            gols_fora_real = fora_info['gols']
            resultado_real = 'V' if gols_casa_real > gols_fora_real else ('D' if gols_casa_real < gols_fora_real else 'E')
            acertou = (rec == 'Vitória Casa' and resultado_real == 'V') or \
                      (rec == 'Empate' and resultado_real == 'E') or \
                      (rec == 'Vitória Fora' and resultado_real == 'D')

            # Armazena TUDO para exibição
            resultados.append({
                'data': data_jogo,
                'time_casa': time_casa, 'time_fora': time_fora,
                'mpv_casa': (mpv_casa_raw - 1000) / 10,
                'mpv_fora': (mpv_fora_raw - 1000) / 10,
                'ima_casa': ima_casa, 'ima_fora': ima_fora,
                'janelas_casa': (n_G10_casa, n_G5_casa, n_G3_casa, n_L5_casa, n_L3_casa),
                'janelas_fora': (n_G10_fora, n_G5_fora, n_G3_fora, n_L5_fora, n_L3_fora),
                'ata_casa': ata_casa, 'def_casa': def_casa, 'mei_casa': mei_casa, 'for_casa': for_casa, 'cons_casa': cons_casa, 'res_casa': res_casa,
                'ata_fora': ata_fora, 'def_fora': def_fora, 'mei_fora': mei_fora, 'for_fora': for_fora, 'cons_fora': cons_fora, 'res_fora': res_fora,
                'ovr_casa': ovrall_casa, 'ovr_fora': ovrall_fora,
                'prob_casa': prob_casa, 'prob_empate': prob_empate, 'prob_fora': prob_fora,
                'recomendacao': rec, 'rec_prob': rec_prob, 'selo': selo,
                'resultado_real': resultado_real, 'acertou': acertou
            })

            historico.append(casa_info)
            historico.append(fora_info)
            progress.progress((idx + 1) / total)

        st.session_state.resultados_backtest = resultados

    # ============================================================
    # EXIBIÇÃO PAGINADA (10 POR VEZ) COM DETALHAMENTO INTERNO
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
            with st.expander(f"{res['time_casa']} vs {res['time_fora']} – {res['data'].strftime('%d/%m/%Y')}"):
                # Linha 1: MPVs e Recomendação
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("MPV Casa", f"{res['mpv_casa']:.1f}")
                col2.metric("MPV Fora", f"{res['mpv_fora']:.1f}")
                col3.metric("Diferença", f"{abs(res['mpv_casa'] - res['mpv_fora']):.1f}")
                col4.metric("Resultado", res['resultado_real'])

                # Recomendação
                st.write(f"**MyPredict Recomenda:** {res['recomendacao']} (Prob: {res['rec_prob']:.1%}, Selo: {res['selo']})")
                st.write(f"Acertou: {'✅' if res['acertou'] else '❌'}")

                # --- IMA Detalhado ---
                st.markdown("#### IMA (Índice de Momento Atual)")
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    st.write(f"**{res['time_casa']}**")
                    st.write(f"G10: {res['janelas_casa'][0]:.1f} | G5: {res['janelas_casa'][1]:.1f} | G3: {res['janelas_casa'][2]:.1f}")
                    st.write(f"L5: {res['janelas_casa'][3]:.1f} | L3: {res['janelas_casa'][4]:.1f}")
                    st.metric("IMA Casa", f"{res['ima_casa']:.1f}")
                with col_i2:
                    st.write(f"**{res['time_fora']}**")
                    st.write(f"G10: {res['janelas_fora'][0]:.1f} | G5: {res['janelas_fora'][1]:.1f} | G3: {res['janelas_fora'][2]:.1f}")
                    st.write(f"L5: {res['janelas_fora'][3]:.1f} | L3: {res['janelas_fora'][4]:.1f}")
                    st.metric("IMA Fora", f"{res['ima_fora']:.1f}")

                # --- OVRall Detalhado ---
                st.markdown("#### OVRall (Força Geral)")
                col_o1, col_o2 = st.columns(2)
                with col_o1:
                    st.write(f"**{res['time_casa']}**")
                    st.write(f"ATA: {res['ata_casa']:.1f} | DEF: {res['def_casa']:.1f} | MEI: {res['mei_casa']:.1f}")
                    st.write(f"FOR: {res['for_casa']:.1f} | CONS: {res['cons_casa']:.1f} | RES: {res['res_casa']:.1f}")
                    st.metric("OVRall Casa", f"{res['ovr_casa']:.1f}")
                with col_o2:
                    st.write(f"**{res['time_fora']}**")
                    st.write(f"ATA: {res['ata_fora']:.1f} | DEF: {res['def_fora']:.1f} | MEI: {res['mei_fora']:.1f}")
                    st.write(f"FOR: {res['for_fora']:.1f} | CONS: {res['cons_fora']:.1f} | RES: {res['res_fora']:.1f}")
                    st.metric("OVRall Fora", f"{res['ovr_fora']:.1f}")

                # Probabilidades 1X2
                st.markdown("#### Probabilidades MyPredict")
                col_p1, col_p2, col_p3 = st.columns(3)
                col_p1.metric("Casa", f"{res['prob_casa']:.1%}")
                col_p2.metric("Empate", f"{res['prob_empate']:.1%}")
                col_p3.metric("Fora", f"{res['prob_fora']:.1%}")

        # --- Resumo da Temporada ---
        st.markdown("---")
        st.subheader("📊 Desempenho do MyPredict na Temporada")
        total_jogos = len(resultados)
        acertos = sum(1 for r in resultados if r['acertou'])
        taxa = (acertos / total_jogos) * 100 if total_jogos > 0 else 0
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Jogos", total_jogos)
        col2.metric("Acertos", acertos)
        col3.metric("Taxa de Acerto", f"{taxa:.1f}%")

        st.subheader("Desempenho por Selo")
        for selo_nome in ["🥇 Ouro", "🟢 Verde", "⚪ Marginal", "🔴 Sem selo"]:
            jogos_selo = [r for r in resultados if r['selo'] == selo_nome]
            if jogos_selo:
                acertos_selo = sum(1 for r in jogos_selo if r['acertou'])
                taxa_selo = (acertos_selo / len(jogos_selo)) * 100
                st.write(f"{selo_nome}: {len(jogos_selo)} jogos, {acertos_selo} acertos ({taxa_selo:.1f}%)")
    else:
        st.info("Clique em 'Iniciar Backtest 1X2' para processar os jogos.")
