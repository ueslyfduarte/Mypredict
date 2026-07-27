import time
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
import json
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
REQUEST_DELAY = 4
CACHE_DIR = Path('cache/fbref_stats')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_ler(chave):
    arq = CACHE_DIR / f"{chave}.json"
    if arq.exists():
        with open(arq, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def _cache_escrever(chave, dados):
    with open(CACHE_DIR / f"{chave}.json", 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2, default=str)

def _get(url):
    headers = {'User-Agent': USER_AGENT}
    time.sleep(REQUEST_DELAY)
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def obter_codigo_fbref(nome_liga):
    cache_file = CACHE_DIR / 'fbref_codes.json'
    codes = {}
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            codes = json.load(f)
    else:
        url = 'https://fbref.com/en/comps/'
        html_str = _get(url)
        soup = BeautifulSoup(html_str, 'html.parser')
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    link = cells[0].find('a')
                    if link:
                        nome = link.get_text(strip=True)
                        href = link.get('href', '')
                        codigo = href.split('/')[-1]
                        codes[nome.lower()] = codigo
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(codes, f, ensure_ascii=False, indent=2)

    nome_lower = nome_liga.lower()
    if nome_lower in codes:
        return codes[nome_lower]
    for nome, codigo in codes.items():
        if nome_lower in nome or nome in nome_lower:
            return codigo
    return None

def obter_stats_time(liga, temporada, time):
    chave = f'stats_{liga}_{temporada}_{time}'
    cached = _cache_ler(chave)
    if cached:
        return cached

    codigo = obter_codigo_fbref(liga)
    if not codigo:
        raise ValueError(f"Liga '{liga}' não encontrada no FBref.")
    url = f'https://fbref.com/en/comps/{codigo}/{temporada}/stats/{temporada}-{codigo}-Stats'
    html_str = _get(url)
    soup = BeautifulSoup(html_str, 'html.parser')
    stats_table = None
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and 'div_stats_standard' in text):
        comment_soup = BeautifulSoup(comment, 'html.parser')
        table = comment_soup.find('table', id=lambda x: x and 'stats_standard' in x)
        if table:
            stats_table = table
            break
    if not stats_table:
        table = soup.find('table', id=lambda x: x and 'stats_standard' in x)
        if table:
            stats_table = table
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
