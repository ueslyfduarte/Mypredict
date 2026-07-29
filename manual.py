# manual.py — MyPredict 2.0 (completo, com detalhamento)
import re
from ratings import (
    calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv,
    obter_prateleira, _percentil, calcular_pontuacao_jogo
)
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from utils import extrair_jogos, para_float

def processar_texto_ia(texto):
    """Parser antigo (mantido para compatibilidade)."""
    # Código do teu parser original, não vou repetir para não alongar.
    # Mantém o que já tinhas.
    pass

def processar_lista_simples(texto):
    """Nova entrada: apenas valores separados por vírgula."""
    texto = texto.replace('\n', ',').replace(';', ',')
    partes = [p.strip() for p in texto.split(',') if p.strip()]

    dados = {
        'time_casa': "", 'time_fora': "",
        'pos_casa': 1, 'pos_fora': 2,
        'jogos_casa': [], 'jogos_fora': [],
        'ovrall_casa': {}, 'ovrall_fora': {},
        'ic_casa': {}, 'ic_fora': {},
        'media_gols_casa': MEDIA_GOLS_CASA_LIGA, 'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
        'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
        'media_esc_casa': 5.0, 'media_esc_fora': 4.5,
        'prateleiras_extra': {}
    }

    idx = 0
    try:
        # 1. Times e posições (4 primeiros valores)
        dados['time_casa'] = partes[idx]; idx += 1
        dados['time_fora'] = partes[idx]; idx += 1
        dados['pos_casa'] = int(partes[idx]); idx += 1
        dados['pos_fora'] = int(partes[idx]); idx += 1

        # 2. Jogos casa (10 jogos * 3 = 30 valores)
        for _ in range(10):
            res = partes[idx]; adv = partes[idx+1]; mand = partes[idx+2].upper() == 'S'
            dados['jogos_casa'].append({"resultado": res, "adversario": adv, "mandante": mand})
            idx += 3

        # 3. Jogos fora (30 valores)
        for _ in range(10):
            res = partes[idx]; adv = partes[idx+1]; mand = partes[idx+2].upper() == 'S'
            dados['jogos_fora'].append({"resultado": res, "adversario": adv, "mandante": mand})
            idx += 3

        # 4. OVRall casa (23 valores)
        chaves_ovr = ["gols_media","gols_sofridos_media","xg_media","xga_media","finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media","chutes_media","desarmes_intercep_media","posse_media","passes_certos_pct","passes_chave_media","assistencias_media","conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro","desvio_gols_sofridos","pontos_pos_desvantagem_media","gols_ultimos_15min_media","pontos_apos_derrota_media","diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
        for k in chaves_ovr:
            dados['ovrall_casa'][k] = para_float(partes[idx]); idx += 1

        # 5. OVRall fora (23 valores)
        for k in chaves_ovr:
            dados['ovrall_fora'][k] = para_float(partes[idx]); idx += 1

        # 6. IC casa (5 valores)
        chaves_ic = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
        for k in chaves_ic:
            dados['ic_casa'][k] = para_float(partes[idx]); idx += 1

        # 7. IC fora (5 valores)
        for k in chaves_ic:
            dados['ic_fora'][k] = para_float(partes[idx]); idx += 1

        # 8. Médias da liga (6 valores)
        dados['media_gols_casa'] = para_float(partes[idx]); idx += 1
        dados['media_gols_fora'] = para_float(partes[idx]); idx += 1
        dados['media_ht_casa'] = para_float(partes[idx]); idx += 1
        dados['media_ht_fora'] = para_float(partes[idx]); idx += 1
        dados['media_esc_casa'] = para_float(partes[idx]); idx += 1
        dados['media_esc_fora'] = para_float(partes[idx]); idx += 1

        # 9. Prateleiras (restante)
        while idx < len(partes):
            if ':' in partes[idx]:
                adv, prat = partes[idx].split(':', 1)
                dados['prateleiras_extra'][adv.strip()] = prat.strip()
            idx += 1
    except IndexError:
        pass

    return dados

def executar_manual(dados):
    """Executa o cálculo e retorna (resultados, erro), incluindo detalhamento."""
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
        '5CF': [j for j in dados['jogos_fora'] if j['mandante']][:5],
        '3CF': [j for j in dados['jogos_fora'] if j['mandante']][:3],
    }

    # IMA – cálculo principal
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
    dados_liga = {k: [dados['ovrall_casa'].get(k, 0) or 0, dados['ovrall_fora'].get(k, 0) or 0] for k in set(dados['ovrall_casa']) | set(dados['ovrall_fora'])}
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

    # Mercados
    bonus_casa = calcular_bonus_casa(dados['ovrall_casa'].get('diff_aprov_casa_fora') or 0)
    p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

    over25 = prob_over_2_5(
        dados['ovrall_casa'].get('gols_media'), dados['ovrall_fora'].get('gols_media'),
        dados['ovrall_casa'].get('gols_sofridos_media'), dados['ovrall_fora'].get('gols_sofridos_media'),
        media_casa=dados.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA), media_fora=dados.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)
    )
    gols_esp_casa = _gols_esperados(dados['ovrall_casa'].get('gols_media'), dados['ovrall_fora'].get('gols_sofridos_media'), dados.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA))
    gols_esp_fora = _gols_esperados(dados['ovrall_fora'].get('gols_media'), dados['ovrall_casa'].get('gols_sofridos_media'), dados.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA))
    btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)
    gol_ht = prob_gol_ht(
        dados['ovrall_casa'].get('gols_ht_media', 0.5) or 0.5,
        dados['ovrall_fora'].get('gols_ht_media', 0.5) or 0.5,
        dados['ovrall_casa'].get('gols_ht_sofridos_media', 0.5) or 0.5,
        dados['ovrall_fora'].get('gols_ht_sofridos_media', 0.5) or 0.5,
        media_ht_casa=dados.get('media_ht_casa', 0.75), media_ht_fora=dados.get('media_ht_fora', 0.65)
    )
    esc = prob_over_escanteios(
        dados['ovrall_casa'].get('escanteios_media', 5.0) or 5.0,
        dados['ovrall_fora'].get('escanteios_media', 5.0) or 5.0,
        dados['ovrall_casa'].get('escanteios_sofridos_media', 5.0) or 5.0,
        dados['ovrall_fora'].get('escanteios_sofridos_media', 5.0) or 5.0,
        media_casa=dados.get('media_esc_casa', 5.0), media_fora=dados.get('media_esc_fora', 4.5)
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
