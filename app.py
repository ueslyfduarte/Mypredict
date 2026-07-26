"""
MyPredict 2.0 - App Principal
Interface Streamlit para exibir ratings, probabilidades e selos.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import (
    calcular_IMA,
    calcular_ATA,
    calcular_DEF,
    calcular_OVRall,
    inicializar_MPV,
    atualizar_MPV,
    probabilidades_1x2,
    calcular_edge,
    determinar_selo
)

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="MyPredict 2.0",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ MyPredict 2.0")
st.markdown("### Previsão Esportiva com Método Próprio")

# ============================================================
# CARREGAR DADOS (aqui você pode trocar pela API ou banco de dados)
# ============================================================
@st.cache_data
def carregar_dados():
    """Carrega os jogos do CSV. Substitua pelo seu pipeline real."""
    try:
        df = pd.read_csv("data/exemplo_jogos.csv", parse_dates=["data"])
        # Converte para lista de dicionários (formato que o core.py espera)
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
        st.error("Arquivo 'data/exemplo_jogos.csv' não encontrado. Usando dados vazios.")
        return []

jogos = carregar_dados()

if not jogos:
    st.stop()

# ============================================================
# SELEÇÃO DE TIMES
# ============================================================
times_disponiveis = sorted(list(set(j['time'] for j in jogos)))

col1, col2 = st.columns(2)
with col1:
    time_casa = st.selectbox("🏠 Time Mandante", times_disponiveis, index=0)
with col2:
    time_fora = st.selectbox("✈️ Time Visitante", times_disponiveis, index=min(1, len(times_disponiveis)-1))

# Data de referência para o cálculo (última data disponível ou hoje)
ultima_data = max(j['data'] for j in jogos)
data_ref = st.date_input("📅 Data de referência", value=ultima_data)

# ============================================================
# CÁLCULOS
# ============================================================
# Converte data para datetime
data_ref_dt = datetime.combine(data_ref, datetime.min.time())

# IMA e desvio
ima_casa, desvio_casa = calcular_IMA(jogos, time_casa, data_ref_dt, mando_proximo='casa')
ima_fora, desvio_fora = calcular_IMA(jogos, time_fora, data_ref_dt, mando_proximo='fora')

# OVRall (simplificado)
ata_casa = calcular_ATA(jogos, time_casa, data_ref_dt)
def_casa = calcular_DEF(jogos, time_casa, data_ref_dt)
ovrall_casa = calcular_OVRall([ata_casa, def_casa, 50, 50, 50, 50])

ata_fora = calcular_ATA(jogos, time_fora, data_ref_dt)
def_fora = calcular_DEF(jogos, time_fora, data_ref_dt)
ovrall_fora = calcular_OVRall([ata_fora, def_fora, 50, 50, 50, 50])

# MPV
mpv_casa = inicializar_MPV(ovrall_casa)
mpv_fora = inicializar_MPV(ovrall_fora)

# Probabilidades
prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_casa, mpv_fora)

# Edge e Selo (odds de exemplo; depois você usará odds reais)
odd_casa = 2.0  # placeholder
odd_empate = 3.0
odd_fora = 3.0

edge_casa = calcular_edge(prob_casa, odd_casa)
edge_empate = calcular_edge(prob_empate, odd_empate)
edge_fora = calcular_edge(prob_fora, odd_fora)

dif_mpv = abs(mpv_casa + 75 - mpv_fora)  # diferença com mando
desvio_medio = (desvio_casa + desvio_fora) / 2

selo_casa = determinar_selo(edge_casa, dif_mpv, desvio_medio)
selo_empate = determinar_selo(edge_empate, dif_mpv, desvio_medio)
selo_fora = determinar_selo(edge_fora, dif_mpv, desvio_medio)

# ============================================================
# EXIBIÇÃO NA TELA
# ============================================================
st.markdown("---")

# Linha 1: Cards dos times
col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    st.subheader(f"🏠 {time_casa}")
    st.metric("IMA", f"{ima_casa:.1f}", delta=None)
    st.metric("OVRall", f"{ovrall_casa:.1f}")
    st.metric("MPV", f"{mpv_casa:.0f}")
with col3:
    st.subheader(f"✈️ {time_fora}")
    st.metric("IMA", f"{ima_fora:.1f}")
    st.metric("OVRall", f"{ovrall_fora:.1f}")
    st.metric("MPV", f"{mpv_fora:.0f}")

# Linha 2: Probabilidades
st.markdown("---")
st.subheader("📊 Probabilidades Calculadas")
col_prob1, col_prob2, col_prob3 = st.columns(3)
with col_prob1:
    st.metric("Vitória Casa", f"{prob_casa:.1%}", delta=f"Edge: {edge_casa:+.1%}")
    st.write(f"Selo: {selo_casa}")
with col_prob2:
    st.metric("Empate", f"{prob_empate:.1%}", delta=f"Edge: {edge_empate:+.1%}")
    st.write(f"Selo: {selo_empate}")
with col_prob3:
    st.metric("Vitória Fora", f"{prob_fora:.1%}", delta=f"Edge: {edge_fora:+.1%}")
    st.write(f"Selo: {selo_fora}")

# Linha 3: Selos de destaque
st.markdown("---")
st.subheader("🏅 Oportunidades MyPredict")
for resultado, selo in [("Casa", selo_casa), ("Empate", selo_empate), ("Fora", selo_fora)]:
    if "Dourado" in selo:
        st.success(f"🥇 **{resultado}**: Selo Dourado! Alto valor identificado.")
    elif "Verde" in selo:
        st.info(f"🟢 **{resultado}**: Selo Verde. Boa oportunidade.")
