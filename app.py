"""
MyPredict 2.0 - Interface Moderna (Preto, Dourado e Branco)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import (
    calcular_IMA,
    calcular_ATA,
    calcular_DEF,
    calcular_MEI,
    calcular_FOR,
    calcular_CONS,
    calcular_RES,
    calcular_OVRall,
    inicializar_MPV,
    atualizar_MPV,
    probabilidades_1x2,
    calcular_edge,
    determinar_selo
)

# ============================================================
# CONFIGURAÇÃO VISUAL
# ============================================================
st.set_page_config(page_title="MyPredict 2.0", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    .stApp { background-color: #111111; color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6 { color: #DAA520 !important; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; color: #FFFFFF; }
    .stButton>button {
        background-color: #DAA520; color: #000; border: none;
        font-weight: bold; font-size: 1.2rem; padding: 0.5rem 2rem; border-radius: 8px;
    }
    .positivo { color: #00C853; font-weight: bold; }
    .negativo { color: #FF1744; font-weight: bold; }
    .barra-bg { background-color: #333; border-radius: 5px; height: 22px; width: 100%; margin: 4px 0; }
    .barra-preenchimento {
        background-color: #DAA520; height: 22px; border-radius: 5px;
        text-align: right; padding-right: 6px; color: #000;
        font-weight: bold; font-size: 0.8rem; line-height: 22px;
    }
    .mpv-destaque { font-size: 3rem; font-weight: bold; color: #DAA520; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CARREGAR DADOS
# ============================================================
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("data/exemplo_jogos.csv", parse_dates=["data"])
        jogos = []
        for _, row in df.iterrows():
            jogos.append({
                'data': row['data'],
                'time': row['time'],
                'adv': row['adv'],
                'mando': row['mando'],
                'resultado': row['resultado'],
                'gols': row['gols'],
                'prat_time': row['prat_time'],
                'prat_adv': row['prat_adv']
            })
        return jogos
    except FileNotFoundError:
        st.error("Arquivo 'data/exemplo_jogos.csv' não encontrado.")
        return []

jogos = carregar_dados()
if not jogos:
    st.stop()

times_disponiveis = sorted(list(set(j['time'] for j in jogos)))

# ============================================================
# PAINEL DE BOAS-VINDAS
# ============================================================
st.markdown("<h1 style='text-align: center;'>⚽ MyPredict 2.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #CCCCCC;'>Análise Preditiva com Método Próprio</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #DAA520; font-style: italic;'>\"O futebol é a coisa mais importante entre as coisas menos importantes.\" – Arrigo Sacchi</p>", unsafe_allow_html=True)
st.markdown("---")

# ============================================================
# SELEÇÃO DE TIMES
# ============================================================
col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    time_casa = st.selectbox("🏠 Time Mandante", times_disponiveis, index=0)
with col2:
    st.markdown("<h2 style='text-align: center; color: #DAA520;'>VS</h2>", unsafe_allow_html=True)
with col3:
    time_fora = st.selectbox("✈️ Time Visitante", times_disponiveis, index=min(1, len(times_disponiveis)-1))

ultima_data = max(j['data'] for j in jogos)
data_ref = st.date_input("📅 Data de referência", value=ultima_data)

# ============================================================
# CONTEXTO DA LIGA (ANTES DOS CÁLCULOS, JÁ QUE NÃO DEPENDE DELES)
# ============================================================
st.markdown("---")
st.markdown("### 🏆 Contexto na Liga")

times_dict = {t: {'P': 0, 'J': 0, 'V': 0, 'E': 0, 'D': 0, 'GP': 0} for t in times_disponiveis}
for j in jogos:
    t = j['time']
    if j['resultado'] == 'V':
        times_dict[t]['V'] += 1
        times_dict[t]['P'] += 3
    elif j['resultado'] == 'E':
        times_dict[t]['E'] += 1
        times_dict[t]['P'] += 1
    else:
        times_dict[t]['D'] += 1
    times_dict[t]['J'] += 1
    times_dict[t]['GP'] += j['gols']

tabela = []
for time, stats in times_dict.items():
    tabela.append([time, stats['J'], stats['V'], stats['E'], stats['D'], stats['GP'], stats['P']])
df_tabela = pd.DataFrame(tabela, columns=["Time", "J", "V", "E", "D", "GP", "Pts"])
df_tabela = df_tabela.sort_values("Pts", ascending=False).reset_index(drop=True)
df_tabela.index = df_tabela.index + 1

def highlight_linha(s):
    return ['background-color: #DAA520; color: #000' if s.name in [time_casa, time_fora] else '' for _ in s]

st.dataframe(df_tabela.style.apply(highlight_linha, axis=0), use_container_width=True)

pos_casa = df_tabela[df_tabela['Time'] == time_casa].index[0] if not df_tabela[df_tabela['Time'] == time_casa].empty else None
pos_fora = df_tabela[df_tabela['Time'] == time_fora].index[0] if not df_tabela[df_tabela['Time'] == time_fora].empty else None
if pos_casa and pos_fora:
    contexto = f"Na classificação atual, **{time_casa}** ocupa a {pos_casa}ª posição, enquanto **{time_fora}** está em {pos_fora}º. "
    if pos_casa < pos_fora:
        contexto += "O time da casa possui melhor campanha."
    elif pos_casa > pos_fora:
        contexto += "O visitante vem apresentando melhor desempenho na tabela."
    else:
        contexto += "Ambos estão na mesma posição, sugerindo um duelo bastante parelho."
    st.markdown(contexto)

st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
gerar = st.button("⚡ Gerar MyPredict")
st.markdown("</div>", unsafe_allow_html=True)

if gerar:
    data_ref_dt = datetime.combine(data_ref, datetime.min.time())

    # ---------- FUNÇÃO AUXILIAR PARA MPV HISTÓRICO ----------
    def calcular_MPV_final(time, jogos, data_ref_dt):
        jogos_time = sorted([j for j in jogos if j['time'] == time and j['data'] <= data_ref_dt], key=lambda x: x['data'])
        if not jogos_time:
            return inicializar_MPV(50.0)
        ovrall_inicial = calcular_OVRall([calcular_ATA(jogos, time, data_ref_dt),
                                          calcular_DEF(jogos, time, data_ref_dt),
                                          calcular_MEI(jogos, time, data_ref_dt),
                                          calcular_FOR(jogos, time, data_ref_dt),
                                          calcular_CONS(jogos, time, data_ref_dt),
                                          calcular_RES(jogos, time, data_ref_dt)])
        mpv = inicializar_MPV(ovrall_inicial)
        for jogo in jogos_time:
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

    # ---------- CÁLCULOS PRINCIPAIS ----------
    ima_casa, desvio_casa = calcular_IMA(jogos, time_casa, data_ref_dt, mando_proximo='casa')
    ima_fora, desvio_fora = calcular_IMA(jogos, time_fora, data_ref_dt, mando_proximo='fora')

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

    mpv_casa_raw = calcular_MPV_final(time_casa, jogos, data_ref_dt)
    mpv_fora_raw = calcular_MPV_final(time_fora, jogos, data_ref_dt)

    prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa_raw, mpv_fora_raw)

    odd_casa, odd_empate, odd_fora = 2.0, 3.0, 3.0
    edge_casa = calcular_edge(prob_casa, odd_casa)
    edge_empate = calcular_edge(prob_empate, odd_empate)
    edge_fora = calcular_edge(prob_fora, odd_fora)

    dif_mpv = abs(mpv_casa_raw + 75 - mpv_fora_raw)
    desvio_medio = (desvio_casa + desvio_fora) / 2
    selo_casa = determinar_selo(edge_casa, dif_mpv, desvio_medio)
    selo_empate = determinar_selo(edge_empate, dif_mpv, desvio_medio)
    selo_fora = determinar_selo(edge_fora, dif_mpv, desvio_medio)

    mpv_casa = (mpv_casa_raw - 1000) / 10
    mpv_fora = (mpv_fora_raw - 1000) / 10

    # ---------- SETAS IMA ----------
    IMA_REF = {1: 70, 2: 60, 3: 50, 4: 40, 5: 30}
    prat_casa = next((j['prat_time'] for j in jogos if j['time'] == time_casa), 3)
    prat_fora = next((j['prat_time'] for j in jogos if j['time'] == time_fora), 3)

    def seta_ima(ima_val, prateleira):
        ref = IMA_REF.get(prateleira, 50)
        if ima_val > 1.1 * ref:
            return "🔺 Superando"
        elif ima_val < 0.9 * ref:
            return "🔻 Abaixo"
        else:
            return "✅ Dentro"

    seta_casa = seta_ima(ima_casa, prat_casa)
    seta_fora = seta_ima(ima_fora, prat_fora)

    # ---------- SEÇÃO IMA (MOMENTO) ----------
    st.markdown("---")
    st.markdown("### 📈 Momento Atual (IMA)")
    col_ima1, col_ima2 = st.columns(2)
    with col_ima1:
        st.metric(f"{time_casa} (Casa)", f"{ima_casa:.1f}")
        st.markdown(f"**{seta_casa}** em relação à expectativa da prateleira")
    with col_ima2:
        st.metric(f"{time_fora} (Fora)", f"{ima_fora:.1f}")
        st.markdown(f"**{seta_fora}** em relação à expectativa da prateleira")

    # ---------- MÉTRICAS DETALHADAS ----------
    st.markdown("---")
    st.markdown("### 🔍 Métricas Detalhadas do Modelo")
    nomes = ["ATA (Ataque)", "DEF (Defesa)", "MEI (Meio-campo)", "FOR (Força)", "CONS (Consistência)", "RES (Resiliência)", "OVRall (Força Geral)"]
    valores_casa = [ata_casa, def_casa, mei_casa, for_casa, cons_casa, res_casa, ovrall_casa]
    valores_fora = [ata_fora, def_fora, mei_fora, for_fora, cons_fora, res_fora, ovrall_fora]
    descricoes = [
        "Capacidade ofensiva ajustada à defesa adversária",
        "Solidez defensiva ajustada ao ataque adversário",
        "Controle de jogo, passes e criação",
        "Dificuldade imposta aos adversários",
        "Regularidade dos resultados esperados",
        "Capacidade de reagir a situações adversas",
        "Força geral combinada das seis dimensões"
    ]

    for i, (nome, desc) in enumerate(zip(nomes, descricoes)):
        st.markdown(f"**{nome}** — *{desc}*")
        col_bar1, col_bar2 = st.columns(2)
        with col_bar1:
            st.markdown(f"<div class='barra-bg'><div class='barra-preenchimento' style='width:{valores_casa[i]}%;'>{valores_casa[i]:.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'>{time_casa}: {valores_casa[i]:.1f}</p>", unsafe_allow_html=True)
        with col_bar2:
            st.markdown(f"<div class='barra-bg'><div class='barra-preenchimento' style='width:{valores_fora[i]}%;'>{valores_fora[i]:.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center;'>{time_fora}: {valores_fora[i]:.1f}</p>", unsafe_allow_html=True)

    # ---------- ANÁLISE DO CONFRONTO ----------
    st.markdown("---")
    st.markdown("### 📝 Análise do Confronto")
    favorito = time_casa if prob_casa > prob_fora else time_fora
    underdog = time_fora if prob_casa > prob_fora else time_casa
    prob_favorito = max(prob_casa, prob_fora)
    descricao = (
        f"De acordo com o modelo MyPredict, o **{favorito}** é o favorito para esta partida, "
        f"com **{prob_favorito:.1%}** de probabilidade de vitória. "
    )
    if abs(prob_casa - prob_fora) < 0.15:
        descricao += "No entanto, o confronto é bastante equilibrado, com chances reais para ambos os lados. "
    else:
        descricao += "A superioridade prevista é clara, embora o futebol sempre permita surpresas. "
    if prob_empate > 0.30:
        descricao += "A probabilidade de empate é elevada, refletindo um possível equilíbrio tático ou histórico de confrontos diretos."
    st.markdown(descricao)

    # ---------- PROBABILIDADES E VALOR ----------
    st.markdown("---")
    st.markdown("### 📊 Probabilidades e Valor")
    col_prob1, col_prob2, col_prob3 = st.columns(3)

    def mostra_edge(edge_val):
        if edge_val > 0:
            return f"<span class='positivo'>+{edge_val:.1%}</span>"
        else:
            return f"<span class='negativo'>{edge_val:.1%}</span>"

    with col_prob1:
        st.markdown(f"<h3 style='color: #DAA520;'>Vitória {time_casa}</h3>", unsafe_allow_html=True)
        st.metric("Probabilidade", f"{prob_casa:.1%}")
        st.markdown(f"Edge: {mostra_edge(edge_casa)}", unsafe_allow_html=True)
        st.write(f"Selo: {selo_casa}")

    with col_prob2:
        st.markdown(f"<h3 style='color: #DAA520;'>Empate</h3>", unsafe_allow_html=True)
        st.metric("Probabilidade", f"{prob_empate:.1%}")
        st.markdown(f"Edge: {mostra_edge(edge_empate)}", unsafe_allow_html=True)
        st.write(f"Selo: {selo_empate}")

    with col_prob3:
        st.markdown(f"<h3 style='color: #DAA520;'>Vitória {time_fora}</h3>", unsafe_allow_html=True)
        st.metric("Probabilidade", f"{prob_fora:.1%}")
        st.markdown(f"Edge: {mostra_edge(edge_fora)}", unsafe_allow_html=True)
        st.write(f"Selo: {selo_fora}")

    st.caption("Edge: vantagem percentual sobre a odd de referência. Positivo (verde) indica valor esperado positivo.")
    for resultado, selo in [(f"{time_casa} (Casa)", selo_casa), ("Empate", selo_empate), (f"{time_fora} (Fora)", selo_fora)]:
        if "Dourado" in selo:
            st.success(f"🥇 **{resultado}**: Selo Dourado! Alto valor identificado.")
        elif "Verde" in selo:
            st.info(f"🟢 **{resultado}**: Selo Verde. Boa oportunidade.")

    # ---------- MPV EM DESTAQUE (FINAL) ----------
    st.markdown("---")
    st.markdown("### 💎 MyPredict Value (MPV)")
    col_mpv1, col_mpv2 = st.columns(2)
    with col_mpv1:
        st.markdown(f"<div class='mpv-destaque'>{mpv_casa:.1f}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{time_casa}</p>", unsafe_allow_html=True)
    with col_mpv2:
        st.markdown(f"<div class='mpv-destaque'>{mpv_fora:.1f}</div>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center;'>{time_fora}</p>", unsafe_allow_html=True)
    diff_mpv = abs(mpv_casa - mpv_fora)
    melhor = time_casa if mpv_casa > mpv_fora else time_fora
    st.markdown(f"<p style='text-align: center; color: #DAA520;'>Diferença: {diff_mpv:.1f} pontos a favor do <b>{melhor}</b></p>", unsafe_allow_html=True)
