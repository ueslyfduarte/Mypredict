import streamlit as st
import requests

st.title("Teste de Conexão Definitivo: API-Football")

# Busca a chave cadastrada na plataforma web do Streamlit
if "API_KEY" in st.secrets:
    api_key = st.secrets["API_KEY"]
else:
    st.error("A variável 'API_KEY' não foi encontrada nos Secrets!")
    st.stop()

# URL e Headers otimizados para evitar o bloqueio da Cloudflare
url = "https://api-sports.io"

headers = {
    'x-apisports-key': api_key,
    'Accept': 'application/json',
    'Connection': 'keep-alive'
}

if st.button("Testar Conexão Oficial"):
    with st.spinner("Autenticando com o servidor de dados..."):
        try:
            # Cria uma sessão HTTP estável para manter os cabeçalhos limpos
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=15)
            
            if response.status_code == 403:
                st.error("Erro 403: Acesso negado pelo servidor.")
                st.info("Dica: Confirme se o código inserido no painel de Secrets do Streamlit não possui espaços em branco ou aspas duplicadas.")
                st.code(response.text[:300])
                
            elif response.status_code != 200:
                st.error(f"O servidor retornou um código de erro: {response.status_code}")
                st.code(response.text[:300])
                
            else:
                data = response.json()
                
                # Valida se a chave foi aceita internamente pelo sistema da API-Sports
                if data.get("errors"):
                    st.error("A API-Sports recusou o token fornecido:")
                    st.json(data["errors"])
                else:
                    st.success("Conexão estabelecida com sucesso! 🎉")
                    
                    status_resposta = data["response"]
                    st.write(f"**Plano Ativo:** {status_resposta['subscription']['plan']}")
                    st.write(f"**Requisições Consumidas Hoje:** {status_resposta['requests']['current']} / {status_resposta['requests']['limit_day']}")
                    
        except requests.exceptions.Timeout:
            st.error("Tempo limite esgotado ao tentar alcançar o servidor da API.")
        except Exception as e:
            st.error(f"Erro inesperado no sistema: {e}")
