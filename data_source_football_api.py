# data_source_football_api.py — MyPredict 2.0 (dinâmico e sem conflitos)
import time
import requests
from pathlib import Path
import json
import os
from datetime import datetime, timedelta

API_KEY = os.environ.get("FOOTBALL_API_KEY")
if API_KEY is None:
    try:
        import streamlit as st
        API_KEY = st.secrets["FOOTBALL_API_KEY"]
    except:
        raise RuntimeError("Chave da API não encontrada. Configure FOOTBALL_API_KEY nos secrets do Streamlit.")

BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}
CACHE_DIR = Path("cache/football_api")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Cache com validade (24 horas)
def _cache_valido(arq):
    if not arq.exists():
        return False
    idade = datetime.now() - datetime.fromtimestamp(arq.stat().st_mtime)
    return idade < timedelta(hours=24)

def _cache_ler(chave):
    arq = CACHE_DIR / f"{chave}.json"
    if _cache_valido(arq):
        with open(arq, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def _cache_escrever(chave, dados):
    with open(CACHE_DIR / f"{chave}.json", 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

def _get(url):
    time.sleep(6)
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

# ------------------------------------------------------------
# Funções dinâmicas de ligas e temporadas
# ------------------------------------------------------------
def listar_ligas():
    """Retorna {nome_exibicao: codigo_api} de todas as competições disponíveis."""
    cache_key = "available_leagues"
    cached = _cache_ler(cache_key)
    if cached:
        return cached

    data = _get(f"{BASE_URL}/competitions")
    ligas = {}
    for comp in data.get("competitions", []):
        nome = comp["name"]
        codigo = comp["code"]
        # Filtra apenas ligas de futebol adulto (não copas ou feminino)
        if comp.get("type") == "LEAGUE" and comp.get("plan") == "TIER_ONE":
            ligas[nome] = codigo
    _cache_escrever(cache_key, ligas)
    return ligas

def listar_temporadas(codigo_liga):
    """Retorna lista de anos (ex.: [2024, 2023, 2022]) disponíveis para a liga."""
    cache_key = f"seasons_{codigo_liga}"
    cached = _cache_ler(cache_key)
    if cached:
        return cached

    try:
        data = _get(f"{BASE_URL}/competitions/{codigo_liga}/teams")  # endpoint leve
        # Na resposta, há um filtro de season; vamos extrair da URL permitida
        # Como a API não tem um endpoint direto de temporadas, faremos uma tentativa
        # de listar anos comuns. A melhor abordagem é usar o endpoint de partidas
        # e deduzir os anos disponíveis. Para simplificar, vamos gerar uma lista
        # de anos prováveis e testar um por um (com cache agressivo).
        anos = []
        for ano in range(datetime.now().year, datetime.now().year - 10, -1):
            try:
                _get(f"{BASE_URL}/competitions/{codigo_liga}/matches?season={ano}&dateFrom={ano}-01-01&dateTo={ano}-12-31")
                anos.append(ano)
            except requests.exceptions.HTTPError:
                continue
        if not anos:
            # fallback: últimos 5 anos
            anos = list(range(datetime.now().year, datetime.now().year - 5, -1))
        _cache_escrever(cache_key, anos)
        return anos
    except:
        # fallback estático caso a API falhe
        return list(range(datetime.now().year, datetime.now().year - 5, -1))

# ------------------------------------------------------------
# Funções de dados (classificação e partidas) — INALTERADAS
# ------------------------------------------------------------
def obter_classificacao(liga_nome, temporada):
    ligas = listar_ligas()
    codigo = ligas.get(liga_nome)
    if not codigo:
        raise ValueError(f"Liga '{liga_nome}' não encontrada na API.")
    chave = f"class_{codigo}_{temporada}"
    cached = _cache_ler(chave)
    if cached:
        return {int(k): v for k, v in cached.items()}

    url = f"{BASE_URL}/competitions/{codigo}/standings?season={temporada}"
    data = _get(url)
    standings = data['standings'][0]['table']
    classif = {}
    for entry in standings:
        pos = entry['position']
        nome = entry['team']['name']
        classif[pos] = nome
    _cache_escrever(chave, classif)
    return classif

def obter_partidas_time(liga_nome, temporada, time):
    ligas = listar_ligas()
    codigo = ligas.get(liga_nome)
    if not codigo:
        raise ValueError(f"Liga '{liga_nome}' não encontrada na API.")
    chave = f"partidas_{codigo}_{temporada}_{time}"
    cached = _cache_ler(chave)
    if cached:
        return cached

    url = f"{BASE_URL}/competitions/{codigo}/matches?season={temporada}"
    data = _get(url)
    jogos = []
    for match in data['matches']:
        if match['status'] != 'FINISHED':
            continue
        home = match['homeTeam']['name']
        away = match['awayTeam']['name']
        if time.lower() not in (home.lower(), away.lower()):
            continue

        mandante_flag = time.lower() == home.lower()
        gols_casa = match['score']['fullTime']['home'] or 0
        gols_fora = match['score']['fullTime']['away'] or 0
        gols_pro = gols_casa if mandante_flag else gols_fora
        gols_contra = gols_fora if mandante_flag else gols_casa
        adversario = away if mandante_flag else home

        ht = match['score']['halfTime']
        ht_casa = ht['home'] if ht['home'] is not None else 0
        ht_fora = ht['away'] if ht['away'] is not None else 0
        ht_placar = [ht_casa, ht_fora] if mandante_flag else [ht_fora, ht_casa]

        resultado = 'V' if gols_pro > gols_contra else ('E' if gols_pro == gols_contra else 'D')

        jogos.append({
            'data': match['utcDate'][:10],
            'resultado': resultado,
            'adversario': adversario,
            'mandante': mandante_flag,
            'gols_pro': gols_pro,
            'gols_contra': gols_contra,
            'ht_placar': ht_placar,
            'xg': None, 'xga': None,
            'finalizacoes_tot': None, 'finalizacoes_alvo': None,
            'posse': None, 'passes_certos': None, 'passes_totais': None,
            'passes_chave': None, 'assistencias': None,
            'desarmes': None, 'interceptacoes': None,
            'escanteios': None, 'escanteios_sofridos': None,
            'gols_ultimos_15': None,
        })
    jogos.sort(key=lambda x: x['data'])
    _cache_escrever(chave, jogos)
    return jogos

def obter_stats_time(liga_nome, temporada, time):
    return {}
