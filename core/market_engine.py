# core/market_engine.py
import math
from config import (
    IMA_FACTOR, IC_FACTOR, CONSISTENCY_FACTOR,
    MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA,
    PROPORCAO_GOLS_HT, MARGEM_SEGURANCA_ESCANTEIOS
)
from core.ratings import calcular_consistencia

def _poisson(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (lam ** k) * math.exp(-lam) / math.factorial(k)

def _ajuste_ima_ic(ima_casa, ima_fora, ic_casa, ic_fora):
    ima_medio = (ima_casa + ima_fora) / 2
    ic_medio = (ic_casa + ic_fora) / 2
    fator_ima = 1 + IMA_FACTOR * (ima_medio - 50)
    fator_ic = 1 + IC_FACTOR * (ic_medio - 50)
    return fator_ima * fator_ic

def _ajuste_consistencia(ovr_casa, ovr_fora):
    cons_casa = calcular_consistencia(ovr_casa.get('desvio_pontos'))
    cons_fora = calcular_consistencia(ovr_fora.get('desvio_pontos'))
    return (cons_casa + cons_fora) / 2

def _valor_ou_padrao(valor, padrao):
    return valor if valor is not None else padrao

def prob_1x2_v2(mpv_casa, mpv_fora, bonus_casa):
    SIGMOID_K = 0.12
    SIGMA_EMPATE = 15.0
    PROB_EMPATE_BASE = 0.28

    delta = (mpv_casa - mpv_fora) + bonus_casa
    p1 = 1.0 / (1.0 + math.exp(-SIGMOID_K * delta))
    pX = PROB_EMPATE_BASE * math.exp(-((abs(delta) / SIGMA_EMPATE) ** 2))
    p2 = max(0.0, 1.0 - p1 - pX)
    total = p1 + pX + p2
    if total > 0:
        p1 /= total
        pX /= total
        p2 /= total
    return p1, pX, p2

def prob_over25(ovr_casa, ovr_fora, ima_casa, ima_fora, ic_casa, ic_fora,
                media_casa=MEDIA_GOLS_CASA_LIGA, media_fora=MEDIA_GOLS_FORA_LIGA):
    gols_casa = _valor_ou_padrao(ovr_casa.get('gols_media'), media_casa)
    gols_fora = _valor_ou_padrao(ovr_fora.get('gols_media'), media_fora)
    gols_sofridos_casa = _valor_ou_padrao(ovr_casa.get('gols_sofridos_media'), media_casa)
    gols_sofridos_fora = _valor_ou_padrao(ovr_fora.get('gols_sofridos_media'), media_fora)

    esp_casa = gols_casa * (gols_sofridos_fora / media_fora) if media_fora > 0 else gols_casa
    esp_fora = gols_fora * (gols_sofridos_casa / media_casa) if media_casa > 0 else gols_fora

    fator = _ajuste_ima_ic(ima_casa, ima_fora, ic_casa, ic_fora)
    conf = _ajuste_consistencia(ovr_casa, ovr_fora)
    fator *= (0.8 + 0.4 * conf)

    lam = (esp_casa + esp_fora) * fator
    prob = 1.0 - sum(_poisson(k, lam) for k in range(3))
    return max(0.0, min(1.0, prob))

def prob_btts(ovr_casa, ovr_fora, ima_casa, ima_fora, ic_casa, ic_fora,
              media_casa=MEDIA_GOLS_CASA_LIGA, media_fora=MEDIA_GOLS_FORA_LIGA):
    gols_casa = _valor_ou_padrao(ovr_casa.get('gols_media'), media_casa)
    gols_fora = _valor_ou_padrao(ovr_fora.get('gols_media'), media_fora)
    gols_sofridos_casa = _valor_ou_padrao(ovr_casa.get('gols_sofridos_media'), media_casa)
    gols_sofridos_fora = _valor_ou_padrao(ovr_fora.get('gols_sofridos_media'), media_fora)

    esp_casa = gols_casa * (gols_sofridos_fora / media_fora) if media_fora > 0 else gols_casa
    esp_fora = gols_fora * (gols_sofridos_casa / media_casa) if media_casa > 0 else gols_fora

    fator = _ajuste_ima_ic(ima_casa, ima_fora, ic_casa, ic_fora)
    conf = _ajuste_consistencia(ovr_casa, ovr_fora)
    fator *= (0.8 + 0.4 * conf)

    p0_casa = _poisson(0, esp_casa * fator)
    p0_fora = _poisson(0, esp_fora * fator)
    return (1.0 - p0_casa) * (1.0 - p0_fora)

def prob_gol_ht_v2(ovr_casa, ovr_fora, ima_casa, ima_fora, ic_casa, ic_fora,
                   media_ht_casa=0.75, media_ht_fora=0.65):
    gols_casa = _valor_ou_padrao(ovr_casa.get('gols_ht_media'), media_ht_casa)
    gols_fora = _valor_ou_padrao(ovr_fora.get('gols_ht_media'), media_ht_fora)
    gols_sofridos_casa = _valor_ou_padrao(ovr_casa.get('gols_ht_sofridos_media'), media_ht_casa)
    gols_sofridos_fora = _valor_ou_padrao(ovr_fora.get('gols_ht_sofridos_media'), media_ht_fora)

    esp_casa = gols_casa * (gols_sofridos_fora / media_ht_fora) if media_ht_fora > 0 else gols_casa
    esp_fora = gols_fora * (gols_sofridos_casa / media_ht_casa) if media_ht_casa > 0 else gols_fora

    fator = _ajuste_ima_ic(ima_casa, ima_fora, ic_casa, ic_fora)
    lam = (esp_casa + esp_fora) * fator
    p0 = _poisson(0, lam)
    return 1.0 - p0

def prob_over_escanteios_v2(ovr_casa, ovr_fora, ima_casa, ima_fora, ic_casa, ic_fora,
                            media_casa=5.0, media_fora=4.5, margem=MARGEM_SEGURANCA_ESCANTEIOS):
    esc_casa = _valor_ou_padrao(ovr_casa.get('escanteios_media'), media_casa)
    esc_fora = _valor_ou_padrao(ovr_fora.get('escanteios_media'), media_fora)
    esc_sofridos_casa = _valor_ou_padrao(ovr_casa.get('escanteios_sofridos_media'), media_casa)
    esc_sofridos_fora = _valor_ou_padrao(ovr_fora.get('escanteios_sofridos_media'), media_fora)

    lam_casa = esc_casa * (esc_sofridos_fora / media_fora) if media_fora > 0 else esc_casa
    lam_fora = esc_fora * (esc_sofridos_casa / media_casa) if media_casa > 0 else esc_fora

    fator = _ajuste_ima_ic(ima_casa, ima_fora, ic_casa, ic_fora)
    lam = (lam_casa + lam_fora) * fator
    prob = 1.0 - sum(_poisson(k, lam) for k in range(9))
    return min(1.0, prob + margem/100)
