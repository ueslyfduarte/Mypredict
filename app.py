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

BASE_URL = "https://api-sports.io"


# ---------------------------------------------------------------------
# [MÓDULO 2] MONITOR DE CONSUMO DA API (TOPO DA PÁGINA)
# ---------------------------------------------------------------------

col_req1, col_req2 = st.columns(2)

with col_req1:
    st.metric(label="📊 Requisições Gastas Hoje", value=st.session_state.requisicoes_feitas)

with col_req2:
    st.metric(label="🚨 Limite do Seu Plano", value=st.session_state.limite_diario)

st.divider()

        st.rerun()
