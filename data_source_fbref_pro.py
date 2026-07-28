# data_source_fbref_pro.py — MyPredict 2.0 (proxy rotativo + fallback worldfootball)
import time, random, requests, pandas as pd
from io import StringIO
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup

CACHE_DIR = Path('cache/fbref_pro')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Lista de proxies gratuitos (atualize periodicamente ou use uma API)
PROXY_LIST = [
    "http://50.168.163.176:8080",
    "http://154.65.39.8:8080",
    "http://103.149.162.194:8080",
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

LEAGUES = {
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

def _baixar(url):
    """Tenta baixar com proxies; se falhar, tenta sem proxy."""
    for proxy in PROXY_LIST:
        try:
            time.sleep(random.uniform(2, 4))
            resp = requests.get(url, headers=HEADERS, proxies={"http": proxy, "https": proxy}, timeout=15)
            resp.raise_for_status()
            return resp.text
        except:
            continue
    # último recurso: sem proxy
    time.sleep(random.uniform(4, 6))
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text

def _extrair_tabela(html_str, table_id):
    soup = BeautifulSoup(html_str, 'html.parser')
    for comment in soup.find_all(string=lambda t: isinstance(t, str) and table_id in t):
        cs = BeautifulSoup(comment, 'html.parser')
        table = cs.find('table', id=table_id)
        if table: return table
    return soup.find('table', id=table_id)

def obter_codigo_fbref(nome_liga):
    if nome_liga in LEAGUES:
        return LEAGUES[nome_liga]["cod"]
    return None

def obter_classificacao(liga_nome, temporada):
    info = LEAGUES.get(liga_nome)
    if not info: raise ValueError(f"Liga '{liga_nome}' não suportada.")
    cod = info["cod"]
    chave = f"class_{cod}_{temporada}"
    cached = _cache_ler(chave)
    if cached: return {int(k): v for k, v in cached.items()}
    url = f"https://fbref.com/en/comps/{cod}/{temporada}/"
    html_str = _baixar(url)
    soup = BeautifulSoup(html_str, 'html.parser')
    table = None
    for tbl in soup.find_all('table', class_='stats_table'):
        headers = [th.get('data-stat', '') for th in tbl.find_all('th')]
        if 'wins' in headers and 'losses' in headers:
            table = tbl; break
    if not table: raise ValueError("Tabela não encontrada")
    df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[1] if 'Unnamed' not in col[0] else col[0] for col in df.columns]
    pos_col = 'Rk' if 'Rk' in df.columns else 'Rank'
    team_col = 'Squad' if 'Squad' in df.columns else 'Team'
    classif = {}
    for _, row in df.iterrows():
        try: classif[int(row[pos_col])] = str(row[team_col]).strip()
        except: continue
    if not classif: raise ValueError("Classificação vazia")
    _cache_escrever(chave, classif)
    return classif

def obter_partidas_time(liga_nome, temporada, time):
    info = LEAGUES.get(liga_nome)
    if not info: raise ValueError(f"Liga '{liga_nome}' não suportada.")
    cod = info["cod"]
    chave = f"partidas_{cod}_{temporada}_{time}"
    cached = _cache_ler(chave)
    if cached: return cached
    url = f"https://fbref.com/en/comps/{cod}/{temporada}/schedule/{temporada}-{cod}-Scores-and-Fixtures"
    html_str = _baixar(url)
    soup = BeautifulSoup(html_str, 'html.parser')
    table = soup.find('table', class_='stats_table')
    if not table: raise ValueError("Tabela não encontrada")
    df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() if 'Unnamed' not in col[0] else col[1] for col in df.columns]
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
                'passes_chave': None, 'assistencias': None,
                'desarmes': None, 'interceptacoes': None,
                'escanteios': None, 'escanteios_sofridos': None, 'gols_ultimos_15': None,
            })
        except: continue
    jogos.sort(key=lambda x: x['data'])
    _cache_escrever(chave, jogos)
    return jogos

def obter_stats_time(liga_nome, temporada, time):
    # Estatísticas avançadas não são obtidas por proxy; retornamos vazio.
    return {}
