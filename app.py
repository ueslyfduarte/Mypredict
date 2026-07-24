import streamlit as st
import requests

# Configuração da página
st.set_page_config(page_title="MyPredicts - Teste de Ligas", layout="wide")

st.title("🔍 Buscador Direto de Ligas - MyPredicts")

# ---------------------------------------------------------------------
# [MÓDULO 1] CONFIGURAÇÃO DE ACESSO
# ---------------------------------------------------------------------
if "MINHA_API_KEY" in st.secrets:
    HEADERS = {
        'x-apisports-key': st.secrets["MINHA_API_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
else:
    st.error("⚠️ ERRO CRÍTICO: Configure a tag 'MINHA_API_KEY' no painel do Streamlit (Secrets).")
    st.stop()

BASE_URL = "https://api-sports.io"


# ---------------------------------------------------------------------
# [MÓDULO 2] REQUISIÇÃO DIRETA À API
# ---------------------------------------------------------------------
@st.cache_data(ttl=86400)
def api_buscar_todas_as_ligas():
    """Busca a lista completa de ligas direto no servidor da API Football"""
    try:
        url = f"{BASE_URL}/leagues"
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code == 200:
            return response.json().get("response", [])
        return []
    except Exception as e:
        st.error(f"Erro físico de conexão: {e}")
        return []


# Dispara a busca assim que a página carrega
dados_ligas = api_buscar_todas_as_ligas()

# ---------------------------------------------------------------------
# [MÓDULO 3] INTERFACE VISUAL
# ---------------------------------------------------------------------
if dados_ligas:
    # Transforma o retorno da API em um dicionário organizado por Nome da Liga e País
    dict_leagues = {f"{item['league']['name']} ({item['country']['name']})": item['league']['id'] for item in dados_ligas}
    lista_nomes_ordenados = sorted(list(dict_leagues.keys()))
    
    st.success(f"✅ Sucesso! Foram encontradas {len(dados_ligas)} ligas em tempo real na API.")
    
    # Renderiza o seletor com busca nativa do Streamlit
    liga_escolhida = st.selectbox(
        "Digite ou role para selecionar uma Liga:",
        options=lista_nomes_ordenados,
        index=0
    )
    
    # Mostra o ID real da liga selecionada na tela
    st.info(f"ID oficial da liga selecionada na API Football: **{dict_leagues[liga_escolhida]}**")

else:
    st.error("❌ A API retornou uma lista vazia ou a conexão falhou. Verifique se o seu token está ativo ou se o limite por minuto foi excedido.")
