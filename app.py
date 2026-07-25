import streamlit as st
import requests

st.set_page_config(page_title="Analisador ImA por Confronto", layout="wide")

# =========================================================================
# MÓDULO 1: PONTE DE CONEXÃO COM A API
# =========================================================================
def buscar_dados_api(endpoint_url):
    try:
        API_KEY = st.secrets["API_SPORTS_KEY"]
        headers = {'x-apisports-key': API_KEY}
        response = requests.get(endpoint_url, headers=headers)
        dados_brutos = response.json()
        
        if "errors" in dados_brutos and dados_brutos["errors"]:
            return {"sucesso": False, "erro": dados_brutos["errors"], "dados": []}
            
        return {"sucesso": True, "erro": None, "dados": dados_brutos.get("response", [])}
    except Exception as e:
        return {"sucesso": False, "erro": str(e), "dados": []}

# =========================================================================
# PASSO 3: RETROVISOR DE AJUSTE DE EMPATES
# =========================================================================
def calcular_pontos_retrovisor(mando, resultado, prateleira_rival):
    if resultado == "VITÓRIA": return 3.0
    if resultado == "DERROTA": return 0.0
    
    if mando == "VISITANTE":
        if prateleira_rival == "Elite (Top 4)": return 3.0 * 0.666
        else: return 3.0 * 1.000
    else: # MANDANTE
        if prateleira_rival in ["Elite (Top 4)", "Igual"]: return 3.0 * 0.666
        elif prateleira_rival == "Meio de Tabela": return 3.0 * 0.333
        elif prateleira_rival == "Z-4": return 0.0
    return 1.0

# =========================================================================
# MOTOR DE PROCESSAMENTO DO ImA (PASSO 2)
# =========================================================================
def processar_aproveitamento_bloco(lista_jogos, id_time, limite_jogos, apenas_mando=False, tipo_mando="home"):
    if not lista_jogos: return 50.0
    pontos_convertidos, jogos_contados = 0, 0
    
    for jogo in lista_jogos:
        if jogos_contados >= limite_jogos: break
        is_home = jogo["teams"]["home"]["id"] == id_time
        if apenas_mando:
            if tipo_mando == "home" and not is_home: continue
            if tipo_mando == "away" and is_home: continue
            
        gols_casa = jogo["goals"]["home"]
        gols_fora = jogo["goals"]["away"]
        mando_atual = "MANDANTE" if is_home else "VISITANTE"
        
        if gols_casa == gols_fora: res_tipo = "EMPATE"
        elif (gols_casa > gols_fora and is_home) or (gols_fora > gols_casa and not is_home): res_tipo = "VITÓRIA"
        else: res_tipo = "DERROTA"
            
        prateleira_ficticia_rival = "Meio de Tabela"
        pontos_convertidos += calcular_pontos_retrovisor(mando_atual, res_tipo, prateleira_ficticia_rival)
        jogos_contados += 1
        
    if jogos_contados == 0: return 50.0
    return (pontos_convertidos / (jogos_contados * 3)) * 100

def calcular_ima_final(cc3, cc5, g3, g5, g10, tab_dinamica):
    sub_campo = (cc3 * 0.65) + (cc5 * 0.35)
    sub_geral = (g3 * 0.50) + (g5 * 0.35) + (g10 * 0.15)
    return (sub_campo * 0.45) + (sub_geral * 0.35) + (tab_dinamica * 0.20)

# =========================================================================
# INTERFACE DE SELEÇÃO INTELIGENTE
# =========================================================================
st.title("📈 Analisador Inteligente de Confrontos (ImA)")
st.write("Selecione a temporada para listar os confrontos e datas reais disponíveis.")

BASE_URL = "https://v3.football.api-sports.io"
ID_LIGA = "39" # Premier League

temporada = st.selectbox("1º Passo: Escolha a Temporada Histórica:", ["2023", "2022", "2024"])

# Chamada automática para buscar TODAS as partidas do ano e alimentar o menu
url_todas_fixtures = f"{BASE_URL}/fixtures?league={ID_LIGA}&season={temporada}"

with st.spinner("Mapeando calendário e buscando datas dos jogos na API..."):
    resposta_calendario = buscar_dados_api(url_todas_fixtures)

if resposta_calendario["sucesso"] and resposta_calendario["dados"]:
    lista_jogos_brutos = resposta_calendario["dados"]
    
    # Cria uma lista formatada em texto para o usuário escolher no menu do Streamlit
    opcoes_menu = []
    mapa_confrontos = {}
    
    for item in lista_jogos_brutos:
        data_resumida = item["fixture"]["date"][:10] # Pega apenas YYYY-MM-DD
        rodada_nome = item["fixture"]["round"]
        casa = item["teams"]["home"]["name"]
        fora = item["teams"]["away"]["name"]
        
        texto_opcao = f"📅 {data_resumida} - ({rodada_nome}) - {casa} vs {fora}"
        opcoes_menu.append(texto_opcao)
        mapa_confrontos[texto_opcao] = item
        
    # Ordena as opções por data para facilitar a busca do usuário
    opcoes_menu.sort()
    
    confronto_selecionado = st.selectbox("2º Passo: Selecione o Confronto Desejado:", options=opcoes_menu)
    
    if st.button("🚀 Calcular ImA Deste Confronto"):
        jogo_escolhido = mapa_confrontos[confronto_selecionado]
        
        id_h = jogo_escolhido["teams"]["home"]["id"]
        name_h = jogo_escolhido["teams"]["home"]["name"]
        id_a = jogo_escolhido["teams"]["away"]["id"]
        name_a = jogo_escolhido["teams"]["away"]["name"]
        g_h_real = jogo_escolhido["goals"]["home"]
        g_a_real = jogo_escolhido["goals"]["away"]
        
        with st.spinner(f"Varrendo histórico de {name_h} e {name_a}..."):
            url_h_hist = f"{BASE_URL}/fixtures?team={id_h}&season={temporada}&last=10"
            url_a_hist = f"{BASE_URL}/fixtures?team={id_a}&season={temporada}&last=10"
            
            res_h = buscar_dados_api(url_h_hist)
            res_a = buscar_dados_api(url_a_hist)
            
            if res_h["sucesso"] and res_a["sucesso"]:
                # Mandante
                cc3_h = processar_aproveitamento_bloco(res_h["dados"], id_h, 3, apenas_mando=True, tipo_mando="home")
                cc5_h = processar_aproveitamento_bloco(res_h["dados"], id_h, 5, apenas_mando=True, tipo_mando="home")
                g3_h  = processar_aproveitamento_bloco(res_h["dados"], id_h, 3)
                g5_h  = processar_aproveitamento_bloco(res_h["dados"], id_h, 5)
                g10_h = processar_aproveitamento_bloco(res_h["dados"], id_h, 10)
                im_home = calcular_ima_final(cc3_h, cc5_h, g3_h, g5_h, g10_h, 60.0)
                
                # Visitante
                cc3_a = processar_aproveitamento_bloco(res_a["dados"], id_a, 3, apenas_mando=True, tipo_mando="away")
                cc5_a = processar_aproveitamento_bloco(res_a["dados"], id_a, 5, apenas_mando=True, tipo_mando="away")
                g3_a  = processar_aproveitamento_bloco(res_a["dados"], id_a, 3)
                g5_a  = processar_aproveitamento_bloco(res_a["dados"], id_a, 5)
                g10_a = processar_aproveitamento_bloco(res_a["dados"], id_a, 10)
                im_away = calcular_ima_final(cc3_a, cc5_a, g3_a, g5_a, g10_a, 60.0)
                
                disparidade_ima = im_home - im_away
                
                st.markdown("### 📊 Laudo Crítico do Confronto")
                st.info(f"**Resultado oficial ocorrido no dia:** {g_h_real} x {g_a_real}")
                
                col1, col2, col3 = st.columns(3)
                with col1: st.metric(f"ImA {name_h} (Mandante)", f"{im_home:.1f}")
                with col2: st.metric("Disparidade ImA", f"{disparidade_ima:+.1f}")
                with col3: st.metric(f"ImA {name_a} (Visitante)", f"{im_away:.1f}")
else:
    st.error("Falha ao mapear o calendário da liga ou limite atingido. Verifique seus Secrets.")

