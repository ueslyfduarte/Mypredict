# data_source_football_api.py — MyPredict 2.0 (corrigido)
import time
import requests
from pathlib import Path
import json
import os

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

LEAGUES = {
    "Brasileirão": "BSA",
    "Premier League": "PL",
    "La Liga": "PD",
    "Bundesliga": "BL1",
    "Serie A": "SA",
    "Ligue 1": "FL1",
    "Eredivisie": "DED",
    "Primeira Liga": "PPL",
    "MLS": "MLS1",
}

def _cache_ler(chave):
    arq = CACHE_DIR / f"{chave}.json"
    if arq.exists():
        with open(arq, 'r', encoding='utf-8') as f: return json.load(f)
    return None

def _cache_escrever(chave, dados):
    with open(CACHE_DIR / f"{chave}.json", 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

def _get(url):
    time.sleep(6)
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def obter_codigo_fbref(nome_liga):
    return LEAGUES.get(nome_liga, nome_liga)

def obter_classificacao(liga_nome, temporada):
    codigo = LEAGUES.get(liga_nome)
    if not codigo:
        raise ValueError(f"Liga '{liga_nome}' não suportada.")
    chave = f"class_{codigo}_{temporada}"
    cached = _cache_ler(chave)
    if cached:
        return {int(k): v for k, v in cached.items()}
    
    # A API espera o ano de início da temporada (ex.: 2023 para 2023/2024)
    for ano_tentativa in [temporada, temporada - 1]:
        url = f"{BASE_URL}/competitions/{codigo}/standings?season={ano_tentativa}"
        try:
            data = _get(url)
            standings = data['standings'][0]['table']
            classif = {}
            for entry in standings:
                pos = entry['position']
                nome = entry['team']['name']
                classif[pos] = nome
            _cache_escrever(chave, classif)
            return classif
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                continue
            raise
    raise ValueError(f"Não foi possível obter classificação para {liga_nome} {temporada}")

def obter_partidas_time(liga_nome, temporada, time):
    codigo = LEAGUES.get(liga_nome)
    if not codigo:
        raise ValueError(f"Liga '{liga_nome}' não suportada.")
    chave = f"partidas_{codigo}_{temporada}_{time}"
    cached = _cache_ler(chave)
    if cached:
        return cached
    
    for ano_tentativa in [temporada, temporada - 1]:
        url = f"{BASE_URL}/competitions/{codigo}/matches?season={ano_tentativa}"
        try:
            data = _get(url)
            break
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                continue
            raise
    else:
        raise ValueError(f"Não foi possível obter partidas para {liga_nome} {temporada}")
    
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
