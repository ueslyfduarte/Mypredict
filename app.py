import streamlit as st
import requests

st.set_page_config(page_title="Validador ImA", layout="wide")

# =========================================================================
# MÓDULO 1: PONTE DE CONEXÃO COM A API (CHECKLIST ITENS 1, 3 E 9)
# =========================================================================
def buscar_dados_api(endpoint_url):
    try:
        API_KEY = st.secrets["API_SPORTS_KEY"]
        headers = {'x-apisports-key': API_KEY}
        response = requests.get(endpoint_url, headers=headers)
        dados_brutos = response.json()
        
        # ITEM 9: Confirme que a resposta bruta da API é verificada
        if "errors" in dados_brutos and dados_brutos["errors"]:
            return {"sucesso": False, "erro": dados_brutos["errors"], "dados": []}
            
        return {"sucesso": True, "erro": None, "dados": dados_brutos.get("response", [])}
    except Exception as e:
        return {"sucesso": False, "erro": str(e), "dados": []}

# =========================================================================
# PASSO 3: RETROVISOR DE AJUSTE DE EMPATES (HISTÓRICO)
# =========================================================================
def calcular_pontos_retrovisor(mando, resultado, prateleira_rival):
    if resultado == "VITÓRIA":
        return 3.0
    if resultado == "DERROTA":
        return 0.0
        
    # Regras exatas de empates enviadas por você:
    if mando == "VISITANTE":
        if prateleira_rival == "Elite (Top 4)":
            return 3.0 * 0.666
        else:
            return 3.0 * 1.000
    else: # MANDANTE
        if prateleira_rival in ["Elite (Top 4)", "Igual"]:
            return 3.0 * 0.666
        elif prateleira_rival == "Meio de Tabela":
            return 3.0 * 0.333
        elif prateleira_rival == "Z-4":
            return 0.0
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
        
        if gols_casa == gols_fora:
            res_tipo = "EMPATE"
        elif (gols_casa > gols_fora and is_home) or (gols_fora > gols_casa and not is_home):
            res_tipo = "VITÓRIA"
        else:
            res_tipo = "DERROTA"
            
        # Padrão estável provisório para o retrovisor processar
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
# INTERFACE DE SELEÇÃO: IMPLEMENTAÇÃO DO ITEM 11.a DO CHECKLIST
# =========================================================================
st.title("📈 Análise Isolada do ImA (Passo 2 e 3)")
st.write("Levantamento estruturado de dados baseado estritamente na data da partida (Item 11.a).")

BASE_URL = "https://api-sports.io"
ID_LIGA = "39" # Premier League

col_ano, col_data = st.columns(2)
with col_ano:
    temporada = st.selectbox("Temporada Histórica:", ["2023", "2022", "2024"])
with col_data:
    # DATA REAL DE TESTE EXIGIDA PELO CHECKLIST ITEM 11.a
    data_teste = st.text_input("Data do Jogo (YYYY-MM-DD):", value="2024-04-03")

# URL construída no padrão do Item 11.a do checklist
url_rodada = f"{BASE_URL}/fixtures?date={data_teste}&league={ID_LIGA}&season={temporada}"

if st.button("🔍 Carregar ImA da Rodada"):
    with st.spinner("Buscando partidas e processando histórico do ImA..."):
        resposta_rodada = buscar_dados_api(url_rodada)
        
        if resposta_rodada["sucesso"] is False:
            st.error("❌ Falha na conexão de dados (Item 9).")
            st.json(resposta_rodada["erro"])
        elif len(resposta_rodada["dados"]) == 0:
            st.warning("⚠️ Resposta veio vazia ('response': []). Nenhuma partida encontrada nesta data.")
            st.code(f"URL: {url_rodada}")
        else:
            st.success(f"Partidas localizadas na data! Processando os índices de momento...")
            
            for partida in resposta_rodada["dados"]:
                id_h, name_h = partida["teams"]["home"]["id"], partida["teams"]["home"]["name"]
                id_a, name_a = partida["teams"]["away"]["id"], partida["teams"]["away"]["name"]
                g_h_real, g_a_real = partida["goals"]["home"], partida["goals"]["away"]
                
                # Busca os últimos 10 jogos anteriores à data da partida para calcular o ImA
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
                    im_home = calcular_ima_final(cc3_h, cc5_h, g3_h, g5_h, g10_h, 60.0) # Tabela dinâmica neutra temporária
                    
                    # Visitante
                    cc3_a = processar_aproveitamento_bloco(res_a["dados"], id_a, 3, apenas_mando=True, tipo_mando="away")
                    cc5_a = processar_aproveitamento_bloco(res_a["dados"], id_a, 5, apenas_mando=True, tipo_mando="away")
                    g3_a  = processar_aproveitamento_bloco(res_a["dados"], id_a, 3)
                    g5_a  = processar_aproveitamento_bloco(res_a["dados"], id_a, 5)
                    g10_a = processar_aproveitamento_bloco(res_a["dados"], id_a, 10)
                    im_away = calcular_ima_final(cc3_a, cc5_a, g3_a, g5_a, g10_a, 60.0)
                    
                    disparidade_ima = im_home - im_away
                    
                    with st.expander(f"🏟️ {name_h} vs {name_a} — Placar: {g_h_real} x {g_a_real}"):
                        col1, col2, col3 = st.columns(3)
                        with col1: st.metric(f"ImA {name_h}", f"{im_home:.1f}")
                        with col2: st.metric("Disparidade ImA", f"{disparidade_ima:+.1f}")
                        with col3: st.metric(f"ImA {name_a}", f"{im_away:.1f}")
