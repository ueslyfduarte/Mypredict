import streamlit as st
import requests

# ==========================================
# CONFIGURAÇÃO DE ACESSO DA API (PRODUÇÃO)
# ==========================================
# Este bloco valida sua credencial em segundo plano de forma silenciosa.
if "MINHA_API_KEY" in st.secrets:
    API_KEY = st.secrets["MINHA_API_KEY"]
    HEADERS = {
        'x-apisports-key': API_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
else:
    st.error("⚠️ ERRO CRÍTICO: Configure a tag 'MINHA_API_KEY' no painel do Streamlit.")
    st.stop()  # Interrompe o app caso você esqueça de configurar no site

 (Sua configuração de chaves HEADERS e BASE_URL aqui...)

def puxar_todas_ligas():
    url = f"{BASE_URL}/leagues"
    try:
        response = requests.get(url, headers=HEADERS)
        return response.json().get("response", []) if response.status_code == 200 else []
    except:
        return []
# ==========================================
# DESENVOLVA SEU APLICATIVO ABAIXO
# ==========================================
# A partir daqui a tela está 100% em branco e pronta para o seu layout.




# =====================================================================
# INTERFACE DE ENTRADA (SELEÇÃO EM CASCATA)
# =====================================================================
st.header("🎯 Configuração da Partida")

# 1. Carrega todas as ligas disponíveis na API para o primeiro menu
lista_ligas = puxar_todas_ligas()

# Cria uma lista amigável de nomes para o usuário ler: "Nome da Liga (País)"
opcoes_ligas = {f"{l['league']['name']} ({l['country']['name']})": l['league']['id'] for l in lista_ligas}

liga_escolhida = st.selectbox(
    "Selecione a Liga ou Copa:",
    options=[""] + list(opcoes_ligas.keys()),
    index=0
)

# Se o usuário escolheu uma liga válida, libera o próximo passo
if liga_escolhida != "":
    id_liga_atual = opcoes_ligas[liga_escolhida]
    
    st.divider()
    st.subheader("👥 Seleção dos Times")
    
    # 2. Busca os times da liga selecionada em segundo plano
    # Nota: Ajuste o ano da temporada conforme a necessidade do seu plano da API
    lista_times = puxar_times_da_liga(id_liga=id_liga_atual, ano_temporada=2026)
    opcoes_times = {t['team']['name']: t['team']['id'] for t in lista_times}
    nomes_times = sorted(list(opcoes_times.keys()))
    
    # Cria duas colunas lado a lado para selecionar o confronto
    col1, col2 = st.columns(2)
    
    with col1:
        time_casa = st.selectbox("Mandante (Casa):", options=[""] + nomes_times, index=0)
        
    with col2:
        # Filtra para não deixar selecionar o mesmo time no menu de visitante
        nomes_fora = [t for t in nomes_times if t != time_casa] if time_casa else nomes_times
        time_fora = st.selectbox("Visitante (Fora):", options=[""] + nomes_fora, index=0)
        
    # 3. Validação final: Se ambos os times forem preenchidos, libera o gatilho de extração
    if time_casa != "" and time_fora != "":
        id_casa = opcoes_times[time_casa]
        id_fora = opcoes_times[time_fora]
        
        st.divider()
        
        # Botão principal que executa a busca pesada de dados na API
        if st.button("🚀 Carregar e Armazenar Dados do Confronto", type="primary"):
            with st.spinner("Buscando estatísticas e histórico H2H na API-Football..."):
                
                # Salva os nomes na memória para uso posterior
                st.session_state.time_casa = time_casa
                st.session_state.time_fora = time_fora
                
                # Dispara a função que alimenta o banco_dados_partida em segundo plano
                extrair_e_armazenar_dados_confronto(
                    id_liga=id_liga_atual, 
                    id_casa=id_casa, 
                    id_fora=id_fora, 
                    ano_temporada=2026
                )
                
            st.success(f"Dados de {time_casa} x {time_fora} armazenados com sucesso na memória!")

