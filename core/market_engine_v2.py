import pickle
import numpy as np
from scipy.stats import poisson

try:
    with open('calibration_params.pkl', 'rb') as f:
        _params = pickle.load(f)
except FileNotFoundError:
    _params = {}

def _calc_lam(dim_h, dim_a, ovr_h, ovr_a, ic_h, ic_a, elo_h, elo_a, super_h, super_a,
              coefs, feats, default_lam=1.5):
    if coefs and feats:
        log_lam = coefs.get('const', 0)
        for feat in feats:
            if feat.startswith('dim_h_'):
                val = dim_h.get(feat[6:], 50)
            elif feat.startswith('dim_a_'):
                val = dim_a.get(feat[6:], 50)
            elif feat == 'ovr_h': val = ovr_h
            elif feat == 'ovr_a': val = ovr_a
            elif feat == 'ic_h': val = ic_h
            elif feat == 'ic_a': val = ic_a
            elif feat == 'elo_h': val = elo_h
            elif feat == 'elo_a': val = elo_a
            elif feat == 'super_h': val = super_h
            elif feat == 'super_a': val = super_a
            else: continue
            log_lam += coefs.get(feat, 0) * val
        return np.exp(log_lam)
    else:
        return default_lam

def predict_over25(dim_h, dim_a, ovr_h, ovr_a, ic_h, ic_a, elo_h, elo_a, super_h, super_a,
                   gols_media_casa=1.5, gols_media_fora=1.2, gols_sofridos_casa=1.2, gols_sofridos_fora=1.5,
                   media_casa=1.5, media_fora=1.2):
    if _params.get('over_coefs'):
        lam = _calc_lam(dim_h, dim_a, ovr_h, ovr_a, ic_h, ic_a, elo_h, elo_a, super_h, super_a,
                        _params['over_coefs'], _params.get('features_over', []))
        return 1 - poisson.cdf(2, lam)
    else:
        lam_casa = gols_media_casa * (gols_sofridos_fora / media_fora) if media_fora else gols_media_casa
        lam_fora = gols_media_fora * (gols_sofridos_casa / media_casa) if media_casa else gols_media_fora
        return 1 - poisson.cdf(2, lam_casa + lam_fora)

def predict_btts(dim_h, dim_a, ovr_h, ovr_a, ic_h, ic_a, elo_h, elo_a, super_h, super_a,
                 gols_media_casa=1.5, gols_media_fora=1.2, gols_sofridos_casa=1.2, gols_sofridos_fora=1.5,
                 media_casa=1.5, media_fora=1.2):
    if _params.get('btts_coefs_home') and _params.get('btts_coefs_away'):
        lam_h = _calc_lam(dim_h, dim_a, ovr_h, ovr_a, ic_h, ic_a, elo_h, elo_a, super_h, super_a,
                          _params['btts_coefs_home'], _params.get('features_h_goals', []))
        lam_a = _calc_lam(dim_h, dim_a, ovr_h, ovr_a, ic_h, ic_a, elo_h, elo_a, super_h, super_a,
                          _params['btts_coefs_away'], _params.get('features_a_goals', []))
        return (1 - poisson.pmf(0, lam_h)) * (1 - poisson.pmf(0, lam_a))
    else:
        lam_h = gols_media_casa * (gols_sofridos_fora / media_fora) if media_fora else gols_media_casa
        lam_a = gols_media_fora * (gols_sofridos_casa / media_casa) if media_casa else gols_media_fora
        return (1 - poisson.pmf(0, lam_h)) * (1 - poisson.pmf(0, lam_a))

def predict_1x2(mpv_tatico_h, mpv_tatico_a, ovr_h, ovr_a, ic_h, ic_a, elo_h, elo_a, super_h, super_a):
    model = _params.get('logreg')
    if model is not None and _params.get('features_1x2'):
        feats = _params['features_1x2']
        X = []
        for f in feats:
            if f == 'mpv_tatico_h': X.append(mpv_tatico_h)
            elif f == 'mpv_tatico_a': X.append(mpv_tatico_a)
            elif f == 'ovr_h': X.append(ovr_h)
            elif f == 'ovr_a': X.append(ovr_a)
            elif f == 'ic_h': X.append(ic_h)
            elif f == 'ic_a': X.append(ic_a)
            elif f == 'elo_h': X.append(elo_h)
            elif f == 'elo_a': X.append(elo_a)
            elif f == 'super_h': X.append(super_h)
            elif f == 'super_a': X.append(super_a)
            else: X.append(0)
        probs = model.predict_proba([X])[0]
        return {'casa': probs[0], 'empate': probs[1], 'fora': probs[2]}
    else:
        # fallback com fórmula sigmoide
        diff = mpv_tatico_h - mpv_tatico_a
        p_casa = 1 / (1 + np.exp(-0.12 * diff))
        p_empate = 0.28 * np.exp(-(abs(diff)/15)**2)
        p_fora = 1 - p_casa - p_empate
        return {'casa': p_casa, 'empate': p_empate, 'fora': p_fora}

def predict_ht_goal(dim_h, dim_a, ovr_h, ovr_a, ic_h, ic_a, elo_h, elo_a, super_h, super_a,
                    gols_ht_casa=0.5, gols_ht_fora=0.5, gols_ht_sofridos_casa=0.5, gols_ht_sofridos_fora=0.5):
    # por enquanto, fallback manual
    lam = (gols_ht_casa * (gols_ht_sofridos_fora / 0.65)) + (gols_ht_fora * (gols_ht_sofridos_casa / 0.75))
    return 1 - poisson.pmf(0, lam)

def predict_corners(dim_h, dim_a, ovr_h, ovr_a, ic_h, ic_a, elo_h, elo_a, super_h, super_a,
                    esc_casa=5.0, esc_fora=5.0, esc_sofridos_casa=5.0, esc_sofridos_fora=5.0):
    # fallback manual
    lam = (esc_casa * (esc_sofridos_fora / 4.5)) + (esc_fora * (esc_sofridos_casa / 5.0))
    return 1 - poisson.cdf(8, lam)

def get_mp_weights():
    return _params.get('mp_weights', {'mpv_tatico': 0.3, 'ovr': 0.25, 'ic': 0.15, 'elo': 0.2, 'super': 0.1})
