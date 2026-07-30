import pickle
import numpy as np
from core.ratings import (
    calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv,
    obter_prateleira, _percentil, calcular_pontuacao_jogo
)
from core.elo import calcular_elo, normalizar_elo
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA, FATOR_SUPERACAO, ELO_WEIGHT, ELO_K

from core.tactical_dimensions import compute_all_dimensions, modulate_with_context, compute_mpv
from core.market_engine_v2 import (
    predict_over25, predict_btts, predict_1x2, predict_ht_goal, predict_corners
)
from core.markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht, prob_over_escanteios,
    calcular_bonus_casa, _gols_esperados
)

try:
    from core.contrast import contrast_vector, critical_routes, generate_heatmap
    CONTRAST_AVAILABLE = True
except ImportError:
    CONTRAST_AVAILABLE = False

def _build_stats_for_dimensions(ovrall_dict):
    """Converte o dicionário do time para valores simples (usados pelas dimensões táticas)."""
    return {
        'gols_media': ovrall_dict.get('gols_media', 1.4),
        'gols_sofridos_media': ovrall_dict.get('gols_sofridos_media', 1.4),
        'chutes_media': ovrall_dict.get('chutes_media', 12),
        'chutes_alvo_media': ovrall_dict.get('finalizacoes_alvo_media', 4.5),
        'chutes_alvo_sofridos_media': ovrall_dict.get('finalizacoes_alvo_sofridas_media', 4.5),
        'escanteios_media': ovrall_dict.get('escanteios_media', 5.0),
        'posse_media': ovrall_dict.get('posse_media', 50.0),
        'conversao': ovrall_dict.get('conversao', 0.25),
        'gols_escanteio': ovrall_dict.get('gols_escanteio', 0.36),
        'gols_sofridos_escanteio': ovrall_dict.get('gols_sofridos_escanteio', 0.21),
    }

def aproveitamento_contra_prateleira(jogos, prateleira_alvo):
    if not jogos:
        return 50.0
    jogos_alvo = [j for j in jogos if j.get('prateleira_adv') == prateleira_alvo]
    if len(jogos_alvo) >= 3:
        pontos = sum(3 if j['resultado'] == 'V' else 1 if j['resultado'] == 'E' else 0 for j in jogos_alvo)
        return (pontos / (len(jogos_alvo) * 3)) * 100
    else:
        total = jogos[:10]
        pontos = sum(3 if j['resultado'] == 'V' else 1 if j['resultado'] == 'E' else 0 for j in total)
        return (pontos / (len(total) * 3)) * 100 if total else 50.0

def executar_manual(dados, pkl_path='calibration_params.pkl'):
    # --- Benchmarks (manuais ou do pkl) ---
    if dados.get('benchmarks_usr'):
        benchmarks = dados['benchmarks_usr']
    else:
        try:
            with open(pkl_path, 'rb') as f:
                calib = pickle.load(f)
            benchmarks = calib['benchmarks']
        except:
            benchmarks = {}

    # --- Prateleiras ---
    prat_real_casa = obter_prateleira(dados['pos_casa'])
    prat_real_fora = obter_prateleira(dados['pos_fora'])
    prateleiras = {
        dados['time_casa']: prat_real_casa,
        dados['time_fora']: prat_real_fora
    }
    for j in dados.get('jogos_casa', []) + dados.get('jogos_fora', []):
        prat_adv = j.get('prateleira_adv', 'Media')
        nome_adv = j.get('adversario', '')
        if nome_adv and nome_adv not in prateleiras:
            prateleiras[nome_adv] = prat_adv
    for adv, prat in dados.get('prateleiras_extra', {}).items():
        if adv not in prateleiras:
            prateleiras[adv] = prat

    # --- IMA ---
    if len(dados.get('jogos_casa', [])) >= 5 and len(dados.get('jogos_fora', [])) >= 5:
        rec_casa = {
            '10G': dados['jogos_casa'][:10], '5G': dados['jogos_casa'][:5], '3G': dados['jogos_casa'][:3],
            '5CF': [j for j in dados['jogos_casa'] if j['mandante']][:5],
            '3CF': [j for j in dados['jogos_casa'] if j['mandante']][:3],
        }
        rec_fora = {
            '10G': dados['jogos_fora'][:10], '5G': dados['jogos_fora'][:5], '3G': dados['jogos_fora'][:3],
            '5CF': [j for j in dados['jogos_fora'] if not j['mandante']][:5],
            '3CF': [j for j in dados['jogos_fora'] if not j['mandante']][:3],
        }
        ima_casa = calcular_ima(dados['time_casa'], rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                                rec_casa['5CF'], rec_casa['3CF'], prateleiras)
        ima_fora = calcular_ima(dados['time_fora'], rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                                rec_fora['5CF'], rec_fora['3CF'], prateleiras)

        def detalhar_ima(time, recs):
            detalhes = {}
            for nome, jogos in recs.items():
                if not jogos:
                    detalhes[nome] = []
                    continue
                pts = []
                for j in jogos:
                    prat_time = prateleiras[time]
                    prat_adv = j.get('prateleira_adv', prateleiras.get(j['adversario'], 'Media'))
                    pontos = calcular_pontuacao_jogo(j['resultado'], prat_time, prat_adv)
                    pts.append({
                        'jogo': f"{j['resultado']} vs {j.get('adversario', '?')}",
                        'pontos': pontos,
                        'prateleira_time': prat_time,
                        'prateleira_adv': prat_adv
                    })
                detalhes[nome] = pts
            return detalhes

        ima_det_casa = detalhar_ima(dados['time_casa'], rec_casa)
        ima_det_fora = detalhar_ima(dados['time_fora'], rec_fora)
    else:
        ima_casa = 50.0
        ima_fora = 50.0
        ima_det_casa = {}
        ima_det_fora = {}

    # --- OVRall ---
    dados_liga = {}
    todas_chaves = set(dados.get('ovrall_casa', {}).keys()) | set(dados.get('ovrall_fora', {}).keys())
    for k in todas_chaves:
        vc = dados.get('ovrall_casa', {}).get(k)
        vf = dados.get('ovrall_fora', {}).get(k)
        valores = []
        if vc is not None: valores.append(vc)
        if vf is not None: valores.append(vf)
        if valores: dados_liga[k] = valores
    ovrall_val_casa = calcular_ovrall(dados.get('ovrall_casa', {}), dados_liga)
    ovrall_val_fora = calcular_ovrall(dados.get('ovrall_fora', {}), dados_liga)

    dims = {
        'Ataque': [('gols_media', False), ('xg_media', False), ('finalizacoes_alvo_media', False), ('conversao', False)],
        'Defesa': [('gols_sofridos_media', True), ('xga_media', True), ('finalizacoes_alvo_sofridas_media', True), ('desarmes_intercep_media', False)],
        'MeioCampo': [('posse_media', False), ('passes_certos_pct', False), ('passes_chave_media', False), ('assistencias_media', False), ('chutes_media', False)],
        'Consistencia': [('desvio_pontos', True), ('desvio_gols_pro', True), ('desvio_gols_sofridos', True), ('clean_sheets_pct', False)],
        'Resiliencia': [('pontos_pos_desvantagem_media', False), ('gols_ultimos_15min_media', False), ('pontos_apos_derrota_media', False), ('diff_aprov_casa_fora', True), ('aprov_viradas_favor', False), ('aprov_viradas_contra', True)],
    }
    notas_casa = {}
    notas_fora = {}
    detalhes_ovr = {}
    for nome, indicadores in dims.items():
        det_casa = []
        det_fora = []
        for ind, menor in indicadores:
            vc = dados.get('ovrall_casa', {}).get(ind)
            vf = dados.get('ovrall_fora', {}).get(ind)
            if vc is not None and vf is not None and dados_liga.get(ind):
                lista = dados_liga[ind]
                perc_c = _percentil(vc, lista, menor)
                perc_f = _percentil(vf, lista, menor)
                det_casa.append((ind, vc, perc_c))
                det_fora.append((ind, vf, perc_f))
        if det_casa:
            notas_casa[nome] = sum(x[2] for x in det_casa) / len(det_casa)
            notas_fora[nome] = sum(x[2] for x in det_fora) / len(det_fora)
            detalhes_ovr[nome] = {'casa': det_casa, 'fora': det_fora}

    # --- IC ---
    ic_casa = dados.get('ic_casa', {})
    ic_fora = dados.get('ic_fora', {})
    ic_casa['contra_escalao_adversario'] = aproveitamento_contra_prateleira(dados.get('jogos_casa', []), prat_real_fora) / 100.0
    ic_fora['contra_escalao_adversario'] = aproveitamento_contra_prateleira(dados.get('jogos_fora', []), prat_real_casa) / 100.0
    ic_val_casa = calcular_ic(ic_casa)
    ic_val_fora = calcular_ic(ic_fora)

    # --- MPV base ---
    mpv_base_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
    mpv_base_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

    # --- Superação ---
    niveis = {'Elite':5, 'Alta':4, 'Media':3, 'Baixa':2, 'Critica':1}
    def fator_superacao(prat_real, prat_projetada):
        diff = niveis.get(prat_real, 3) - niveis.get(prat_projetada, 3)
        return diff * FATOR_SUPERACAO
    superacao_casa = fator_superacao(prat_real_casa, dados.get('prat_casa', 'Media'))
    superacao_fora = fator_superacao(prat_real_fora, dados.get('prat_fora', 'Media'))
    mpv_base_casa += max(-10.0, min(10.0, superacao_casa))
    mpv_base_fora += max(-10.0, min(10.0, superacao_fora))

    # --- ELO ---
    elo_casa = calcular_elo(dados['time_casa'], dados.get('jogos_casa', []), prateleiras, k=ELO_K)
    elo_fora = calcular_elo(dados['time_fora'], dados.get('jogos_fora', []), prateleiras, k=ELO_K)
    elos_liga = [elo_casa, elo_fora]
    elo_norm_casa = normalizar_elo(elo_casa, elos_liga)
    elo_norm_fora = normalizar_elo(elo_fora, elos_liga)

    mpv_casa = ELO_WEIGHT * elo_norm_casa + (1 - ELO_WEIGHT) * mpv_base_casa
    mpv_fora = ELO_WEIGHT * elo_norm_fora + (1 - ELO_WEIGHT) * mpv_base_fora

    # ================================================================
    # PROBABILIDADES ORIGINAIS
    # ================================================================
    bonus_casa = calcular_bonus_casa(dados.get('ovrall_casa', {}).get('diff_aprov_casa_fora', 0))
    p1_orig, pX_orig, p2_orig = prob_1x2(mpv_base_casa, mpv_base_fora, bonus_casa)

    gols_media_casa = dados.get('ovrall_casa', {}).get('gols_media', 1.5)
    gols_media_fora = dados.get('ovrall_fora', {}).get('gols_media', 1.2)
    gols_sofridos_casa = dados.get('ovrall_casa', {}).get('gols_sofridos_media', 1.2)
    gols_sofridos_fora = dados.get('ovrall_fora', {}).get('gols_sofridos_media', 1.5)
    over25_orig = prob_over_2_5(gols_media_casa, gols_media_fora, gols_sofridos_casa, gols_sofridos_fora)

    media_gols_casa_liga = dados.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA)
    media_gols_fora_liga = dados.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)
    gols_esp_casa = _gols_esperados(gols_media_casa, gols_sofridos_fora, media_gols_fora_liga)
    gols_esp_fora = _gols_esperados(gols_media_fora, gols_sofridos_casa, media_gols_casa_liga)
    btts_orig = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)

    gol_ht_orig = prob_gol_ht(
        dados.get('ovrall_casa', {}).get('gols_ht_media', 0.5) or 0.5,
        dados.get('ovrall_fora', {}).get('gols_ht_media', 0.5) or 0.5,
        dados.get('ovrall_casa', {}).get('gols_ht_sofridos_media', 0.5) or 0.5,
        dados.get('ovrall_fora', {}).get('gols_ht_sofridos_media', 0.5) or 0.5
    )
    esc_orig = prob_over_escanteios(
        dados.get('ovrall_casa', {}).get('escanteios_media', 5.0) or 5.0,
        dados.get('ovrall_fora', {}).get('escanteios_media', 5.0) or 5.0,
        dados.get('ovrall_casa', {}).get('escanteios_sofridos_media', 5.0) or 5.0,
        dados.get('ovrall_fora', {}).get('escanteios_sofridos_media', 5.0) or 5.0
    )

    # ================================================================
    # MODELO CALIBRADO E DIMENSÕES TÁTICAS
    # ================================================================
    try:
        if not dados.get('benchmarks_usr'):
            with open(pkl_path, 'rb') as f:
                calib = pickle.load(f)
            benchmarks = calib.get('benchmarks', benchmarks)
            dimension_weights = calib.get('dimension_weights', {})
        else:
            dimension_weights = {}
    except:
        dimension_weights = {}

    stats_casa = _build_stats_for_dimensions(dados.get('ovrall_casa', {}))
    stats_fora = _build_stats_for_dimensions(dados.get('ovrall_fora', {}))

    INDICATORS_MAP = {
        'ataque_posicional': ['gols_media', 'chutes_alvo_media', 'conversao'],
        'ataque_transicao': [],
        'defesa_organizada': ['gols_sofridos_media', 'chutes_alvo_sofridos_media'],
        'defesa_transicao': [],
        'bola_parada_ofensiva': ['gols_escanteio'],
        'bola_parada_defensiva': ['gols_sofridos_escanteio'],
        'controle_meio_campo': ['posse_media'],
        'pressao_alta': [],
        'resistencia_pressao': [],
    }

    dims_casa_raw = compute_all_dimensions(stats_casa, INDICATORS_MAP, benchmarks)
    dims_fora_raw = compute_all_dimensions(stats_fora, INDICATORS_MAP, benchmarks)

    dims_casa_mod = modulate_with_context(dims_casa_raw, ima_casa, ic_val_casa)
    dims_fora_mod = modulate_with_context(dims_fora_raw, ima_fora, ic_val_fora)

    mpv_tactical_casa = compute_mpv(dims_casa_mod, dimension_weights) if dimension_weights else 50.0
    mpv_tactical_fora = compute_mpv(dims_fora_mod, dimension_weights) if dimension_weights else 50.0

    ovr_casa = ovrall_val_casa
    ovr_fora = ovrall_val_fora
    ic_casa = ic_val_casa
    ic_fora = ic_val_fora
    elo_casa = elo_norm_casa
    elo_fora = elo_norm_fora
    super_casa = superacao_casa
    super_fora = superacao_fora

    adv_probs_1x2 = predict_1x2(mpv_tactical_casa, mpv_tactical_fora, ovr_casa, ovr_fora, ic_casa, ic_fora, elo_casa, elo_fora, super_casa, super_fora)
    adv_over25 = predict_over25(dims_casa_mod, dims_fora_mod, ovr_casa, ovr_fora, ic_casa, ic_fora, elo_casa, elo_fora, super_casa, super_fora,
                                gols_media_casa, gols_media_fora, gols_sofridos_casa, gols_sofridos_fora, media_gols_casa_liga, media_gols_fora_liga)
    adv_btts = predict_btts(dims_casa_mod, dims_fora_mod, ovr_casa, ovr_fora, ic_casa, ic_fora, elo_casa, elo_fora, super_casa, super_fora,
                            gols_media_casa, gols_media_fora, gols_sofridos_casa, gols_sofridos_fora, media_gols_casa_liga, media_gols_fora_liga)
    adv_ht = predict_ht_goal(dims_casa_mod, dims_fora_mod, ovr_casa, ovr_fora, ic_casa, ic_fora, elo_casa, elo_fora, super_casa, super_fora,
                             dados.get('ovrall_casa', {}).get('gols_ht_media', 0.5) or 0.5,
                             dados.get('ovrall_fora', {}).get('gols_ht_media', 0.5) or 0.5,
                             dados.get('ovrall_casa', {}).get('gols_ht_sofridos_media', 0.5) or 0.5,
                             dados.get('ovrall_fora', {}).get('gols_ht_sofridos_media', 0.5) or 0.5)
    adv_esc = predict_corners(dims_casa_mod, dims_fora_mod, ovr_casa, ovr_fora, ic_casa, ic_fora, elo_casa, elo_fora, super_casa, super_fora,
                              dados.get('ovrall_casa', {}).get('escanteios_media', 5.0) or 5.0,
                              dados.get('ovrall_fora', {}).get('escanteios_media', 5.0) or 5.0,
                              dados.get('ovrall_casa', {}).get('escanteios_sofridos_media', 5.0) or 5.0,
                              dados.get('ovrall_fora', {}).get('escanteios_sofridos_media', 5.0) or 5.0)

    # ================================================================
    # PROBABILIDADES MÉDIAS
    # ================================================================
    def media_prob(orig, adv):
        if adv is None: return orig
        return (orig + adv) / 2.0

    p1 = media_prob(p1_orig, adv_probs_1x2['casa'])
    pX = media_prob(pX_orig, adv_probs_1x2['empate'])
    p2 = media_prob(p2_orig, adv_probs_1x2['fora'])
    over25 = media_prob(over25_orig, adv_over25)
    btts = media_prob(btts_orig, adv_btts)
    gol_ht = media_prob(gol_ht_orig, adv_ht)
    esc = media_prob(esc_orig, adv_esc)

    # ================================================================
    # CONTRASTE TÁTICO
    # ================================================================
    deltas = {}
    routes = []
    heatmap_img = None
    if CONTRAST_AVAILABLE:
        deltas = contrast_vector(dims_casa_mod, dims_fora_mod)
        routes = critical_routes(deltas)
        heatmap_img = generate_heatmap(deltas)

    # ================================================================
    # EDGE SCORE (odds de mercado)
    # ================================================================
    odds = dados.get('odds', {})
    edges = {}
    if odds.get('odd_casa') and odds.get('odd_empate') and odds.get('odd_fora'):
        impl_c = 1 / odds['odd_casa']
        impl_e = 1 / odds['odd_empate']
        impl_f = 1 / odds['odd_fora']
        total_impl = impl_c + impl_e + impl_f
        edges['edge_casa'] = p1 - (impl_c / total_impl)
        edges['edge_empate'] = pX - (impl_e / total_impl)
        edges['edge_fora'] = p2 - (impl_f / total_impl)
    if odds.get('odd_over'):
        edges['edge_over'] = over25 - (1 / odds['odd_over'])
    if odds.get('odd_btts'):
        edges['edge_btts'] = btts - (1 / odds['odd_btts'])
    if odds.get('odd_ht'):
        edges['edge_ht'] = gol_ht - (1 / odds['odd_ht'])
    if odds.get('odd_esc'):
        edges['edge_esc'] = esc - (1 / odds['odd_esc'])

    # ================================================================
    # RESULTADO
    # ================================================================
    res = {
        'time_casa': dados['time_casa'], 'time_fora': dados['time_fora'],
        'p1': p1, 'pX': pX, 'p2': p2,
        'over25': over25, 'btts': btts, 'gol_ht': gol_ht, 'esc': esc,
        'p1_orig': p1_orig, 'pX_orig': pX_orig, 'p2_orig': p2_orig,
        'over25_orig': over25_orig, 'btts_orig': btts_orig,
        'gol_ht_orig': gol_ht_orig, 'esc_orig': esc_orig,
        'p1_adv': adv_probs_1x2['casa'], 'pX_adv': adv_probs_1x2['empate'], 'p2_adv': adv_probs_1x2['fora'],
        'over25_adv': adv_over25, 'btts_adv': adv_btts,
        'gol_ht_adv': adv_ht, 'esc_adv': adv_esc,
        'ima_casa': ima_casa, 'ima_fora': ima_fora,
        'mpv_casa': mpv_casa, 'mpv_fora': mpv_fora,
        'ovrall_casa': ovrall_val_casa, 'ovrall_fora': ovrall_val_fora,
        'ic_casa': ic_val_casa, 'ic_fora': ic_val_fora,
        'notas_casa': notas_casa, 'notas_fora': notas_fora,
        'detalhes_ima': {'casa': ima_det_casa, 'fora': ima_det_fora},
        'detalhes_ovr': detalhes_ovr,
        'prateleiras': prateleiras,
        'superacao_casa': superacao_casa, 'superacao_fora': superacao_fora,
        'prat_real_casa': prat_real_casa, 'prat_real_fora': prat_real_fora,
        'prat_proj_casa': dados.get('prat_casa', 'Media'),
        'prat_proj_fora': dados.get('prat_fora', 'Media'),
        'elo_norm_casa': elo_norm_casa, 'elo_norm_fora': elo_norm_fora,
        'mpv_tactical_casa': mpv_tactical_casa, 'mpv_tactical_fora': mpv_tactical_fora,
        'tactical': {
            'dimensions_casa': dims_casa_mod,
            'dimensions_fora': dims_fora_mod,
            'deltas': deltas,
            'critical_routes': routes,
            'heatmap': heatmap_img,
        } if CONTRAST_AVAILABLE else None,
        'edges': edges,
        'benchmarks': benchmarks,
    }
    return res, None
