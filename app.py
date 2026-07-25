# scraper_fbref.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
from datetime import datetime, timedelta

# -----------------------------------------------------------------
# CONFIGURAÇÕES DE RESPEITO AO SITE
# -----------------------------------------------------------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
PAUSA_MIN = 2   # segundos
PAUSA_MAX = 5   # segundos
CACHE_DIR = "cache_fbref"
CACHE_VALIDADE_HORAS = 6

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# -----------------------------------------------------------------
# FUNÇÕES AUXILIARES
# -----------------------------------------------------------------
def pausa_respeitosa():
    """Aguarda um tempo aleatório para evitar bloqueios."""
    time.sleep(random.uniform(PAUSA_MIN, PAUSA_MAX))

def cache_valido(nome_arquivo):
    """Verifica se o cache ainda está dentro da validade."""
    caminho = os.path.join(CACHE_DIR, nome_arquivo)
    if not os.path.exists(caminho):
        return False
    mod_time = datetime.fromtimestamp(os.path.getmtime(caminho))
    return (datetime.now() - mod_time) < timedelta(hours=CACHE_VALIDADE_HORAS)

def salvar_cache(df, nome_arquivo):
    """Salva DataFrame em CSV no cache."""
    caminho = os.path.join(CACHE_DIR, nome_arquivo)
    df.to_csv(caminho, index=False)

def carregar_cache(nome_arquivo):
    """Carrega DataFrame do cache."""
    caminho = os.path.join(CACHE_DIR, nome_arquivo)
    return pd.read_csv(caminho)

# -----------------------------------------------------------------
# PARSING DAS TABELAS
# -----------------------------------------------------------------
def extrair_estatisticas_padrao(soup):
    """Procura a tabela de estatísticas padrão (Standard Stats)."""
    tabela = soup.find("table", {"id": "stats_standard"})
    if not tabela:
        return None
    df = pd.read_html(str(tabela))[0]
    # Limpeza básica: remover linhas de cabeçalho duplicadas
    df = df.dropna(subset=["Jogador"]).reset_index(drop=True)
    return df

def extrair_estatisticas_gols(soup):
    """Tabela de chutes e gols (Shooting)."""
    tabela = soup.find("table", {"id": "stats_shooting"})
    if not tabela:
        return None
    df = pd.read_html(str(tabela))[0]
    df = df.dropna(subset=["Jogador"]).reset_index(drop=True)
    return df

# -----------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE RASPAGEM
# -----------------------------------------------------------------
def buscar_dados_time(url_time, temporada="2024"):
    """
    Retorna um dicionário com médias do time para o simulador.
    url_time: URL da página do time no FBref (ex: https://fbref.com/pt/equipes/...)
    """
    nome_cache = f"{url_time.split('/')[-2]}_{temporada}.csv"
    
    if cache_valido(nome_cache):
        print("📦 Dados carregados do cache.")
        df = carregar_cache(nome_cache)
    else:
        print("🌐 Raspando dados do FBref...")
        response = requests.get(url_time, headers=HEADERS)
        if response.status_code != 200:
            raise Exception(f"Erro ao acessar {url_time}: {response.status_code}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        pausa_respeitosa()
        
        # Extrair tabelas
        df_std = extrair_estatisticas_padrao(soup)
        df_shoot = extrair_estatisticas_gols(soup)
        
        if df_std is None:
            raise Exception("Tabela de estatísticas padrão não encontrada.")
        
        # Combinar dados relevantes (exemplo simplificado)
        # Em uma versão completa, mapearíamos colunas específicas
        df = df_std.copy()
        salvar_cache(df, nome_cache)
    
    # Converter para o formato do simulador (médias)
    # Isso exigiria mapear colunas do FBref para nossas variáveis
    # Por enquanto, retornamos um dicionário de exemplo
    dados = {
        'gols': df['Gols'].mean() if 'Gols' in df.columns else None,
        'chutes_gol': df['Chutes'].mean() if 'Chutes' in df.columns else None,
        # ... outros mapeamentos
    }
    return dados
