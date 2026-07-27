# ratings.py — MyPredict 2.0
# Cálculo do IMA, OVRall, IC e MPV.

from config import (
    PRATELEIRAS, PONTOS_BASE,
    BONUS_SIMETRICOS, BONUS_VITORIA_ASSIM, BONUS_DERROTA_ASSIM, BONUS_EMPATE,
    PESOS_RECORTES, PISO_IMA, TETO_IMA,
    PESOS_OVRALL, PESOS_MPV, PESOS_IC, JOGOS_CONFRONTO_DIRETO
)


# ------------------------------------------------------------
# FUNÇÕES AUXILIARES GERAIS
# ------------------------------------------------------------

def obter_prateleira(posicao: int) -> str:
    """Retorna o nome da prateleira de acordo com a posição na tabela projetada."""
    for nome, (inf, sup) in PRATELEIRAS.items():
        if inf <= posicao <= sup:
            return nome
    return 'Critica'


def _percentil(valor: float, lista: list, menor_melhor: bool = False) -> float:
    """Nota 0-100 baseada no percentil do valor em relação à lista."""
    if not lista:
        return 50.0
    ordenado = sorted(lista)
    n = len(ordenado)
    pos = sum(1 for x in ordenado if x < valor)
    percentil = (pos / n) * 100
    return 100.0 - percentil if menor_melhor else percentil


# ------------------------------------------------------------
# 1. IMA
# ------------------------------------------------------------

def calcular_pontuacao_jogo(resultado: str, prateleira_time: str, prateleira_adv: str) -> float:
    """Pontuação ajustada de um jogo conforme as prateleiras."""
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


def calcular_ima(
    time: str,
    jogos_10G: list,
    jogos_5G: list,
    jogos_3G: list,
    jogos_5CF: list,
    jogos_3CF: list,
    prateleiras: dict
) -> float:
    """
    Calcula o Índice de Momento Atual (IMA) de um time (0–100).
    prateleiras: dict {time: prateleira}
    """
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


# ------------------------------------------------------------
# 2. OVRall
# ------------------------------------------------------------

def calcular_ovrall(dados_time: dict, dados_liga: dict) -> float:
    """
    Calcula a nota OVRall (45 a 100) baseada em indicadores reais.
    dados_time: dict com médias/desvios do time (chaves como 'gols_media', etc.)
    dados_liga: dict com listas de valores de todos os times para cada indicador.
    """
    dims = {
        'Ataque': [
            ('gols_media', False),
            ('xg_media', False),
            ('finalizacoes_alvo_media', False),
            ('conversao', False),
        ],
        'Defesa': [
            ('gols_sofridos_media', True),
            ('xga_media', True),
            ('finalizacoes_alvo_sofridas_media', True),
            ('desarmes_intercep_media', False),
        ],
        'MeioCampo': [
            ('posse_media', False),
            ('passes_certos_pct', False),
            ('passes_chave_media', False),
            ('assistencias_media', False),
            ('chutes_media', False),                     # NOVO
        ],
        'Consistencia': [
            ('desvio_pontos', True),
            ('desvio_gols_pro', True),
            ('desvio_gols_sofridos', True),
            ('clean_sheets_pct', False),
        ],
        'Resiliencia': [
            ('pontos_pos_desvantagem_media', False),
            ('gols_ultimos_15min_media', False),
            ('pontos_apos_derrota_media', False),
            ('diff_aprov_casa_fora', True),
            ('aprov_viradas_favor', False),              # NOVO
            ('aprov_viradas_contra', True),              # NOVO
        ],
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
        else:
            notas_dimensoes[dimensao] = None

    disponiveis = {d: v for d, v in notas_dimensoes.items() if v is not None}
    if not disponiveis:
        return 45.0

    peso_total_disp = sum(PESOS_OVRALL[d] for d in disponiveis)
    ovrall_bruto = 0.0
    for d, nota in disponiveis.items():
        peso_ajustado = PESOS_OVRALL[d] / peso_total_disp
        ovrall_bruto += peso_ajustado * nota

    ovrall = 45.0 + (ovrall_bruto * 0.55)
    return max(45.0, min(100.0, ovrall))


# ------------------------------------------------------------
# 3. IC (Índice de Contexto)
# ------------------------------------------------------------

def calcular_confronto_direto(time: str, adversario: str, jogos_historicos: list) -> float:
    """Aproveitamento nos últimos JOGOS_CONFRONTO_DIRETO confrontos."""
    if not jogos_historicos:
        return 50.0
    jogos = jogos_historicos[-JOGOS_CONFRONTO_DIRETO:]
    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos)
    max_possivel = len(jogos) * 3
    return (pontos / max_possivel) * 100 if max_possivel else 50.0


def calcular_desempenho_contra_escalao(
    time: str, escalao_alvo: str, prateleiras: dict, jogos_temporada: list
) -> float:
    """Aproveitamento contra times de um determinado escalão."""
    jogos_filtrados = [j for j in jogos_temporada
                       if prateleiras.get(j['adversario']) == escalao_alvo]
    if not jogos_filtrados:
        return 50.0
    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos_filtrados)
    max_possivel = len(jogos_filtrados) * 3
    return (pontos / max_possivel) * 100


def calcular_fator_casa(time: str, mandante: bool, jogos_temporada: list) -> float:
    """Aproveitamento como mandante (se mandante=True) ou visitante."""
    if mandante:
        jogos_filtrados = [j for j in jogos_temporada if j['mandante']]
    else:
        jogos_filtrados = [j for j in jogos_temporada if not j['mandante']]
    if not jogos_filtrados:
        return 50.0
    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos_filtrados)
    max_possivel = len(jogos_filtrados) * 3
    return (pontos / max_possivel) * 100


def calcular_odds(odds_casa: float, odds_empate: float, odds_fora: float, mandante: bool) -> float:
    """Probabilidade implícita da odd (0-100) ou None."""
    if None in (odds_casa, odds_empate, odds_fora):
        return None
    prob_casa = 1 / odds_casa
    prob_empate = 1 / odds_empate
    prob_fora = 1 / odds_fora
    total = prob_casa + prob_empate + prob_fora
    prob_casa /= total
    prob_empate /= total
    prob_fora /= total
    return (prob_casa * 100) if mandante else (prob_fora * 100)


def calcular_ic(fatores: dict, pesos: dict = None) -> float:
    """Consolida os fatores contextuais em 0-100."""
    if pesos is None:
        pesos = PESOS_IC
    disponiveis = {k: v for k, v in fatores.items() if v is not None}
    if not disponiveis:
        return 50.0
    peso_total = sum(pesos.get(k, 0) for k in disponiveis)
    if peso_total == 0:
        return 50.0
    ic = sum((pesos.get(k, 0) / peso_total) * disponiveis[k] for k in disponiveis)
    return max(0.0, min(100.0, ic))


# ------------------------------------------------------------
# 4. MPV
# ------------------------------------------------------------

def calcular_mpv(ima: float, ovrall: float, ic: float, pesos: dict = None) -> float:
    """Combina IMA, OVRall e IC no rating MPV (0-100)."""
    if pesos is None:
        pesos = PESOS_MPV
    return pesos['IMA'] * ima + pesos['OVRall'] * ovrall + pesos['IC'] * ic
