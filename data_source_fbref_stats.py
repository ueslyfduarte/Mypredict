# data_source_fbref_stats.py — MyPredict 2.0
import time
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
import json
from lxml import html

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
    """
    Busca o código da competição no FBref (ex.: '24' para Brasileirão)
    a partir do nome da liga. Retorna None se não encontrar.
    """
    cache_file = CACHE_DIR / 'fbref_codes.json'
    codes = {}
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            codes = json.load(f)
    else:
        url = 'https://fbref.com/en/comps/'
        html_str = _get(url)
        tree = html.fromstring(html_str)
        for table in tree.xpath("//table[contains(@id, 'comps')]"):
            for row in table.xpath(".//tr"):
                cells = row.xpath("./td")
                if len(cells) >= 2:
                    link = cells[0].xpath("./a")
                    if link:
                        nome = link[0].text.strip()
                        href = link[0].get('href', '')
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
    tree = html.fromstring(html_str)

    # Procura tabela dentro de comentários (padrão FBref)
    stats_table = None
    for comment in tree.xpath("//comment()"):
        if 'div_stats_standard' in comment.text:
            inner_tree = html.fromstring(comment.text)
            stats_table = inner_tree.xpath("//table[contains(@id, 'stats_standard')]")
            if stats_table:
                stats_table = stats_table[0]
                break
    if stats_table is None:
        stats_table = tree.xpath("//table[contains(@id, 'stats_standard')]")
        if stats_table:
            stats_table = stats_table[0]
    if stats_table is None:
        raise ValueError(f"Tabela de estatísticas não encontrada para {liga} {temporada}")

    df = pd.read_html(StringIO(html.tostring(stats_table, encoding='unicode')), flavor='lxml')[0]
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
