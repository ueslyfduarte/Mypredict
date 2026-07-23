import streamlit as st
import cloudscraper

st.title("Teste de Conexão Corrigido: API-Football")

# Busca a chave cadastrada na plataforma web do Streamlit
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    st.error("A variável 'API_KEY' não foi encontrada nos Secrets!")
    st.stop()

# URL oficial e segura de status
url = "https://api-sports.io"

headers = {
    'x-apisports-key': api_key
}

if st.button("Testar Conexão Oficial"):
    with st.spinner("Burlando proteção Cloudflare e Autenticando..."):
        try:
            # Inicializa o scraper que simula perfeitamente um navegador real
            scraper = cloudscraper.create_scraper()
            
            # Faz a requisição usando o scraper no lugar do requests
            response = scraper.get(url, headers=headers)
            
            if response.status_code != 200:
                st.error(f"O servidor retornou um código de erro: {response.status_code}")
                st.text("Texto retornado pelo servidor:")
                st.code(response.text[:500])
            else:
                data = response.json()
                
                if not data.get("errors"):
                    st.success("Conexão validada! Sua API_Football está funcionando. 🎉")
                    
                    status_resposta = data["response"]
                    st.write(f"**Plano Atual:** {status_resposta['subscription']['plan']}")
                    st.write(f"**Requisições do Dia:** {status_resposta['requests']['current']} / {status_resposta['requests']['limit_day']}")
                else:
                    st.error("A API rejeitou a credencial. Verifique se a sua chave nos Secrets está certa.")
                    st.json(data.get("errors"))
                    
        except Exception as e:
            st.error(f"Erro inesperado no aplicativo: {e}")
