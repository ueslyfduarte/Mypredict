# core/calculations.py — Orquestração dos cálculos (automático e manual)
from core.ratings import (
    calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv,
    obter_prateleira, _percentil, calcular_pontuacao_jogo
)
from core.markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

def executar_automatico(liga_nome, temporada, time_casa, time_fora, classificacao_ant, prateleiras,
                        dados_casa, dados_fora, jogos_casa, jogos_fora):
    """Cálculo completo no modo automático (sem IC e OVRall detalhados)."""
    if not classificacao_ant:
        return None, "Classificação indisponível."
    if not dados_casa or not dados_fora:
        return None, "Partidas não encontradas."

    rec_casa = {
        '10G': jogos_casa[:10], '5G': jogos_casa[:5], '3G': jogos_casa[:3],
        '5CF': [j for j in jogos_casa if j['mandante']][:5],
        '3CF': [j for j in jogos_casa if j['mandante']][:3],
    }
    rec_fora = {
        '10G': jogos_fora[:10], '5G': jogos_fora[:5], '3G': jogos_fora[:3],
        '5CF': [j for j in jogos_fora if not j['mandante']][:5],
        '3CF': [j for j in jogos_fora if not j['mandante']][:3],
    }

    ima_casa = calcular_ima(time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                            rec_casa['5CF'], rec_casa['3CF'], prateleiras)
    ima_fora = calcular_ima(time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                            rec_fora['5CF'], rec_fora['3CF'], prateleiras)

    # No modo automático, OVRall e IC são fixos em 50 (neutro)
    mpv_casa = calcular_mpv(ima_casa, 50.0, 50.0)
    mpv_fora = calcular_mpv(ima_fora, 50.0, 50.0)

    bonus_casa = calcular_bonus_casa(dados_casa.get('diff_aprov_casa_fora'))
    p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)
    over25 = prob_over_2_5(
        dados_casa.get('gols_media'), dados_fora.get('gols_media'),
        dados_casa.get('gols_sofridos_media'), dados_fora.get('gols_sofridos_media')
    )
    gols_esp_casa = _gols_esperados(dados_casa.get('gols_media'), dados_fora.get('gols_sofridos_media'), MEDIA_GOLS_FORA_LIGA)
    gols_esp_fora = _gols_esperados(dados_fora.get('gols_media'), dados_casa.get('gols_sofridos_media'), MEDIA_GOLS_CASA_LIGA)
    btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)
    gol_ht = prob_gol_ht(
        dados_casa.get('gols_ht_media', 0.5) or 0.5,
        dados_fora.get('gols_ht_media', 0.5) or 0.5,
        dados_casa.get('gols_ht_sofridos_media', 0.5) or 0.5,
        dados_fora.get('gols_ht_sofridos_media', 0.5) or 0.5
    )
    esc = prob_over_escanteios(
        dados_casa.get('escanteios_media', 5.0) or 5.0,
        dados_fora.get('escanteios_media', 5.0) or 5.0,
        dados_casa.get('escanteios_sofridos_media', 5.0) or 5.0,
        dados_fora.get('escanteios_sofridos_media', 5.0) or 5.0
    )

    return {
        'time_casa': time_casa, 'time_fora': time_fora,
        'p1': p1, 'pX': pX, 'p2': p2,
        'rec_p1': (p1 >= 0.60), 'rec_p2': (p2 >= 0.60),
        'over25': over25, 'btts': btts, 'gol_ht': gol_ht, 'esc': esc,
        'ima_casa': ima_casa, 'ima_fora': ima_fora,
        'mpv_casa': mpv_casa, 'mpv_fora': mpv_fora,
    }, None

def executar_manual(dados):
    """Cálculo completo no modo manual, com detalhamento."""
    if len(dados['jogos_casa']) < 5 or len(dados['jogos_fora']) < 5:
        return None, f"Poucos jogos: Casa={len(dados['jogos_casa'])}, Fora={len(dados['jogos_fora'])}"
    if not dados['ovrall_casa'] or not dados['ovrall_fora']:
        return None, "Métricas OVRall não encontradas."

    # Prateleiras
    prat_casa = obter_prateleira(dados['pos_casa'])
    prat_fora = obter_prateleira(dados['pos_fora'])
    prateleiras = {dados['time_casa']: prat_casa, dados['time_fora']: prat_fora}
    for j in dados['jogos_casa'] + dados['jogos_fora']:
        if j['adversario'] not in prateleiras:
            prateleiras[j['adversario']] = "Media"
    for adv, prat in dados.get('prateleiras_extra', {}).items():
        if adv in prateleiras:
            prateleiras[adv] = prat

    # Recortes
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

    # Detalhamento IMA
    def detalhar_ima(time, recs):
        detalhes = {}
        for nome, jogos in recs.items():
            if not jogos:
                detalhes[nome] = []
                continue
            pts = []
            for j in jogos:
                prat_time = prateleiras[time]
                prat_adv = prateleiras.get(j['adversario'], "Media")
                pontos = calcular_pontuacao_jogo(j['resultado'], prat_time, prat_adv)
                pts.append({
                    'jogo': f"{j['resultado']} vs {j['adversario']}",
                    'pontos': pontos,
                    'prateleira_time': prat_time,
                    'prateleira_adv': prat_adv
                })
            detalhes[nome] = pts
        return detalhes

    ima_det_casa = detalhar_ima(dados['time_casa'], rec_casa)
    ima_det_fora = detalhar_ima(dados['time_fora'], rec_fora)

    # OVRall
    dados_liga = {k: [dados['ovrall_casa'].get(k, 0) or 0, dados['ovrall_fora'].get(k, 0) or 0]
                  for k in set(dados['ovrall_casa']) | set(dados['ovrall_fora'])}
    ovrall_val_casa = calcular_ovrall(dados['ovrall_casa'], dados_liga)
    ovrall_val_fora = calcular_ovrall(dados['ovrall_fora'], dados_liga)

    # Detalhamento OVRall
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
            vc = dados['ovrall_casa'].get(ind)
            vf = dados['ovrall_fora'].get(ind)
            if vc is not None and vf is not None:
                lista = [vc, vf]
                perc_c = _percentil(vc, lista, menor)
                perc_f = _percentil(vf, lista, menor)
                det_casa.append((ind, vc, perc_c))
                det_fora.append((ind, vf, perc_f))
        if det_casa:
            notas_casa[nome] = sum(x[2] for x in det_casa) / len(det_casa)
            notas_fora[nome] = sum(x[2] for x in det_fora) / len(det_fora)
            detalhes_ovr[nome] = {'casa': det_casa, 'fora': det_fora}

    # IC
    ic_val_casa = calcular_ic(dados['ic_casa'])
    ic_val_fora = calcular_ic(dados['ic_fora'])

    # MPV
    mpv_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
    mpv_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

    # Mercados (versão enriquecida com IMA e IC)
    from core.market_engine import (
        prob_1x2_v2, prob_over25, prob_btts, prob_gol_ht_v2, prob_over_escanteios_v2
    )

    bonus_casa = calcular_bonus_casa(dados['ovrall_casa'].get('diff_aprov_casa_fora') or 0)
    p1, pX, p2 = prob_1x2_v2(mpv_casa, mpv_fora, bonus_casa)

    over25 = prob_over25(
        dados['ovrall_casa'], dados['ovrall_fora'],
        ima_casa, ima_fora, ic_val_casa, ic_val_fora,
        media_casa=dados.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA),
        media_fora=dados.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)
    )
    btts = prob_btts(
        dados['ovrall_casa'], dados['ovrall_fora'],
        ima_casa, ima_fora, ic_val_casa, ic_val_fora,
        media_casa=dados.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA),
        media_fora=dados.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)
    )
    gol_ht = prob_gol_ht_v2(
        dados['ovrall_casa'], dados['ovrall_fora'],
        ima_casa, ima_fora, ic_val_casa, ic_val_fora,
        media_ht_casa=dados.get('media_ht_casa', 0.75),
        media_ht_fora=dados.get('media_ht_fora', 0.65)
    )
    esc = prob_over_escanteios_v2(
        dados['ovrall_casa'], dados['ovrall_fora'],
        ima_casa, ima_fora, ic_val_casa, ic_val_fora,
        media_casa=dados.get('media_esc_casa', 5.0),
        media_fora=dados.get('media_esc_fora', 4.5)
    )

    return {
        'time_casa': dados['time_casa'], 'time_fora': dados['time_fora'],
        'p1': p1, 'pX': pX, 'p2': p2,
        'over25': over25, 'btts': btts, 'gol_ht': gol_ht, 'esc': esc,
        'ima_casa': ima_casa, 'ima_fora': ima_fora,
        'mpv_casa': mpv_casa, 'mpv_fora': mpv_fora,
        'ovrall_casa': ovrall_val_casa, 'ovrall_fora': ovrall_val_fora,
        'ic_casa': ic_val_casa, 'ic_fora': ic_val_fora,
        'notas_casa': notas_casa, 'notas_fora': notas_fora,
        'detalhes_ima': {'casa': ima_det_casa, 'fora': ima_det_fora},
        'detalhes_ovr': detalhes_ovr,
        'prateleiras': prateleiras,
    }, None
