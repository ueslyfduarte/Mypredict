import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuração essencial da página
st.set_page_config(
    page_title="Meu App Esportivo",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Meu Painel de Análise Esportiva")

# =========================================================================
# MÓDULO 1: PONTE DE CONEXÃO COM A API (CORRIGIDO)
# =========================================================================

# Constantes da API
API_BASE_URL = "https://v3.football.api-sports.io"
CACHE_EXPIRACAO_HORAS = 6  # Cache de 6 horas para economizar requisições

def pegar_chave_api():
    """Busca a chave da API dos secrets do Streamlit"""
    try:
        return st.secrets["API_FOOTBALL_KEY"]
    except KeyError:
        st.error("❌ Chave 'API_FOOTBALL_KEY' não encontrada nos secrets.")
        st.info("💡 Configure em: Streamlit Cloud > Settings > Secrets")
        return None

def pegar_headers():
    """Monta os headers corretos para API-Football"""
    api_key = pegar_chave_api()
    if not api_key:
        return None
    return {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }

def buscar_dados_api(endpoint, params=None):
    """
    Função isolada que faz a ponte com a API-Football.
    
    Parâmetros:
        endpoint: Caminho da API (ex: '/teams', '/fixtures', '/standings')
        params: Dicionário com filtros (ex: {'league': 71, 'season': 2024})
    
    Retorna:
        dict com 'sucesso', 'erro', 'dados'
    """
    headers = pegar_headers()
    if not headers:
        return {"sucesso": False, "erro": "Chave API não configurada", "dados": None}
    
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        
        # Verifica se a requisição funcionou
        if response.status_code != 200:
            return {
                "sucesso": False,
                "erro": f"Erro HTTP {response.status_code}",
                "dados": None
            }
        
        dados_brutos = response.json()
        
        # Verifica erros da API
        if "errors" in dados_brutos and dados_brutos["errors"]:
            erro_msg = dados_brutos["errors"]
            if isinstance(erro_msg, dict):
                erro_msg = str(erro_msg)
            return {"sucesso": False, "erro": erro_msg, "dados": None}
        
        # Mostra quantas requisições ainda restam no plano free
        if 'x-ratelimit-requests-remaining' in response.headers:
            restantes = response.headers['x-ratelimit-requests-remaining']
            st.sidebar.metric("Requisições Restantes Hoje", restantes)
        
        return {
            "sucesso": True,
            "erro": None,
            "dados": dados_brutos.get("response", [])
        }
        
    except requests.exceptions.ConnectionError:
        return {"sucesso": False, "erro": "Sem conexão com a internet", "dados": None}
    except requests.exceptions.Timeout:
        return {"sucesso": False, "erro": "Tempo de resposta esgotado", "dados": None}
    except Exception as e:
        return {"sucesso": False, "erro": f"Erro inesperado: {str(e)}", "dados": None}

# =========================================================================
# MÓDULO 2: FUNÇÕES AUXILIARES PARA BUSCAS COMUNS
# =========================================================================

def buscar_ligas_disponiveis():
    """Busca todas as ligas disponíveis na API"""
    resultado = buscar_dados_api("/leagues")
    return resultado

def buscar_times_por_liga(liga_id, temporada=2024):
    """Busca todos os times de uma liga específica"""
    resultado = buscar_dados_api("/teams", params={
        "league": liga_id,
        "season": temporada
    })
    return resultado

def buscar_classificacao(liga_id, temporada=2024):
    """Busca a tabela de classificação"""
    resultado = buscar_dados_api("/standings", params={
        "league": liga_id,
        "season": temporada
    })
    return resultado

def buscar_ultimas_partidas(time_id, quantidade=10):
    """Busca as últimas partidas de um time"""
    resultado = buscar_dados_api("/fixtures", params={
        "team": time_id,
        "last": quantidade,
        "status": "FT"  # Apenas partidas finalizadas
    })
    return resultado

# =========================================================================
# MÓDULO 3: INTERFACE DO USUÁRIO
# =========================================================================

# Menu lateral
st.sidebar.header("📋 Navegação")
aba = st.sidebar.selectbox(
    "Escolha a seção:",
    ["Status da API", "Buscar Times", "Classificação", "Últimas Partidas"]
)

# Aba 1: Status da API
if aba == "Status da API":
    st.header("🔌 Status da Conexão")
    
    if st.button("Testar Conexão"):
        with st.spinner("Conectando com a API-Football..."):
            resultado = buscar_ligas_disponiveis()
            
            if resultado["sucesso"]:
                st.success("✅ API conectada com sucesso!")
                st.write(f"Total de ligas disponíveis: {len(resultado['dados'])}")
            else:
                st.error(f"❌ Falha na conexão: {resultado['erro']}")

# Aba 2: Buscar Times
elif aba == "Buscar Times":
    st.header("🔍 Buscar Times")
    
    nome_time = st.text_input("Digite o nome do time:")
    
    if st.button("Buscar") and nome_time:
        with st.spinner(f"Buscando '{nome_time}'..."):
            resultado = buscar_dados_api("/teams", params={"search": nome_time})
            
            if resultado["sucesso"]:
                times = resultado["dados"]
                if times:
                    st.success(f"{len(times)} time(s) encontrado(s)")
                    for item in times:
                        time = item["team"]
                        st.write(f"• **{time['name']}** ({time['country']}) - ID: {time['id']}")
                else:
                    st.warning("Nenhum time encontrado com esse nome.")
            else:
                st.error(f"Erro: {resultado['erro']}")

# Aba 3: Classificação
elif aba == "Classificação":
    st.header("📊 Classificação")
    
    # IDs das principais ligas
    ligas = {
        "Brasileirão Série A": 71,
        "Premier League": 39,
        "La Liga": 140,
        "Série A Italiana": 135,
        "Bundesliga": 78
    }
    
    liga_escolhida = st.selectbox("Escolha a liga:", list(ligas.keys()))
    
    if st.button("Carregar Tabela"):
        with st.spinner("Carregando classificação..."):
            resultado = buscar_classificacao(ligas[liga_escolhida])
            
            if resultado["sucesso"] and resultado["dados"]:
                # Extrai a tabela
                tabela = resultado["dados"][0]["league"]["standings"][0]
                
                # Cria DataFrame para mostrar bonito
                dados_tabela = []
                for pos in tabela:
                    dados_tabela.append({
                        "Pos": pos["rank"],
                        "Time": pos["team"]["name"],
                        "Pts": pos["points"],
                        "J": pos["all"]["played"],
                        "V": pos["all"]["win"],
                        "E": pos["all"]["draw"],
                        "D": pos["all"]["lose"],
                        "SG": pos["goalsDiff"]
                    })
                
                df = pd.DataFrame(dados_tabela)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.error(f"Erro: {resultado['erro']}")

# Aba 4: Últimas Partidas
elif aba == "Últimas Partidas":
    st.header("📅 Últimas Partidas")
    st.info("Busque um time primeiro na aba 'Buscar Times' e anote o ID.")
    
    time_id = st.number_input("ID do time:", min_value=1, value=127)
    
    if st.button("Carregar Partidas"):
        with st.spinner("Buscando últimas partidas..."):
            resultado = buscar_ultimas_partidas(time_id, 5)
            
            if resultado["sucesso"] and resultado["dados"]:
                st.success(f"{len(resultado['dados'])} partidas encontradas")
                for partida in resultado["dados"]:
                    casa = partida["teams"]["home"]["name"]
                    fora = partida["teams"]["away"]["name"]
                    gols_casa = partida["goals"]["home"]
                    gols_fora = partida["goals"]["away"]
                    data = partida["fixture"]["date"][:10]
                    
                    st.write(f"📅 {data} | {casa} {gols_casa} x {gols_fora} {fora}")
            else:
                st.error(f"Erro: {resultado['erro']}")

# =========================================================================
# RODAPÉ
# =========================================================================
st.sidebar.divider()
st.sidebar.caption(f"Plano Free API-Football | 100 req/dia")
st.sidebar.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
