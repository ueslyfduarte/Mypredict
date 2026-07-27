# data_source_fbref_stats.py — MyPredict 2.0
# Scraping de estatísticas agregadas por time no FBref (médias da temporada).
# Baseado nas técnicas da biblioteca soccerdata, adaptado para requests + lxml.

import time
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
import json
import warnings
from lxml import html, etree

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
REQUEST_DELAY = 4  # segundos entre requisições

CACHE_DIR = Path('cache/fbref_stats')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Mapeamento liga -> (slug do FBref, nome da pasta)
LIGAS_FBREF = {
    'Brasileirão': ('24', 'Serie-A'),
    'Premier League': ('9', 'Premier-League'),
    'La Liga': ('12', 'La-Liga'),
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

def _get(url):
    headers = {'User-Agent': USER_AGENT}
    time.sleep(REQUEST_DELAY)
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text

def obter_stats_time(liga, temporada, time):
    """
    Retorna um dicionário com médias da temporada para o time:
    - gols_media, gols_sofridos_media, xg_media, xga_media,
    - finalizacoes_tot_media, finalizacoes_alvo_media,
    - posse_media, passes_certos_pct, passes_chave_media,
    - assistencias_media, escanteios_media, escanteios_sofridos_media,
    - desarmes_media, interceptacoes_media, etc.
    """
    chave = f'stats_{liga}_{temporada}_{time}'
    cached = _cache_ler(chave)
    if cached:
        return cached

    comp, slug = LIGAS_FBREF[liga]
    # URL da página de estatísticas de equipes da liga (standard stats)
    url = f'https://fbref.com/en/comps/{comp}/{temporada}/stats/{temporada}-{slug}-Stats'
    html_str = _get(url)

    # Parse com lxml
    tree = html.fromstring(html_str)

    # A tabela "stats_standard" geralmente está dentro de um comentário no HTML
    # O soccerdata usa: tree.xpath("//comment()[contains(.,'div_stats_standard')]")
    # Vamos replicar isso.
    stats_table = None
    for comment in tree.xpath("//comment()"):
        if 'div_stats_standard' in comment.text:
            # Extrai o HTML do comentário
            inner_tree = html.fromstring(comment.text)
            # Procura pela tabela id="stats_standard"
            stats_table = inner_tree.xpath("//table[contains(@id, 'stats_standard')]")
            if stats_table:
                stats_table = stats_table[0]
                break

    if stats_table is None:
        # Fallback: tenta achar diretamente (pode não funcionar)
        stats_table = tree.xpath("//table[contains(@id, 'stats_standard')]")
        if stats_table:
            stats_table = stats_table[0]

    if stats_table is None:
        raise ValueError(f"Tabela de estatísticas não encontrada para {liga} {temporada}")

    # Converter para DataFrame
    df = pd.read_html(StringIO(html.tostring(stats_table, encoding='unicode')), flavor='lxml')[0]
    # Limpeza de colunas multi-nível (como no soccerdata)
    df.columns = ['_'.join(col).strip() if 'Unnamed' not in col[0] else col[1] for col in df.columns]
    df = df.rename(columns={'Squad': 'team'})
    df = df[~df['team'].str.contains('Squad')]  # remove cabeçalhos extras
    df = df.set_index('team')

    # Procurar o time (case-insensitive)
    match = None
    for t in df.index:
        if time.lower() in t.lower():
            match = t
            break
    if not match:
        raise ValueError(f"Time '{time}' não encontrado na tabela de stats do FBref.")

    row = df.loc[match]
    # Converter para numérico
    for col in row.index:
        try:
            row[col] = pd.to_numeric(row[col])
        except (ValueError, TypeError):
            row[col] = None

    # Mapear campos de interesse
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
        'escanteios_media': None,  # Não está na standard; pode ser obtido em outra página
        'escanteios_sofridos_media': None,
    }

    # Ajustar se valores são por 90 min ou totais (se for total, precisamos dividir por jogos)
    # A maioria das colunas "Per 90 Minutes" já está normalizada.
    # Se não, poderíamos pegar o número de jogos e dividir, mas a tabela padrão já oferece por 90 min.
    # Vamos garantir que sejam números.
    for k, v in dados.items():
        if v is not None and not isinstance(v, (int, float)):
            dados[k] = None

    _cache_escrever(chave, dados)
    return dados
