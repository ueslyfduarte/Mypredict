# data_loader.py — MyPredict 2.0
# Carregamento de dados, herança estatística, projeção de prateleiras.

from config import (
    JOGOS_BASE_OVRALL, POS_REF_PROMOVIDO, POS_REF_REBAIXADO,
    NUM_PROMOVIDOS, PONTOS_BASE, JOGOS_CONFRONTO_DIRETO
)
from statistics import stdev, mean


# ------------------------------------------------------------
# FUNÇÕES PLACEHOLDER DE FONTE DE DADOS (substituir por API/CSV)
# ------------------------------------------------------------

def carregar_jogos_temporada(time: str, liga: str, temporada: int) -> list:
    """
    Retorna lista de jogos de um time na temporada/liga.
    Campos esperados: data, resultado ('V','E','D'), adversario, mandante (bool),
    gols_pro, gols_contra, finalizacoes_tot, finalizacoes_alvo, posse,
    passes_certos, passes_totais, passes_chave, assistencias, xg, xga,
    desarmes, interceptacoes, ht_placar (lista [gols_time, gols_adv]),
    escanteios, escanteios_sofridos, gols_ultimos_15, etc.
    """
    return []


def carregar_confrontos_diretos(time: str, adversario: str, liga: str) -> list:
    """Últimos confrontos entre time e adversário (independente de temporada)."""
    return []


def classificação_anterior(liga: str, temporada: int) -> dict:
    """Retorna {posicao: nome_time} da classificação final."""
    return {}


def _obter_promovidos_ordenados(liga: str, temporada_atual: int) -> list:
    """Retorna lista de nomes dos times promovidos, do 1º ao 4º colocado."""
    return []


def _obter_rebaixados(liga: str, temporada: int) -> list:
    """Retorna lista de nomes dos times rebaixados na temporada."""
    return []


def carregar_odds_partida(casa: str, fora: str, liga: str) -> tuple:
    """Retorna (odds_casa, odds_empate, odds_fora) ou (None, None, None)."""
    return None, None, None


# ------------------------------------------------------------
# PROJEÇÃO DE PRATELEIRAS (início de temporada)
# ------------------------------------------------------------

def gerar_prateleiras(liga: str, temporada_atual: int) -> dict:
    """
    Retorna {time: prateleira} com base na classificação anterior,
    substituindo rebaixados pelos promovidos (ordenados) nas mesmas posições.
    """
    class_ant = classificação_anterior(liga, temporada_atual - 1)
    if not class_ant:
        return {}

    promovidos = _obter_promovidos_ordenados(liga, temporada_atual)
    rebaixados = _obter_rebaixados(liga, temporada_atual - 1)

    pos_rebaixados = sorted([pos for pos, time in class_ant.items() if time in rebaixados])

    nova_class = class_ant.copy()
    for i, time_prom in enumerate(promovidos):
        if i < len(pos_rebaixados):
            nova_class[pos_rebaixados[i]] = time_prom

    from ratings import obter_prateleira
    prateleiras = {}
    for pos, time in nova_class.items():
        prateleiras[time] = obter_prateleira(pos)

    return prateleiras


# ------------------------------------------------------------
# HERANÇA DE DADOS (OVRall / IMA)
# ------------------------------------------------------------

def obter_ultimos_jogos_com_heranca(
    time: str, liga: str, temporada_atual: int,
    classificação_anterior: dict, n: int = JOGOS_BASE_OVRALL
) -> list:
    """
    Últimos n jogos do time na divisão, herdando jogos do time de referência
    se o time não tem histórico suficiente.
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

    if _time_subiu(time, liga, temporada_atual):
        ref_pos = POS_REF_PROMOVIDO
    elif _time_desceu(time, liga, temporada_atual):
        ref_pos = POS_REF_REBAIXADO
    else:
        ref_pos = None

    ref_time = classificação_anterior.get(ref_pos) if ref_pos else None

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


def _time_subiu(time: str, liga: str, temporada: int) -> bool:
    promovidos = _obter_promovidos_ordenados(liga, temporada)
    return time in promovidos


def _time_desceu(time: str, liga: str, temporada: int) -> bool:
    rebaixados = _obter_rebaixados(liga, temporada - 1)
    return time in rebaixados


# ------------------------------------------------------------
# EXTRAÇÃO DE RECORTES (IMA)
# ------------------------------------------------------------

def extrair_recortes_ima(jogos: list, time_mandante: bool) -> dict:
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


# ------------------------------------------------------------
# AGREGADORES DE ESTATÍSTICAS (OVRall e mercados)
# ------------------------------------------------------------

def _media(lista):
    return mean(lista) if lista else None

def _desvio(lista):
    return stdev(lista) if len(lista) > 1 else 0.0

def _aproveitamento(jogos):
    if not jogos: return None
    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos)
    return (pontos / (len(jogos) * 3)) * 100

def _gols_ultimos_15min(jogos):
    gols = [j.get('gols_ultimos_15', 0) for j in jogos]
    return _media(gols)

def _pontos_pos_desvantagem(jogos):
    desv = [j for j in jogos if j.get('ht_placar') and j['ht_placar'][0] < j['ht_placar'][1]]
    return _aproveitamento(desv)

def _pontos_apos_derrota(jogos):
    # placeholder
    return None

def _diff_casa_fora(jogos):
    casa = [j for j in jogos if j['mandante']]
    fora = [j for j in jogos if not j['mandante']]
    ap_casa = _aproveitamento(casa) if casa else 0
    ap_fora = _aproveitamento(fora) if fora else 0
    return ap_casa - ap_fora

def _aprov_viradas_favor(jogos):
    desv = [j for j in jogos if j.get('ht_placar') and j['ht_placar'][0] < j['ht_placar'][1]]
    return _aproveitamento(desv)

def _aprov_viradas_contra(jogos):
    vant = [j for j in jogos if j.get('ht_placar') and j['ht_placar'][0] > j['ht_placar'][1]]
    if not vant:
        return None
    pontos_obtidos = sum(PONTOS_BASE[j['resultado']] for j in vant)
    max_pontos = len(vant) * 3
    pontos_perdidos = max_pontos - pontos_obtidos
    return (pontos_perdidos / max_pontos) * 100

def _gols_ht_media(jogos):
    gols_ht = []
    for j in jogos:
        if j.get('ht_placar'):
            gols_ht.append(j['ht_placar'][0])
    return _media(gols_ht)

def _gols_ht_sofridos_media(jogos):
    gols_ht = []
    for j in jogos:
        if j.get('ht_placar'):
            gols_ht.append(j['ht_placar'][1])
    return _media(gols_ht)

def _escanteios_media(jogos, chave='escanteios'):
    valores = [j.get(chave) for j in jogos if j.get(chave) is not None]
    return _media(valores)


def obter_dados_ovrall_time(time: str, liga: str, temporada_atual: int,
                            classificacao_ant: dict) -> dict:
    """
    Retorna dicionário com todas as estatísticas agregadas do time
    nos últimos JOGOS_BASE_OVRALL jogos (com herança).
    """
    jogos = obter_ultimos_jogos_com_heranca(time, liga, temporada_atual,
                                            classificacao_ant, JOGOS_BASE_OVRALL)
    if not jogos:
        return {}

    n = len(jogos)
    gols = [j['gols_pro'] for j in jogos]
    gols_sofridos = [j['gols_contra'] for j in jogos]
    xg = [j.get('xg') for j in jogos if j.get('xg') is not None]
    xga = [j.get('xga') for j in jogos if j.get('xga') is not None]
    finalizacoes_alvo = [j.get('finalizacoes_alvo') for j in jogos if j.get('finalizacoes_alvo') is not None]
    finalizacoes_alvo_sofridas = [j.get('finalizacoes_alvo_sofridas') for j in jogos if j.get('finalizacoes_alvo_sofridas') is not None]
    chutes = [j.get('finalizacoes_tot', 0) for j in jogos]
    desarmes_intercep = [j.get('desarmes', 0) + j.get('interceptacoes', 0) for j in jogos]
    posse = [j.get('posse') for j in jogos if j.get('posse') is not None]
    passes_certos = [j.get('passes_certos') for j in jogos if j.get('passes_certos') is not None]
    passes_totais = [j.get('passes_totais') for j in jogos if j.get('passes_totais') is not None]
    passes_chave = [j.get('passes_chave') for j in jogos if j.get('passes_chave') is not None]
    assistencias = [j.get('assistencias') for j in jogos if j.get('assistencias') is not None]
    pontos_por_jogo = [PONTOS_BASE[j['resultado']] for j in jogos]

    dados = {
        'gols_media': _media(gols),
        'gols_sofridos_media': _media(gols_sofridos),
        'xg_media': _media(xg),
        'xga_media': _media(xga),
        'finalizacoes_alvo_media': _media(finalizacoes_alvo),
        'finalizacoes_alvo_sofridas_media': _media(finalizacoes_alvo_sofridas),
        'chutes_media': _media(chutes),
        'desarmes_intercep_media': _media(desarmes_intercep),
        'posse_media': _media(posse),
        'passes_certos_pct': (sum(passes_certos)/sum(passes_totais))*100 if passes_totais and sum(passes_totais)>0 else None,
        'passes_chave_media': _media(passes_chave),
        'assistencias_media': _media(assistencias),
        'conversao': (sum(gols)/sum(chutes))*100 if sum(chutes)>0 else None,
        'clean_sheets_pct': (sum(1 for g in gols_sofridos if g==0)/n)*100,
        'desvio_pontos': _desvio(pontos_por_jogo),
        'desvio_gols_pro': _desvio(gols),
        'desvio_gols_sofridos': _desvio(gols_sofridos),
        'pontos_pos_desvantagem_media': _pontos_pos_desvantagem(jogos),
        'gols_ultimos_15min_media': _gols_ultimos_15min(jogos),
        'pontos_apos_derrota_media': _pontos_apos_derrota(jogos),
        'diff_aprov_casa_fora': _diff_casa_fora(jogos),
        'aprov_viradas_favor': _aprov_viradas_favor(jogos),
        'aprov_viradas_contra': _aprov_viradas_contra(jogos),
        # Mercados
        'gols_ht_media': _gols_ht_media(jogos),
        'gols_ht_sofridos_media': _gols_ht_sofridos_media(jogos),
        'escanteios_media': _escanteios_media(jogos, 'escanteios'),
        'escanteios_sofridos_media': _escanteios_media(jogos, 'escanteios_sofridos'),
    }

    return {k: v for k, v in dados.items() if v is not None}


def obter_dados_liga(liga: str, temporada_atual: int) -> dict:
    """Retorna dicionário com listas de cada indicador para todos os times da liga."""
    prateleiras = gerar_prateleiras(liga, temporada_atual)
    times = list(prateleiras.keys())
    dados_liga = {}
    for time in times:
        dados_time = obter_dados_ovrall_time(time, liga, temporada_atual, classificação_anterior(liga, temporada_atual-1))
        for chave, valor in dados_time.items():
            dados_liga.setdefault(chave, []).append(valor)
    return dados_liga
