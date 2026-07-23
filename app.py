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


# ==========================================
# DESENVOLVA SEU APLICATIVO ABAIXO
# ==========================================
# A partir daqui a tela está 100% em branco e pronta para o seu layout.

