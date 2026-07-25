import streamlit as st
import requests

st.set_page_config(page_title="Sistema Analítico Composto", layout="wide")

# =========================================================================
# MÓDULO 1: PONTE DE CONEXÃO COM A API (MANTENHA INTACTA)
# =========================================================================
def buscar_dados_api(endpoint_url):
    try:
        API_KEY = st.secrets["API_SPORTS_KEY"]
        headers = {'x-apisports-key': API_KEY}
        response = requests.get(endpoint_url, headers=headers)
        dados_brutos = response.json()
        
        if "errors" in dados_brutos and dados_brutos["errors"]:
            return {"sucesso": False, "erro": dados_brutos["errors"], "dados": None}
        return {"sucesso": True, "erro": None, "dados": dados_brutos.get("response", [])}
    except Exception as e:
        return {"sucesso": False, "erro": str(e), "dados": None}

# =========================================================================
# MOTOR MATEMÁTICO: SEUS CÁLCULOS DO PASSO 2, PASSO 3 E IRC
# =========================================================================

def calcular_retrovisor_empate(mando, prateleira_rival):
    """
    PASSO 3: RETROVISOR DE AJUSTE DE EMPATES
    Retorna o percentual que um empate vale em termos de aproveitamento (0.0 a 1.0)
    """
    if mando == "VISITANTE":
        if prateleira_rival == "Elite (Top 4)":
            return 0.666
        else:
            return 1.000 # Contra igual ou inferior vale 100%
    else: # MANDANTE
        if prateleira_rival in ["Elite (Top 4)", "Igual"]:
            return 0.666
        elif prateleira_rival == "Meio de Tabela":
            return 0.333
        elif prateleira_rival == "Z-4":
            return 0.000 # Fiasco
    return 0.333 # Padrão neutro

def calcular_fac(rodada):
    """ Determina o Fator de Altura da Competição com base na rodada """
    if 1 <= rodada <= 10: return 0.30
    if 11 <= rodada <= 25: return 0.60
    if 26 <= rodada <= 33: return 0.85
    return 1.00

def calcular_irc(rodada, nota_posicao, prospecção_elite, orgulho_ferido, revanche):
    """ ÍNDICE DE RESPOSTA COMPETITIVA CONTROLADO (IRC) """
    fac = calcular_fac(rodada)
    
    # Aplicação do FPT (Fator de Prospecção Teórica)
    fpt = -10 if (1 <= rodada <= 10 and prospecção_elite) else 0
    urgencia_real = nota_posicao + fpt
    
    # Fórmula Base
    nota_irc = 50 + (urgencia_real + orgulho_ferido + revanche) * fac
    
    # Aplicação de Teto e Piso estritos
    return max(0.0, min(100.0, nota_irc))

def calcular_im(bloco_campo_3, bloco_campo_5, geral_3, geral_5, geral_10, tabela_dinamica):
    """ PASSO 2: ÍNDICE DE MOMENTO (Escala 0 a 100) """
    # 1. Bloco Condição de Campo (45%)
    sub_campo = (bloco_campo_3 * 0.65) + (bloco_campo_5 * 0.35)
    # 2. Bloco Geral (35%)
    sub_geral = (geral_3 * 0.50) + (geral_5 * 0.35) + (geral_10 * 0.15)
    # 3. Tabela Dinâmica (20%)
    sub_tabela = tabela_dinamica
    
    # Soma Ponderada Final
    return (sub_campo * 0.45) + (sub_geral * 0.35) + (sub_tabela * 0.20)

# =========================================================================
# INTERFACE GRÁFICA (STREAMLIT)
# =========================================================================
st.title("🏆 Simulador Analítico Avançado de Futebol")
st.write("Processamento matemático de volatilidade, resiliência psicológica e ajustes de prateleira.")

# Painel lateral para configurações do campeonato
st.sidebar.header("⚙️ Contexto da Competição")
rodada_atual = st.sidebar.number_input("Rodada Atual do Confronto:", min_value=1, max_value=38, value=8)
fac_atual = calcular_fac(rodada_atual)
st.sidebar.metric("FAC Ativo (Peso Temporal)", f"{fac_atual:.2f}")

# Painel de Seleção das Prateleiras (Passo 3)
st.sidebar.subheader("👑 Definição de Prateleiras do Rival")
prateleira_visitante = st.sidebar.selectbox("Prateleira do Visitante (Para o Mandante):", ["Elite (Top 4)", "Meio de Tabela", "Z-4"])
prateleira_mandante = st.sidebar.selectbox("Prateleira do Mandante (Para o Visitante):", ["Elite (Top 4)", "Meio de Tabela", "Z-4"])

# Entrada de dados simulados/reais para os cálculos
st.header("⚔️ Configuração das Variáveis das Equipes")

col_m, col_v = st.columns(2)

with col_m:
    st.subheader("🏠 Dados do Mandante")
    nome_m = st.text_input("Equipe Mandante:", value="Arsenal")
    overall_m = st.slider("Overall Estrutural (Ataque/Defesa/Meio):", 0, 100, 82, key="ov_m")
    
    st.markdown("**Desempenho Recente (Pontos Convertidos pelo Passo 3):**")
    cc_3_m = st.slider("Aproveitamento Últimos 3 em Casa (0-100):", 0, 100, 80, key="cc3m")
    cc_5_m = st.slider("Aproveitamento Últimos 5 em Casa (0-100):", 0, 100, 70, key="cc5m")
    g_3_m = st.slider("Aproveitamento Últimos 3 Gerais (0-100):", 0, 100, 90, key="g3m")
    g_5_m = st.slider("Aproveitamento Últimos 5 Gerais (0-100):", 0, 100, 75, key="g5m")
    g_10_m = st.slider("Aproveitamento Últimos 10 Gerais (0-100):", 0, 100, 65, key="g10m")
    tab_m = st.slider("Tabela Dinâmica (Posição Real vs Recente):", 0, 100, 70, key="tabm")
    
    st.markdown("**Gatilhos Psicológicos (IRC):**")
    nota_pos_m = st.number_input("Nota Posição Atual Mandante (-30 a 30):", value=15, key="posm")
    elite_m = st.checkbox("Time tem Prospecção Teórica de 'Elite'?", value=True, key="elitem")
    orgulho_m = st.selectbox("Vem de Goleada/Derrota Vergonhosa?", [0, 10, 20], format_func=lambda x: "Não (+0)" if x==0 else "Derrota inferior (+10)" if x==10 else "Goleada Humilhante (+20)", key="orgm")
    revanche_m = st.checkbox("Jogo é uma Revanche recente?", value=False, key="revm")

with col_v:
    st.subheader("🚀 Dados do Visitante")
    nome_v = st.text_input("Equipe Visitante:", value="Chelsea")
    overall_v = st.slider("Overall Estrutural (Ataque/Defesa/Meio):", 0, 100, 78, key="ov_v")
    
    st.markdown("**Desempenho Recente (Pontos Convertidos pelo Passo 3):**")
    cc_3_v = st.slider("Aproveitamento Últimos 3 Fora (0-100):", 0, 100, 40, key="cc3v")
    cc_5_v = st.slider("Aproveitamento Últimos 5 Fora (0-100):", 0, 100, 50, key="cc5v")
    g_3_v = st.slider("Aproveitamento Últimos 3 Gerais (0-100):", 0, 100, 60, key="g3v")
    g_5_v = st.slider("Aproveitamento Últimos 5 Gerais (0-100):", 0, 100, 55, key="g5v")
    g_10_v = st.slider("Aproveitamento Últimos 10 Gerais (0-100):", 0, 100, 60, key="g10v")
    tab_v = st.slider("Tabela Dinâmica (Posição Real vs Recente):", 0, 100, 50, key="tabv")
    
    st.markdown("**Gatilhos Psicológicos (IRC):**")
    nota_pos_v = st.number_input("Nota Posição Atual Visitante (-30 a 30):", value=5, key="posv")
    elite_v = st.checkbox("Time tem Prospecção Teórica de 'Elite'?", value=False, key="elitev")
    orgulho_v = st.selectbox("Vem de Goleada/Derrota Vergonhosa?", [0, 10, 20], format_func=lambda x: "Não (+0)" if x==0 else "Derrota inferior (+10)" if x==10 else "Goleada Humilhante (+20)", key="orgv")
    revanche_v = st.checkbox("Jogo é uma Revanche recente?", value=True, key="revv")

# =========================================================================
# PASSO 4: PROCESSAMENTO FINAL E TELA DE CONFRONTO DIRETO
# =========================================================================
st.divider()
st.header("🎯 PASSO 4: Tela de Confronto Direto e Nota Unificada")

# Executa as equações matemáticas para o Mandante
im_final_m = calcular_im(cc_3_m, cc_5_m, g_3_m, g_5_m, g_10_m, tab_m)
irc_final_m = calcular_irc(rodada_actual, nota_pos_m, elite_m, orgulho_m, revanche_m * 10)
juncao_m = (overall_m + im_final_m + irc_final_m) / 3

# Executa as equações matemáticas para o Visitante
im_final_v = calcular_im(cc_3_v, cc_5_v, g_3_v, g_5_v, g_10_v, tab_v)
irc_final_v = calcular_irc(rodada_actual, nota_pos_v, elite_v, orgulho_v, revanche_v * 10)
juncao_v = (overall_v + im_final_v + irc_final_v) / 3

# Diferença Crítica Final
disparidade = juncao_m - juncao_v

# Exibição dos resultados em painéis paralelos comparativos
col_res_m, col_disp, col_res_v = st.columns([2, 1, 2])

with col_res_m:
    st.metric(label=f"🔰 Nota Junção {nome_m}", value=f"{juncao_m:.2f} / 100")
    st.write(f"• **Overall:** {overall_m}")
    st.write(f"• **Índice de Momento (IM):** {im_final_m:.1f}")
    st.write(f"• **Resposta Competitiva (IRC):** {irc_final_m:.1f}")

with col_disp:
    st.markdown("<p style='text-align: center; font-weight: bold;'>Disparidade Crítica</p>", unsafe_allow_html=True)
    cor_disp = "green" if disparidade > 10 else "red" if disparidade < -10 else "orange"
    st.markdown(f"<h2 style='text-align: center; color: {cor_disp};'>{disparidade:+.2f}</h2>", unsafe_allow_html=True)

with col_res_v:
    st.metric(label=f"🚀 Nota Junção {nome_v}", value=f"{juncao_v:.2f} / 100")
    st.write(f"• **Overall:** {overall_v}")
    st.write(f"• **Índice de Momento (IM):** {im_final_v:.1f}")
    st.write(f"• **Resposta Competitiva (IRC):** {irc_final_v:.1f}")

# Painel demonstrativo do ajuste de empate do Passo 3
st.markdown("### 🎛️ Painel de Consulta do Passo 3 (Ajuste de Empates)")
emp_m = calcular_retrovisor_empate("MANDANTE", prateleira_visitante)
emp_v = calcular_retrovisor_empate("VISITANTE", prateleira_mandante)
st.caption(f"Se este jogo terminar empatado no histórico: Para o mandante vale **{emp_m*100:.1f}%** de uma vitória. Para o visitante vale **{emp_v*100:.1f}%**.")
