# data_loader.py — MyPredict 2.0
# Carregamento de dados, herança estatística, projeção de prateleiras.

from config import JOGOS_BASE_OVRALL, POS_REF_PROMOVIDO, POS_REF_REBAIXADO, PONTOS_BASE
from statistics import stdev, mean
import json
from pathlib import Path
from data_source_worldfootball import obter_classificacao, obter_partidas_time
from data_source_fbref_stats import obter_stats_time as obter_stats_fbref

CONFIG_LIGAS_PATH = 'config_ligas.json'

def _carregar_config_ligas():
    if Path(CONFIG_LIGAS_PATH).exists():
        with open(CONFIG_LIGAS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def classificação_anterior(liga, temporada):
    return obter_classificacao(liga, temporada)

def _obter_promovidos_ordenados(liga, temporada):
    config = _carregar_config_ligas()
    return config.get(liga, {}).get(str(temporada), {}).get('promovidos', [])

def _obter_rebaixados(liga, temporada):
    config = _carregar_config_ligas()
    return config.get(liga, {}).get(str(temporada), {}).get('rebaixados', [])

def gerar_prateleiras(liga, temporada):
    class_ant = classificação_anterior(liga, temporada)
    if not class_ant:
        return {}
    promovidos = _obter_promovidos_ordenados(liga, temporada)
    rebaixados = _obter_rebaixados(liga, temporada - 1) if temporada > 2010 else []
    pos_rebaixados = sorted([pos for pos, time in class_ant.items() if time in rebaixados])
    nova_class = class_ant.copy()
    for i, time_prom in enumerate(promovidos):
        if i < len(pos_rebaixados):
            nova_class[pos_rebaixados[i]] = time_prom
    from ratings import obter_prateleira
    return {time: obter_prateleira(pos) for pos, time in nova_class.items()}

def carregar_jogos_temporada(time, liga, temporada):
    return obter_partidas_time(liga, temporada, time)

def obter_ultimos_jogos_com_heranca(time, liga, temporada_atual, classificacao_ant, n=JOGOS_BASE_OVRALL):
    jogos_reais = []
    temp = temporada_atual
    while len(jogos_reais) < n and temp >= temporada_atual - 3:
        jogos = carregar_jogos_temporada(time, liga, temp)
        jogos_reais.extend(jogos)
        temp -= 1
    jogos_reais.sort(key=lambda j: j['data'], reverse=True)
    if len(jogos_reais) >= n:
        return jogos_reais[:n]
    # herança
    if time in _obter_promovidos_ordenados(liga, temporada_atual):
        ref_pos = POS_REF_PROMOVIDO
    elif time in _obter_rebaixados(liga, temporada_atual - 1):
        ref_pos = POS_REF_REBAIXADO
    else:
        ref_pos = None
    ref_time = classificacao_ant.get(ref_pos) if ref_pos else None
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

def extrair_recortes_ima(jogos, time_mandante):
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

# Funções auxiliares de agregação
def _media(lista):
    return mean(lista) if lista else None
def _desvio(lista):
    return stdev(lista) if len(lista) > 1 else 0.0
def _aproveitamento(jogos):
    if not jogos: return None
    pontos = sum(PONTOS_BASE[j['resultado']] for j in jogos)
    return (pontos / (len(jogos)*3)) * 100
def _gols_ultimos_15min(jogos):
    gols = [j.get('gols_ultimos_15', 0) for j in jogos]
    return _media(gols)
def _pontos_pos_desvantagem(jogos):
    desv = [j for j in jogos if j.get('ht_placar') and j['ht_placar'][0] < j['ht_placar'][1]]
    return _aproveitamento(desv)
def _pontos_apos_derrota(jogos):
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
    if not vant: return None
    pontos_obtidos = sum(PONTOS_BASE[j['resultado']] for j in vant)
    max_pontos = len(vant)*3
    return ((max_pontos - pontos_obtidos)/max_pontos)*100
def _gols_ht_media(jogos):
    gols_ht = [j['ht_placar'][0] for j in jogos if j.get('ht_placar')]
    return _media(gols_ht)
def _gols_ht_sofridos_media(jogos):
    gols_ht = [j['ht_placar'][1] for j in jogos if j.get('ht_placar')]
    return _media(gols_ht)
def _escanteios_media(jogos, chave='escanteios'):
    valores = [j.get(chave) for j in jogos if j.get(chave) is not None]
    return _media(valores)

def obter_dados_ovrall_time(time, liga, temporada_atual, classificacao_ant):
    jogos = obter_ultimos_jogos_com_heranca(time, liga, temporada_atual, classificacao_ant)
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
        'gols_ht_media': _gols_ht_media(jogos),
        'gols_ht_sofridos_media': _gols_ht_sofridos_media(jogos),
        'escanteios_media': _escanteios_media(jogos, 'escanteios'),
        'escanteios_sofridos_media': _escanteios_media(jogos, 'escanteios_sofridos'),
    }

    # Tentar complementar com estatísticas do FBref (não sobrescreve se já existir)
    try:
        stats_fbref = obter_stats_fbref(liga, temporada_atual, time)
        for chave, valor in stats_fbref.items():
            if dados.get(chave) is None and valor is not None:
                dados[chave] = valor
    except Exception:
        pass  # se falhar, segue com os dados originais

    return {k: v for k, v in dados.items() if v is not None}
