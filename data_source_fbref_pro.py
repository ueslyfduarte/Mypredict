# data_source_fbref_pro.py — MyPredict 2.0 (proxy rotativo + fallback worldfootball)
import time, random, requests, pandas as pd
from io import StringIO
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup

CACHE_DIR = Path('cache/fbref_pro')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Lista de proxies públicos (atualize periodicamente)
PROXY_LIST = [
    "http://50.168.163.176:8080",
    "http://154.65.39.8:8080",
    "http://103.149.162.194:8080",
    "http://20.111.54.16:8123",
    "http://47.88.21.226:80",
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Mapeamento de nomes amigáveis para slugs do worldfootball (fallback)
WF_LEAGUES = {
    "Brasileirão": "bra-serie-a",
    "Premier League": "eng-premier-league",
    "La Liga": "esp-primera-division",
    "Bundesliga": "ger-bundesliga",
    "Serie A": "ita-serie-a",
    "Ligue 1": "fra-ligue-1",
    "Eredivisie": "ned-eredivisie",
    "Primeira Liga": "por-primeira-liga",
    "MLS": "usa-major-league-soccer",
    "Championship": "eng-championship",
    "Série B": "bra-serie-b",
}

# Mapeamento FBref (códigos) – usado se proxy funcionar
FBREF_LEAGUES = {
    "Brasileirão":          {"cod": 24, "slug": "Serie-A"},
    "Premier League":       {"cod": 9,  "slug": "Premier-League"},
    "La Liga":              {"cod": 12, "slug": "La-Liga"},
    "Bundesliga":           {"cod": 20, "slug": "Bundesliga"},
    "Serie A":              {"cod": 11, "slug": "Serie-A"},
    "Ligue 1":              {"cod": 13, "slug": "Ligue-1"},
    "Eredivisie":           {"cod": 23, "slug": "Eredivisie"},
    "Primeira Liga":        {"cod": 32, "slug": "Primeira-Liga"},
    "MLS":                  {"cod": 22, "slug": "Major-League-Soccer"},
    "Championship":         {"cod": 10, "slug": "Championship"},
    "Série B":              {"cod": 38, "slug": "Serie-B"},
}

def _cache_ler(chave):
    arq = CACHE_DIR / f"{chave}.json"
    if arq.exists():
        with open(arq, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def _cache_escrever(chave, dados):
    with open(CACHE_DIR / f"{chave}.json", 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

def _baixar_fbref(url):
    """Tenta baixar a URL com proxies; se falhar, tenta sem proxy."""
    for proxy in PROXY_LIST:
        try:
            time.sleep(random.uniform(2, 4))
            resp = requests.get(url, headers=HEADERS,
                                proxies={"http": proxy, "https": proxy}, timeout=15)
            resp.raise_for_status()
            return resp.text
        except Exception:
            continue
    # último recurso: sem proxy
    time.sleep(random.uniform(4, 6))
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text

def _baixar_wf(url):
    """Baixa do worldfootball (mais tolerante)."""
    time.sleep(random.uniform(2, 4))
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text

# ------------------------------------------------------------
# Funções de classificação (tentam FBref, fallback worldfootball)
# ------------------------------------------------------------
def obter_classificacao(liga_nome, temporada):
    # 1. Tenta FBref com proxy
    info_fb = FBREF_LEAGUES.get(liga_nome)
    if info_fb:
        cod = info_fb["cod"]
        chave = f"class_fb_{cod}_{temporada}"
        cached = _cache_ler(chave)
        if cached:
            return {int(k): v for k, v in cached.items()}
        try:
            url = f"https://fbref.com/en/comps/{cod}/{temporada}/"
            html_str = _baixar_fbref(url)
            soup = BeautifulSoup(html_str, 'html.parser')
            table = None
            for tbl in soup.find_all('table', class_='stats_table'):
                headers = [th.get('data-stat', '') for th in tbl.find_all('th')]
                if 'wins' in headers and 'losses' in headers:
                    table = tbl; break
            if table:
                df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[1] if 'Unnamed' not in col[0] else col[0] for col in df.columns]
                pos_col = 'Rk' if 'Rk' in df.columns else 'Rank'
                team_col = 'Squad' if 'Squad' in df.columns else 'Team'
                classif = {}
                for _, row in df.iterrows():
                    try: classif[int(row[pos_col])] = str(row[team_col]).strip()
                    except: continue
                if classif:
                    _cache_escrever(chave, classif)
                    return classif
        except Exception:
            pass  # fallback para worldfootball

    # 2. Fallback worldfootball
    slug = WF_LEAGUES.get(liga_nome)
    if not slug:
        raise ValueError(f"Liga '{liga_nome}' não suportada.")
    chave = f"class_wf_{slug}_{temporada}"
    cached = _cache_ler(chave)
    if cached:
        return {int(k): v for k, v in cached.items()}
    url = f"https://www.worldfootball.net/table/{slug}-{temporada}/"
    html_str = _baixar_wf(url)
    dfs = pd.read_html(StringIO(html_str), flavor='html.parser')
    classif = {}
    for df in dfs:
        if 'Team' in df.columns and '#' in df.columns:
            for _, row in df.iterrows():
                try:
                    pos = int(row['#'])
                    time = str(row['Team']).strip()
                    classif[pos] = time
                except: continue
            if classif: break
    if not classif:
        raise ValueError('Classificação não encontrada no worldfootball.')
    _cache_escrever(chave, classif)
    return classif

def obter_partidas_time(liga_nome, temporada, time):
    # 1. Tenta FBref com proxy
    info_fb = FBREF_LEAGUES.get(liga_nome)
    if info_fb:
        cod = info_fb["cod"]
        chave = f"partidas_fb_{cod}_{temporada}_{time}"
        cached = _cache_ler(chave)
        if cached:
            return cached
        try:
            url = f"https://fbref.com/en/comps/{cod}/{temporada}/schedule/{temporada}-{cod}-Scores-and-Fixtures"
            html_str = _baixar_fbref(url)
            soup = BeautifulSoup(html_str, 'html.parser')
            table = soup.find('table', class_='stats_table')
            if table:
                df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ['_'.join(col).strip() if 'Unnamed' not in col[0] else col[1] for col in df.columns]
                jogos = []
                for _, row in df.iterrows():
                    # ... (mesmo código de extração de partidas do FBref, omitido por brevidade)
                    pass  # Substitua pelo bloco completo de extração do FBref que já usamos antes
                if jogos:
                    _cache_escrever(chave, jogos)
                    return jogos
        except Exception:
            pass  # fallback para worldfootball

    # 2. Fallback worldfootball
    slug = WF_LEAGUES.get(liga_nome)
    if not slug:
        raise ValueError(f"Liga '{liga_nome}' não suportada.")
    chave = f"partidas_wf_{slug}_{temporada}_{time}"
    cached = _cache_ler(chave)
    if cached:
        return cached
    url = f"https://www.worldfootball.net/schedule/{slug}-{temporada}/"
    html_str = _baixar_wf(url)
    dfs = pd.read_html(StringIO(html_str), flavor='html.parser')
    jogos = []
    # ... (código de extração worldfootball, igual ao anterior)
    # (substitua pelo bloco completo de worldfootball)
    if jogos:
        _cache_escrever(chave, jogos)
        return jogos
    raise ValueError('Nenhuma partida encontrada.')

def obter_stats_time(liga_nome, temporada, time):
    # Apenas retorna vazio por enquanto; OVRall se adapta
    return {}
