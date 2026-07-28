# data_source_fbref_selenium.py — MyPredict 2.0 (Selenium profissional)
import time, random, pandas as pd
from io import StringIO
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

CACHE_DIR = Path('cache/fbref_selenium')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento de ligas (nome → código FBref)
LEAGUES = {
    "Premier League":       {"cod": 9,  "slug": "Premier-League"},
    "La Liga":              {"cod": 12, "slug": "La-Liga"},
    "Bundesliga":           {"cod": 20, "slug": "Bundesliga"},
    "Serie A":              {"cod": 11, "slug": "Serie-A"},
    "Ligue 1":              {"cod": 13, "slug": "Ligue-1"},
    "Brasileirão":          {"cod": 24, "slug": "Serie-A"},
    "Eredivisie":           {"cod": 23, "slug": "Eredivisie"},
    "Primeira Liga":        {"cod": 32, "slug": "Primeira-Liga"},
    "MLS":                  {"cod": 22, "slug": "Major-League-Soccer"},
    "Championship":         {"cod": 10, "slug": "Championship"},
    "Série B":              {"cod": 38, "slug": "Serie-B"},
}

def _init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def _baixar_com_selenium(url):
    driver = _init_driver()
    try:
        driver.get(url)
        time.sleep(random.uniform(5, 8))
        return driver.page_source
    finally:
        driver.quit()

def _cache_ler(chave):
    arq = CACHE_DIR / f"{chave}.json"
    if arq.exists():
        with open(arq, 'r', encoding='utf-8') as f: return json.load(f)
    return None

def _cache_escrever(chave, dados):
    with open(CACHE_DIR / f"{chave}.json", 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

def obter_classificacao(liga_nome, temporada):
    info = LEAGUES.get(liga_nome)
    if not info: raise ValueError(f"Liga '{liga_nome}' não suportada.")
    cod = info["cod"]
    chave = f"class_{cod}_{temporada}"
    cached = _cache_ler(chave)
    if cached: return {int(k): v for k, v in cached.items()}
    url = f"https://fbref.com/en/comps/{cod}/{temporada}/"
    html_str = _baixar_com_selenium(url)
    soup = BeautifulSoup(html_str, 'html.parser')
    table = None
    for tbl in soup.find_all('table', class_='stats_table'):
        headers = [th.get('data-stat', '') for th in tbl.find_all('th')]
        if 'wins' in headers and 'losses' in headers:
            table = tbl; break
    if not table: raise ValueError("Tabela não encontrada")
    df = pd.read_html(StringIO(str(table)), flavor='lxml')[0]
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
    html_str = _baixar_com_selenium(url)
    soup = BeautifulSoup(html_str, 'html.parser')
    table = soup.find('table', class_='stats_table')
    if not table: raise ValueError("Tabela não encontrada")
    df = pd.read_html(StringIO(str(table)), flavor='lxml')[0]
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
                'passes_chave': None, 'assistencias': None, 'desarmes': None,
                'interceptacoes': None, 'escanteios': None, 'escanteios_sofridos': None,
                'gols_ultimos_15': None,
            })
        except: continue
    jogos.sort(key=lambda x: x['data'])
    _cache_escrever(chave, jogos)
    return jogos

def obter_stats_time(liga_nome, temporada, time):
    info = LEAGUES.get(liga_nome)
    if not info: return {}
    cod, slug = info["cod"], info["slug"]
    chave = f"stats_{cod}_{temporada}_{time}"
    cached = _cache_ler(chave)
    if cached: return cached
    url = f"https://fbref.com/en/comps/{cod}/{temporada}/stats/{temporada}-{slug}-Stats"
    html_str = _baixar_com_selenium(url)
    soup = BeautifulSoup(html_str, 'html.parser')
    table = soup.find('table', id='stats_standard')
    if not table:
        for comment in soup.find_all(string=lambda t: isinstance(t, str) and 'stats_standard' in t):
            cs = BeautifulSoup(comment, 'html.parser')
            table = cs.find('table', id='stats_standard')
            if table: break
    if not table: return {}
    df = pd.read_html(StringIO(str(table)), flavor='lxml')[0]
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() if 'Unnamed' not in col[0] else col[1] for col in df.columns]
    df = df.rename(columns={'Squad': 'team'})
    df = df[~df['team'].str.contains('Squad')]
    df = df.set_index('team')
    match = None
    for t in df.index:
        if time.lower() in t.lower(): match = t; break
    if not match: return {}
    row = df.loc[match]
    mp = row.get('MP', 1)
    dados = {}
    if 'Gls' in row: dados['gols_media'] = row['Gls'] / mp
    if 'GA' in row: dados['gols_sofridos_media'] = row['GA'] / mp
    if 'xG' in row: dados['xg_media'] = row['xG'] / mp
    if 'xGA' in row: dados['xga_media'] = row['xGA'] / mp
    if 'Poss' in row: dados['posse_media'] = row['Poss']
    if 'Cmp%' in row: dados['passes_certos_pct'] = row['Cmp%']
    if 'KP' in row: dados['passes_chave_media'] = row['KP'] / mp
    if 'Ast' in row: dados['assistencias_media'] = row['Ast'] / mp
    if 'Tkl' in row: dados['desarmes_media'] = row['Tkl'] / mp
    if 'Int' in row: dados['interceptacoes_media'] = row['Int'] / mp
    dados['escanteios_media'] = None
    dados['escanteios_sofridos_media'] = None
    resultado = {k: v for k, v in dados.items() if v is not None}
    _cache_escrever(chave, resultado)
    return resultado
