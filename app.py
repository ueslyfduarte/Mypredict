import streamlit as st
import requests

# Configurações iniciais da página
st.set_page_config(page_title="Dashboard de Futebol", page_icon="⚽", layout="wide")
st.title("🏆 Explorador de Ligas de Futebol")

# 1. Recupera a chave do st.secrets
api_key = st.secrets["MINHA_API_KEY"]
headers = {'x-apisports-key': api_key}

# 2. Busca a lista de países (AGORA COM OS IMPORTS CORRETOS NO TOPO)
@st.cache_data
def buscar_paises():
    url = "https://api-sports.io"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            st.error(f"Erro da API: Status {response.status_code}")
            return []
        
        dados_json = response.json()
        if dados_json.get("errors"):
            st.error(f"Detalhes do erro na API: {dados_json['errors']}")
            return []
            
        return dados_json.get("response", [])
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return []

# 3. Busca as ligas do país selecionado
def buscar_ligas_por_pais(nome_pais):
    url = f"https://api-sports.io{nome_pais}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("response", [])
    return []

# Execução principal do App
lista_paises = buscar_paises()

if lista_paises:
    mapeamento_paises = {p["name"]: p["flag"] for p in lista_paises}
    nomes_paises = sorted(list(mapeamento_paises.keys()))
    
    col1, col2 = st.columns([3, 1])
    with col1:
        pais_selecionado = st.selectbox("Selecione um País:", nomes_paises)
    
    with col2:
        bandeira = mapeamento_paises[pais_selecionado]
        if bandeira:
            st.image(bandeira, width=60)
            
    st.divider()
    
    st.subheader(f"Ligas disponíveis em: {pais_selecionado}")
    with st.spinner("Carregando campeonatos..."):
        ligas = buscar_ligas_por_pais(pais_selecionado)
        
    if ligas:
        for item in ligas:
            liga_info = item["league"]
            col_logo, col_texto = st.columns([1, 10])
            
            with col_logo:
                if liga_info["logo"]:
                    st.image(liga_info["logo"], width=40)
            
            with col_texto:
                st.markdown(f"**{liga_info['name']}** (Tipo: *{liga_info['type']}*)")
                st.caption(f"ID da Liga: {liga_info['id']}")
            st.write("")
    else:
        st.warning("Nenhuma liga encontrada para este país.")
