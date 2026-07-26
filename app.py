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
st.set_page_config(
    page_title="MyPredict 2.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS customizado
st.markdown("""
<style>
    .stApp {
        background-color: #111111;
        color: #FFFFFF;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #DAA520 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #DAA520;
        color: #000000;
        border: none;
        font-weight: bold;
        font-size: 1.2rem;
        padding: 0.5rem 2rem;
        border-radius: 8px;
    }
    .positivo { color: #00C853; font-weight: bold; }
    .negativo { color: #FF1744; font-weight: bold; }
    .barra-bg {
        background-color: #333333;
        border-radius: 5px;
        height: 20px;
        width: 100%;
        margin: 4px 0;
    }
    .barra-preenchimento {
        background-color: #DAA520;
        height: 20px;
        border-radius: 5px;
        text-align: right;
        padding-right: 5px;
        color: #000;
        font-weight: bold;
        font-size: 0.8rem;
        line-height: 20px;
    }
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
st.markdown("<p style='text-align: center; color: #CCCCCC; font-size: 1.2rem;'>Análise Preditiva com Método Próprio</p>", unsafe_allow_html=True)
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

st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
gerar = st.button("⚡ Gerar MyPredict")
st.markdown("</div>", unsafe_allow_html=True)

if gerar:
    data_ref_dt = datetime.combine(data_ref, datetime.min.time())

    # ---------- CÁLCULOS ----------
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

    mpv_casa_raw = inicializar_MPV(ovrall_casa)
    mpv_fora_raw = inicializar_MPV(ovrall_fora)
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

    # ---------- RESUMO DAS EQUIPES ----------
    st.markdown("---")
    st.markdown("### 📊 Resumo das Equipes")
    col1, col2, col3 = st.columns([3, 1, 3])
    with col1:
        st.markdown(f"<h2 style='color: #DAA520;'>{time_casa} (Casa)</h2>", unsafe_allow_html=True)
        st.metric("MPV (0-100)", f"{mpv_casa:.1f}")
        st.metric("IMA (Momento)", f"{ima_casa:.1f}")
        st.metric("OVRall (Força Geral)", f"{ovrall_casa:.1f}")
    with col2:
        st.markdown("<h1 style='text-align: center; color: #DAA520;'>VS</h1>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<h2 style='color: #DAA520;'>{time_fora} (Fora)</h2>", unsafe_allow_html=True)
        st.metric("MPV (0-100)", f"{mpv_fora:.1f}")
        st.metric("IMA (Momento)", f"{ima_fora:.1f}")
        st.metric("OVRall (Força Geral)", f"{ovrall_fora:.1f}")

    # ---------- PROBABILIDADES E SELOS ----------
    st.markdown("---")
    st.markdown("### 📈 Probabilidades e Valor")
    col_prob1, col_prob2, col_prob3 = st.columns(3)
    def format_edge(valor):
        cor = "positivo" if valor > 0 else "negativo"
        return f"<span class='{cor}'>{valor:+.1%}</span>"

    with col_prob1:
        st.markdown(f"<h3 style='color: #DAA520;'>Vitória {time_casa}</h3>", unsafe_allow_html=True)
        st.metric("Probabilidade", f"{prob_casa:.1%}")
        st.markdown(f"Edge: {format_edge(edge_casa)}", unsafe_allow_html=True)
        st.write(f"Selo: {selo_casa}")
    with col_prob2:
        st.markdown(f"<h3 style='color: #DAA520;'>Empate</h3>", unsafe_allow_html=True)
        st.metric("Probabilidade", f"{prob_empate:.1%}")
        st.markdown(f"Edge: {format_edge(edge_empate)}", unsafe_allow_html=True)
        st.write(f"Selo: {selo_empate}")
    with col_prob3:
        st.markdown(f"<h3 style='color: #DAA520;'>Vitória {time_fora}</h3>", unsafe_allow_html=True)
        st.metric("Probabilidade", f"{prob_fora:.1%}")
        st.markdown(f"Edge: {format_edge(edge_fora)}", unsafe_allow_html=True)
        st.write(f"Selo: {selo_fora}")

    for resultado, selo in [(f"{time_casa} (Casa)", selo_casa), ("Empate", selo_empate), (f"{time_fora} (Fora)", selo_fora)]:
        if "Dourado" in selo:
            st.success(f"🥇 **{resultado}**: Selo Dourado! Alto valor identificado.")
        elif "Verde" in selo:
            st.info(f"🟢 **{resultado}**: Selo Verde. Boa oportunidade.")

    # ---------- ANÁLISE DESCRITIVA ----------
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

    # ---------- MÉTRICAS DETALHADAS LADO A LADO COM BARRAS ----------
    st.markdown("---")
    st.markdown("### 🔍 Métricas Detalhadas do Modelo")

    # Definição dos pesos e descrições
    pesos_ovr = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
    nomes = ["ATA (Ataque)", "DEF (Defesa)", "MEI (Meio-campo)", "FOR (Força)", "CONS (Consistência)", "RES (Resiliência)"]
    descricoes = [
        "Capacidade ofensiva ajustada à defesa adversária",
        "Solidez defensiva ajustada ao ataque adversário",
        "Controle de jogo, passes e qualidade de criação",
        "Dificuldade imposta aos adversários, imposição física",
        "Regularidade dos resultados dentro do esperado",
        "Capacidade de reagir a situações adversas"
    ]
    valores_casa = [ata_casa, def_casa, mei_casa, for_casa, cons_casa, res_casa]
    valores_fora = [ata_fora, def_fora, mei_fora, for_fora, cons_fora, res_fora]

    # Cria duas colunas para cada time
    col_met_casa, col_met_fora = st.columns(2)

    def barra_html(valor, largura=100):
        """Retorna HTML para barra de progresso dourada."""
        return f"""
        <div class="barra-bg" style="width:{largura}px;">
            <div class="barra-preenchimento" style="width:{valor}%;">{valor:.0f}</div>
        </div>
        """

    with col_met_casa:
        st.markdown(f"<h3 style='color: #DAA520;'>{time_casa}</h3>", unsafe_allow_html=True)
        for nome, valor, desc in zip(nomes, valores_casa, descricoes):
            st.markdown(f"**{nome}** — *{desc}*")
            st.markdown(barra_html(valor), unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**OVRall (Força Geral)** = {ovrall_casa:.1f}")
        st.markdown("Pesos: ATA 25% | DEF 25% | MEI 20% | FOR 15% | CONS 10% | RES 5%")

    with col_met_fora:
        st.markdown(f"<h3 style='color: #DAA520;'>{time_fora}</h3>", unsafe_allow_html=True)
        for nome, valor, desc in zip(nomes, valores_fora, descricoes):
            st.markdown(f"**{nome}** — *{desc}*")
            st.markdown(barra_html(valor), unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"**OVRall (Força Geral)** = {ovrall_fora:.1f}")
        st.markdown("Pesos: ATA 25% | DEF 25% | MEI 20% | FOR 15% | CONS 10% | RES 5%")

    # IMA e MPV extras
    st.markdown("---")
    col_extra1, col_extra2 = st.columns(2)
    with col_extra1:
        st.metric("IMA (Momento Atual)", f"{ima_casa:.1f}")
        st.metric("MPV (Rating 0-100)", f"{mpv_casa:.1f}")
    with col_extra2:
        st.metric("IMA (Momento Atual)", f"{ima_fora:.1f}")
        st.metric("MPV (Rating 0-100)", f"{mpv_fora:.1f}")

    # ---------- TABELA DA LIGA ----------
    st.markdown("---")
    st.markdown("### 🏆 Contexto na Liga")

    # Classificação simples
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
            contexto += "O time da casa possui melhor campanha, o que corrobora o favoritismo indicado pelo MPV."
        elif pos_casa > pos_fora:
            contexto += "O visitante vem apresentando melhor desempenho na tabela, o que pode equilibrar o confronto."
        else:
            contexto += "Ambos estão na mesma posição, sugerindo um duelo bastante parelho."
        st.markdown(contexto)
