# data/api_football.py — Conexão com API-Football v3
import time
import requests
import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta

API_KEY = st.secrets["API_FOOTBALL_KEY"]
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

# Cache em disco com validade (fallback caso não haja cache do Streamlit)
CACHE_DIR = Path("cache/api_football")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _update_rate_limits(response):
    """Atualiza limites a partir dos headers (não usados diretamente, mas armazenados)."""
    # Apenas para debug
    pass

@st.cache_data(ttl=86400, show_spinner="Buscando ligas...")
def listar_ligas():
    """Retorna dicionário {nome: id} das ligas disponíveis."""
    try:
        resp = requests.get(f"{BASE_URL}/leagues?current=true", headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        ligas = {}
        for item in data.get("response", []):
            nome = item["league"]["name"]
            liga_id = item["league"]["id"]
            ligas[nome] = liga_id
        if ligas:
            return ligas
    except Exception as e:
        # Fallback estático se a API falhar
        pass

    # Fallback offline
    FALLBACK = {
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
    return FALLBACK

@st.cache_data(ttl=86400, show_spinner="Buscando temporadas...")
def listar_temporadas(liga_id):
    """Retorna lista de anos disponíveis para a liga."""
    try:
        resp = requests.get(f"{BASE_URL}/leagues?id={liga_id}", headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        seasons = data["response"][0]["seasons"]
        anos = sorted([s["year"] for s in seasons], reverse=True)
        return anos
    except:
        # Fallback: últimos 5 anos
        return list(range(datetime.now().year, datetime.now().year - 5, -1))

@st.cache_data(ttl=3600, show_spinner="Obtendo classificação...")
def obter_classificacao(liga_nome, temporada):
    """Retorna dicionário {posição: nome_time} da classificação."""
    ligas = listar_ligas()
    liga_id = ligas.get(liga_nome)
    if not liga_id:
        return {}
    try:
        resp = requests.get(f"{BASE_URL}/standings?league={liga_id}&season={temporada}", headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        standings = data["response"][0]["league"]["standings"][0]
        classif = {}
        for entry in standings:
            pos = entry["rank"]
            nome = entry["team"]["name"]
            classif[pos] = nome
        return classif
    except:
        return {}

@st.cache_data(ttl=3600, show_spinner="Buscando partidas...")
def obter_partidas_time(liga_nome, temporada, time):
    """Retorna lista de jogos do time na liga/temporada."""
    ligas = listar_ligas()
    liga_id = ligas.get(liga_nome)
    if not liga_id:
        return []
    # Obter ID do time
    classif = obter_classificacao(liga_nome, temporada)
    time_id = None
    for nome in classif.values():
        if time.lower() == nome.lower():
            try:
                resp = requests.get(f"{BASE_URL}/teams?league={liga_id}&season={temporada}&search={nome}", headers=HEADERS)
                resp.raise_for_status()
                data = resp.json()
                if data.get("response"):
                    time_id = data["response"][0]["team"]["id"]
                    break
            except:
                continue
    if not time_id:
        return []

    # Buscar partidas
    try:
        resp = requests.get(f"{BASE_URL}/fixtures?team={time_id}&season={temporada}", headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
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
        return jogos
    except:
        return []

@st.cache_data(ttl=3600, show_spinner="Buscando estatísticas...")
def obter_stats_time(liga_nome, temporada, time):
    """Retorna estatísticas agregadas do time (médias)."""
    ligas = listar_ligas()
    liga_id = ligas.get(liga_nome)
    if not liga_id:
        return {}
    classif = obter_classificacao(liga_nome, temporada)
    time_id = None
    for nome in classif.values():
        if time.lower() == nome.lower():
            try:
                resp = requests.get(f"{BASE_URL}/teams?league={liga_id}&season={temporada}&search={nome}", headers=HEADERS)
                resp.raise_for_status()
                data = resp.json()
                if data.get("response"):
                    time_id = data["response"][0]["team"]["id"]
                    break
            except:
                continue
    if not time_id:
        return {}
    try:
        resp = requests.get(f"{BASE_URL}/teams/statistics?team={time_id}&league={liga_id}&season={temporada}", headers=HEADERS)
        resp.raise_for_status()
        stats = resp.json()["response"]
        if not stats:
            return {}
        stats = stats[0]
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
        if "possession" in stats:
            dados['posse_media'] = float(stats["possession"].get("average", "0").replace('%', ''))
        if "total" in passes:
            dados['passes_certos_media'] = passes["total"].get("accurate", 0) / mp if mp > 0 else 0
        if "accuracy" in passes:
            dados['passes_certos_pct'] = int(passes["accuracy"].get("total", "0").replace('%', ''))
        if "total" in shots:
            dados['finalizacoes_tot_media'] = shots["total"].get("total", 0) / mp if mp > 0 else 0
        if "on" in shots:
            dados['finalizacoes_alvo_media'] = shots["on"].get("total", 0) / mp if mp > 0 else 0

        return {k: v for k, v in dados.items() if v is not None}
    except:
        return {}
