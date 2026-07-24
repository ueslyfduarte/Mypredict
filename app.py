import streamlit as st
import requests

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

# Configuração da página movida para baixo do Módulo 1
st.set_page_config(page_title="MyPredicts - Teste de Ligas", layout="wide")


# ---------------------------------------------------------------------
# BUSCADOR DE TIMES CONECTADO DIRETO À API
# ---------------------------------------------------------------------
st.title("⚽ Buscador Direto de Times - MyPredicts")

# Cria uma caixa de texto para digitar o nome do clube real na API
termo_busca = st.text_input("Digite o nome do time para pesquisar (Ex: Real Madrid, Flamengo...):", value="")

if termo_busca:
    with st.spinner(f"Buscando '{termo_busca}' diretamente no servidor da API..."):
        try:
            url = f"{BASE_URL}/teams"
            # O parâmetro 'search' faz o filtro por texto direto no banco de dados da API Football
            parametros = {"search": termo_busca}
            response = requests.get(url, headers=HEADERS, params=parametros, timeout=12)
            
            if response.status_code == 200:
                dados_times = response.json().get("response", [])
                
                if dados_times:
                    # Mapeia os times retornados em um dicionário {Nome (País): ID}
                    dict_times = {f"{item['team']['name']} ({item['team']['country']})": item['team']['id'] for item in dados_times}
                    lista_nomes = sorted(list(dict_times.keys()))
                    
                    st.success(f"✅ Encontrado(s) {len(dados_times)} time(s) correspondente(s) na API.")
                    
                    # Exibe o resultado em um seletor para rolagem ou pesquisa rápida
                    time_escolhido = st.selectbox("Selecione o clube encontrado:", options=lista_nomes)
                    
                    # Mostra o ID real e oficial do clube na tela
                    st.info(f"ID oficial do **{time_escolhido}** na API Football: **{dict_times[time_escolhido]}**")
                else:
                    st.warning("⚠️ Nenhum time encontrado com esse nome na API Football. Tente conferir a grafia.")
            else:
                st.error(f"❌ Erro de resposta da API: Código {response.status_code}")
                
        except Exception as e:
            st.error(f"❌ Falha de conexão com a API: {e}")
ornou uma lista vazia ou a conexão falhou. Verifique se o seu token está ativo ou se o limite por minuto foi excedido.")
