import numpy as np

def compute_dimension_score(team_stats, dimension_name, indicators_map, benchmarks):
    indicadores = indicators_map.get(dimension_name, [])
    if not indicadores:
        return 50.0
    scores = []
    for ind in indicadores:
        if ind not in team_stats or ind not in benchmarks:
            continue
        val = team_stats[ind]
        b = benchmarks[ind]
        if b['std'] == 0:
            z = 0
        else:
            z = (val - b['mean']) / b['std']
        if b.get('lower_better', False):
            z = -z
        score = 100 / (1 + np.exp(-1.5 * z))
        scores.append(score)
    if not scores:
        return 50.0
    return np.mean(scores)

def compute_all_dimensions(team_stats, indicators_map, benchmarks):
    dims = {}
    for dim_name in indicators_map:
        dims[dim_name] = compute_dimension_score(team_stats, dim_name, indicators_map, benchmarks)
    return dims

def modulate_with_context(dimensions, ima, ic, ima_sens=0.3, ic_sens=0.2):
    modulated = {}
    ima_factor = 1 + ima_sens * (ima - 50) / 50
    ic_factor = 1 + ic_sens * (ic - 50) / 50
    for dim, score in dimensions.items():
        adjusted = score * ima_factor * ic_factor
        modulated[dim] = max(0, min(100, adjusted))
    return modulated

def compute_mpv(dimensions, weights):
    total = 0
    total_weight = 0
    for dim, w in weights.items():
        if dim in dimensions:
            total += dimensions[dim] * w
            total_weight += w
    if total_weight == 0:
        return 50.0
    return total / total_weight
