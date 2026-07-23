import streamlit as st
import requests

st.title("🔧 Verificador de Chave da API")

# Lê a chave salva no sistema de Secrets do Streamlit
if "MINHA_API_KEY" in st.secrets:
    minha_chave = st.secrets["MINHA_API_KEY"]
    
    # Endpoint de testes que não consome créditos diários
    url = "https://v3.football.api-sports.io/status"
    headers = {
        'x-apisports-key': minha_chave  # Ou 'x-rapidapi-key' se assinou pela RapidAPI
    }

    if st.button("Verificar Conexão"):
        try:
            response = requests.get(url, headers=headers)
            dados = response.json()

            # Se não houver erros na resposta da API
            if response.status_code == 200 and not dados.get("errors"):
                st.success("✅ Sua chave está ativa e funcionando perfeitamente!")
                
                # Mostra informações da sua conta e plano técnico
                conta = dados["response"]["subscription"]
                requisicoes = dados["response"]["requests"]
                st.write(f"**Plano:** {conta['plan']} (Ativo: {conta['active']})")
                st.write(f"**Requisições hoje:** {requisicoes['current']} de {requisicoes['limit_day']}")
            else:
                st.error(f"❌ Erro na API: {dados.get('errors')}")
        except Exception as e:
            st.error(f"Erro ao tentar conectar: {e}")
else:
    st.warning("⚠️ Você ainda não configurou o Secrets com a tag 'MINHA_API_KEY'.")
