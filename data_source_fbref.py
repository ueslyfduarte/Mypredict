# data_source_fbref.py — MyPredict 2.0
# Fonte de dados: web scraping do FBref (estatísticas completas).

import time
import requests
import pandas as pd
from io import StringIO
from functools import lru_cache
from typing import List, Dict, Optional, Tuple

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
CACHE = {}  # cache simples em memória

def _get(url: str) -> str:
    """Faz requisição HTTP com delay e user-agent."""
    if url in CACHE:
        return CACHE[url]
    headers = {'User-Agent': USER_AGENT}
    time.sleep(4)  # respeitar o site
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    CACHE[url] = resp.text
    return resp.text

# ------------------------------------------------------------
# CONFIGURAÇÃO DE LIGAS (ID FBref e nome)
# ------------------------------------------------------------
LIGAS = {
    'Brasileirão': ('24', 'Serie-A'),
    'Premier League': ('9', 'Premier-League'),
    'La Liga': ('12', 'La-Liga'),
    # Adicione outras conforme necessário
}

def _id_liga(liga: str) -> Tuple[str, str]:
    return LIGAS.get(liga, ('24', 'Serie-A'))

def _url_base(liga: str, temporada: int) -> str:
    comp, nome = _id_liga(liga)
    # Exemplo: https://fbref.com/en/comps/24/2024/schedule/2024-Serie-A-Scores-and-Fixtures
    return f'https://fbref.com/en/comps/{comp}/{temporada}/schedule/{temporada}-{nome}-Scores-and-Fixtures'

# ------------------------------------------------------------
# 1. CLASSIFICAÇÃO DA TEMPORADA
# ------------------------------------------------------------
def obter_classificacao(liga: str, temporada: int) -> Dict[int, str]:
    """
    Retorna {posição: nome_time} a partir da tabela de classificação do FBref.
    """
    comp, _ = _id_liga(liga)
    url = f'https://fbref.com/en/comps/{comp}/{temporada}/{temporada}-{_id_liga(liga)[1]}-Stats'
    html = _get(url)
    dfs = pd.read_html(StringIO(html))
    # A tabela de classificação geralmente é a primeira que contém "Rk" ou "Squad"
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
                return classif
    raise ValueError(f'Classificação não encontrada para {liga} {temporada}')

# ------------------------------------------------------------
# 2. PARTIDAS DE UM TIME EM UMA TEMPORADA
# ------------------------------------------------------------
def _extrair_partidas_da_tabela(df: pd.DataFrame, time: str, temporada: int, liga: str) -> List[Dict]:
    """
    Processa um DataFrame da página de agenda do time para extrair lista de jogos.
    """
    jogos = []
    for _, row in df.iterrows():
        if pd.isna(row.get('Date')):
            continue
        try:
            data = pd.to_datetime(row['Date'])
            mandante = str(row['Home']).strip() if 'Home' in row else None
            visitante = str(row['Away']).strip() if 'Away' in row else None
            gols_casa = int(row['GF']) if 'GF' in row else None
            gols_fora = int(row['GA']) if 'GA' in row else None

            if not mandante or not visitante or gols_casa is None or gols_fora is None:
                continue

            # Determinar se o time é mandante ou visitante
            if time.lower() in mandante.lower():
                adversario = visitante
                mandante_flag = True
                gols_pro = gols_casa
                gols_contra = gols_fora
            elif time.lower() in visitante.lower():
                adversario = mandante
                mandante_flag = False
                gols_pro = gols_fora
                gols_contra = gols_casa
            else:
                continue  # jogo não envolve esse time

            # Resultado
            if gols_pro > gols_contra:
                resultado = 'V'
            elif gols_pro == gols_contra:
                resultado = 'E'
            else:
                resultado = 'D'

            # Placar HT (se disponível)
            ht_placar = None
            if 'HT' in row and isinstance(row['HT'], str):
                ht = row['HT'].split('–')
                if len(ht) == 2:
                    try:
                        ht_casa = int(ht[0].strip())
                        ht_fora = int(ht[1].strip())
                        if mandante_flag:
                            ht_placar = [ht_casa, ht_fora]
                        else:
                            ht_placar = [ht_fora, ht_casa]
                    except:
                        pass

            # Estatísticas avançadas (serão preenchidas após scrape da página de match)
            jogo = {
                'data': data,
                'resultado': resultado,
                'adversario': adversario,
                'mandante': mandante_flag,
                'gols_pro': gols_pro,
                'gols_contra': gols_contra,
                'ht_placar': ht_placar,
                'xg': None,
                'xga': None,
                'finalizacoes_tot': None,
                'finalizacoes_alvo': None,
                'posse': None,
                'passes_certos': None,
                'passes_totais': None,
                'passes_chave': None,
                'assistencias': None,
                'desarmes': None,
                'interceptacoes': None,
                'escanteios': None,
                'escanteios_sofridos': None,
                'gols_ultimos_15': None,  # requer match report detalhado
            }
            jogos.append(jogo)
        except Exception:
            continue
    return jogos

def obter_partidas_time(liga: str, temporada: int, time: str) -> List[Dict]:
    """
    Retorna lista de todas as partidas do time na temporada, com estatísticas básicas.
    Para obter estatísticas avançadas (posse, passes, xG), é necessário visitar cada página de match.
    Essa função retorna as básicas; as avançadas podem ser preenchidas opcionalmente.
    """
    url = _url_base(liga, temporada)
    html = _get(url)
    dfs = pd.read_html(StringIO(html))
    # Procurar a tabela que contém as partidas do time
    # O FBref geralmente divide em tabelas por semana, mas podemos concatenar.
    # Estratégia: ler todas as tabelas e filtrar linhas onde Home ou Away contêm o nome do time.
    todos_jogos = []
    for df in dfs:
        if 'Home' in df.columns and 'Away' in df.columns:
            todos_jogos.extend(_extrair_partidas_da_tabela(df, time, temporada, liga))
    if not todos_jogos:
        # Fallback: tentar scraping específico da página do time
        return _scrape_pagina_time(liga, temporada, time)
    return sorted(todos_jogos, key=lambda x: x['data'])

def _scrape_pagina_time(liga: str, temporada: int, time: str) -> List[Dict]:
    """Scrapeia a página individual do time na temporada (caso a abordagem geral falhe)."""
    # Implementação simplificada: retornar lista vazia e avisar
    print(f'Aviso: não foi possível extrair partidas para {time} via tabela geral.')
    return []
