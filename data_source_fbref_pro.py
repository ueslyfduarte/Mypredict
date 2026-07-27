# data_source_fbref_pro.py — MyPredict 2.0 (scraper profissional)
import time
import random
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup

# ------------------------------------------------------------
# Configurações de scraping (inspiradas no BaseRequestsReader)
# ------------------------------------------------------------
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/59.0.3071.86 Safari/537.36"
)
RATE_LIMIT = 6        # segundos de espera base
MAX_DELAY = 3         # variação aleatória adicional
MAX_RETRIES = 3       # tentativas por URL
CACHE_DIR = Path("cache/fbref_pro")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento de nome amigável → código numérico do FBref (e slug para stats)
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

# ------------------------------------------------------------
# Funções auxiliares de cache e requisição
# ------------------------------------------------------------
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
    s.headers.update({"User-Agent": USER_AGENT})
    return s

def _baixar(url):
    """Baixa uma URL com retentativas e delays."""
    sessao = _criar_sessao()
    for tentativa in range(MAX_RETRIES):
        try:
            time.sleep(RATE_LIMIT + random.random() * MAX_DELAY)
            resp = sessao.get(url, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            if tentativa == MAX_RETRIES - 1:
                raise ConnectionError(f"Falha ao acessar {url} após {MAX_RETRIES} tentativas.") from e
            time.sleep(2 ** tentativa)  # espera exponencial
            sessao = _criar_sessao()    # nova sessão

def _extrair_tabela(html_str, table_id):
    """Procura tabela no HTML, incluindo comentários."""
    soup = BeautifulSoup(html_str, 'html.parser')
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and table_id in text):
        comment_soup = BeautifulSoup(comment, 'html.parser')
        table = comment_soup.find('table', id=table_id)
        if table:
            return table
    return soup.find('table', id=table_id)

# ------------------------------------------------------------
# Funções públicas (usadas pelo data_loader)
# ------------------------------------------------------------
def obter_codigo_fbref(nome_liga):
    """Retorna o código numérico da liga (não essencial, mas mantido para compatibilidade)."""
    if nome_liga in LEAGUES:
        return LEAGUES[nome_liga]["cod"]
    return None

def obter_classificacao(liga_nome, temporada):
    """Retorna {posição: time} a partir da página principal da competição."""
    info = LEAGUES.get(liga_nome)
    if not info:
        raise ValueError(f"Liga '{liga_nome}' não suportada.")
    cod = info["cod"]
    chave = f"class_{cod}_{temporada}"
    cached = _cache_ler(chave)
    if cached:
        return {int(k): v for k, v in cached.items()}

    url = f"https://fbref.com/en/comps/{cod}/{temporada}/"
    html_str = _baixar(url)
    soup = BeautifulSoup(html_str, 'html.parser')

    # Procura tabela de classificação (colunas com 'wins' e 'losses')
    table = None
    for tbl in soup.find_all('table', class_='stats_table'):
        headers = [th.get('data-stat', '') for th in tbl.find_all('th')]
        if 'wins' in headers and 'losses' in headers:
            table = tbl
            break
    if not table:
        raise ValueError(f"Tabela de classificação não encontrada em {url}")

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
        raise ValueError("Não foi possível extrair a classificação.")
    _cache_escrever(chave, classif)
    return classif

def obter_partidas_time(liga_nome, temporada, time):
    """Retorna lista de jogos do time com HT."""
    info = LEAGUES.get(liga_nome)
    if not info:
        raise ValueError(f"Liga '{liga_nome}' não suportada.")
    cod = info["cod"]
    chave = f"partidas_{cod}_{temporada}_{time}"
    cached = _cache_ler(chave)
    if cached:
        return cached

    url = f"https://fbref.com/en/comps/{cod}/{temporada}/schedule/{temporada}-{cod}-Scores-and-Fixtures"
    html_str = _baixar(url)
    soup = BeautifulSoup(html_str, 'html.parser')
    table = soup.find('table', class_='stats_table')
    if not table:
        raise ValueError(f"Tabela de partidas não encontrada em {url}")

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

            # HT
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
            elif time.lower() == visitante.lower():
                adversario = mandante
                mandante_flag = False
                gols_pro = gols_fora
                gols_contra = gols_casa
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
                'ht_placar': ht_placar,
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

def obter_stats_time(liga_nome, temporada, time):
    """Retorna estatísticas agregadas do time (médias) a partir da tabela de stats."""
    info = LEAGUES.get(liga_nome)
    if not info:
        return {}
    cod = info["cod"]
    slug = info["slug"]
    chave = f"stats_{cod}_{temporada}_{time}"
    cached = _cache_ler(chave)
    if cached:
        return cached

    url = f"https://fbref.com/en/comps/{cod}/{temporada}/stats/{temporada}-{slug}-Stats"
    html_str = _baixar(url)
    table = _extrair_tabela(html_str, 'stats_standard')
    if not table:
        return {}

    df = pd.read_html(StringIO(str(table)), flavor='html.parser')[0]
    if isinstance(df.columns, pd.MultiIndex):
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
        return {}

    row = df.loc[match]
    dados = {}
    # Médias por 90 minutos ou totais (preferimos per 90)
    mp = row.get('MP', 1)
    if 'Gls' in row:
        dados['gols_media'] = row['Gls'] / mp
    if 'GA' in row:
        dados['gols_sofridos_media'] = row['GA'] / mp
    if 'xG' in row:
        dados['xg_media'] = row['xG'] / mp
    if 'xGA' in row:
        dados['xga_media'] = row['xGA'] / mp
    if 'Poss' in row:
        dados['posse_media'] = row['Poss']
    if 'Cmp%' in row:
        dados['passes_certos_pct'] = row['Cmp%']
    if 'KP' in row:
        dados['passes_chave_media'] = row['KP'] / mp
    if 'Ast' in row:
        dados['assistencias_media'] = row['Ast'] / mp
    if 'Tkl' in row:
        dados['desarmes_media'] = row['Tkl'] / mp
    if 'Int' in row:
        dados['interceptacoes_media'] = row['Int'] / mp
    # Escanteios podem estar na tabela 'misc', mas não na standard; deixamos None
    dados['escanteios_media'] = None
    dados['escanteios_sofridos_media'] = None

    resultado = {k: v for k, v in dados.items() if v is not None}
    _cache_escrever(chave, resultado)
    return resultado
