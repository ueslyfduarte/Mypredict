# data_source_fbref_stats.py — MyPredict 2.0 (usando fbrefdata)
from fbrefdata import FBref
import pandas as pd

# Instância global (cache automático, sem precisar de Selenium)
_fbref = FBref(no_store=False, no_cache=False)

def obter_codigo_fbref(nome_liga):
    """Não precisamos mais de código numérico; a biblioteca resolve por nome."""
    return nome_liga  # Apenas retorna o nome; a biblioteca aceita nomes padronizados.

def obter_classificacao(liga_nome, temporada):
    """Retorna {posição: time} usando a biblioteca."""
    df = _fbref.read_team_season_stats(stat_type="standard", opponent_stats=False)
    # Filtra pela liga e temporada
    df = df[df.index.get_level_values('league') == liga_nome]
    df = df[df.index.get_level_values('season') == temporada]
    if df.empty:
        raise ValueError(f"Classificação não encontrada para {liga_nome} {temporada}")
    # A tabela já contém a posição (Rk) e o time (Squad)
    classif = {}
    for idx, row in df.iterrows():
        pos = int(idx[0])  # O índice contém a posição? Vamos ajustar.
        # O DataFrame retornado tem índice 'team', mas precisamos da posição.
        # Na verdade, read_team_season_stats não inclui classificação diretamente.
        # Melhor usar read_schedule para obter a tabela de classificação?
        pass
    # ... (precisa de ajustes, veja explicação abaixo)
