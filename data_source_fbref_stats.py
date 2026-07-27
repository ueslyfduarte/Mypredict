# data_source_fbref_stats.py — MyPredict 2.0 (versão final funcional)
import time
import random
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}
CACHE_DIR = Path('cache/fbref_stats')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

FBREF_CODES = {
    "brasileirão": 24,
    "campeonato brasileiro série a": 24,
    "premier league": 9,
    "la liga": 12,
    "bundesliga": 20,
    "serie a": 11,
    "ligue 1": 13,
    "eredivisie": 23,
    "primeira liga": 32,
    "mls": 22,
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

def _criar_sessao():
    s = requests.Session()
    s.headers.update(HEADERS)
    return s

def _get(url):
    sessao = _criar_sessao()
    time.sleep(random.uniform(4, 7))
    resp = sessao.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text

def _extrair_tabela_por_id(html_str, table_id):
    soup = BeautifulSoup(html_str, 'html.parser')
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and table_id in text):
        comment_soup = BeautifulSoup(comment, 'html.parser')
        table = comment_soup.find('table', id=table_id)
        if table:
            return table
    table = soup.find('table', id=table_id)
    return table

# ------------------------------------------------------------
# 1. CÓDIGO DA LIGA
# ------------------------------------------------------------
def obter_codigo_fbref(nome_liga):
    nome_lower = nome_liga.lower().strip()
    if nome_lower in FBREF_CODES:
        return FBREF_CODES[nome_lower]
    cache_file = CACHE_DIR / 'fbref_codes.json'
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            codes = json.load(f)
        if nome_lower in codes:
            return codes[nome_lower]
    try:
        url = 'https://fbref.com/en/comps/'
        html_str = _get(url)
        soup = BeautifulSoup(html_str, 'html.parser')
        codes = {}
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    link = cells[0].find('a')
                    if link:
                        nome = link.get_text(strip=True).lower()
                        codigo = int(link['href'].split('/')[-1])
                        codes[nome] = codigo
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(codes, f, ensure_ascii=False, indent=2)
        return codes.get(nome_lower)
    except:
        return None

# ------------------------------------------------------------
# 2. CLASSIFICAÇÃO
# ------------------------------------------------------------
def obter_classificacao(liga_codigo, temporada):
    chave = f'class_{liga_codigo}_{temporada}'
    cached = _cache_ler(chave)
    if cached:
        return {int(k): v for k, v in cached.items()}

    url = f'https://fbref.com/en/comps/{liga_codigo}/{temporada}/'
    html_str = _get(url)
    soup = BeautifulSoup(html_str, 'html.parser')

    table = None
    for tbl in soup.find_all('table', class_='stats_table'):
        headers = [th.get('data-stat', '') for th in tbl.find_all('th')]
        if 'wins' in headers and 'losses' in headers:
            table = tbl
            break
    if not table:
        for tbl in soup.find_all('table'):
            if tbl.find('th', {'data-stat': 'rank'}):
                table = tbl
                break
    if not table:
        raise ValueError(f'Classificação não encontrada para código {liga_codigo} temporada {temporada}')

    df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[1] if 'Unnamed' not in col[0] else col[0] for col in df.columns]

    pos_col = 'Rk' if 'Rk' in df.columns else 'Rank'
    team_col = 'Squad' if 'Squad' in df.columns else 'Team'
    classif = {}
    for _, row in df.iterrows():
        try:
            pos = int(row[pos_col])
            nome = str(row[team_col]).strip()
            classif[pos] = nome
        except:
            continue
    if not classif:
        raise ValueError('Não foi possível extrair a classificação.')
    _cache_escrever(chave, classif)
    return classif

# ------------------------------------------------------------
# 3. PARTIDAS DE UM TIME (com HT)
# ------------------------------------------------------------
def obter_partidas_time(liga_codigo, temporada, time):
    chave = f'partidas_{liga_codigo}_{temporada}_{time}'
    cached = _cache_ler(chave)
    if cached:
        return cached

    url = f'https://fbref.com/en/comps/{liga_codigo}/{temporada}/schedule/{temporada}-{liga_codigo}-Scores-and-Fixtures'
    html_str = _get(url)
    soup = BeautifulSoup(html_str, 'html.parser')

    table = soup.find('table', class_='stats_table')
    if not table:
        raise ValueError(f'Tabela de partidas não encontrada em {url}')

    df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() if 'Unnamed' not in col[0] else col[1] for col in df.columns]

    jogos = []
    for _, row in df.iterrows():
        try:
            mandante = str(row['Home']).strip() if 'Home' in row else None
            visitante = str(row['Away']).strip() if 'Away' in row else None
            if not mandante or not visitante:
                continue

            gols_casa = row.get('GF')
            gols_fora = row.get('GA')
            if pd.isna(gols_casa) or pd.isna(gols_fora):
                continue
            gols_casa = int(gols_casa)
            gols_fora = int(gols_fora)

            ht_str = ''
            for col in ['HT', 'Half-time', 'Ht']:
                if col in row and isinstance(row[col], str):
                    ht_str = row[col]
                    break
            ht_placar = None
            if ht_str and '–' in ht_str:
                try:
                    ht_casa, ht_fora = map(int, ht_str.split('–'))
                    if time.lower() == mandante.lower():
                        ht_placar = [ht_casa, ht_fora]
                    else:
                        ht_placar = [ht_fora, ht_casa]
                except:
                    pass

            data_str = str(row.get('Date', ''))
            try:
                data = datetime.strptime(data_str, '%Y-%m-%d')
            except:
                data = datetime.now()

            if time.lower() == mandante.lower():
                adversario = visitante
                mandante_flag = True
                gols_pro = gols_casa
                gols_contra = gols_fora
                ht = ht_placar if ht_placar else None
            elif time.lower() == visitante.lower():
                adversario = mandante
                mandante_flag = False
                gols_pro = gols_fora
                gols_contra = gols_casa
                ht = [ht_placar[1], ht_placar[0]] if ht_placar else None
            else:
                continue

            resultado = 'V' if gols_pro > gols_contra else ('E' if gols_pro == gols_contra else 'D')

            jogos.append({
                'data': data,
                'resultado': resultado,
                'adversario': adversario,
                'mandante': mandante_flag,
                'gols_pro': gols_pro,
                'gols_contra': gols_contra,
                'ht_placar': ht,
                'xg': None, 'xga': None,
                'finalizacoes_tot': None, 'finalizacoes_alvo': None,
                'posse': None, 'passes_certos': None, 'passes_totais': None,
                'passes_chave': None, 'assistencias': None,
                'desarmes': None, 'interceptacoes': None,
                'escanteios': None, 'escanteios_sofridos': None,
                'gols_ultimos_15': None,
            })
        except:
            continue

    jogos.sort(key=lambda x: x['data'])
    _cache_escrever(chave, jogos)
    return jogos

# ------------------------------------------------------------
# 4. ESTATÍSTICAS AGREGADAS (OVRall)
# ------------------------------------------------------------
def obter_stats_time(liga, temporada, time):
    chave = f'stats_{liga}_{temporada}_{time}'
    cached = _cache_ler(chave)
    if cached:
        return cached

    codigo = obter_codigo_fbref(liga) if isinstance(liga, str) else liga
    if not codigo:
        raise ValueError(f"Liga '{liga}' não encontrada.")
    url = f'https://fbref.com/en/comps/{codigo}/{temporada}/stats/{temporada}-{codigo}-Stats'
    html_str = _get(url)
    stats_table = _extrair_tabela_por_id(html_str, 'stats_standard')
    if not stats_table:
        raise ValueError(f"Tabela de estatísticas não encontrada para {liga} {temporada}")

    df = pd.read_html(StringIO(str(stats_table)), flavor='html.parser')[0]
    df.columns = ['_'.join(col).strip() if 'Unnamed' not in col[0] else col[1] for col in df.columns]
    df = df.rename(columns={'Squad': 'team'})
    df = df[~df['team'].str.contains('Squad')]
    df = df.set_index('team')

    match = None
    for t in df.index:
        if time.lower() in t.lower():
            match = t
            break
    if not match:
        raise ValueError(f"Time '{time}' não encontrado na tabela de stats do FBref.")

    row = df.loc[match]
    dados = {
        'gols_media': row.get('Gls_Per 90 Minutes') or row.get('Gls'),
        'gols_sofridos_media': row.get('GA_Per 90 Minutes') or row.get('GA'),
        'xg_media': row.get('xG_Per 90 Minutes') or row.get('xG'),
        'xga_media': row.get('xGA_Per 90 Minutes') or row.get('xGA'),
        'finalizacoes_tot_media': row.get('Sh_Per 90 Minutes') or row.get('Sh'),
        'finalizacoes_alvo_media': row.get('SoT_Per 90 Minutes') or row.get('SoT'),
        'posse_media': row.get('Poss_Per 90 Minutes') or row.get('Poss'),
        'passes_certos_pct': row.get('Cmp%'),
        'passes_chave_media': row.get('KP'),
        'assistencias_media': row.get('Ast_Per 90 Minutes') or row.get('Ast'),
        'desarmes_media': row.get('Tkl_Per 90 Minutes') or row.get('Tkl'),
        'interceptacoes_media': row.get('Int_Per 90 Minutes') or row.get('Int'),
        'escanteios_media': None,
        'escanteios_sofridos_media': None,
    }
    for k, v in dados.items():
        if v is not None and not isinstance(v, (int, float)):
            dados[k] = None

    _cache_escrever(chave, dados)
    return dados
