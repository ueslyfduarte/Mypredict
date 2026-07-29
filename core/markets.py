# core/markets.py — Cálculo de probabilidades de mercado
import math
from config import (
    SIGMOID_K, SIGMA_EMPATE, PROB_EMPATE_BASE,
    MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA,
    PROPORCAO_GOLS_HT, MARGEM_SEGURANCA_ESCANTEIOS,
    MAX_BONUS_CASA_MPV, FATOR_BONUS_CASA
)

def _gols_esperados(gols_pro, gols_sofridos_adv, media_liga):
    """Gols esperados de um time com base em seus gols marcados e na defesa adversária."""
    if gols_pro is None or gols_sofridos_adv is None:
        return 0.0
    return max(0.0, gols_pro * (gols_sofridos_adv / media_liga)) if media_liga > 0 else gols_pro

def calcular_bonus_casa(diff_aprov_casa_fora):
    """Bônus de mando de campo baseado na diferença de aproveitamento casa/fora."""
    if diff_aprov_casa_fora is None:
        return 0.0
    bonus = min(MAX_BONUS_CASA_MPV, max(0, (diff_aprov_casa_fora / 100) * FATOR_BONUS_CASA * 10))
    return bonus

def prob_1x2(mpv_casa, mpv_fora, bonus_casa):
    """Probabilidades 1X2 usando MPV e bônus casa."""
    delta = (mpv_casa - mpv_fora) + bonus_casa
    p1 = 1.0 / (1.0 + math.exp(-SIGMOID_K * delta))
    pX = PROB_EMPATE_BASE * math.exp(-((abs(delta) / SIGMA_EMPATE) ** 2))
    p2 = max(0.0, 1.0 - p1 - pX)
    # Normalizar
    total = p1 + pX + p2
    if total > 0:
        p1 /= total
        pX /= total
        p2 /= total
    return p1, pX, p2

def prob_over_2_5(gols_casa, gols_fora, gols_sofridos_casa, gols_sofridos_fora,
                  media_casa=MEDIA_GOLS_CASA_LIGA, media_fora=MEDIA_GOLS_FORA_LIGA):
    """Probabilidade de mais de 2.5 gols na partida."""
    # Gols esperados
    gols_esp_casa = _gols_esperados(gols_casa, gols_sofridos_fora, media_fora)
    gols_esp_fora = _gols_esperados(gols_fora, gols_sofridos_casa, media_casa)
    # Usamos Poisson bivariado: P(total > 2.5) = 1 - P(0)-P(1)-P(2)
    # Aproximação pela soma de duas Poisson independentes
    def poisson_pmf(k, lam):
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return (lam ** k) * math.exp(-lam) / math.factorial(k)
    total_lam = gols_esp_casa + gols_esp_fora
    prob = 0.0
    for k in range(3):  # 0,1,2
        prob += poisson_pmf(k, total_lam)
    return max(0.0, 1.0 - prob)

def prob_ambas_marcam(gols_esp_casa, gols_esp_fora):
    """Probabilidade de ambos marcarem (BTTS)."""
    # Pelo menos um gol de cada
    p0_casa = math.exp(-gols_esp_casa) if gols_esp_casa > 0 else 1.0
    p0_fora = math.exp(-gols_esp_fora) if gols_esp_fora > 0 else 1.0
    return (1.0 - p0_casa) * (1.0 - p0_fora)

def prob_gol_ht(gols_ht_casa, gols_ht_fora, gols_ht_sofridos_casa, gols_ht_sofridos_fora,
                media_ht_casa=0.75, media_ht_fora=0.65):
    """Probabilidade de haver gol no primeiro tempo."""
    gols_casa = _gols_esperados(gols_ht_casa, gols_ht_sofridos_fora, media_ht_fora)
    gols_fora = _gols_esperados(gols_ht_fora, gols_ht_sofridos_casa, media_ht_casa)
    lam = gols_casa + gols_fora
    p0 = math.exp(-lam) if lam > 0 else 1.0
    return 1.0 - p0

def prob_over_escanteios(esc_casa, esc_fora, esc_sofridos_casa, esc_sofridos_fora,
                         media_casa=5.0, media_fora=4.5, margem=MARGEM_SEGURANCA_ESCANTEIOS):
    """Probabilidade de mais de 8.5 escanteios (limiar comum)."""
    # Média esperada de escanteios
    lam_casa = esc_casa * (esc_sofridos_fora / media_fora) if media_fora > 0 else esc_casa
    lam_fora = esc_fora * (esc_sofridos_casa / media_casa) if media_casa > 0 else esc_fora
    total_lam = lam_casa + lam_fora
    # Poisson para k > 8.5 -> 9 ou mais
    prob = 0.0
    for k in range(9, 20):  # limite arbitrário
        prob += (total_lam ** k) * math.exp(-total_lam) / math.factorial(k)
    return min(1.0, prob + margem/100)  # margem de segurança
