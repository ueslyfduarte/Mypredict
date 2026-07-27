# data_loader.py — MyPredict 2.0
# Carregamento de dados, herança estatística e extração de recortes.

from config import JOGOS_BASE_OVRALL, POS_REF_PROMOVIDO, POS_REF_REBAIXADO, JOGOS_CONFRONTO_DIRETO


def carregar_jogos_temporada(time: str, liga: str, temporada: int) -> list:
    """
    Retorna lista de todos os jogos de um time em uma determinada liga e temporada.
    Placeholder — conectar com API/CSV real.
    Campos esperados: data, resultado, adversario, mandante, gols_pro, gols_contra, ...
    """
    return []


def carregar_confrontos_diretos(time: str, adversario: str, liga: str, limite: int = JOGOS_CONFRONTO_DIRETO) -> list:
    """
    Retorna lista dos últimos confrontos entre time e adversário (qualquer competição/temporada).
    Campos: data, resultado (do ponto de vista do time), etc.
    Placeholder.
    """
    return []


def classificação_anterior(liga: str, temporada: int) -> dict:
    """Retorna {posicao: nome_time} da temporada anterior."""
    return {}


def time_eh_promovido(time: str, liga: str, temporada_atual: int) -> bool:
    return False


def time_eh_rebaixado(time: str, liga: str, temporada_atual: int) -> bool:
    return False


def obter_time_por_posicao(classificacao: dict, posicao: int) -> str:
    return classificacao.get(posicao)


def obter_ultimos_jogos_com_heranca(
    time: str,
    liga: str,
    temporada_atual: int,
    classificacao_anterior: dict,
    n: int = JOGOS_BASE_OVRALL
) -> list:
    """
    Retorna lista com os últimos n jogos do time na divisão.
    Se o time não possui histórico suficiente, completa com jogos do time de referência.
    """
    jogos_reais = []
    temp = temporada_atual
    while len(jogos_reais) < n and temp >= temporada_atual - 3:
        jogos = carregar_jogos_temporada(time, liga, temp)
        jogos_reais.extend(jogos)
        temp -= 1
    jogos_reais.sort(key=lambda j: j['data'], reverse=True)

    if len(jogos_reais) >= n:
        return jogos_reais[:n]

    if time_eh_promovido(time, liga, temporada_atual):
        ref_time = obter_time_por_posicao(classificacao_anterior, POS_REF_PROMOVIDO)
    elif time_eh_rebaixado(time, liga, temporada_atual):
        ref_time = obter_time_por_posicao(classificacao_anterior, POS_REF_REBAIXADO)
    else:
        ref_time = None

    if ref_time:
        jogos_ref = []
        temp = temporada_atual - 1
        while len(jogos_ref) < (n - len(jogos_reais)) and temp >= temporada_atual - 3:
            jogos = carregar_jogos_temporada(ref_time, liga, temp)
            jogos_ref.extend(jogos)
            temp -= 1
        jogos_ref.sort(key=lambda j: j['data'], reverse=True)

        todos_jogos = jogos_reais + jogos_ref[:n - len(jogos_reais)]
        todos_jogos.sort(key=lambda j: j['data'], reverse=True)
        return todos_jogos[:n]

    return jogos_reais[:n]


def extrair_recortes_ima(jogos: list, time_mandante: bool) -> dict:
    """
    A partir da lista de jogos (ordenados por data decrescente),
    retorna dict com os recortes: 10G, 5G, 3G, 5CF, 3CF.
    """
    recortes = {
        '10G': jogos[:10],
        '5G':  jogos[:5],
        '3G':  jogos[:3],
    }
    condicao = lambda j: j['mandante'] if time_mandante else not j['mandante']
    jogos_mando = [j for j in jogos if condicao(j)]
    recortes['5CF'] = jogos_mando[:5]
    recortes['3CF'] = jogos_mando[:3]
    return recortes


def carregar_odds_partida(casa: str, fora: str, liga: str) -> tuple:
    """
    Retorna (odds_casa, odds_empate, odds_fora) para a partida.
    Placeholder — integrar com API de odds.
    """
    return None, None, None
