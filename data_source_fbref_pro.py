# data_source_fbref_pro.py — MyPredict 2.0 (proxy + fallback worldfootball)
import time, random, requests, pandas as pd
from io import StringIO
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup

CACHE_DIR = Path('cache/fbref_pro')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Proxies públicos (atualize periodicamente se necessário)
PROXY_LIST = [
    "http://50.168.163.176:8080",
    "http://154.65.39.8:8080",
    "http://103.149.162.194:8080",
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Mapeamento worldfootball (fallback)
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

# Mapeamento FBref (códigos) – tentado primeiro com proxy
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
        with open(arq, 'r', encoding='utf-8') as f: return json.load(f)
    return None

def _cache_escrever(chave, dados):
    with open(CACHE_DIR / f"{chave}.json", 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

def _baixar_fbref(url):
    for proxy in PROXY_LIST:
        try:
            time.sleep(random.uniform(2, 4))
            resp = requests.get(url, headers=HEADERS, proxies={"http": proxy, "https": proxy}, timeout=15)
            resp.raise_for_status()
            return resp.text
        except: continue
    time.sleep(random.uniform(4, 6))
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text

def _baixar_wf(url):
    time.sleep(random.uniform(2, 4))
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text

# ------------------------------------------------------------
# Função comum para extrair jogos do worldfootball
# ------------------------------------------------------------
def _extrair_jogos_wf(html_str, time):
    dfs = pd.read_html(StringIO(html_str), flavor='html.parser')
    jogos = []
    for df in dfs:
        if 'Home' not in df.columns or 'Away' not in df.columns: continue
        for _, row in df.iterrows():
            try:
                mandante = str(row['Home']).strip()
                visitante = str(row['Away']).strip()
                gols_str = str(row.get('Result', '')).strip()
                if ':' not in gols_str: continue
                gols_casa, gols_fora = map(int, gols_str.split(':'))
                ht_str = str(row.get('HT', '')).strip()
                ht_placar = None
                if ':' in ht_str:
                    ht_casa, ht_fora = map(int, ht_str.split(':'))
                    ht_placar = [ht_casa, ht_fora]
                data_str = str(row.get('Date', ''))
                try: data = datetime.strptime(data_str, '%d/%m/%Y')
                except: data = datetime.now()
                if time.lower() not in mandante.lower() and time.lower() not in visitante.lower(): continue
                if time.lower() in mandante.lower():
                    adversario = visitante; mandante_flag = True
                    gols_pro, gols_contra = gols_casa, gols_fora
                    ht = ht_placar
                else:
                    adversario = mandante; mandante_flag = False
                    gols_pro, gols_contra = gols_fora, gols_casa
                    ht = [ht_placar[1], ht_placar[0]] if ht_placar else None
                resultado = 'V' if gols_pro > gols_contra else ('E' if gols_pro == gols_contra else 'D')
                jogos.append({
                    'data': data, 'resultado': resultado, 'adversario': adversario,
                    'mandante': mandante_flag, 'gols_pro': gols_pro, 'gols_contra': gols_contra,
                    'ht_placar': ht,
                    'xg': None, 'xga': None, 'finalizacoes_tot': None, 'finalizacoes_alvo': None,
                    'posse': None, 'passes_certos': None, 'passes_totais': None,
                    'passes_chave': None, 'assistencias': None, 'desarmes': None,
                    'interceptacoes': None, 'escanteios': None, 'escanteios_sofridos': None,
                    'gols_ultimos_15': None,
                })
            except: continue
    return sorted(jogos, key=lambda x: x['data'])

# ------------------------------------------------------------
# Função comum para extrair jogos do FBref
# ------------------------------------------------------------
def _extrair_jogos_fbref(df, time):
    jogos = []
    for _, row in df.iterrows():
        try:
            mandante = str(row['Home']).strip() if 'Home' in row else None
            visitante = str(row['Away']).strip() if 'Away' in row else None
            if not mandante or not visitante: continue
            gols_casa = row.get('GF'); gols_fora = row.get('GA')
            if pd.isna(gols_casa) or pd.isna(gols_fora): continue
            gols_casa, gols_fora = int(gols_casa), int(gols_fora)
            ht_str = ''
            for col in ['HT', 'Half-time', 'Ht']:
                if col in row and isinstance(row[col], str):
                    ht_str = row[col]; break
            ht_placar = None
            if ht_str and '–' in ht_str:
                try:
                    ht_casa, ht_fora = map(int, ht_str.split('–'))
                    ht_placar = [ht_casa, ht_fora] if time.lower() == mandante.lower() else [ht_fora, ht_casa]
                except: pass
            data_str = str(row.get('Date', ''))
            try: data = datetime.strptime(data_str, '%Y-%m-%d')
            except: data = datetime.now()
            if time.lower() == mandante.lower():
                adversario = visitante; mandante_flag = True
                gols_pro, gols_contra = gols_casa, gols_fora
            elif time.lower() == visitante.lower():
                adversario = mandante; mandante_flag = False
                gols_pro, gols_contra = gols_fora, gols_casa
            else: continue
            resultado = 'V' if gols_pro > gols_contra else ('E' if gols_pro == gols_contra else 'D')
            jogos.append({
                'data': data, 'resultado': resultado, 'adversario': adversario,
                'mandante': mandante_flag, 'gols_pro': gols_pro, 'gols_contra': gols_contra,
                'ht_placar': ht_placar,
                'xg': None, 'xga': None, 'finalizacoes_tot': None, 'finalizacoes_alvo': None,
                'posse': None, 'passes_certos': None, 'passes_totais': None,
                'passes_chave': None, 'assistencias': None, 'desarmes': None,
                'interceptacoes': None, 'escanteios': None, 'escanteios_sofridos': None,
                'gols_ultimos_15': None,
            })
        except: continue
    return sorted(jogos, key=lambda x: x['data'])

# ------------------------------------------------------------
# Funções de classificação
# ------------------------------------------------------------
def obter_classificacao(liga_nome, temporada):
    # 1. Tenta FBref com proxy
    info_fb = FBREF_LEAGUES.get(liga_nome)
    if info_fb:
        cod = info_fb["cod"]
        chave = f"class_fb_{cod}_{temporada}"
        cached = _cache_ler(chave)
        if cached: return {int(k): v for k, v in cached.items()}
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
        except: pass

    # 2. Fallback worldfootball
    slug = WF_LEAGUES.get(liga_nome)
    if not slug: raise ValueError(f"Liga '{liga_nome}' não suportada.")
    chave = f"class_wf_{slug}_{temporada}"
    cached = _cache_ler(chave)
    if cached: return {int(k): v for k, v in cached.items()}
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
    if not classif: raise ValueError('Classificação não encontrada no worldfootball.')
    _cache_escrever(chave, classif)
    return classif

# ------------------------------------------------------------
# Funções de partidas
# ------------------------------------------------------------
def obter_partidas_time(liga_nome, temporada, time):
    # 1. Tenta FBref com proxy
    info_fb = FBREF_LEAGUES.get(liga_nome)
    if info_fb:
        cod = info_fb["cod"]
        chave = f"partidas_fb_{cod}_{temporada}_{time}"
        cached = _cache_ler(chave)
        if cached: return cached
        try:
            url = f"https://fbref.com/en/comps/{cod}/{temporada}/schedule/{temporada}-{cod}-Scores-and-Fixtures"
            html_str = _baixar_fbref(url)
            soup = BeautifulSoup(html_str, 'html.parser')
            table = soup.find('table', class_='stats_table')
            if table:
                df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ['_'.join(col).strip() if 'Unnamed' not in col[0] else col[1] for col in df.columns]
                jogos = _extrair_jogos_fbref(df, time)
                if jogos:
                    _cache_escrever(chave, jogos)
                    return jogos
        except: pass

    # 2. Fallback worldfootball
    slug = WF_LEAGUES.get(liga_nome)
    if not slug: raise ValueError(f"Liga '{liga_nome}' não suportada.")
    chave = f"partidas_wf_{slug}_{temporada}_{time}"
    cached = _cache_ler(chave)
    if cached: return cached
    url = f"https://www.worldfootball.net/schedule/{slug}-{temporada}/"
    html_str = _baixar_wf(url)
    jogos = _extrair_jogos_wf(html_str, time)
    if jogos:
        _cache_escrever(chave, jogos)
        return jogos
    raise ValueError('Nenhuma partida encontrada.')

def obter_stats_time(liga_nome, temporada, time):
    return {}
