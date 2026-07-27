import time
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
REQUEST_DELAY = 3
CACHE_DIR = Path('cache/worldfootball')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

SLUG_CACHE_FILE = CACHE_DIR / 'slugs.json'

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

def obter_slug_liga(nome_liga):
    """Retorna o slug da liga no worldfootball.net a partir do nome."""
    slugs = {}
    if SLUG_CACHE_FILE.exists():
        with open(SLUG_CACHE_FILE, 'r', encoding='utf-8') as f:
            slugs = json.load(f)
    else:
        url = 'https://www.worldfootball.net/competitions/'
        html_str = _get(url)
        soup = BeautifulSoup(html_str, 'html.parser')
        for table in soup.find_all('table', class_='standard_tabelle'):
            for a in table.find_all('a', href=True):
                href = a['href']
                nome = a.get_text(strip=True)
                if not nome:
                    continue
                # Extrai slug base (sem temporada)
                slug_completo = href.strip('/').split('/')[0]
                slug_base = '-'.join([p for p in slug_completo.split('-') if not p.isdigit()])
                slugs[nome.lower()] = slug_base
        with open(SLUG_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(slugs, f, ensure_ascii=False, indent=2)

    nome_lower = nome_liga.lower()
    if nome_lower in slugs:
        return slugs[nome_lower]
    for nome, slug in slugs.items():
        if nome_lower in nome or nome in nome_lower:
            return slug
    return None

def obter_classificacao(liga_slug, temporada):
    chave = f'class_{liga_slug}_{temporada}'
    cached = _cache_ler(chave)
    if cached:
        return {int(k): v for k, v in cached.items()}
    url = f'https://www.worldfootball.net/table/{liga_slug}-{temporada}/'
    html_str = _get(url)
    dfs = pd.read_html(StringIO(html_str), flavor='html.parser')
    classif = {}
    for df in dfs:
        if 'Team' in df.columns and '#' in df.columns:
            for _, row in df.iterrows():
                try:
                    pos = int(row['#'])
                    time = str(row['Team']).strip()
                    classif[pos] = time
                except:
                    continue
            if classif:
                break
    if not classif:
        raise ValueError(f'Classificação não encontrada em {url}')
    _cache_escrever(chave, classif)
    return classif

def obter_partidas_time(liga_slug, temporada, time):
    chave = f'partidas_{liga_slug}_{temporada}_{time}'
    cached = _cache_ler(chave)
    if cached:
        return cached
    url = f'https://www.worldfootball.net/schedule/{liga_slug}-{temporada}/'
    html_str = _get(url)
    dfs = pd.read_html(StringIO(html_str), flavor='html.parser')
    jogos = []
    for df in dfs:
        if 'Home' not in df.columns or 'Away' not in df.columns:
            continue
        for _, row in df.iterrows():
            try:
                mandante = str(row['Home']).strip()
                visitante = str(row['Away']).strip()
                gols_str = str(row.get('Result', '')).strip()
                if ':' not in gols_str:
                    continue
                gols_casa, gols_fora = map(int, gols_str.split(':'))
                ht_str = str(row.get('HT', '')).strip()
                ht_placar = None
                if ':' in ht_str:
                    ht_casa, ht_fora = map(int, ht_str.split(':'))
                    ht_placar = [ht_casa, ht_fora]
                data_str = str(row.get('Date', ''))
                try:
                    data = datetime.strptime(data_str, '%d/%m/%Y')
                except:
                    data = datetime.now()

                if time.lower() not in mandante.lower() and time.lower() not in visitante.lower():
                    continue
                if time.lower() in mandante.lower():
                    adversario = visitante
                    mandante_flag = True
                    gols_pro = gols_casa
                    gols_contra = gols_fora
                    ht = ht_placar
                else:
                    adversario = mandante
                    mandante_flag = False
                    gols_pro = gols_fora
                    gols_contra = gols_casa
                    ht = [ht_placar[1], ht_placar[0]] if ht_placar else None

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
