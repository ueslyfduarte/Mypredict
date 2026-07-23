import streamlit as st
import requests

st.title("Análise Preditiva - Teste de Conexão")

# 1. Puxa a chave salva no painel de Secrets do Streamlit Cloud
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    st.error("A variável 'API_KEY' não foi encontrada nos Secrets do site!")
    st.stop()

# 2. URL original envelopada dentro do Proxy para mascarar o IP do Streamlit
url_original = "https://api-sports.io"
url = f"https://allorigins.win{url_original}"

headers = {
    'x-apisports-key': api_key
}

# 3. Botão para realizar o teste de validação na tela
if st.button("Verificar Conexão Agora"):
    with st.spinner("Conectando de forma segura através do Proxy..."):
        try:
            # Faz a requisição através da ponte do proxy
            response = requests.get(url, headers=headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                # Se houver algum erro de digitação na chave, a API nos avisa aqui
                if data.get("errors"):
                    st.error("O servidor respondeu, mas a sua CHAVE está inválida ou incorreta:")
                    st.json(data["errors"])
                else:
                    st.success("Sua conexão e sua chave estão 100% corretas! 🎉")
                    
                    # Exibe os limites do seu plano na tela
                    status = data["response"]
                    st.write(f"**Seu Plano:** {status['subscription']['plan']}")
                    st.write(f"**Requisições Hoje:** {status['requests']['current']} / {status['requests']['limit_day']}")
            else:
                st.error(f"O Proxy retornou o código de erro: {response.status_code}")
                st.code(response.text[:300])
                
        except Exception as e:
            st.error(f"Não foi possível alcançar o servidor: {e}")

