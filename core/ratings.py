# core/ratings.py — Cálculos de IMA, OVRall, IC e MPV
from config import (
    PESOS_OVRALL, PESOS_MPV, PESOS_IC
)

def _percentil(valor, lista, menor_melhor=False):
    if not lista:
        return 50.0
    if len(set(lista)) == 1:
        return 50.0
    ordenado = sorted(lista)
    n = len(ordenado)
    pos = sum(1 for x in ordenado if x < valor)
    percentil = (pos / n) * 100
    return 100.0 - percentil if menor_melhor else percentil

def calcular_ima(odd_time, odd_empate, odd_adv, jogos_recentes):
    """
    Calcula o IMA baseado na odd atual + resultados recentes (com mando de campo).

    Parâmetros:
    - odd_time: odd para vitória do time analisado no próximo jogo
    - odd_empate, odd_adv: odds 1X2 do próximo jogo
    - jogos_recentes: lista de dicionários com 'resultado' (V/E/D);
                      se a lista estiver vazia, o IMA será apenas a expectativa.

    Retorna: IMA (0-100)
    """
    # 1. Probabilidade implícita atual (sem margem)
    inv_time = 1.0 / odd_time
    inv_emp = 1.0 / odd_empate
    inv_adv = 1.0 / odd_adv
    soma = inv_time + inv_emp + inv_adv
    E_atual = inv_time / soma   # escala 0-1

    # 2. Aproveitamento real recente (se houver jogos)
    if not jogos_recentes:
        return max(0.0, min(100.0, E_atual * 100.0))

    pontos = sum(3 if j['resultado'] == 'V' else 1 if j['resultado'] == 'E' else 0 for j in jogos_recentes)
    max_pontos = len(jogos_recentes) * 3
    A_real = pontos / max_pontos if max_pontos > 0 else 0.0

    # 3. Delta e IMA
    delta = A_real - E_atual
    ima = (E_atual * 100.0) + (delta * 100.0)
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
