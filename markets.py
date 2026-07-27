import math
from config import (
    MAX_BONUS_CASA_MPV, FATOR_BONUS_CASA,
    SIGMOID_K, SIGMA_EMPATE, PROB_EMPATE_BASE,
    MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA,
    PROPORCAO_GOLS_HT, MARGEM_SEGURANCA_ESCANTEIOS
)

def calcular_bonus_casa(diff_aprov_casa_fora):
    if diff_aprov_casa_fora is None: return 0.0
    bonus = diff_aprov_casa_fora * FATOR_BONUS_CASA
    return max(0.0, min(MAX_BONUS_CASA_MPV, bonus))

def prob_1x2(mpv_casa, mpv_fora, bonus_casa):
    diff = mpv_casa - mpv_fora + bonus_casa
    p_casa = 1.0 / (1.0 + math.exp(-SIGMOID_K * diff))
    p_empate = PROB_EMPATE_BASE * math.exp(- (diff ** 2) / (2 * SIGMA_EMPATE ** 2))
    p_fora = 1.0 - p_casa - p_empate
    p_casa = max(0.001, min(0.999, p_casa))
    p_empate = max(0.001, min(0.999, p_empate))
    p_fora = max(0.001, min(0.999, p_fora))
    total = p_casa + p_empate + p_fora
    return (p_casa / total, p_empate / total, p_fora / total)

def _poisson_pmf(lmbda, k):
    if lmbda <= 0: return 0.0
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)

def _gols_esperados(gols_time, gols_sofridos_adv, media_liga):
    if None in (gols_time, gols_sofridos_adv, media_liga) or media_liga == 0:
        return 0.0
    ataque = gols_time / media_liga
    defesa = gols_sofridos_adv / media_liga
    return ataque * defesa * media_liga

def prob_over(total_esperado, linha):
    if total_esperado <= 0: return 0.5
    prob = 1.0 - sum(_poisson_pmf(total_esperado, k) for k in range(int(linha) + 1))
    return max(0.0, min(1.0, prob))

def prob_ambas_marcam(gols_esperados_casa, gols_esperados_fora):
    p_casa = 1.0 - _poisson_pmf(gols_esperados_casa, 0)
    p_fora = 1.0 - _poisson_pmf(gols_esperados_fora, 0)
    return p_casa * p_fora

def prob_over_2_5(casa_media, fora_media, def_casa, def_fora,
                  media_casa=MEDIA_GOLS_CASA_LIGA, media_fora=MEDIA_GOLS_FORA_LIGA):
    if None in (casa_media, fora_media, def_casa, def_fora): return 0.5
    gols_casa = _gols_esperados(casa_media, def_fora, media_casa)
    gols_fora = _gols_esperados(fora_media, def_casa, media_fora)
    return prob_over(gols_casa + gols_fora, 2.5)

def prob_over_1_5(casa_media, fora_media, def_casa, def_fora,
                  media_casa=MEDIA_GOLS_CASA_LIGA, media_fora=MEDIA_GOLS_FORA_LIGA):
    if None in (casa_media, fora_media, def_casa, def_fora): return 0.5
    gols_casa = _gols_esperados(casa_media, def_fora, media_casa)
    gols_fora = _gols_esperados(fora_media, def_casa, media_fora)
    return prob_over(gols_casa + gols_fora, 1.5)

def prob_gol_ht(gols_ht_casa, gols_ht_fora, gols_ht_sofridos_casa, gols_ht_sofridos_fora,
                media_ht_casa=None, media_ht_fora=None):
    if None in (gols_ht_casa, gols_ht_fora, gols_ht_sofridos_casa, gols_ht_sofridos_fora):
        return None
    if media_ht_casa is None: media_ht_casa = MEDIA_GOLS_CASA_LIGA * PROPORCAO_GOLS_HT
    if media_ht_fora is None: media_ht_fora = MEDIA_GOLS_FORA_LIGA * PROPORCAO_GOLS_HT
    gols_esp_casa = _gols_esperados(gols_ht_casa, gols_ht_sofridos_fora, media_ht_casa)
    gols_esp_fora = _gols_esperados(gols_ht_fora, gols_ht_sofridos_casa, media_ht_fora)
    prob_0 = _poisson_pmf(gols_esp_casa, 0) * _poisson_pmf(gols_esp_fora, 0)
    return 1.0 - prob_0

def prob_over_escanteios(esc_casa, esc_fora, esc_sof_casa, esc_sof_fora,
                         media_casa=5.5, media_fora=4.5, margem=MARGEM_SEGURANCA_ESCANTEIOS):
    if None in (esc_casa, esc_fora, esc_sof_casa, esc_sof_fora): return None
    esc_esp_casa = (esc_casa / media_casa) * (esc_sof_fora / media_fora) * media_casa
    esc_esp_fora = (esc_fora / media_fora) * (esc_sof_casa / media_casa) * media_fora
    total_esperado = esc_esp_casa + esc_esp_fora
    linha = total_esperado - margem
    if linha < 0: linha = 0.0
    return prob_over(total_esperado, linha) if total_esperado > 0 else 0.5
