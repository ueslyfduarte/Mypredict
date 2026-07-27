# markets.py — MyPredict 2.0
# Conversão de métricas em probabilidades para mercados de apostas.

import math
from config import (
    MAX_BONUS_CASA_MPV, FATOR_BONUS_CASA,
    SIGMOID_K, SIGMA_EMPATE, PROB_EMPATE_BASE,
    MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA,
    PROPORCAO_GOLS_HT, MARGEM_SEGURANCA_ESCANTEIOS
)


# ------------------------------------------------------------
# FUNÇÃO AUXILIAR – BÔNUS DE CASA DINÂMICO
# ------------------------------------------------------------

def calcular_bonus_casa(diff_aprov_casa_fora: float) -> float:
    """
    Transforma a diferença de aproveitamento casa-fora (%) em bônus de MPV.
    Piso 0, teto MAX_BONUS_CASA_MPV.
    """
    if diff_aprov_casa_fora is None:
        return 0.0
    bonus = diff_aprov_casa_fora * FATOR_BONUS_CASA
    return max(0.0, min(MAX_BONUS_CASA_MPV, bonus))


# ------------------------------------------------------------
# 1. PROBABILIDADES 1X2
# ------------------------------------------------------------

def prob_1x2(mpv_casa: float, mpv_fora: float, bonus_casa: float) -> tuple:
    """
    Retorna (p_casa, p_empate, p_fora) normalizadas.
    bonus_casa: vantagem do mandante em pontos de MPV (já calculada).
    """
    diff = mpv_casa - mpv_fora + bonus_casa

    p_casa = 1.0 / (1.0 + math.exp(-SIGMOID_K * diff))
    p_empate = PROB_EMPATE_BASE * math.exp(- (diff ** 2) / (2 * SIGMA_EMPATE ** 2))
    p_fora = 1.0 - p_casa - p_empate

    p_casa = max(0.001, min(0.999, p_casa))
    p_empate = max(0.001, min(0.999, p_empate))
    p_fora = max(0.001, min(0.999, p_fora))

    total = p_casa + p_empate + p_fora
    return (p_casa / total, p_empate / total, p_fora / total)


# ------------------------------------------------------------
# 2. OVER/UNDER GOLS E AMBAS MARCAM
# ------------------------------------------------------------

def _poisson_pmf(lmbda: float, k: int) -> float:
    if lmbda < 0:
        lmbda = 0
    return (lmbda ** k) * math.exp(-lmbda) / math.factorial(k)


def _gols_esperados(gols_time: float, gols_sofridos_adv: float, media_liga: float) -> float:
    if media_liga == 0:
        return 0
    ataque = gols_time / media_liga
    defesa = gols_sofridos_adv / media_liga
    return ataque * defesa * media_liga


def prob_over(total_esperado: float, linha: float) -> float:
    """Probabilidade de total de gols > linha."""
    prob = 1.0 - sum(_poisson_pmf(total_esperado, k) for k in range(int(linha) + 1))
    return max(0.0, min(1.0, prob))


def prob_ambas_marcam(gols_esperados_casa: float, gols_esperados_fora: float) -> float:
    p_casa = 1.0 - _poisson_pmf(gols_esperados_casa, 0)
    p_fora = 1.0 - _poisson_pmf(gols_esperados_fora, 0)
    return p_casa * p_fora


def prob_over_1_5(casa_media: float, fora_media: float, def_casa: float, def_fora: float,
                  media_casa: float = MEDIA_GOLS_CASA_LIGA,
                  media_fora: float = MEDIA_GOLS_FORA_LIGA) -> float:
    gols_casa = _gols_esperados(casa_media, def_fora, media_casa)
    gols_fora = _gols_esperados(fora_media, def_casa, media_fora)
    return prob_over(gols_casa + gols_fora, 1.5)


def prob_over_2_5(casa_media: float, fora_media: float, def_casa: float, def_fora: float,
                  media_casa: float = MEDIA_GOLS_CASA_LIGA,
                  media_fora: float = MEDIA_GOLS_FORA_LIGA) -> float:
    gols_casa = _gols_esperados(casa_media, def_fora, media_casa)
    gols_fora = _gols_esperados(fora_media, def_casa, media_fora)
    return prob_over(gols_casa + gols_fora, 2.5)


# ------------------------------------------------------------
# 3. GOL HT (Over 0.5)
# ------------------------------------------------------------

def prob_gol_ht(
    gols_ht_casa: float,
    gols_ht_fora: float,
    gols_ht_sofridos_casa: float,
    gols_ht_sofridos_fora: float,
    media_ht_casa: float = None,
    media_ht_fora: float = None
) -> float:
    if None in (gols_ht_casa, gols_ht_fora, gols_ht_sofridos_casa, gols_ht_sofridos_fora):
        return None

    if media_ht_casa is None:
        media_ht_casa = MEDIA_GOLS_CASA_LIGA * PROPORCAO_GOLS_HT
    if media_ht_fora is None:
        media_ht_fora = MEDIA_GOLS_FORA_LIGA * PROPORCAO_GOLS_HT

    gols_esp_casa = _gols_esperados(gols_ht_casa, gols_ht_sofridos_fora, media_ht_casa)
    gols_esp_fora = _gols_esperados(gols_ht_fora, gols_ht_sofridos_casa, media_ht_fora)

    prob_0 = _poisson_pmf(gols_esp_casa, 0) * _poisson_pmf(gols_esp_fora, 0)
    return 1.0 - prob_0


# ------------------------------------------------------------
# 4. ESCANTEIOS (linha dinâmica com margem de segurança)
# ------------------------------------------------------------

def prob_over_escanteios(
    escanteios_casa: float,
    escanteios_fora: float,
    escanteios_sofridos_casa: float,
    escanteios_sofridos_fora: float,
    media_esc_casa_liga: float = 5.5,
    media_esc_fora_liga: float = 4.5,
    margem: float = MARGEM_SEGURANCA_ESCANTEIOS
) -> float:
    """
    Retorna probabilidade de over na linha (total esperado - margem).
    """
    if None in (escanteios_casa, escanteios_fora, escanteios_sofridos_casa, escanteios_sofridos_fora):
        return None

    esc_casa = (escanteios_casa / media_esc_casa_liga) * (escanteios_sofridos_fora / media_esc_fora_liga) * media_esc_casa_liga
    esc_fora = (escanteios_fora / media_esc_fora_liga) * (escanteios_sofridos_casa / media_esc_casa_liga) * media_esc_fora_liga
    total_esperado = esc_casa + esc_fora

    linha = total_esperado - margem
    if linha < 0:
        linha = 0.0
    return prob_over(total_esperado, linha) if total_esperado > 0 else 0.5
