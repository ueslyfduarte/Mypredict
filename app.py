# app.py — MyPredict 2.0
# Interface Streamlit (frontend)

import streamlit as st
from data_loader import (
    gerar_prateleiras, obter_ultimos_jogos_com_heranca, extrair_recortes_ima,
    obter_dados_ovrall_time, classificação_anterior, carregar_confrontos_diretos,
    carregar_odds_partida
)
from ratings import calcular_ima, calcular_ic, calcular_mpv
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa,
    _gols_esperados  # necessário para Ambas Marcam
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

st.set_page_config(page_title="MyPredict 2.0", layout="wide")
st.title("MyPredict 2.0")
st.markdown("### Previsões para o confronto")

# --- inputs (exemplo fixo, depois interativo)
time_casa = "Flamengo"
time_fora = "Palmeiras"
liga = "Brasileirão"
temporada = 2025

# 1. Projeção de prateleiras
prateleiras = gerar_prateleiras(liga, temporada)
class_ant = classificação_anterior(liga, temporada - 1)

# 2. Dados OVRall / brutos para mercados
dados_casa = obter_dados_ovrall_time(time_casa, liga, temporada, class_ant)
dados_fora = obter_dados_ovrall_time(time_fora, liga, temporada, class_ant)

# 3. Calcular IMA
jogos_casa = obter_ultimos_jogos_com_heranca(time_casa, liga, temporada, class_ant, n=20)
rec_casa = extrair_recortes_ima(jogos_casa, True)
jogos_fora = obter_ultimos_jogos_com_heranca(time_fora, liga, temporada, class_ant, n=20)
rec_fora = extrair_recortes_ima(jogos_fora, False)

ima_casa = calcular_ima(time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                        rec_casa['5CF'], rec_casa['3CF'], prateleiras)
ima_fora = calcular_ima(time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                        rec_fora['5CF'], rec_fora['3CF'], prateleiras)

# 4. OVRall (placeholder até termos dados_liga)
# Aqui podemos usar um valor neutro ou extrair a nota real se tivermos dados_liga
# Por simplicidade, usaremos 50.0; no futuro, calcular_ovrall(dados_casa, dados_liga)
ovrall_casa = 50.0
ovrall_fora = 50.0

# 5. Calcular IC
# Confronto direto
confrontos = carregar_confrontos_diretos(time_casa, time_fora, liga)
# Para simplificar, usaremos valores fixos nos outros fatores
ic_casa = calcular_ic({
    'confronto_direto': None,  # não implementado
    'mesmo_escalao': None,
    'contra_escalao_adversario': None,
    'fator_casa': None,
    'odds': None
})
ic_fora = calcular_ic({
    'confronto_direto': None,
    'mesmo_escalao': None,
    'contra_escalao_adversario': None,
    'fator_casa': None,
    'odds': None
})

# 6. MPV
mpv_casa = calcular_mpv(ima_casa, ovrall_casa, ic_casa)
mpv_fora = calcular_mpv(ima_fora, ovrall_fora, ic_fora)

# 7. Bônus de casa dinâmico
bonus_casa = calcular_bonus_casa(dados_casa.get('diff_aprov_casa_fora', 0))

# 8. Mercados
p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

# Over 2.5
over25 = prob_over_2_5(
    dados_casa.get('gols_media'), dados_fora.get('gols_media'),
    dados_casa.get('gols_sofridos_media'), dados_fora.get('gols_sofridos_media')
)

# Ambas Marcam
gols_esp_casa = _gols_esperados(dados_casa.get('gols_media'), dados_fora.get('gols_sofridos_media'), MEDIA_GOLS_CASA_LIGA)
gols_esp_fora = _gols_esperados(dados_fora.get('gols_media'), dados_casa.get('gols_sofridos_media'), MEDIA_GOLS_FORA_LIGA)
btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)

# Gol HT
gol_ht = prob_gol_ht(
    dados_casa.get('gols_ht_media'), dados_fora.get('gols_ht_media'),
    dados_casa.get('gols_ht_sofridos_media'), dados_fora.get('gols_ht_sofridos_media')
)

# Escanteios
esc = prob_over_escanteios(
    dados_casa.get('escanteios_media'), dados_fora.get('escanteios_media'),
    dados_casa.get('escanteios_sofridos_media'), dados_fora.get('escanteios_sofridos_media')
)

# Exibir
col1, col2, col3 = st.columns(3)
col1.metric("Vitória Casa", f"{p1:.1%}")
col2.metric("Empate", f"{pX:.1%}")
col3.metric("Vitória Fora", f"{p2:.1%}")

col4, col5, col6 = st.columns(3)
col4.metric("Over 2.5", f"{over25:.1%}" if over25 else "N/D")
col5.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")
col6.metric("Gol HT", f"{gol_ht:.1%}" if gol_ht else "N/D")

st.metric("Over Escanteios (linha dinâmica)", f"{esc:.1%}" if esc else "N/D")
