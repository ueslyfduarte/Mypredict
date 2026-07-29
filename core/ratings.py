# core/ratings.py — Cálculos de IMA, OVRall, IC e MPV
from config import (
    PRATELEIRAS, PONTOS_BASE,
    BONUS_SIMETRICOS, BONUS_VITORIA_ASSIM, BONUS_DERROTA_ASSIM, BONUS_EMPATE,
    PESOS_RECORTES, PISO_IMA, TETO_IMA,
    PESOS_OVRALL, PESOS_MPV, PESOS_IC, JOGOS_CONFRONTO_DIRETO
)

def obter_prateleira(posicao):
    for nome, (inf, sup) in PRATELEIRAS.items():
        if inf <= posicao <= sup:
            return nome
    return 'Critica'

def _percentil(valor, lista, menor_melhor=False):
    if not lista:
        return 50.0
    ordenado = sorted(lista)
    n = len(ordenado)
    pos = sum(1 for x in ordenado if x < valor)
    percentil = (pos / n) * 100
    return 100.0 - percentil if menor_melhor else percentil

def calcular_pontuacao_jogo(resultado, prateleira_time, prateleira_adv):
    pontos = PONTOS_BASE[resultado]
    if resultado == 'V':
        if (prateleira_time, prateleira_adv) in BONUS_VITORIA_ASSIM:
            pontos += BONUS_VITORIA_ASSIM[(prateleira_time, prateleira_adv)]
        elif (prateleira_time, prateleira_adv) in BONUS_SIMETRICOS:
            pontos += BONUS_SIMETRICOS[(prateleira_time, prateleira_adv)][0]
    elif resultado == 'D':
        if (prateleira_time, prateleira_adv) in BONUS_DERROTA_ASSIM:
            pontos += BONUS_DERROTA_ASSIM[(prateleira_time, prateleira_adv)]
        elif (prateleira_time, prateleira_adv) in BONUS_SIMETRICOS:
            pontos += BONUS_SIMETRICOS[(prateleira_time, prateleira_adv)][1]
    elif resultado == 'E':
        if (prateleira_time, prateleira_adv) in BONUS_EMPATE:
            pontos += BONUS_EMPATE[(prateleira_time, prateleira_adv)]
    return pontos

def calcular_ima(time, jogos_10G, jogos_5G, jogos_3G, jogos_5CF, jogos_3CF, prateleiras):
    def media_recorte(jogos):
        if not jogos:
            return 0.0
        pts = []
        for j in jogos:
            prat_time = prateleiras[time]
            prat_adv = prateleiras[j['adversario']]
            pts.append(calcular_pontuacao_jogo(j['resultado'], prat_time, prat_adv))
        return sum(pts) / len(pts)
    medias = {
        '10G': media_recorte(jogos_10G),
        '5G':  media_recorte(jogos_5G),
        '3G':  media_recorte(jogos_3G),
        '5CF': media_recorte(jogos_5CF),
        '3CF': media_recorte(jogos_3CF),
    }
    ima_bruto = sum(medias[k] * PESOS_RECORTES[k] for k in PESOS_RECORTES)
    ima = (ima_bruto - PISO_IMA) / (TETO_IMA - PISO_IMA) * 100
    return max(0.0, min(100.0, ima))

def calcular_ovrall(dados_time, dados_liga):
    dims = {
        'Ataque': [('gols_media', False), ('xg_media', False), ('finalizacoes_alvo_media', False), ('conversao', False)],
        'Defesa': [('gols_sofridos_media', True), ('xga_media', True), ('finalizacoes_alvo_sofridas_media', True), ('desarmes_intercep_media', False)],
        'MeioCampo': [('posse_media', False), ('passes_certos_pct', False), ('passes_chave_media', False), ('assistencias_media', False), ('chutes_media', False)],
        'Consistencia': [('desvio_pontos', True), ('desvio_gols_pro', True), ('desvio_gols_sofridos', True), ('clean_sheets_pct', False)],
        'Resiliencia': [('pontos_pos_desvantagem_media', False), ('gols_ultimos_15min_media', False), ('pontos_apos_derrota_media', False), ('diff_aprov_casa_fora', True), ('aprov_viradas_favor', False), ('aprov_viradas_contra', True)],
    }
    notas_dimensoes = {}
    for dimensao, indicadores in dims.items():
        notas = []
        for indicador, menor_melhor in indicadores:
            val_time = dados_time.get(indicador)
            val_liga = dados_liga.get(indicador)
            if val_time is not None and val_liga:
                notas.append(_percentil(val_time, val_liga, menor_melhor))
        if notas:
            notas_dimensoes[dimensao] = sum(notas) / len(notas)
    disponiveis = {d: v for d, v in notas_dimensoes.items()}
    if not disponiveis:
        return 45.0
    peso_total_disp = sum(PESOS_OVRALL[d] for d in disponiveis)
    ovrall_bruto = 0.0
    for d, nota in disponiveis.items():
        peso_ajustado = PESOS_OVRALL[d] / peso_total_disp
        ovrall_bruto += peso_ajustado * nota
    ovrall = 45.0 + (ovrall_bruto * 0.55)
    return max(45.0, min(100.0, ovrall))

def calcular_confronto_direto(time, adversario, jogos_historicos):
    if not jogos_historicos:
        return 50.0
    jogos = jogos_historicos[-JOGOS_CONFRONTO_DIRETO:]
    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos)
    max_possivel = len(jogos) * 3
    return (pontos / max_possivel) * 100 if max_possivel else 50.0

def calcular_desempenho_contra_escalao(time, escalao_alvo, prateleiras, jogos_temporada):
    jogos_filtrados = [j for j in jogos_temporada if prateleiras.get(j['adversario']) == escalao_alvo]
    if not jogos_filtrados:
        return 50.0
    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos_filtrados)
    return (pontos / (len(jogos_filtrados) * 3)) * 100

def calcular_fator_casa(time, mandante, jogos_temporada):
    jogos_filtrados = [j for j in jogos_temporada if j['mandante'] == mandante]
    if not jogos_filtrados:
        return 50.0
    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos_filtrados)
    return (pontos / (len(jogos_filtrados) * 3)) * 100

def calcular_odds(odds_casa, odds_empate, odds_fora, mandante):
    if None in (odds_casa, odds_empate, odds_fora):
        return None
    prob_casa = 1/odds_casa
    prob_empate = 1/odds_empate
    prob_fora = 1/odds_fora
    total = prob_casa + prob_empate + prob_fora
    prob_casa /= total
    prob_empate /= total
    prob_fora /= total
    return (prob_casa * 100) if mandante else (prob_fora * 100)

def calcular_ic(fatores, pesos=None):
    if pesos is None:
        pesos = PESOS_IC
    disponiveis = {k: v for k, v in fatores.items() if v is not None}
    if not disponiveis:
        return 50.0
    peso_total = sum(pesos.get(k, 0) for k in disponiveis)
    if peso_total == 0:
        return 50.0
    ic = sum((pesos.get(k, 0)/peso_total) * disponiveis[k] for k in disponiveis)
    return max(0.0, min(100.0, ic))

def calcular_mpv(ima, ovrall, ic, pesos=None):
    if pesos is None:
        pesos = PESOS_MPV
    return pesos['IMA'] * ima + pesos['OVRall'] * ovrall + pesos['IC'] * ic
def calcular_consistencia(desvio_pontos, volatilidade_ima=None):
    """
    Retorna um fator de consistência (0 a 1) baseado no desvio padrão de pontos.
    Quanto menor o desvio, mais consistente.
    volatilidade_ima: opcional, desvio padrão dos últimos IMA (não implementado ainda).
    """
    if desvio_pontos is None:
        return 0.5
    # Desvio máximo esperado ~1.5 (3 pontos de amplitude)
    return max(0.0, min(1.0, 1.0 - (desvio_pontos / 1.5)))
