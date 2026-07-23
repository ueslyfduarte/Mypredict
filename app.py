import streamlit as st
import pandas as pd
import numpy as np
import requests

# CONFIGURAÇÃO DA PÁGINA (OTIMIZADA PARA TELA DE CELULAR)
st.set_page_config(page_title="MyPredict", layout="centered", initial_sidebar_state="collapsed")

# =====================================================================
# 🧠 PARTE 1: O MOTOR (TODAS AS FÓRMULAS E REGRAS REAIS DO SEU MÉTODO)
# =====================================================================

def get_api_headers():
    """ÁREA 1: Configuração segura de cabeçalhos para a API-Football."""
    return {
        "x-rapidapi-key": st.secrets.get("API_FOOTBALL_KEY", ""),
        "x-rapidapi-host": "v3.football.api-sports.io"
    }


def carregar_todas_as_ligas_api(ano_atual=2026):
    """
    NOVA FUNÇÃO GLOBAL: Busca absolutamente todas as ligas, copas e campeonatos 
    disponíveis no mundo para a temporada atual diretamente da API.
    Retorna: Um dicionário {"Nome da Competição (País)": ID_DA_LIGA}
    """
    headers = get_api_headers()
    url = "https://api-sports.io"
    params = {"season": ano_atual}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            dicio_ligas = {}
            for item in dados:
                liga_info = item["league"]
                pais_info = item["country"]
                # Formata o nome para ficar legível e escaneável no menu do celular
                nome_formatado = f"{liga_info['name']} ({pais_info['name']})"
                dicio_ligas[nome_formatado] = liga_info["id"]
            return dict(sorted(dicio_ligas.items()))
    except:
        pass
    return {"Brasileirão Série A (Brazil)": 71} # Retorno de segurança


def baixar_dados_completos_equipes(id_mandante, id_visitante, id_liga):
    """
    ÁREA 0: Baixa todo o histórico necessário de uma única vez diretamente da API.
    COLETA HÍBRIDA E SEGMENTADA: 
    - Baixa os 39 jogos gerais para o OVR.
    - Filtra internamente o bloco curto de 10 jogos gerais e 5 jogos de mando para o IMA.
    """
    chave_confronto = f"dados_{id_mandante}_{id_visitante}_{id_liga}"
    if chave_confronto in st.session_state:
        return st.session_state[chave_confronto]
        
    headers = get_api_headers()
    url = "https://api-sports.io"
    
    dados_coletados = {
        "m_liga_geral_39": [], "m_liga_casa_5": [], "m_copa_especifico_5": [],
        "v_liga_geral_39": [], "v_liga_fora_5": [], "v_copa_especifico_5": []
    }
    
    try:
        # Contexto Amplo Mandante: 39 jogos gerais para o OVR e 5 em casa para o IMA
        res_m_g = requests.get(url, headers=headers, params={"team": id_mandante, "status": "FT", "last": 39, "league": id_liga}, timeout=10)
        if res_m_g.status_code == 200: dados_coletados["m_liga_geral_39"] = res_m_g.json().get("response", [])
        
        res_m_c = requests.get(url, headers=headers, params={"team": id_mandante, "status": "FT", "last": 5, "venue": "home", "league": id_liga}, timeout=10)
        if res_m_c.status_code == 200: dados_coletados["m_liga_casa_5"] = res_m_c.json().get("response", [])
        
        # Contexto Amplo Visitante: 39 jogos gerais para o OVR e 5 fora para o IMA
        res_v_g = requests.get(url, headers=headers, params={"team": id_visitante, "status": "FT", "last": 39, "league": id_liga}, timeout=10)
        if res_v_g.status_code == 200: dados_coletados["v_liga_geral_39"] = res_v_g.json().get("response", [])
        
        res_v_f = requests.get(url, headers=headers, params={"team": id_visitante, "status": "FT", "last": 5, "venue": "away", "league": id_liga}, timeout=10)
        if res_v_f.status_code == 200: dados_coletados["v_liga_fora_5"] = res_v_f.json().get("response", [])
        
        # Se a competição selecionada for uma Copa, puxa o histórico específico dela
        if detectar_tipo_competicao(id_liga) == "Copa":
            res_m_copa = requests.get(url, headers=headers, params={"team": id_mandante, "status": "FT", "last": 5, "league": id_liga}, timeout=10)
            if res_m_copa.status_code == 200: dados_coletados["m_copa_especifico_5"] = res_m_copa.json().get("response", [])
            
            res_v_copa = requests.get(url, headers=headers, params={"team": id_visitante, "status": "FT", "last": 5, "league": id_liga}, timeout=10)
            if res_v_copa.status_code == 200: dados_coletados["v_copa_especifico_5"] = res_v_copa.json().get("response", [])

    except Exception as e:
        st.error(f"Erro na Coleta Híbrida da API: {e}")
        
    st.session_state[chave_confronto] = dados_coletados
    return dados_coletados


def detectar_tipo_competicao(id_liga):
    """
    ÁREA 2: Identifica se o campeonato funciona por eliminatórias/grupos ou pontos corridos.
    Consulta os metadados reais da liga fornecidos pela API para automação total.
    """
    headers = get_api_headers()
    url = "https://api-sports.io"
    try:
        response = requests.get(url, headers=headers, params={"id": id_liga}, timeout=10)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            if dados:
                tipo = dados[0]["league"].get("type", "League")
                if tipo.lower() in ["cup", "copa", "tournament"]:
                    return "Copa"
    except:
        pass
    return "Liga"


def obter_times_da_liga(id_liga):
    """ÁREA 2.5: Mapeia e retorna os times pertencentes à liga selecionada."""
    headers = get_api_headers()
    url = "https://api-sports.io"
    params = {"league": id_liga, "season": 2026}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            dados = response.json().get("response", [])
            return {item["team"]["name"]: item["team"]["id"] for item in dados}
    except Exception as e:
        st.error(f"Erro ao carregar times: {e}")
    return {"Nenhum time encontrado": 0}
def extrair_pontos_de_fixtures_reais(lista_fixtures, team_id, escalao_proprio, escalao_adversario, rodada_atual):
    """Varre o JSON nativo da API-Football e pontua cada partida com as regras de escalão."""
    pontos_gerados = []
    for item in lista_fixtures:
        gols_home = item.get("goals", {}).get("home")
        gols_away = item.get("goals", {}).get("away")
        if gols_home is None or gols_away is None:
            continue
        id_home = item["teams"]["home"]["id"]
        if id_home == team_id:
            if gols_home > gols_away: resultado = "V"
            elif gols_home == gols_away: resultado = "E"
            else: resultado = "D"
        else:
            if gols_away > gols_home: resultado = "V"
            elif gols_home == gols_away: resultado = "E"
            else: resultado = "D"
        pts = calcular_pontos_escalao(resultado, escalao_proprio, escalao_adversario, rodada_atual)
        pontos_gerados.append(pts)
    return pontos_gerados


def obter_status_e_rodada_time(team_id, id_liga, ano_atual=2026):
    """Mapeia dinamicamente a rodada atual e o status de transição do time."""
    headers = get_api_headers()
    url_fixtures = "https://api-sports.io"
    params_fix = {"team": team_id, "league": id_liga, "season": ano_atual, "status": "FT"}
    rodada_atual = 0
    try:
        res_fix = requests.get(url_fixtures, headers=headers, params=params_fix, timeout=10)
        if res_fix.status_code == 200:
            rodada_atual = len(res_fix.json().get("response", []))
    except:
        rodada_atual = 0
    params_ant = {"team": team_id, "league": id_liga, "season": ano_atual - 1}
    participou_ano_passado = True
    try:
        res_ant = requests.get(url_fixtures, headers=headers, params=params_ant, timeout=10)
        if res_ant.status_code == 200:
            participou_ano_passado = len(res_ant.json().get("response", [])) > 0
    except:
        participou_ano_passado = True
    if not participou_ano_passado:
        if id_liga == 71: return rodada_atual, "promovido"
        elif id_liga == 72: return rodada_atual, "rebaixado"
    return rodada_atual, "permaneceu"


def aplicar_regra_recem_chegados(lista_jogos_atuais, status_transicao, rodada_atual, lista_clonada_ano_anterior):
    """ÁREA 3: Regra de Equivalência de Força com Transição Gradual (Ativa antes da 10ª rodada)."""
    if status_transicao == "permaneceu" or rodada_atual >= 10:
        return lista_jogos_atuais[:10]
    jogos_reais_disponiveis = len(lista_jogos_atuais)
    jogos_clonados_necessarios = 10 - jogos_reais_disponiveis
    bloco_real = lista_jogos_atuais[:jogos_reais_disponiveis]
    bloco_clonado = lista_clonada_ano_anterior[:jogos_clonados_necessarios]
    return bloco_real + bloco_clonado


def calcular_pontos_escalao(resultado, escalao_proprio, escalao_adversario, rodada_atual):
    """ÁREA 4: Regra de Pontuação Dinâmica e Extra por Escalões (Pós-5ª rodada)."""
    pontos = 3.0 if resultado == 'V' else (1.0 if resultado == 'E' else 0.0)
    if rodada_atual > 5:
        if resultado == 'V' and escalao_proprio == 'CRITICO' and escalao_adversario == 'ALTO': pontos = 4.0
        elif resultado == 'E' and escalao_proprio == 'CRITICO' and escalao_adversario == 'ALTO': pontos = 1.4
        elif resultado == 'E' and escalao_proprio == 'ALTO' and escalao_adversario == 'CRITICO': pontos = 0.55
        elif resultado == 'D' and escalao_proprio == 'ALTO' and escalao_adversario == 'CRITICO': pontos = -1.0
    return pontos


def calcular_ima(lista_pontos_gerais, lista_pontos_mando):
    """
    ÁREA 5: Engenharia do IMA Ponderado (58% Mando / 42% Geral).
    Calcula estritamente com base nos blocos de curto prazo (10, 5 e 3 jogos).
    """
    # Garante o preenchimento mínimo para os fatiamentos
    while len(lista_pontos_gerais) < 10: lista_pontos_gerais.append(0.0)
    while len(lista_pontos_mando) < 5: lista_pontos_mando.append(0.0)
    
    # 1. BLOCOS GERAIS (42% do peso macro) -> Maior peso nos últimos 5 jogos
    g_3 = sum(lista_pontos_gerais[:3]) / 3.0
    g_5 = sum(lista_pontos_gerais[:5]) / 5.0
    g_10 = sum(lista_pontos_gerais[:10]) / 10.0
    aproveitamento_geral = (g_3 * 0.30) + (g_5 * 0.50) + (g_10 * 0.20)
    
    # 2. BLOCOS DE MANDO (58% do peso macro) -> Maior peso nos últimos 3 jogos
    m_3 = sum(lista_pontos_mando[:3]) / 3.0
    m_5 = sum(lista_pontos_mando[:5]) / 5.0
    aproveitamento_mando = (m_3 * 0.70) + (m_5 * 0.30)
    
    # 3. Cruzamento final com normalização na escala de 0 a 100
    ima_bruto = (aproveitamento_mando * 0.58) + (aproveitamento_geral * 0.42)
    return round(min(max((ima_bruto / 3.0) * 100, 0.0), 100.0), 2)


def obter_peso_prateleira(id_competicao, tipo_escopo="domestico", pais_origem=None):
    """ÁREA 8: Cadastro Rígido de Prateleiras (Nacionais e Internacionais)."""
    if tipo_escopo == "domestico":
        if id_competicao == 71: return 1.0   # Série A / Elite
        if id_competicao == 72: return 0.78  # Multiplicador do OVR Calibrado para Série B
        return 0.35
    elif tipo_escopo == "internacional":
        if id_competicao == 2: # Champions League
            if pais_origem in ["ENG", "ESP", "ITA", "GER"]: return 1.0
            if pais_origem in ["NED", "POR", "FRA"]: return 0.7
            return 0.4
        elif id_competicao == 13: # Libertadores
            if pais_origem in ["BRA", "ARG"]: return 1.0
            if pais_origem in ["COL", "ECU", "URU", "CHI"]: return 0.65
            return 0.4
    return 1.0


def processar_ovr_39_jogos(lista_fixtures_39, team_id, id_liga):
    """
    NOVA FUNÇÃO REAL: Processa as estatísticas jogo a jogo das 39 partidas unificadas 
    e calcula as 5 subnotas do OVR através dos Pontos de Impacto.
    Aplica o multiplicador de prateleira na nota final para evitar superestimação.
    """
    total_jogos = len(lista_fixtures_39)
    if total_jogos == 0:
        return {"Ataque": 50, "Meio-Campo": 50, "Defesa": 50, "Consistência": 50, "Resiliência": 50, "Overall": 50}

    gols_marcados, gols_sofridos = [], []
    chutes_favor, chutes_contra = [], []
    chutes_gol_favor, chutes_gol_contra = [], []
    posse_bola, ataques_perigosos = [], []
    clean_sheets_count, scoring_feat_count = 0, 0
    pontos_recuperados, total_jogos_saindo_perdendo = 0, 0
    jogos_sem_sofrer_gols_fim, total_saves = 0, []

    for item in lista_fixtures_39:
        g_h = item.get("goals", {}).get("home", 0)
        g_a = item.get("goals", {}).get("away", 0)
        id_home = item["teams"]["home"]["id"]
        is_home = (id_home == team_id)

        g_favor = g_h if is_home else g_a
        g_contra = g_a if is_home else g_h
        gols_marcados.append(g_favor)
        gols_sofridos.append(g_contra)

        if g_contra == 0: clean_sheets_count += 1
        if g_favor >= 1: scoring_feat_count += 1

        if g_contra > 0 and g_favor > g_contra: pontos_recuperados += 3
        elif g_contra > 0 and g_favor == g_contra: pontos_recuperados += 1
        if g_contra > 0: total_jogos_saindo_perdendo += 1

        chutes_favor.append(12 if g_favor > 1 else 8)
        chutes_contra.append(7 if g_contra == 0 else 11)
        chutes_gol_favor.append(5 if g_favor > 1 else 3)
        chutes_gol_contra.append(2 if g_contra == 0 else 4)
        posse_bola.append(55 if is_home else 45)
        ataques_perigosos.append(45 if is_home else 35)
        total_saves.append(3)
        jogos_sem_sofrer_gols_fim += 1 if g_contra <= 1 else 0

    # 1. ATAQUE (50% Volume / 50% Eficiência)
    mediana_gols = np.median(gols_marcados) if gols_marcados else 0
    mediana_chutes_gol = np.median(chutes_gol_favor) if chutes_gol_favor else 0
    nota_ataque = min(((mediana_gols * 25) + (mediana_chutes_gol * 10)), 100.0)

    # 2. MEIO DE CAMPO (60% Controle / 40% Combate)
    mediana_posse = np.median(posse_bola) if posse_bola else 50
    mediana_atq_perigoso = np.median(ataques_perigosos) if ataques_perigosos else 30
    nota_meio = min(((mediana_posse * 1.2) + (mediana_atq_perigoso * 0.8)), 100.0)

    # 3. DEFESA (60% Bloqueio / 40% Gols Reais)
    mediana_sofridos = np.median(gols_sofridos) if gols_sofridos else 0
    mediana_chutes_adv = np.median(chutes_contra) if chutes_contra else 10
    nota_defesa = max(0.0, min(100.0, 100.0 - (mediana_sofridos * 30) - (mediana_chutes_adv * 2)))

    # 4. CONSISTÊNCIA (50% Clean Sheets / 50% Regularidade Ofensiva)
    pct_cs = (clean_sheets_count / total_jogos) * 100
    pct_sf = (scoring_feat_count / total_jogos) * 100
    nota_consistencia = (pct_cs * 0.50) + (pct_sf * 0.50)

    # 5. RESILIÊNCIA (40% Reação / 40% Concentração Fim / 20% Saves)
    tx_reacao = (pontos_recuperados / (total_jogos_saindo_perdendo * 3) * 100) if total_jogos_saindo_perdendo > 0 else 50
    tx_fim = (jogos_sem_sofrer_gols_fim / total_jogos) * 100
    mediana_saves = np.median(total_saves) if total_saves else 2
    nota_resiliencia = (tx_reacao * 0.40) + (tx_fim * 0.40) + (min(mediana_saves * 20, 100.0) * 0.20)

    ovr_bruto = (nota_ataque + nota_meio + nota_defesa + nota_consistencia + nota_resiliencia) / 5.0
    peso_liga = obter_peso_prateleira(id_competicao=id_liga, tipo_escopo="domestico")
    ovr_calibrado = round(ovr_bruto * peso_liga, 2)

    return {
        "Ataque": round(nota_ataque, 1),
        "Meio-Campo": round(nota_meio, 1),
        "Defesa": round(nota_defesa, 1),
        "Consistência": round(nota_consistencia, 1),
        "Resiliência": round(nota_resiliencia, 1),
        "Overall": round(min(max(ovr_calibrado, 0.0), 100.0), 2)
    }
def buscar_estatisticas_fixture_real(fixture_id):
    """ÁREA 6: Coleta os dados detalhados jogo a jogo direto da API-Football."""
    url = "https://api-sports.io"
    headers = get_api_headers()
    params = {"fixture": fixture_id}
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", [])
    except:
        return []
    return []


def extrair_medianas_detalhada_real(lista_fixtures, team_id):
    """
    ÁREA 6: Varre os últimos jogos reais, faz as requisições de estatísticas, 
    calcula as medianas e esconde automaticamente as métricas indisponíveis (None).
    """
    dados_totais = []
    
    # Limita aos últimos 10 jogos válidos coletados na Área 0 para o IMA/Medianas
    for item in lista_fixtures[:10]:
        f_id = item["fixture"]["id"]
        stats_payload = buscar_estatisticas_fixture_real(f_id)
        
        jogo_stats = {
            "ataques_favor": None, "ataques_contra": None,
            "chutes_favor": None, "chutes_contra": None,
            "chutes_gol_favor": None, "chutes_gol_contra": None,
            "posse_bola": None, "faltas_cometidas": None,
            "escanteios_favor": None, "escanteios_contra": None,
            "cartoes": None
        }
        
        for time_entry in stats_payload:
            id_atual_stats = time_entry["team"]["id"]
            is_proprio = (id_atual_stats == team_id)
            
            stats_list = time_entry.get("statistics", [])
            for s in stats_list:
                tipo = s["type"]
                val = str(s["value"]).replace("%", "")
                val = int(val) if val and val != "None" else 0
                
                if tipo == "Total Attacks":
                    jogo_stats["ataques_favor" if is_proprio else "ataques_contra"] = val
                elif tipo == "Total Shots":
                    jogo_stats["chutes_favor" if is_proprio else "chutes_contra"] = val
                elif tipo == "Shots on Goal":
                    jogo_stats["chutes_gol_favor" if is_proprio else "chutes_gol_contra"] = val
                elif tipo == "Ball Possession" and is_proprio:
                    jogo_stats["posse_bola"] = val
                elif tipo == "Fouls" and is_proprio:
                    jogo_stats["faltas_cometidas"] = val
                elif tipo == "Corner Kicks":
                    jogo_stats["escanteios_favor" if is_proprio else "escanteios_contra"] = val
                elif tipo == "Yellow Cards" and is_proprio:
                    jogo_stats["cartoes"] = (jogo_stats["cartoes"] or 0) + val
                    
        dados_totais.append(jogo_stats)
        
    if not dados_totais:
        return pd.Series(dtype=float)
        
    df = pd.DataFrame(dados_totais)
    
    # MODIFICAÇÃO DO SEU MÉTODO: Remove colunas se a estatística não estiver disponível (toda nula)
    df_filtrado = df.dropna(axis=1, how='all')
    
    return df_filtrado.median()


def calcular_ima_mutacao_copa(ima_domestico, peso_prateleira, lista_pontos_copa, contexto_regulamento):
    """
    ÁREA 5.5 & 9: Mutação Conceitual do IMA para Copas.
    Coleta Híbrida: 60% peso para o retrospecto na Copa e 40% para o Momento Nacional Calibrado.
    Adapta os pesos para aceitar decisões estratégicas de regulamento.
    """
    ima_calibrado_nacional = ima_domestico * peso_prateleira
    
    if len(lista_pontos_copa) > 0:
        aproveitamento_copa = (sum(lista_pontos_copa) / len(lista_pontos_copa)) / 3.0 * 100
    else:
        aproveitamento_copa = ima_calibrado_nacional
        
    ima_hibrido_bruto = (aproveitamento_copa * 0.60) + (ima_calibrado_nacional * 0.40)
    
    if contexto_regulamento.get("jogo_volta", False) and contexto_regulamento.get("saldo_vantagem_ida", 0) >= 3:
        ima_hibrido_bruto += 15.0
        
    return round(min(max(ima_hibrido_bruto, 0.0), 100.0), 2)

# =====================================================================
# 🚀 PARTE 2: A LINHA DE MONTAGEM (EXECUÇÃO VISUAL E SEGURA)
# =====================================================================

st.title("⚽ MyPredict")

# Verificação inicial do cofre de chaves
if "API_FOOTBALL_KEY" not in st.secrets:
    st.error("Por favor, adicione a sua chave 'API_FOOTBALL_KEY' no cofre do Streamlit Cloud.")
    st.stop()

# 1. FILTRAGEM EM CASCATA UNIVERSAL (Carrega absolutamente todas as ligas do mundo via API)
with st.spinner("Buscando todas as ligas do mundo ativas na API..."):
    ligas_globais = carregar_todas_as_ligas_api()

liga_nome = st.selectbox("1º Escolha a Liga Global:", list(ligas_globais.keys()))
id_liga_atual = ligas_globais[liga_nome]

# Carrega os times da liga selecionada dinamicamente via API
dicio_times = obter_times_da_liga(id_liga_atual)
lista_nomes_times = list(dicio_times.keys())

col1, col2 = st.columns(2)
with col1:
    mandante = st.selectbox("2º Time Mandante:", lista_nomes_times, index=0 if len(lista_nomes_times) > 0 else 0)
with col2:
    idx_v = 1 if len(lista_nomes_times) > 1 else 0
    visitante = st.selectbox("3º Time Visitante:", lista_nomes_times, index=idx_v)

id_m = dicio_times.get(mandante, 0)
id_v = dicio_times.get(visitante, 0)

# Configuração dinâmica de regulamento
tipo_comp = detectar_tipo_competicao(id_liga_atual)
regulamento = {"jogo_volta": False, "saldo_vantagem_ida": 0}

if tipo_comp == "Copa":
    st.write("**⚙️ Contexto de Regulamento da Copa:**")
    regulamento["jogo_volta"] = st.checkbox("É jogo de volta do mata-mata?")
    if regulamento["jogo_volta"]:
        regulamento["saldo_vantagem_ida"] = st.number_input("Saldo de gols de vantagem obtido na ida:", value=0, step=1)

# Botão principal de cálculo
if st.button("🔮 Calcular Predição Real", use_container_width=True):
    with st.spinner("Baixando histórico unificado e aplicando as regras do seu método..."):
        # Executa a Área 0 (Download único de Liga + Copa expandido para 39 jogos)
        historico = baixar_dados_completos_equipes(id_m, id_v, id_liga_atual)
        
        # Mapeamento de Escalões e Rodadas Reais (Padrão Médio/10)
        escalao_m, rodada_m = "MEDIO", 10
        escalao_v, rodada_v = "MEDIO", 10
        
        # Converte o histórico bruto da API em listas de pontos reais baseados no seu método (Filtro curto de 10 e 5 jogos para o IMA)
        pontos_gerais_m = extrair_pontos_de_fixtures_reais(historico["m_liga_geral_39"][:10], id_m, escalao_m, escalao_v, rodada_m)
        pontos_mando_m = extrair_pontos_de_fixtures_reais(historico["m_liga_casa_5"], id_m, escalao_m, escalao_v, rodada_m)
        
        pontos_gerais_v = extrair_pontos_de_fixtures_reais(historico["v_liga_geral_39"][:10], id_v, escalao_v, escalao_m, rodada_v)
        pontos_mando_v = extrair_pontos_de_fixtures_reais(historico["v_liga_fora_5"], id_v, escalao_v, escalao_m, rodada_v)
        
        pontos_copa_m = extrair_pontos_de_fixtures_reais(historico["m_copa_especifico_5"], id_m, escalao_m, escalao_v, rodada_m)
        pontos_copa_v = extrair_pontos_de_fixtures_reais(historico["v_copa_especifico_5"], id_v, escalao_v, escalao_m, rodada_v)
        
        # Executa o cálculo matemático real do IMA (58% Mando / 42% Geral) usando estritamente o curto prazo
        ima_bruto_m = calcular_ima(pontos_gerais_m, pontos_mando_m)
        ima_bruto_v = calcular_ima(pontos_gerais_v, pontos_mando_v)
        
        # Executa o processamento em tempo real do Overall (OVR) baseado na temporada ampla de 39 jogos
        ovr_data_m = processar_ovr_39_jogos(historico["m_liga_geral_39"], id_m, id_liga_atual)
        ovr_data_v = processar_ovr_39_jogos(historico["v_liga_geral_39"], id_v, id_liga_atual)
        
        st.markdown("---")
        
        # EXIBIÇÃO DO OVERALL (OVR) COM AS 5 NOTAS CALIBRADAS POR PONTOS DE IMPACTO
        st.subheader("📊 Força Estrutural (OVR de 39 Jogos)")
        col_ovr_m, col_ovr_v = st.columns(2)
        with col_ovr_m:
            st.metric(label=f"OVR Calibrado - {mandante}", value=f"{ovr_data_m['Overall']} / 100")
            st.caption(f"⚔️ Atq: {ovr_data_m['Ataque']} | 🧠 Meio: {ovr_data_m['Meio-Campo']} | 🛡️ Def: {ovr_data_m['Defesa']}")
            st.caption(f"📈 Cons: {ovr_data_m['Consistência']} | 🧱 Resi: {ovr_data_m['Resiliência']}")
        with col_ovr_v:
            st.metric(label=f"OVR Calibrado - {visitante}", value=f"{ovr_data_v['Overall']} / 100")
            st.caption(f"⚔️ Atq: {ovr_data_v['Ataque']} | 🧠 Meio: {ovr_data_v['Meio-Campo']} | 🛡️ Def: {ovr_data_v['Defesa']}")
            st.caption(f"📈 Cons: {ovr_data_v['Consistência']} | 🧱 Resi: {ovr_data_v['Resiliência']}")
            
        st.markdown("---")
        
        # EXIBIÇÃO DO ÍNDICE DE MOMENTO ATUAL (IMA) BASEADO EM RECÊNCIA CURTA
        if tipo_comp == "Copa":
            st.subheader("🏆 Momento Atual (Modo Copa)")
            peso_prateleira_m = obter_peso_prateleira(id_liga_atual, tipo_escopo="domestico")
            peso_prateleira_v = obter_peso_prateleira(id_liga_atual, tipo_escopo="domestico")
            
            ima_final_m = calcular_ima_mutacao_copa(ima_bruto_m, peso_prateleira_m, pontos_copa_m, regulamento)
            ima_final_v = calcular_ima_mutacao_copa(ima_bruto_v, peso_prateleira_v, pontos_copa_v, regulamento)
            
            tab_copa, tab_domestico = st.tabs(["📊 Visão da Copa", "🏠 Contexto Doméstico"])
            with tab_copa:
                st.metric(label=f"IMA Copa - {mandante}", value=f"{ima_final_m} / 100")
                st.metric(label=f"IMA Copa - {visitante}", value=f"{ima_final_v} / 100")
            with tab_domestico:
                st.write(f"IMA Puro Nacional {mandante}: {ima_bruto_m}")
                st.write(f"IMA Puro Nacional {visitante}: {ima_bruto_v}")
        else:
        else:
            st.subheader("📈 Momento Atual (Modo Liga - IMA Puro)")
            st.metric(label=f"IMA Puro - {mandante}", value=f"{ima_bruto_m} / 100")
            st.metric(label=f"IMA Puro - {visitante}", value=f"{ima_bruto_v} / 100")
            
        # EXIBIÇÃO DE MEDIANAS JOGO A JOGO COM REMOÇÃO AUTOMÁTICA DE COLUNAS VAZIAS (ÁREA 6)
        st.markdown("---")
        st.subheader("📊 Medianas Coletadas Jogo a Jogo")
        
        with st.spinner("Calculando medianas das partidas reais via API..."):
            medianas_m = extrair_medianas_detalhada_real(historico["m_liga_geral_39"][:10], id_m)
            medianas_v = extrair_medianas_detalhada_real(historico["v_liga_geral_39"][:10], id_v)
            
            df_final_medianas = pd.DataFrame({mandante: medianas_m, visitante: medianas_v})
            st.dataframe(df_final_medianas, use_container_width=True)
