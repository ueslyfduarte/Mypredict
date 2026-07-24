@st.cache_data
def buscar_paises():
    url = "https://api-sports.io"
    try:
        response = requests.get(url, headers=headers)
        # Se a API rejeitar a chave, o status não será 200
        if response.status_code != 200:
            st.error(f"Erro da API: Status {response.status_code} - {response.text}")
            return []
        
        dados_json = response.json()
        # Verifica se a API retornou alguma mensagem de erro interna no JSON
        if dados_json.get("errors"):
            st.error(f"Detalhes do erro na API: {dados_json['errors']}")
            return []
            
        return dados_json.get("response", [])
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return []
