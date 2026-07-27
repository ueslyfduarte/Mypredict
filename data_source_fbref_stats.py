# data_source_fbref_stats.py — MyPredict 2.0
# Fonte de dados: FBref (classificação, partidas com HT, estatísticas agregadas)

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

# Mapeamento estático de nomes de liga → código FBref (fallback)
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
    """Extrai tabela do HTML, procurando dentro de comentários também."""
    soup = BeautifulSoup(html_str, 'html.parser')
    # Tenta primeiro dentro de comentários
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and table_id in text):
        comment_soup = BeautifulSoup(comment, 'html.parser')
        table = comment_soup.find('table', id=table_id)
        if table:
            return table
    # Fallback direto
    table = soup.find('table', id=table_id)
    return table

# ------------------------------------------------------------
# 1. CÓDIGO DA LIGA
# ------------------------------------------------------------
def obter_codigo_fbref(nome_liga):
    """Retorna código numérico da liga no FBref."""
    nome_lower = nome_liga.lower().strip()
    if nome_lower in FBREF_CODES:
        return FBREF_CODES[nome_lower]
    # Busca automática
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
    """Retorna {posicao: nome_time} da tabela oficial da liga."""
    chave = f'class_{liga_codigo}_{temporada}'
    cached = _cache_ler(chave)
    if cached:
        return {int(k): v for k, v in cached.items()}

    # A classificação está na página inicial da competição, ex.:
    url = f'https://fbref.com/en/comps/{liga_codigo}/{temporada}/'
    html_str = _get(url)
    soup = BeautifulSoup(html_str, 'html.parser')

    # Procura a tabela de classificação (id varia, ex: 'results2024-20251-overall')
    # Vamos buscar pela classe "stats_table" e que contenha coluna "W" (vitórias)
    table = None
    for tbl in soup.find_all('table', class_='stats_table'):
        # Verifica se tem cabeçalho típico de classificação
        if tbl.find('th', {'data-stat': 'wins'}):
            table = tbl
            break
    if not table:
        # Último recurso: tenta usar a tabela de stats (já sabemos que ela lista times)
        url_stats = f'https://fbref.com/en/comps/{liga_codigo}/{temporada}/stats/{temporada}-{liga_codigo}-Stats'
        html_stats = _get(url_stats)
        table_stats = _extrair_tabela_por_id(html_stats, 'stats_standard')
        if table_stats:
            df_stats = pd.read_html(StringIO(str(table_stats)), flavor='html.parser')[0]
            df_stats.columns = ['_'.join(col).strip() if 'Unnamed' not in col[0] else col[1] for col in df_stats.columns]
            df_stats = df_stats.rename(columns={'Squad': 'team'})
            df_stats = df_stats[~df_stats['team'].str.contains('Squad')]
            # Ordem da tabela = classificação? Nem sempre, mas serve como fallback
            classif = {i+1: row['team'] for i, (_, row) in enumerate(df_stats.iterrows())}
            _cache_escrever(chave, classif)
            return classif
        raise ValueError(f'Classificação não encontrada para código {liga_codigo} temporada {temporada}')

    # Se encontrou a tabela de classificação, parseia
    df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
    # As colunas podem vir com multi-nível; vamos simplificar
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[1] if 'Unnamed' not in col[0] else col[0] for col in df.columns]
    # Identifica as colunas: Rank (ou Rk) e Squad (ou Team)
    if 'Rk' in df.columns:
        pos_col = 'Rk'
    elif 'Rank' in df.columns:
        pos_col = 'Rank'
    else:
        # Assume que a primeira coluna é a posição
        pos_col = df.columns[0]
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
        raise ValueError(f'Não foi possível extrair a classificação da tabela.')
    _cache_escrever(chave, classif)
    return classif

# ------------------------------------------------------------
# 3. PARTIDAS DE UM TIME (com HT)
# ------------------------------------------------------------
def obter_partidas_time(liga_codigo, temporada, time):
    """Retorna lista de partidas do time na temporada, com resultado e HT."""
    chave = f'partidas_{liga_codigo}_{temporada}_{time}'
    cached = _cache_ler(chave)
    if cached:
        return cached

    # URL da página de schedule da liga
    url = f'https://fbref.com/en/comps/{liga_codigo}/{temporada}/schedule/{temporada}-{liga_codigo}-Scores-and-Fixtures'
    html_str = _get(url)
    soup = BeautifulSoup(html_str, 'html.parser')
    
    # A tabela de partidas geralmente tem id 'sched_2024-...' (varia), então buscamos por classe
    table = soup.find('table', class_='stats_table')
    if not table:
        raise ValueError(f'Tabela de partidas não encontrada em {url}')
    
    df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
    # Limpeza de colunas multi-nível
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() if 'Unnamed' not in col[0] else col[1] for col in df.columns]
    
    jogos = []
    for _, row in df.iterrows():
        try:
            mandante = str(row['Home']).strip()
            visitante = str(row['Away']).strip()
            gols_casa = int(row['GF']) if 'GF' in row else None
            gols_fora = int(row['GA']) if 'GA' in row else None
            if gols_casa is None or gols_fora is None:
                continue  # jogo ainda não disputado
            # HT placar (coluna 'HT')
            ht_str = str(row.get('HT', '')).strip()
            ht_placar = None
            if '-' in ht_str:
                ht_casa, ht_fora = map(int, ht_str.split('-'))
                ht_placar = [ht_casa, ht_fora]
            
            # Data
            data_str = str(row.get('Date', ''))
            try:
                data = datetime.strptime(data_str, '%Y-%m-%d')
            except:
                data = datetime.now()
            
            # Identificar se o time é mandante ou visitante
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

# ------------------------------------------------------------
# 4. ESTATÍSTICAS AGREGADAS (OVRall) – já existente
# ------------------------------------------------------------
def obter_stats_time(liga, temporada, time):
    # (mantenha o código anterior que já funciona, com a busca em comentários)
    # ... (o mesmo que você já tem, apenas certifique-se de que funciona)
    pass  # substitua pelo bloco real, que não vou repetir para não alongar
