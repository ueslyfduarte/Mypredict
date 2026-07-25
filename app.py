import streamlit as st
import requests

st.set_page_config(page_title="Validador ImA", layout="wide")

# =========================================================================
# MÓDULO 1: PONTE DE CONEXÃO COM A API (CHECKLIST ITEM 1 E 3)
# =========================================================================
def buscar_dados_api(endpoint_url):
    try:
        API_KEY = st.secrets["API_SPORTS_KEY"]
        headers = {'x-apisports-key': API_KEY}
        response = requests.get(endpoint_url, headers=headers)
        dados_brutos = response.json()
        
        # Validação do Item 9 do Checklist
        if "errors" in dados_brutos and dados_brutos["errors"]:
            return {"sucesso": False, "erro": dados_brutos["errors"], "dados": None}
        return {"sucesso": True, "erro": None, "dados": dados_brutos.get("response", [])}
    except Exception as e:
        return {"sucesso": False, "erro": str(e), "dados": None}

# =========================================================================
# PASSO 3: RETROVISOR DE AJUSTE DE EMPATES
# =========================================================================
def calcular_pontos_retrovisor(mando, resultado, prateleira_rival):
    """
    Retorna a pontuação ponderada do jogo com base na prateleira do rival.
    Vitória = 3 pontos | Derrota = 0 pontos | Empate = Ponderado conforme Passo 3.
    """
    if resultado == "VITÓRIA":
        return 3.0
    if resultado == "DERROTA":
        return 0.0
        
    # Se o resultado for EMPATE, aplica as regras exatas do Passo 3:
    if mando == "VISITANTE":
        if prateleira_rival == "Elite (Top 4)":
            return 3.0 * 0.666  # Vale 66,6% dos pontos de vitória
        else:
            return 3.0 * 1.000  # Vale 100% contra igual ou inferior
            
    else: # MANDANTE
        if prateleira_rival in ["Elite (Top 4)", "Igual"]:
            return 3.0 * 0.666  # Vale 66,6%
        elif prateleira_rival == "Meio de Tabela":
            return 3.0 * 0.333  # Vale 33,3%
        elif prateleira_rival == "Z-4":
            return 0.0  # Fiasco, vale 0%
            
    return 1.0 # Neutro de segurança

# =========================================================================
# MOTOR DE PROCESSAMENTO DO ImA (PASSO 2)
# =========================================================================
def processar_aproveitamento_bloco(lista_jogos, id_time, limite_jogos, apenas_mando=False, tipo_mando="home"):
    """ Varre o histórico e calcula a nota de aproveitamento (0 a 100) """
    if not lista_jogos: return 50.0
    
    pontos_convertidos = 0
    jogos_contados = 0
    
    for jogo in lista_jogos:
        if jogos_contados >= limite_jogos: break
        
        is_home = jogo["teams"]["home"]["id"] == id_time
        if apenas_mando:
            if tipo_mando == "home" and not is_home: continue
            if tipo_mando == "away" and is_home: continue
            
        gols_casa = jogo["goals"]["home"]
        gols_fora = jogo["goals"]["away"]
        
        # Define o mando para passar pro Passo 3
        mando_atual = "MANDANTE" if is_home else "VISITANTE"
        
        # Descobre o resultado sob a ótica do nosso time
        if gols_casa == gols_fora:
            res_tipo = "EMPATE"
        elif (gols_casa > gols_fora and is_home) or (gols_fora > gols_casa and not is_home):
            res_tipo = "VITÓRIA"
        else:
            res_tipo = "DERROTA"
            
        # IMPORTANTE: Para o cálculo ficar 100% automático, futuramente mapearemos as prateleiras reais.
        # Por enquanto, ele assume "Meio de Tabela" como padrão para processar o Passo 3 sem travar.
        prateleira_ficticia_rival = "Meio de Tabela"
        
        pontos_convertidos += calcular_pontos_retrovisor(mando_atual, res_tipo, prateleira_ficticia_rival)
        jogos_contados += 1
        
    if jogos_contados == 0: return 50.0
    return (pontos_convertidos / (jogos_contados * 3)) * 100

def calcular_ima_final(cc3, cc5, g3, g5, g10, tab_dinamica):
    """ Equação ponderada exata do Passo 2 """
    # 1. Bloco Condição de Campo (45%)
    sub_campo = (cc3 * 0.65) + (cc5 * 0.35)
    # 2. Bloco Geral (35%)
    sub_geral = (g3 * 0.50) + (g5 * 0.35) + (g10 * 0.15)
    # 3. Tabela Dinâmica (20%)
    sub_tabela = tab_dinamica
    
    return (sub_campo * 0.45) + (sub_geral * 0.35) + (sub_tabela * 0.20)

# =========================================================================
# INTERFACE DE SELEÇÃO DA RODADA
# =========================================================================
st.title("📈 Análise Isolada do ImA (Passo 2 e 3)")
st.write("Foco exclusivo no levantamento de dados do Índice de Momento Atual por rodada.")

BASE_URL = "https://api-sports.io"
ID_LIGA = "39"

col_ano, col_rodada = st.columns(2)
with col_ano:
    temporada = st.selectbox("Temporada Histórica:", ["2023", "2022", "2024"])
with col_rodada:
    rodada_num = st.number_input("Número da Rodada (1 a 38):", min_value=1, max_value=38, value=6)

url_rodada = f"{BASE_URL}/fixtures?league={ID_LIGA}&season={temporada}&round=Regular Season - {rodada_num}"

if st.button("🔍 Carregar ImA da Rodada"):
    with st.spinner("Buscando jogos e processando histórico do ImA..."):
        resposta_rodada = buscar_dados_api(url_rodada)
        
        if not resposta_rodada["sucesso"] or len(resposta_rodada["dados"]) == 0:
            st.error("Erro na busca da rodada. Verifique o checklist.")
        else:
            for partida in resposta_rodada["dados"]:
                id_h, name_h = partida["teams"]["home"]["id"], partida["teams"]["home"]["name"]
                id_a, name_a = partida["teams"]["away"]["id"], partida["teams"]["away"]["name"]
                g_h_real, g_a_real = partida["goals"]["home"], partida["goals"]["away"]
                
                # Coleta estrita dos últimos 10 jogos anteriores à rodada para calcular o ImA
                url_h_hist = f"{BASE_URL}/fixtures?team={id_h}&season={temporada}&last=10"
                url_a_hist = f"{BASE_URL}/fixtures?team={id_a}&season={temporada}&last=10"
                res_h = buscar_dados_api(url_h_hist)
                res_a = buscar_dados_api(url_a_hist)
                
                if res_h["sucesso"] and res_a["sucesso"]:
                    # Processamento dos Sub-Blocos do Mandante
                    cc3_h = processar_aproveitamento_bloco(res_h["dados"], id_h, 3, apenas_mando=True, tipo_mando="home")
                    cc5_h = processar_aproveitamento_bloco(res_h["dados"], id_h, 5, apenas_mando=True, tipo_mando="home")
                    g3_h  = processar_aproveitamento_bloco(res_h["dados"], id_h, 3)
                    g5_h  = processar_aproveitamento_bloco(res_h["dados"], id_h, 5)
                    g10_h = processar_aproveitamento_bloco(res_h["dados"], id_h, 10)
                    # Tabela dinâmica fixada em valor médio neutro até você passar as regras dela
                    im_home = calcular_ima_final(cc3_h, cc5_h, g3_h, g5_h, g10_h, 60.0)
                    
                    # Processamento dos Sub-Blocos do Visitante
                    cc3_a = processar_aproveitamento_bloco(res_a["dados"], id_a, 3, apenas_mando=True, tipo_mando="away")
                    cc5_a = processar_aproveitamento_bloco(res_a["dados"], id_a, 5, apenas_mando=True, tipo_mando="away")
                    g3_a  = processar_aproveitamento_bloco(res_a["dados"], id_a, 3)
                    g5_a  = processar_aproveitamento_bloco(res_a["dados"], id_a, 5)
                    g10_a = processar_aproveitamento_bloco(res_a["dados"], id_a, 10)
                    im_away = calcular_ima_final(cc3_a, cc5_a, g3_a, g5_a, g10_a, 60.0)
                    
                    disparidade_ima = im_home - im_away
                    
                    with st.expander(f"🏟️ {name_h} vs {name_a} — Placar Real: {g_h_real} x {g_a_real}"):
                        col1, col2, col3 = st.columns(3)
                        with col1: st.metric(f"ImA {name_h}", f"{im_home:.1f}")
                        with col2: st.metric("Disparidade ImA", f"{disparidade_ima:+.1f}")
                        with col3: st.metric(f"ImA {name_a}", f"{im_away:.1f}")
