# manual.py — MyPredict 2.0 (lógica do modo manual)
import streamlit as st
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from utils import extrair_jogos, para_float

def processar_texto_ia(texto):
    dados = {
        'time_casa': "Flamengo", 'time_fora': "Palmeiras",
        'pos_casa': 1, 'pos_fora': 2,
        'jogos_casa': [], 'jogos_fora': [],
        'ovrall_casa': {}, 'ovrall_fora': {},
        'ic_casa': {}, 'ic_fora': {},
        'media_gols_casa': MEDIA_GOLS_CASA_LIGA, 'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
        'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
        'media_esc_casa': 5.0, 'media_esc_fora': 4.5,
        'prateleiras_extra': {}
    }

    blocos = texto.strip().split('\n\n')
    for bloco in blocos:
        linhas = bloco.strip().split('\n')
        if not linhas: continue
        primeira = linhas[0].strip()
        if primeira.startswith('Time da casa:'): dados['time_casa'] = primeira.split(':',1)[1].strip()
        elif primeira.startswith('Time da fora:'): dados['time_fora'] = primeira.split(':',1)[1].strip()
        elif 'Posições:' in primeira:
            for l in linhas[1:]:
                if l.startswith('Casa:'):
                    try: dados['pos_casa'] = int(l.split(':')[1].strip())
                    except: pass
                elif l.startswith('Fora:'):
                    try: dados['pos_fora'] = int(l.split(':')[1].strip())
                    except: pass
        elif 'Últimos 10 jogos do time da casa' in primeira:
            dados['jogos_casa'] = extrair_jogos('\n'.join(linhas[1:]))
        elif 'Últimos 10 jogos do time da fora' in primeira:
            dados['jogos_fora'] = extrair_jogos('\n'.join(linhas[1:]))
        elif 'Métricas OVRall do time da casa' in primeira:
            chaves = ["gols_media","gols_sofridos_media","xg_media","xga_media","finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media","chutes_media","desarmes_intercep_media","posse_media","passes_certos_pct","passes_chave_media","assistencias_media","conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro","desvio_gols_sofridos","pontos_pos_desvantagem_media","gols_ultimos_15min_media","pontos_apos_derrota_media","diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
            vals = [para_float(x) for x in linhas[-1].split(',')]
            if len(vals) == 23: dados['ovrall_casa'] = {chaves[i]: vals[i] for i in range(23)}
        elif 'Métricas OVRall do time da fora' in primeira:
            chaves = ["gols_media","gols_sofridos_media","xg_media","xga_media","finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media","chutes_media","desarmes_intercep_media","posse_media","passes_certos_pct","passes_chave_media","assistencias_media","conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro","desvio_gols_sofridos","pontos_pos_desvantagem_media","gols_ultimos_15min_media","pontos_apos_derrota_media","diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
            vals = [para_float(x) for x in linhas[-1].split(',')]
            if len(vals) == 23: dados['ovrall_fora'] = {chaves[i]: vals[i] for i in range(23)}
        elif 'Métricas IC do time da casa' in primeira:
            chaves = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
            vals = [para_float(x) for x in linhas[-1].split(',')]
            if len(vals) == 5: dados['ic_casa'] = {chaves[i]: vals[i] for i in range(5)}
        elif 'Métricas IC do time da fora' in primeira:
            chaves = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
            vals = [para_float(x) for x in linhas[-1].split(',')]
            if len(vals) == 5: dados['ic_fora'] = {chaves[i]: vals[i] for i in range(5)}
        elif 'Médias da Liga' in primeira:
            for l in linhas[1:]:
                if 'casa:' in l: dados['media_gols_casa'] = para_float(l.split(':')[1])
                elif 'fora:' in l: dados['media_gols_fora'] = para_float(l.split(':')[1])
                elif '1º tempo casa:' in l: dados['media_ht_casa'] = para_float(l.split(':')[1])
                elif '1º tempo fora:' in l: dados['media_ht_fora'] = para_float(l.split(':')[1])
                elif 'escanteios casa:' in l: dados['media_esc_casa'] = para_float(l.split(':')[1])
                elif 'escanteios fora:' in l: dados['media_esc_fora'] = para_float(l.split(':')[1])
        elif 'Prateleiras' in primeira:
            for l in linhas[1:]:
                if ':' in l:
                    adv, prat = l.split(':',1)
                    dados['prateleiras_extra'][adv.strip()] = prat.strip()

    if len(dados['jogos_casa']) < 10 or len(dados['jogos_fora']) < 10:
        todos_jogos = extrair_jogos(texto)
        if len(todos_jogos) >= 20:
            dados['jogos_casa'] = todos_jogos[:10]
            dados['jogos_fora'] = todos_jogos[10:20]

    return dados

def executar_manual(dados):
    if len(dados['jogos_casa']) < 10 or len(dados['jogos_fora']) < 10:
        return None, "São necessários 10 jogos para cada time."
    if not dados['ovrall_casa'] or not dados['ovrall_fora']:
        return None, "Métricas OVRall não encontradas."

    prat_casa = obter_prateleira(dados['pos_casa'])
    prat_fora = obter_prateleira(dados['pos_fora'])
    prateleiras = {dados['time_casa']: prat_casa, dados['time_fora']: prat_fora}
    for j in dados['jogos_casa'] + dados['jogos_fora']:
        if j['adversario'] not in prateleiras:
            prateleiras[j['adversario']] = "Media"
    for adv, prat in dados.get('prateleiras_extra', {}).items():
        if adv in prateleiras:
            prateleiras[adv] = prat

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

    ima_casa = calcular_ima(dados['time_casa'], rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                            rec_casa['5CF'], rec_casa['3CF'], prateleiras)
    ima_fora = calcular_ima(dados['time_fora'], rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                            rec_fora['5CF'], rec_fora['3CF'], prateleiras)

    dados_liga = {k: [dados['ovrall_casa'].get(k, 0) or 0, dados['ovrall_fora'].get(k, 0) or 0] for k in set(dados['ovrall_casa']) | set(dados['ovrall_fora'])}
    ovrall_val_casa = calcular_ovrall(dados['ovrall_casa'], dados_liga)
    ovrall_val_fora = calcular_ovrall(dados['ovrall_fora'], dados_liga)

    ic_val_casa = calcular_ic(dados['ic_casa'])
    ic_val_fora = calcular_ic(dados['ic_fora'])

    mpv_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
    mpv_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

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
    }, None
