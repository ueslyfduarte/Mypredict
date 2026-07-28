# data_source_api_football.py — MyPredict 2.0 (API-SPORTS v3)
import time
import requests
from pathlib import Path
import json
import os
from datetime import datetime, timedelta
from collections import deque

# Autenticação
API_KEY = os.environ.get("API_FOOTBALL_KEY")
if API_KEY is None:
    try:
        import streamlit as st
        API_KEY = st.secrets["API_FOOTBALL_KEY"]
    except:
        raise RuntimeError("Chave da API não encontrada. Configure API_FOOTBALL_KEY nos secrets do Streamlit.")

BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}
CACHE_DIR = Path("cache/api_football")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Controle de requisições (leitura dos headers da API)
_daily_remaining = 100
_minute_remaining = 10

def get_api_usage():
    """Retorna (requisições restantes no dia, limite diário)."""
    return _daily_remaining, 100

def _update_rate_limits(response):
    """Atualiza os limites com base nos headers da resposta."""
    global _daily_remaining, _minute_remaining
    if 'x-ratelimit-requests-remaining' in response.headers:
        _daily_remaining = int(response.headers['x-ratelimit-requests-remaining'])
    if 'X-RateLimit-Remaining' in response.headers:
        _minute_remaining = int(response.headers['X-RateLimit-Remaining'])

# Cache com validade variável
def _cache_valido(arq, horas=24):
    if not arq.exists():
        return False
    idade = datetime.now() - datetime.fromtimestamp(arq.stat().st_mtime)
    return idade < timedelta(hours=horas)

def _cache_ler(chave, horas=24):
    arq = CACHE_DIR / f"{chave}.json"
    if _cache_valido(arq, horas):
        with open(arq, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def _cache_escrever(chave, dados):
    with open(CACHE_DIR / f"{chave}.json", 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

def _get(url):
    """Faz a requisição, respeita rate limit e atualiza limites."""
    time.sleep(6)
    resp = requests.get(url, headers=HEADERS)
    _update_rate_limits(resp)
    resp.raise_for_status()
    return resp.json()

# Fallback estático (principais ligas)
FALLBACK_LEAGUES = {
    "Brasileirão": 71,
    "Premier League": 39,
    "La Liga": 140,
    "Bundesliga": 78,
    "Serie A": 135,
    "Ligue 1": 61,
    "Eredivisie": 88,
    "Primeira Liga": 94,
    "MLS": 253,
    "Championship": 40,
    "Série B": 72,
}

# ------------------------------------------------------------
# Funções dinâmicas (com cache e fallback)
# ------------------------------------------------------------
def listar_ligas():
    """Retorna {nome: id} das ligas disponíveis."""
    cache_key = "leagues_list"
    cached = _cache_ler(cache_key, horas=168)  # 7 dias
    if cached:
        return cached

    try:
        data = _get(f"{BASE_URL}/leagues?current=true")
        ligas = {}
        for item in data.get("response", []):
            nome = item["league"]["name"]
            liga_id = item["league"]["id"]
            ligas[nome] = liga_id
        if ligas:
            _cache_escrever(cache_key, ligas)
            return ligas
    except:
        pass

    # Fallback
    _cache_escrever(cache_key, FALLBACK_LEAGUES)
    return FALLBACK_LEAGUES

def listar_temporadas(liga_id):
    """Retorna lista de anos disponíveis para a liga."""
    cache_key = f"seasons_{liga_id}"
    cached = _cache_ler(cache_key, horas=168)
    if cached:
        return cached

    try:
        data = _get(f"{BASE_URL}/leagues?id={liga_id}")
        seasons = data["response"][0]["seasons"]
        anos = sorted([s["year"] for s in seasons], reverse=True)
        _cache_escrever(cache_key, anos)
        return anos
    except:
        anos = list(range(datetime.now().year, datetime.now().year - 5, -1))
        _cache_escrever(cache_key, anos)
        return anos

# ------------------------------------------------------------
# Dados de classificação, partidas e estatísticas
# ------------------------------------------------------------
def obter_classificacao(liga_nome, temporada):
    ligas = listar_ligas()
    liga_id = ligas.get(liga_nome)
    if not liga_id:
        raise ValueError(f"Liga '{liga_nome}' não encontrada.")
    chave = f"standings_{liga_id}_{temporada}"
    cached = _cache_ler(chave, horas=24)
    if cached:
        return {int(k): v for k, v in cached.items()}

    data = _get(f"{BASE_URL}/standings?league={liga_id}&season={temporada}")
    if not data.get("response") or not data["response"][0]["league"]["standings"]:
        raise ValueError("Classificação não disponível para esta liga/temporada.")

    standings = data["response"][0]["league"]["standings"][0]
    classif = {}
    for entry in standings:
        pos = entry["rank"]
        nome = entry["team"]["name"]
        classif[pos] = nome
    _cache_escrever(chave, classif)
    return classif

def obter_partidas_time(liga_nome, temporada, time):
    ligas = listar_ligas()
    liga_id = ligas.get(liga_nome)
    if not liga_id:
        raise ValueError(f"Liga '{liga_nome}' não encontrada.")
    # Precisamos do ID do time. Como o nome pode variar, usamos a classificação para achar o time.
    classif = obter_classificacao(liga_nome, temporada)
    time_id = None
    for pos, nome in classif.items():
        if time.lower() == nome.lower():
            # Buscar ID do time pela API de times
            try:
                data = _get(f"{BASE_URL}/teams?league={liga_id}&season={temporada}&search={nome}")
                if data.get("response"):
                    time_id = data["response"][0]["team"]["id"]
                    break
            except:
                continue
    if not time_id:
        raise ValueError(f"Time '{time}' não encontrado na liga {liga_nome} temporada {temporada}.")

    chave = f"fixtures_{time_id}_{temporada}"
    cached = _cache_ler(chave, horas=24)
    if cached:
        return cached

    data = _get(f"{BASE_URL}/fixtures?team={time_id}&season={temporada}")
    jogos = []
    for match in data.get("response", []):
        fixture = match["fixture"]
        if fixture["status"]["short"] != "FT":
            continue
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        mandante_flag = (home.lower() == time.lower())
        gols_casa = match["goals"]["home"] or 0
        gols_fora = match["goals"]["away"] or 0
        gols_pro = gols_casa if mandante_flag else gols_fora
        gols_contra = gols_fora if mandante_flag else gols_casa
        adversario = away if mandante_flag else home

        ht = match["score"]["halftime"]
        ht_casa = ht["home"] if ht["home"] is not None else 0
        ht_fora = ht["away"] if ht["away"] is not None else 0
        ht_placar = [ht_casa, ht_fora] if mandante_flag else [ht_fora, ht_casa]

        resultado = 'V' if gols_pro > gols_contra else ('E' if gols_pro == gols_contra else 'D')

        jogos.append({
            'data': fixture["date"][:10],
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
    ligas = listar_ligas()
    liga_id = ligas.get(liga_nome)
    if not liga_id:
        return {}
    # Obter ID do time (similar a obter_partidas_time)
    classif = obter_classificacao(liga_nome, temporada)
    time_id = None
    for nome in classif.values():
        if time.lower() == nome.lower():
            data = _get(f"{BASE_URL}/teams?league={liga_id}&season={temporada}&search={nome}")
            if data.get("response"):
                time_id = data["response"][0]["team"]["id"]
                break
    if not time_id:
        return {}

    chave = f"team_stats_{time_id}_{liga_id}_{temporada}"
    cached = _cache_ler(chave, horas=24)
    if cached:
        return cached

    try:
        data = _get(f"{BASE_URL}/teams/statistics?team={time_id}&league={liga_id}&season={temporada}")
        stats = data["response"]
        if not stats:
            return {}
        stats = stats[0]  # A resposta vem como uma lista de um elemento
        fixtures = stats.get("fixtures", {})
        gols = stats.get("goals", {})
        passes = stats.get("passes", {})
        shots = stats.get("shots", {})

        mp = fixtures.get("played", {}).get("total", 1)
        dados = {}
        if "total" in gols.get("for", {}):
            dados['gols_media'] = gols["for"]["total"]["total"] / mp if mp > 0 else 0
        if "total" in gols.get("against", {}):
            dados['gols_sofridos_media'] = gols["against"]["total"]["total"] / mp if mp > 0 else 0
        # Posse de bola (em %)
        if "possession" in stats:
            dados['posse_media'] = float(stats["possession"].get("average", "0").replace('%', ''))
        # Passes
        if "total" in passes:
            dados['passes_certos_media'] = passes["total"].get("accurate", 0) / mp if mp > 0 else 0
        if "accuracy" in passes:
            dados['passes_certos_pct'] = int(passes["accuracy"].get("total", "0").replace('%', ''))
        # Finalizações
        if "total" in shots:
            dados['finalizacoes_tot_media'] = shots["total"].get("total", 0) / mp if mp > 0 else 0
        if "on" in shots:
            dados['finalizacoes_alvo_media'] = shots["on"].get("total", 0) / mp if mp > 0 else 0

        resultado = {k: v for k, v in dados.items() if v is not None}
        _cache_escrever(chave, resultado)
        return resultado
    except:
        return {}
