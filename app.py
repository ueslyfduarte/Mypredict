import streamlit as st
import requests
from datetime import datetime

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
st.set_page_config(page_title="MyPredicts - Estatísticas", layout="wide")


# ---------------------------------------------------------------------
# BUSCADOR DE TIMES E ESTATÍSTICAS REAL DA API
# ---------------------------------------------------------------------
st.title("📊 MyPredicts - Consulta de Estatísticas")

# 1. Entrada de dados do usuário
termo_busca = st.text_input("Digite o nome do time para pesquisar (Ex: Real Madrid, Flamengo...):", value="")

if termo_busca:
    with st.spinner(f"Buscando '{termo_busca}' no servidor da API..."):
        try:
            # Primeiro passo: Descobrir o ID do time digitado
            url_teams = f"{BASE_URL}/teams"
            response_teams = requests.get(url_teams, headers=HEADERS, params={"search": termo_busca}, timeout=12)
            
            if response_teams.status_code == 200:
                dados_times = response_teams.json().get("response", [])
                
                if dados_times:
                    dict_times = {f"{item['team']['name']} ({item['team']['country']})": item for item in dados_times}
                    lista_nomes = sorted(list(dict_times.keys()))
                    
                    # Abre o seletor com os times reais encontrados
                    time_escolhido = st.selectbox("Selecione o clube desejado:", options=lista_nomes)
                    
                    # Captura o objeto do time selecionado e seu respectivo ID
                    clube_objeto = dict_times[time_escolhido]
                    id_time = clube_objeto['team']['id']
                    
                    st.info(f"ID oficial do time na API Football: **{id_time}**")
                    
                    # 2. Definição automática da temporada e parâmetros para a busca estatística
                    ano_atual = datetime.now().year
                    
                    # Vamos buscar uma liga padrão que este time joga (a primeira listada no cadastro dele)
                    # Nota: futuramente isso será integrado ao seu seletor de ligas do topo
                    id_liga_padrao = 71 if clube_objeto['team']['country'] == "Brazil" else 39 # Fallback rápido se não achar
                    
                    st.write("---")
                    st.subheader(f"📈 Estatísticas Reais para {time_escolhido}")
                    
                    # Botão para disparar o consumo do endpoint de estatísticas
                    if st.button("🔥 Puxar Dados de Gols e Desempenho"):
                        with st.spinner("Conectando ao endpoint /teams/statistics..."):
                            
                            url_stats = f"{BASE_URL}/teams/statistics"
                            parametros_stats = {
                                "league": id_liga_padrao,
                                "season": ano_atual,
                                "team": id_time
                            }
                            
                            response_stats = requests.get(url_stats, headers=HEADERS, params=parametros_stats, timeout=12)
                            
                            if response_stats.status_code == 200:
                                json_stats = response_stats.json().get("response", {})
                                
                                if json_stats:
                                    # Extração da Forma Atual (Ex: W-D-L-W)
                                    forma_atual = json_stats.get("form", "Sem dados de forma recente")
                                    st.write(f"**Sequência Recente (Forma):** `{forma_atual}`")
                                    
                                    # Extração de gols utilizando a estrutura real do JSON da API
                                    gols_dados = json_stats.get("goals", {})
                                    
                                    gols_feitos_casa = gols_dados.get("for", {}).get("total", {}).get("home", 0)
                                    gols_feitos_fora = gols_dados.get("for", {}).get("total", {}).get("away", 0)
                                    total_feitos = gols_feitos_casa + gols_feitos_fora
                                    media_feitos = gols_dados.get("for", {}).get("average", {}).get("total", "0.0")
                                    
                                    gols_sofridos_casa = gols_dados.get("against", {}).get("total", {}).get("home", 0)
                                    gols_sofridos_fora = gols_dados.get("against", {}).get("total", {}).get("away", 0)
                                    total_sofridos = gols_sofridos_casa + gols_sofridos_fora
                                    media_sofridos = gols_dados.get("against", {}).get("average", {}).get("total", "0.0")
                                    
                                    # Renderização visual dos dados extraídos na tela do seu App
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.metric(label="Gols Marcados (Temporada)", value=total_feitos, delta=f"Média: {media_feitos}/jogo")
                                        st.caption(f"Casa: {gols_feitos_casa} | Fora: {gols_feitos_fora}")
                                        
                                    with col2:
                                        st.metric(label="Gols Sofridos (Temporada)", value=total_sofridos, delta=f"Média: {media_sofridos}/jogo", delta_color="inverse")
                                        st.caption(f"Casa: {gols_sofridos_casa} | Fora: {gols_sofridos_fora}")
                                else:
                                    st.warning("A API não possui registros estatísticos consolidados para este clube nesta temporada/liga ainda.")
                            else:
                                st.error(f"Erro no endpoint de estatísticas: Código {response_stats.status_code}")
                                
                else:
                    st.warning("⚠️ Nenhum time encontrado com esse nome na API Football.")
            else:
                st.error(f"❌ Erro de resposta da API ao buscar time: Código {response_teams.status_code}")
                
        except Exception as e:
            st.error(f"❌ Falha física de conexão com a API: {e}")
            conexão falhou. Verifique se o seu token está ativo ou se o limite por minuto foi excedido.")
