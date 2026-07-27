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


def percentil_para_nota(valor: float, referencia: list) -> float:
    """
    Converte um valor bruto em nota 0–100 baseada no percentil em relação a uma lista de referência.
    Exemplo: referência são os valores de todos os times da liga.
    """
    if not referencia:
        return 50.0
    referencia_ordenada = sorted(referencia)
    n = len(referencia_ordenada)
    pos = sum(1 for x in referencia_ordenada if x < valor)
    percentil = (pos / n) * 100
    return max(0.0, min(100.0, percentil))


# ------------------------------------------------------------
# 1. IMA
# ------------------------------------------------------------

def calcular_pontuacao_jogo(resultado: str, prateleira_time: str, prateleira_adv: str) -> float:
    """
    Calcula a pontuação ajustada de um jogo para o time analisado,
    aplicando bônus e penalidades conforme as prateleiras.
    """
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
    projecao_classificacao: dict
) -> float:
    """
    Calcula o Índice de Momento Atual (IMA) de um time (0–100).
    """
    def media_recorte(jogos):
        if not jogos:
            return 0.0
        pts = []
        for j in jogos:
            pos_time = projecao_classificacao[time]
            pos_adv = projecao_classificacao[j['adversario']]
            prat_time = obter_prateleira(pos_time)
            prat_adv = obter_prateleira(pos_adv)
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
# 2. OVRall (placeholder com interface definida)
# ------------------------------------------------------------

def calcular_ovrall(estatisticas: dict) -> float:
    """
    Calcula a nota OVRall (45 a 100) baseada em cinco dimensões.
    estatisticas: dict com chaves Ataque, Defesa, MeioCampo, Consistencia, Resiliencia (0–100).
    """
    disponiveis = {dim: valor for dim, valor in estatisticas.items()
                   if valor is not None and dim in PESOS_OVRALL}
    if not disponiveis:
        return 45.0

    pesos_originais = PESOS_OVRALL.copy()
    peso_total_disp = sum(pesos_originais[dim] for dim in disponiveis)
    if peso_total_disp == 0:
        return 45.0

    ovrall_bruto = 0.0
    for dim, valor in disponiveis.items():
        peso_ajustado = pesos_originais[dim] / peso_total_disp
        ovrall_bruto += peso_ajustado * valor

    ovrall = 45.0 + (ovrall_bruto * 0.55)
    return max(45.0, min(100.0, ovrall))


# ------------------------------------------------------------
# 3. IC (Índice de Contexto)
# ------------------------------------------------------------

def calcular_confronto_direto(
    time: str,
    adversario: str,
    jogos_historicos: list
) -> float:
    """
    Retorna nota 0–100 baseada no aproveitamento do time contra o adversário específico
    nos últimos JOGOS_CONFRONTO_DIRETO embates.
    jogos_historicos: lista de jogos entre os dois, com 'resultado' para o time.
    """
    if not jogos_historicos:
        return 50.0  # neutro

    jogos = jogos_historicos[-JOGOS_CONFRONTO_DIRETO:]  # pega os mais recentes
    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos)
    max_possivel = len(jogos) * 3
    if max_possivel == 0:
        return 50.0
    aproveitamento = (pontos / max_possivel) * 100
    return aproveitamento


def calcular_desempenho_contra_escalao(
    time: str,
    escalao_alvo: str,
    projecao_classificacao: dict,
    jogos_temporada: list
) -> float:
    """
    Retorna nota 0–100 baseada no aproveitamento do time contra adversários
    de um determinado escalão, na temporada atual.
    """
    jogos_filtrados = [
        j for j in jogos_temporada
        if obter_prateleira(projecao_classificacao.get(j['adversario'], 99)) == escalao_alvo
    ]
    if not jogos_filtrados:
        return 50.0

    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos_filtrados)
    max_possivel = len(jogos_filtrados) * 3
    aproveitamento = (pontos / max_possivel) * 100
    return aproveitamento


def calcular_fator_casa(
    time: str,
    mandante: bool,
    jogos_temporada: list
) -> float:
    """
    Retorna nota 0–100 do fator casa/fora.
    Se mandante=True, calcula aproveitamento como mandante na temporada;
    caso contrário, aproveitamento como visitante.
    """
    if mandante:
        jogos_filtrados = [j for j in jogos_temporada if j['mandante']]
    else:
        jogos_filtrados = [j for j in jogos_temporada if not j['mandante']]

    if not jogos_filtrados:
        return 50.0

    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos_filtrados)
    max_possivel = len(jogos_filtrados) * 3
    aproveitamento = (pontos / max_possivel) * 100
    return aproveitamento


def calcular_odds(
    odds_casa: float,
    odds_empate: float,
    odds_fora: float,
    mandante: bool
) -> float:
    """
    Converte as odds de 1X2 em probabilidade implícita e retorna a chance
    do time analisado (casa se mandante=True, fora se False) em escala 0–100.
    Se odds não disponíveis, retorna None.
    """
    if None in (odds_casa, odds_empate, odds_fora):
        return None

    prob_casa = 1 / odds_casa
    prob_empate = 1 / odds_empate
    prob_fora = 1 / odds_fora
    total = prob_casa + prob_empate + prob_fora

    # Remove overround
    prob_casa /= total
    prob_empate /= total
    prob_fora /= total

    if mandante:
        return prob_casa * 100
    else:
        return prob_fora * 100


def calcular_ic(fatores: dict, pesos: dict = None) -> float:
    """
    Consolida os fatores contextuais em um único Índice de Contexto (0–100).
    fatores: dict com chaves dos fatores e valores 0–100 (ou None se ausente)
    pesos: dict opcional com pesos para cada fator. Default: PESOS_IC.
    """
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
    """
    Combina IMA, OVRall e IC no rating dinâmico MPV (0–100).
    pesos: dict com 'IMA', 'OVRall', 'IC'. Default: PESOS_MPV.
    """
    if pesos is None:
        pesos = PESOS_MPV

    return (pesos['IMA'] * ima +
            pesos['OVRall'] * ovrall +
            pesos['IC'] * ic)
