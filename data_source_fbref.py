# data_source_fbref.py — MyPredict 2.0
# Fonte de dados: web scraping do FBref com estatísticas completas e cache.

import time
import json
import os
import requests
import pandas as pd
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
REQUEST_DELAY = 4  # segundos entre requisições
CACHE_DIR = Path('cache/fbref')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

LIGAS = {
    'Brasileirão': ('24', 'Serie-A'),
    'Premier League': ('9', 'Premier-League'),
    'La Liga': ('12', 'La-Liga'),
}

# ------------------------------------------------------------
# CACHE PERSISTENTE
# ------------------------------------------------------------
def _cache_arquivo(chave: str) -> Path:
    return CACHE_DIR / f'{chave}.json'

def _cache_ler(chave: str) -> Optional[dict]:
    arq = _cache_arquivo(chave)
    if arq.exists():
        with open(arq, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def _cache_escrever(chave: str, dados: dict):
    with open(_cache_arquivo(chave), 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ------------------------------------------------------------
# HTTP com cache em memória
# ------------------------------------------------------------
_HTTP_CACHE = {}

def _get(url: str) -> str:
    if url in _HTTP_CACHE:
        return _HTTP_CACHE[url]
    headers = {'User-Agent': USER_AGENT}
    time.sleep(REQUEST_DELAY)
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    _HTTP_CACHE[url] = resp.text
    return resp.text

# ------------------------------------------------------------
# 1. CLASSIFICAÇÃO
# ------------------------------------------------------------
def obter_classificacao(liga: str, temporada: int) -> Dict[int, str]:
    chave = f'class_{liga}_{temporada}'
    cached = _cache_ler(chave)
    if cached:
        return {int(k): v for k, v in cached.items()}

    comp, nome = LIGAS[liga]
    url = f'https://fbref.com/en/comps/{comp}/{temporada}/{temporada}-{nome}-Stats'
    html = _get(url)
    dfs = pd.read_html(StringIO(html))
    for df in dfs:
        if 'Squad' in df.columns and 'Rk' in df.columns:
            df = df[df['Rk'].notna()]
            classif = {}
            for _, row in df.iterrows():
                try:
                    pos = int(row['Rk'])
                    time = row['Squad'].strip()
                    classif[pos] = time
                except:
                    continue
            if classif:
                _cache_escrever(chave, classif)
                return classif
    raise ValueError('Classificação não encontrada')

# ------------------------------------------------------------
# 2. PARTIDAS BÁSICAS (resultados, gols, HT)
# ------------------------------------------------------------
def _extrair_partidas_basicas(html: str, time: str) -> List[Dict]:
    dfs = pd.read_html(StringIO(html))
    jogos = []
    for df in dfs:
        if 'Home' not in df.columns or 'Away' not in df.columns:
            continue
        for _, row in df.iterrows():
            try:
                mandante = str(row['Home']).strip()
                visitante = str(row['Away']).strip()
                gols_casa = int(row['GF'])
                gols_fora = int(row['GA'])
                data = pd.to_datetime(row['Date'])

                if time.lower() not in mandante.lower() and time.lower() not in visitante.lower():
                    continue

                if time.lower() in mandante.lower():
                    adversario = visitante
                    mandante_flag = True
                    gols_pro = gols_casa
                    gols_contra = gols_fora
                else:
                    adversario = mandante
                    mandante_flag = False
                    gols_pro = gols_fora
                    gols_contra = gols_casa

                resultado = 'V' if gols_pro > gols_contra else ('E' if gols_pro == gols_contra else 'D')

                # HT
                ht_placar = None
                if 'HT' in row and isinstance(row['HT'], str):
                    partes = row['HT'].split('–')
                    if len(partes) == 2:
                        try:
                            ht_casa = int(partes[0].strip())
                            ht_fora = int(partes[1].strip())
                            ht_placar = [ht_casa, ht_fora] if mandante_flag else [ht_fora, ht_casa]
                        except:
                            pass

                # URL do match report (para scraping avançado)
                match_url = None
                if 'Match Report' in row and isinstance(row['Match Report'], str):
                    # A coluna 'Match Report' contém um link
                    pass  # complexo com pd.read_html, vamos extrair posteriormente

                jogos.append({
                    'data': data,
                    'resultado': resultado,
                    'adversario': adversario,
                    'mandante': mandante_flag,
                    'gols_pro': gols_pro,
                    'gols_contra': gols_contra,
                    'ht_placar': ht_placar,
                    'match_url': None,
                })
            except Exception as e:
                continue
    return sorted(jogos, key=lambda x: x['data'])

def obter_partidas_time(liga: str, temporada: int, time: str) -> List[Dict]:
    chave = f'partidas_{liga}_{temporada}_{time}'
    cached = _cache_ler(chave)
    if cached:
        return cached

    comp, nome = LIGAS[liga]
    url = f'https://fbref.com/en/comps/{comp}/{temporada}/schedule/{temporada}-{nome}-Scores-and-Fixtures'
    html = _get(url)
    jogos = _extrair_partidas_basicas(html, time)
    _cache_escrever(chave, jogos)
    return jogos

# ------------------------------------------------------------
# 3. ESTATÍSTICAS AVANÇADAS (scraping por partida)
# ------------------------------------------------------------
def _extrair_stats_partida(match_url: str, time: str) -> Dict:
    """
    Acessa o match report e retorna dicionário com estatísticas do time.
    Não implementado completamente aqui por complexidade; será chamado sob demanda.
    """
    # Implementação futura: parse da tabela de stats
    return {}

def enriquecer_jogos_com_stats(jogos: List[Dict], time: str, liga: str, temporada: int) -> List[Dict]:
    """
    Para cada jogo, tenta obter estatísticas avançadas via cache ou scraping.
    """
    # Como não temos match_url ainda, essa função é placeholder.
    # Para o teste inicial, vamos preencher com zeros/none e depois evoluir.
    for jogo in jogos:
        jogo.setdefault('xg', 0)
        jogo.setdefault('xga', 0)
        jogo.setdefault('finalizacoes_tot', 0)
        jogo.setdefault('finalizacoes_alvo', 0)
        jogo.setdefault('posse', 0)
        jogo.setdefault('passes_certos', 0)
        jogo.setdefault('passes_totais', 0)
        jogo.setdefault('passes_chave', 0)
        jogo.setdefault('assistencias', 0)
        jogo.setdefault('desarmes', 0)
        jogo.setdefault('interceptacoes', 0)
        jogo.setdefault('escanteios', 0)
        jogo.setdefault('escanteios_sofridos', 0)
        jogo.setdefault('gols_ultimos_15', 0)
    return jogos
