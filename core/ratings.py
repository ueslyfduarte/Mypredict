# core/ratings.py — Cálculos de IMA, OVRall, IC e MPV
import numpy as np
from config import PESOS_MPV, PESOS_IC

def _percentil(valor, lista, menor_melhor=False):
    # (mantida para uso em outros módulos, se necessário)
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
    inv_time = 1.0 / odd_time
    inv_emp = 1.0 / odd_empate
    inv_adv = 1.0 / odd_adv
    soma = inv_time + inv_emp + inv_adv
    E_atual = inv_time / soma

    if not jogos_recentes:
        return max(0.0, min(100.0, E_atual * 100.0))

    pontos = sum(3 if j['resultado'] == 'V' else 1 if j['resultado'] == 'E' else 0 for j in jogos_recentes)
    max_pontos = len(jogos_recentes) * 3
    A_real = pontos / max_pontos if max_pontos > 0 else 0.0
    delta = A_real - E_atual
    ima = (E_atual * 100.0) + (delta * 100.0)
    return max(0.0, min(100.0, ima))

def calcular_ovrall(dados_time, benchmarks_liga, fator_liga=1.0):
    """
    Calcula o OVRall absoluto de um time em relação aos benchmarks da liga.

    Três dimensões principais (Ataque, Defesa, Meio‑Campo) com 3 indicadores cada,
    mais duas acessórias (Consistência, Resiliência) que só contribuem se houver dados.
    """
    dimensoes = {
        'Ataque': {
            'peso': 0.35,
            'indicadores': [
                ('gols_media', False),
                ('xg_media', False),
                ('finalizacoes_alvo_media', False),
            ]
        },
        'Defesa': {
            'peso': 0.35,
            'indicadores': [
                ('gols_sofridos_media', True),
                ('xga_media', True),
                ('desarmes_intercep_media', False),
            ]
        },
        'MeioCampo': {
            'peso': 0.20,
            'indicadores': [
                ('posse_media', False),
                ('passes_certos_pct', False),
                ('passes_chave_media', False),
            ]
        },
        'Consistencia': {
            'peso': 0.05,
            'indicadores': [
                ('desvio_pontos', True),
                ('clean_sheets_pct', False),
            ]
        },
        'Resiliencia': {
            'peso': 0.05,
            'indicadores': [
                ('pontos_pos_desvantagem_media', False),
                ('gols_ultimos_15min_media', False),
            ]
        }
    }

    notas_dimensoes = {}
    soma_pesos = 0.0

    for dim_nome, dim_data in dimensoes.items():
        notas = []
        for indicador, menor_melhor in dim_data['indicadores']:
            if indicador in dados_time and indicador in benchmarks_liga:
                val = dados_time[indicador]
                b = benchmarks_liga[indicador]
                if b['std'] > 0:
                    z = (val - b['mean']) / b['std']
                else:
                    z = 0.0
                if menor_melhor:
                    z = -z
                nota = 100.0 / (1.0 + np.exp(-1.5 * z))
                notas.append(nota)

        if notas:
            notas_dimensoes[dim_nome] = sum(notas) / len(notas)
            soma_pesos += dim_data['peso']

    if soma_pesos == 0:
        ovrall_bruto = 50.0
    else:
        ovrall_bruto = 0.0
        for dim_nome in notas_dimensoes:
            ovrall_bruto += notas_dimensoes[dim_nome] * dimensoes[dim_nome]['peso']
        ovrall_bruto /= soma_pesos

    ovrall = (45.0 + (ovrall_bruto * 0.55)) * fator_liga
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
