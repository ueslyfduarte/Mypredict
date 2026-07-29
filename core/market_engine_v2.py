import pickle
import numpy as np
from scipy.stats import poisson

# Carrega o arquivo calibrado (deve estar na raiz do repositório)
with open('calibration_params.pkl', 'rb') as f:
    _params = pickle.load(f)

# Extrai os objetos necessários
_over_coefs = _params['over_coefs']
_features_over = _params['features_over']
_logreg = _params['logreg']
_dim_weights = _params['dimension_weights']

def predict_over25(dimensions_h, dimensions_a):
    log_lam = _over_coefs['const']
    for feat in _features_over:
        if feat.startswith('dim_h_'):
            dim_name = feat[6:]
            val = dimensions_h.get(dim_name, 50.0)
        else:
            dim_name = feat[6:]
            val = dimensions_a.get(dim_name, 50.0)
        log_lam += _over_coefs.get(feat, 0) * val
    lam = np.exp(log_lam)
    prob = 1.0 - poisson.cdf(2, lam)
    return prob

def predict_1x2(mpv_h, mpv_a):
    probs = _logreg.predict_proba([[mpv_h, mpv_a]])[0]
    return {
        'casa': probs[0],
        'empate': probs[1],
        'fora': probs[2]
    }

def predict_btts(dimensions_h, dimensions_a):
    # Como o modelo BTTS não foi treinado explicitamente, usamos
    # uma aproximação baseada nas dimensões ofensivas/defensivas
    # Vamos adotar um cálculo simples com Poisson independente.
    # Se você quiser um modelo BTTS real, me avise.
    # Aqui, usamos os mesmos coeficientes do over para estimar lambda total
    # e dividimos proporcionalmente (simplificação provisória).
    log_lam = _over_coefs['const']
    for feat in _features_over:
        if feat.startswith('dim_h_'):
            dim_name = feat[6:]
            val = dimensions_h.get(dim_name, 50.0)
        else:
            dim_name = feat[6:]
            val = dimensions_a.get(dim_name, 50.0)
        log_lam += _over_coefs.get(feat, 0) * val
    lam_total = np.exp(log_lam)
    # Divisão bruta: 55% dos gols para o mandante, 45% visitante
    lam_h = lam_total * 0.53
    lam_a = lam_total * 0.47
    p_btts = (1 - poisson.pmf(0, lam_h)) * (1 - poisson.pmf(0, lam_a))
    return p_btts
