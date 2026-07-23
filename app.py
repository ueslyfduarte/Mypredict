import streamlit as st
import requests
from datetime import datetime




# ---------------------------------------------------------------------
# [MÓDULO 1] ACESSO DA API E CONFIGURAÇÕES GLOBAIS
# ---------------------------------------------------------------------

if "MINHA_API_KEY" in st.secrets:
    HEADERS = {
        'x-apisports-key': st.secrets["MINHA_API_KEY"],
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
else:
    st.error("⚠️ ERRO CRÍTICO: Configure a tag 'MINHA_API_KEY' no painel do Streamlit.")
    st.stop()

BASE_URL = "https://v3.football.api-sports.io"




# ---------------------------------------------------------------------
# [MÓDULO 2] INICIALIZAÇÃO DA MEMÓRIA DO APP (SESSION STATE)
# ---------------------------------------------------------------------

if "liga_selecionada" not in st.session_state:
    st.session_state.liga_selecionada = None

if "time_casa" not in st.session_state:
    st.session_state.time_casa = None

if "time_fora" not in st.session_state:
    st.session_state.time_fora = None

if "requisicoes_feitas" not in st.session_state:
    st.session_state.requisicoes_feitas = 0

if "limite_diario" not in st.session_state:
    st.session_state.limite_diario = 





# ---------------------------------------------------------------------
# [MÓDULO 4] MONITOR DE CONSUMO DA API (TOPO DA PÁGINA)
# ---------------------------------------------------------------------

col_req1, col_req2 = st.columns(2)

with col_req1:
    st.metric(label="📊 Requisições Gastas Hoje", value=st.session_state.requisicoes_feitas)

with col_req2:
    st.metric(label="🚨 Limite do Seu Plano", value=st.session_state.limite_diario)

st.write("")
st.write("")
st.divider()
st.write("")
st.write("")





        
        if st.session_state.requisicoes_feitas >= st.session_state.limite_diario:
            st.error("❌ Limite diário de requisições atingido! Volte amanhã para coletar mais dados.")
        else:
            if st.button("🚀 Carregar e Armazenar Dados do Confronto", type="primary"):
                with st.spinner(f"Buscando dados de {temporada_selecionada} na API-Football..."):
                    st.session_state.time_casa = time_casa
                    st.session_state.time_fora = time_fora
                    
                    extrair_e_armazenar_dados_confronto(
                        id_liga=id_liga_atual, 
                        id_casa=id_casa, 
                        id_fora=id_fora, 
                        ano_temporada=ano_api
                    )
                st.rerun()
