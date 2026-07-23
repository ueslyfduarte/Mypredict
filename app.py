import streamlit as st
import requests

st.title("Análise Preditiva - Teste de Conexão")

# 1. Puxa a chave salva no painel do Streamlit
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    st.error("A variável 'API_KEY' não foi encontrada nos Secrets do site!")
    st.stop()

# 2. Rota alternativa oficial da API-Sports para evitar bloqueios de servidores
url = "https://api-sports.io"

headers = {
    'x-apisports-key': api_key
}

# 3. Botão para realizar o teste na tela
if st.button("Verificar Conexão Agora"):
    with st.spinner("Conectando ao servidor..."):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Se a chave estiver errada, a API avisa dentro do JSON
                if data.get("errors"):
                    st.error("A API-Football respondeu, mas diz que sua CHAVE está incorreta:")
                    st.json(data["errors"])
                else:
                    st.success("Sua conexão e sua chave estão 100% corretas! 🎉")
                    
                    # Mostra os dados do seu plano
                    status = data["response"]
                    st.write(f"**Seu Plano:** {status['subscription']['plan']}")
                    st.write(f"**Requisições Restantes Hoje:** {status['requests']['current']} / {status['requests']['limit_day']}")
            else:
                st.error(f"Erro no servidor. Código: {response.status_code}")
                
        except Exception as e:
            st.error(f"Erro ao tentar conectar: {e}")
