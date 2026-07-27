# test_run.py
import json
from data_loader import (
    gerar_prateleiras, obter_ultimos_jogos_com_heranca, extrair_recortes_ima,
    obter_dados_ovrall_time, classificação_anterior
)
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa,
    _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

# Liga e temporada
liga = 'Brasileirão'
temporada = 2024
time_casa = 'Flamengo'
time_fora = 'Palmeiras'

print("Carregando classificação...")
class_ant = classificação_anterior(liga, temporada)

print("Gerando prateleiras...")
prateleiras = gerar_prateleiras(liga, temporada)

print("Obtendo dados OVRall...")
dados_casa = obter_dados_ovrall_time(time_casa, liga, temporada, class_ant)
dados_fora = obter_dados_ovrall_time(time_fora, liga, temporada, class_ant)

print("Calculando IMA...")
jogos_casa = obter_ultimos_jogos_com_heranca(time_casa, liga, temporada, class_ant, n=20)
rec_casa = extrair_recortes_ima(jogos_casa, True)
jogos_fora = obter_ultimos_jogos_com_heranca(time_fora, liga, temporada, class_ant, n=20)
rec_fora = extrair_recortes_ima(jogos_fora, False)

ima_casa = calcular_ima(time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                        rec_casa['5CF'], rec_casa['3CF'], prateleiras)
ima_fora = calcular_ima(time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                        rec_fora['5CF'], rec_fora['3CF'], prateleiras)

# OVRall (placeholder: 50)
ovrall_casa = 50.0
ovrall_fora = 50.0

# IC (placeholder: 50)
ic_casa = 50.0
ic_fora = 50.0

print("Calculando MPV...")
mpv_casa = calcular_mpv(ima_casa, ovrall_casa, ic_casa)
mpv_fora = calcular_mpv(ima_fora, ovrall_fora, ic_fora)

print("Calculando bônus casa...")
bonus_casa = calcular_bonus_casa(dados_casa.get('diff_aprov_casa_fora', 0))

print("Calculando probabilidades...")
p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

over25 = prob_over_2_5(
    dados_casa.get('gols_media'), dados_fora.get('gols_media'),
    dados_casa.get('gols_sofridos_media'), dados_fora.get('gols_sofridos_media')
)

gols_esp_casa = _gols_esperados(dados_casa.get('gols_media'), dados_fora.get('gols_sofridos_media'), MEDIA_GOLS_CASA_LIGA)
gols_esp_fora = _gols_esperados(dados_fora.get('gols_media'), dados_casa.get('gols_sofridos_media'), MEDIA_GOLS_FORA_LIGA)
btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)

gol_ht = prob_gol_ht(
    dados_casa.get('gols_ht_media'), dados_fora.get('gols_ht_media'),
    dados_casa.get('gols_ht_sofridos_media'), dados_fora.get('gols_ht_sofridos_media')
)

print("\n=== RESULTADOS ===")
print(f"1: {p1:.1%} | X: {pX:.1%} | 2: {p2:.1%}")
print(f"Over 2.5: {over25:.1%}")
print(f"Ambas Marcam: {btts:.1%}")
print(f"Gol HT: {gol_ht:.1%}" if gol_ht else "Gol HT: N/D")
