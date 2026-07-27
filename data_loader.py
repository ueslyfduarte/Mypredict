# data_loader.py — MyPredict 2.0
# Funções para carregamento de jogos, classificação e aplicação da herança estatística.

from config import JOGOS_BASE_OVRALL, POS_REF_PROMOVIDO, POS_REF_REBAIXADO


def carregar_jogos_temporada(time: str, liga: str, temporada: int) -> list:
    """
    Retorna lista de jogos de um time em uma determinada liga e temporada.
    Exemplo de dicionário retornado:
        {
            'data': datetime,
            'resultado': 'V'/'E'/'D',
            'adversario': str,
            'mandante': bool,
            'gols_pro': int,
            'gols_contra': int,
            ... (demais estatísticas)
        }
    Esta é uma função placeholder que deve ser implementada com a fonte de dados real.
    """
    # TODO: conectar com API/CSV real
    return []


def classificação_anterior(liga: str, temporada: int) -> dict:
    """
    Retorna a classificação final da temporada anterior.
    Formato: {posicao: nome_time}
    """
    # TODO: implementar
    return {}


def time_eh_promovido(time: str, liga: str, temporada_atual: int) -> bool:
    """Verifica se o time subiu de divisão na temporada atual."""
    # TODO: comparar com lista de promovidos
    return False


def time_eh_rebaixado(time: str, liga: str, temporada_atual: int) -> bool:
    """Verifica se o time desceu de divisão na temporada atual."""
    # TODO: comparar com lista de rebaixados
    return False


def obter_time_por_posicao(classificacao: dict, posicao: int) -> str:
    """Retorna o nome do time na posição indicada da tabela."""
    return classificacao.get(posicao)


def obter_ultimos_jogos_com_heranca(
    time: str,
    liga: str,
    temporada_atual: int,
    classificacao_anterior: dict,
    n: int = JOGOS_BASE_OVRALL
) -> list:
    """
    Retorna os últimos n jogos do time, complementando com jogos do time de referência
    caso o time não tenha histórico suficiente na divisão atual.
    """
    # Busca jogos reais (da temporada atual e anteriores, se existirem)
    jogos_reais = []
    temp = temporada_atual
    while len(jogos_reais) < n and temp >= temporada_atual - 3:
        jogos = carregar_jogos_temporada(time, liga, temp)
        jogos_reais.extend(jogos)
        temp -= 1
    jogos_reais.sort(key=lambda j: j['data'], reverse=True)

    if len(jogos_reais) >= n:
        return jogos_reais[:n]

    # Identifica se é promovido ou rebaixado para aplicar herança
    if time_eh_promovido(time, liga, temporada_atual):
        ref_pos = POS_REF_PROMOVIDO
        ref_time = obter_time_por_posicao(classificacao_anterior, ref_pos)
    elif time_eh_rebaixado(time, liga, temporada_atual):
        ref_pos = POS_REF_REBAIXADO
        ref_time = obter_time_por_posicao(classificacao_anterior, ref_pos)
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

    return jogos_reais[:n]  # fallback sem complemento


def extrair_recortes_ima(jogos: list, time_mandante: bool) -> dict:
    """
    A partir de uma lista de jogos (ordenados por data decrescente),
    extrai os recortes necessários para o cálculo do IMA.
    Retorna um dicionário com as listas:
        '10G', '5G', '3G', '5CF', '3CF'
    O parâmetro time_mandante indica se o time joga em casa na partida atual.
    """
    # Gerais (sem filtro de mando)
    recortes = {
        '10G': jogos[:10],
        '5G':  jogos[:5],
        '3G':  jogos[:3],
    }

    # Filtra por mando: se for mandante na partida atual, busca jogos como mandante;
    # caso contrário, como visitante.
    condicao = lambda j: j['mandante'] if time_mandante else not j['mandante']

    jogos_mando = [j for j in jogos if condicao(j)]
    recortes['5CF'] = jogos_mando[:5]
    recortes['3CF'] = jogos_mando[:3]

    return recortes
