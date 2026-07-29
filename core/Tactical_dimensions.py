# core/tactical_dimensions.py
import numpy as np
from config import (
    LEAGUE_BENCHMARKS,
    DIMENSION_INDICATORS,
    DIMENSION_WEIGHTS,
    IMA_MOD_SENSITIVITY,
    IC_MOD_SENSITIVITY
)

def z_score(value, mean, std):
    """Calcula z-score com proteção contra divisão por zero"""
    if std == 0:
        return 0
    return (value - mean) / std

def z_to_scale(z, k=1.5):
    """Converte z-score para escala 0-100 usando sigmoide"""
    return 100 / (1 + np.exp(-k * z))

def compute_dimension_score(team_data, dimension_name, benchmarks):
    """
    Calcula o escore de uma dimensão tática para um time.
    
    Args:
        team_data: dict com todos os indicadores do time
        dimension_name: string (ex: 'ataque_posicional')
        benchmarks: dict com médias e desvios da liga por indicador
    
    Returns:
        float: escore bruto 0-100
    """
    indicators = DIMENSION_INDICATORS.get(dimension_name, [])
    scores = []
    
    for ind in indicators:
        value = team_data.get(ind)
        if value is None:
            continue
        
        mean = benchmarks[ind]['mean']
        std = benchmarks[ind]['std']
        
        z = z_score(value, mean, std)
        
        # Inverte para indicadores onde menor é melhor
        if benchmarks[ind].get('lower_better', False):
            z = -z
            
        score = z_to_scale(z)
        scores.append(score)
    
    if not scores:
        return 50.0  # neutro se não houver dados
    
    return np.mean(scores)

def compute_all_dimensions(team_data, benchmarks):
    """
    Retorna vetor tático completo para um time.
    
    Returns:
        dict: {dimension_name: raw_score}
    """
    dimensions = {}
    for dim in DIMENSION_INDICATORS.keys():
        dimensions[dim] = compute_dimension_score(team_data, dim, benchmarks)
    return dimensions

def modulate_with_context(raw_scores, ima, ic):
    """
    Aplica modulação de momento (IMA) e contexto (IC) nos escores.
    
    Args:
        raw_scores: dict de scores brutos por dimensão
        ima: float 0-100
        ic: float 0-100
    
    Returns:
        dict: scores modulados
    """
    modulated = {}
    ima_factor = 1 + IMA_MOD_SENSITIVITY * (ima - 50) / 50
    ic_factor = 1 + IC_MOD_SENSITIVITY * (ic - 50) / 50
    
    for dim, score in raw_scores.items():
        adjusted = score * ima_factor * ic_factor
        modulated[dim] = max(0, min(100, adjusted))
    
    return modulated

def compute_mpv_from_dimensions(modulated_scores, weights):
    """
    Calcula o MPV como média ponderada das dimensões táticas.
    
    Args:
        modulated_scores: dict com scores modulados
        weights: dict com peso de cada dimensão
    
    Returns:
        float: MPV 0-100
    """
    total = 0
    weight_sum = 0
    for dim, score in modulated_scores.items():
        w = weights.get(dim, 0)
        total += w * score
        weight_sum += w
    
    return total / weight_sum if weight_sum > 0 else 50.0
