# data_source_api_football.py — MyPredict 2.0 (API-Football v3)
import time
import requests
from pathlib import Path
import json
import os
from datetime import datetime, timedelta
from collections import deque

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

# Controle de requisições
_request_times = deque()

def _register_request():
    agora = datetime.now()
    _request_times.append(agora)
    while _request_times and (agora - _request_times[0]).total_seconds() > 60:
        _request_times.popleft()

def get_api_usage():
    agora = datetime.now()
    while _request_times and (agora - _request_times[0]).total_seconds() > 60:
        _request_times.popleft()
    return len(_request_times), 100  # plano gratuito: 100 req/dia

def _cache_valido(arq):
    if not arq.exists():
        return False
    idade = datetime.now() - datetime.fromtimestamp(arq.stat().st_mtime)
    return idade < timedelta(days=7)

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
    _register_request()
    time.sleep(6)
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

# ------------------------------------------------------------
# IDs das principais ligas (fallback estático)
# ------------------------------------------------------------
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

def listar_ligas():
    """Retorna {nome: id} das ligas disponíveis (com cache e fallback)."""
    cache_key = "leagues_list"
    cached = _cache_ler(cache_key)
    if cached:
        return cached

    try:
        data = _get(f"{BASE_URL}/leagues")
        ligas = {}
        for item in data.get("response", []):
            liga = item["league"]
            nome = liga["name"]
            liga_id = liga["id"]
            ligas[nome] = liga_id
        if ligas:
            _cache_escrever(cache_key, ligas)
            return ligas
    except:
        pass

    _cache_escrever(cache_key, FALLBACK_LEAGUES)
    return FALLBACK_LEAGUES

def listar_temporadas(liga_id):
    """Retorna lista de anos disponíveis para a liga."""
    cache_key = f"seasons_{liga_id}"
    cached = _cache_ler(cache_key)
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

def obter_classificacao(liga_nome, temporada):
    ligas = listar_ligas()
    liga_id = ligas.get(liga_nome)
    if not liga_id:
        raise ValueError(f"Liga '{liga_nome}' não encontrada.")
    chave = f"standings_{liga_id}_{temporada}"
    cached = _cache_ler(chave)
    if cached:
        return {int(k): v for k, v in cached.items()}

    data = _get(f"{BASE_URL}/standings?league={liga_id}&season={temporada}")
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
    chave = f"fixtures_{liga_id}_{temporada}_{time}"
    cached = _cache_ler(chave)
    if cached:
        return cached

    data = _get(f"{BASE_URL}/fixtures?league={liga_id}&season={temporada}")
    jogos = []
    for match in data["response"]:
        fixture = match["fixture"]
        if fixture["status"]["short"] != "FT":
            continue
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        if time.lower() not in (home.lower(), away.lower()):
            continue

        mandante_flag = time.lower() == home.lower()
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
    return {}
