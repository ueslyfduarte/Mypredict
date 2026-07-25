import streamlit as st
import requests
from datetime import datetime

# =========================================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================================
st.set_page_config(
    page_title="Meu App Esportivo",
    page_icon="⚽",
    layout="wide"
)

# =========================================================================
# MENU LATERAL
# =========================================================================
st.sidebar.title("⚽ Menu")
menu = st.sidebar.selectbox(
    "Escolha a seção:",
    ["🔍 Buscar Time", "🧮 Simulador FMP"]
)

# =========================================================================
# CAIXA DE FERRAMENTAS MATEMÁTICA
# =========================================================================
def validar_nota(valor, nome):
    if valor is None:
        raise ValueError(f"{nome} está vazio.")
    if not (0 <= valor <= 100):
        raise ValueError(f"{nome} = {valor} fora do intervalo 0-100.")
    return float(valor)

def calcular_bloco_ataque(fvo, fco):
    return min(100.0, max(0.0, (fvo * 0.60) + (fco * 0.40)))

def calcular_bloco_defesa(frd, fcd_defensivo):
    return min(100.0, max(0.0, (frd * 0.60) + (fcd_defensivo * 0.40)))

def calcular_bloco_consistencia(fdm, ier):
    return (fdm * 0.60) + (ier * 0.40)

def calcular_bloco_resistencia_pressao(fcd_res, egz_res, fri_res, fzc_res):
    return (fcd_res * 0.30) + (egz_res * 0.30) + (fri_res * 0.20) + (fzc_res * 0.20)

def calcular_overall_unificado(consistencia, ataque, defesa, resistencia_pressao):
    return (consistencia * 0.35) + (ataque * 0.25) + (defesa * 0.25) + (resistencia_pressao * 0.15)

def classificar_intervalo_fifa(nota):
    if nota >= 86: return "Elite (86-99)"
    if nota >= 78: return "Alto (78-85)"
    if nota >= 70: return "Médio (70-77)"
    if nota >= 60: return "Baixo (60-69)"
    return "Crítico (<60)"

def calcular_im_final(cc3, cc5, geral_3, geral_5, geral_10, tabela_dinamica):
    sub_campo = (cc3 * 0.65) + (cc5 * 0.35)
    sub_geral = (geral_3 * 0.50) + (geral_5 * 0.35) + (geral_10 * 0.15)
    return (sub_campo * 0.45) + (sub_geral * 0.35) + (tabela_dinamica * 0.20)

def calcular_fac(rodada):
    if 1 <= rodada <= 10: return 0.30
    if 11 <= rodada <= 25: return 0.60
    if 26 <= rodada <= 33: return 0.85
    return 1.00

def calcular_irc_final(rodada, nota_posicao, prospeccao_elite, orgulho_ferido, revanche):
    fac = calcular_fac(rodada)
    fpt = -10 if (1 <= rodada <= 10 and prospeccao_elite) else 0
    urgencia_real = nota_posicao + fpt
    nota_irc = 50 + (urgencia_real + orgulho_ferido + revanche) * fac
    return max(0.0, min(100.0, nota_irc))

def calcular_juncao_unificada(overall, im, irc):
    return (overall + im + irc) / 3

def calcular_probabilidades(nota_time_a, nota_time_b):
    diff = nota_time_a - nota_time_b
    prob_a = 35 + (diff * 0.5 if diff > 0 else diff * 0.3)
    prob_empate = 30 - (abs(diff) * 0.2)
    prob_b = 35 + (abs(diff) * 0.5 if diff < 0 else abs(diff) * 0.3)
    
    prob_a = max(5, min(85, prob_a))
    prob_empate = max(5, min(50, prob_empate))
    prob_b = max(5, min(85, prob_b))
    
    total = prob_a + prob_empate + prob_b
    return prob_a/total*100, prob_empate/total*100, prob_b/total*100

# =========================================================================
# ABA 1: BUSCAR TIME (SEU CÓDIGO ORIGINAL)
# =========================================================================
if menu == "🔍 Buscar Time":
    st.title("🔍 Buscar Time na API-Football")
    
    API_KEY = st.secrets["API_FOOTBALL_KEY"]
    time = st.text_input("Digite o nome de um time (ex: Flamengo):")
    
    if st.button("Buscar Time"):
        if time:
            headers = {
                "x-rapidapi-key": API_KEY,
                "x-rapidapi-host": "v3.football.api-sports.io"
            }
            
            url = "https://v3.football.api-sports.io/teams"
            params = {"search": time}
            
            resposta = requests.get(url, headers=headers, params=params)
            dados = resposta.json()
            
            st.write("Resultado encontrado:")
            st.json(dados)

# =========================================================================
# ABA 2: SIMULADOR FMP
# =========================================================================
elif menu == "🧮 Simulador FMP":
    st.title("🧮 Simulador de Confronto - Método FMP")
    st.caption("Ajuste os valores no menu lateral e clique em CALCULAR")
    
    # Dados do Time A
    st.sidebar.divider()
    st.sidebar.subheader("🏠 Time A (Mandante)")
    nome_time_a = st.sidebar.text_input("Nome", "Flamengo", key="nome_a")
    
    with st.sidebar.expander("📊 Notas do Time A", expanded=False):
        fvo_a = st.slider("FVO - Força Ofensiva", 0, 100, 78, key="fvo_a")
        fco_a = st.slider("FCO - Força Coletiva", 0, 100, 75, key="fco_a")
        frd_a = st.slider("FRD - Resistência Defensiva", 0, 100, 72, key="frd_a")
        fcd_def_a = st.slider("FCD Defensivo", 0, 100, 70, key="fcd_def_a")
        fdm_a = st.slider("FDM - Dinâmica do Meio", 0, 100, 74, key="fdm_a")
        ier_a = st.slider("IER - Efetividade Real", 0, 100, 73, key="ier_a")
        fcd_res_a = st.slider("FCD Resistência", 0, 100, 70, key="fcd_res_a")
        egz_res_a = st.slider("EGZ Resistência", 0, 100, 68, key="egz_res_a")
        fri_res_a = st.slider("FRI Resistência", 0, 100, 72, key="fri_res_a")
        fzc_res_a = st.slider("FZC Resistência", 0, 100, 69, key="fzc_res_a")
    
    with st.sidebar.expander("📈 Momento (Time A)", expanded=False):
        cc3_a = st.slider("Últimos 3 jogos em casa", 0, 100, 70, key="cc3_a")
        cc5_a = st.slider("Últimos 5 jogos em casa", 0, 100, 65, key="cc5_a")
        geral_3_a = st.slider("Geral 3 jogos", 0, 100, 68, key="g3_a")
        geral_5_a = st.slider("Geral 5 jogos", 0, 100, 64, key="g5_a")
        geral_10_a = st.slider("Geral 10 jogos", 0, 100, 60, key="g10_a")
        tabela_din_a = st.slider("Tabela Dinâmica", 0, 100, 58, key="tab_a")
    
    with st.sidebar.expander("🧠 Fatores Psicológicos (Time A)", expanded=False):
        rodada_a = st.number_input("Rodada", 1, 38, 20, key="rod_a")
        nota_pos_a = st.slider("Nota Posição", 0, 100, 65, key="pos_a")
        prospeccao_a = st.checkbox("Prospecção Elite", key="prosp_a")
        orgulho_a = st.slider("Orgulho Ferido", -30, 30, 5, key="org_a")
        revanche_a = st.slider("Revanche", 0, 20, 0, key="rev_a")
    
    # Dados do Time B
    st.sidebar.divider()
    st.sidebar.subheader("🚌 Time B (Visitante)")
    nome_time_b = st.sidebar.text_input("Nome", "Vasco", key="nome_b")
    
    with st.sidebar.expander("📊 Notas do Time B", expanded=False):
        fvo_b = st.slider("FVO - Força Ofensiva", 0, 100, 65, key="fvo_b")
        fco_b = st.slider("FCO - Força Coletiva", 0, 100, 63, key="fco_b")
        frd_b = st.slider("FRD - Resistência Defensiva", 0, 100, 68, key="frd_b")
        fcd_def_b = st.slider("FCD Defensivo", 0, 100, 66, key="fcd_def_b")
        fdm_b = st.slider("FDM - Dinâmica do Meio", 0, 100, 62, key="fdm_b")
        ier_b = st.slider("IER - Efetividade Real", 0, 100, 64, key="ier_b")
        fcd_res_b = st.slider("FCD Resistência", 0, 100, 65, key="fcd_res_b")
        egz_res_b = st.slider("EGZ Resistência", 0, 100, 63, key="egz_res_b")
        fri_res_b = st.slider("FRI Resistência", 0, 100, 66, key="fri_res_b")
        fzc_res_b = st.slider("FZC Resistência", 0, 100, 64, key="fzc_res_b")
    
    with st.sidebar.expander("📈 Momento (Time B)", expanded=False):
        cc3_b = st.slider("Últimos 3 jogos fora", 0, 100, 50, key="cc3_b")
        cc5_b = st.slider("Últimos 5 jogos fora", 0, 100, 48, key="cc5_b")
        geral_3_b = st.slider("Geral 3 jogos", 0, 100, 55, key="g3_b")
        geral_5_b = st.slider("Geral 5 jogos", 0, 100, 52, key="g5_b")
        geral_10_b = st.slider("Geral 10 jogos", 0, 100, 50, key="g10_b")
        tabela_din_b = st.slider("Tabela Dinâmica", 0, 100, 45, key="tab_b")
    
    with st.sidebar.expander("🧠 Fatores Psicológicos (Time B)", expanded=False):
        rodada_b = st.number_input("Rodada", 1, 38, 20, key="rod_b")
        nota_pos_b = st.slider("Nota Posição", 0, 100, 50, key="pos_b")
        prospeccao_b = st.checkbox("Prospecção Elite", key="prosp_b")
        orgulho_b = st.slider("Orgulho Ferido", -30, 30, -5, key="org_b")
        revanche_b = st.slider("Revanche", 0, 20, 10, key="rev_b")
    
    # Botão de calcular
    if st.sidebar.button("🧮 CALCULAR PREVISÃO", type="primary", use_container_width=True):
        
        # Cálculos Time A
        ataque_a = calcular_bloco_ataque(fvo_a, fco_a)
        defesa_a = calcular_bloco_defesa(frd_a, fcd_def_a)
        consistencia_a = calcular_bloco_consistencia(fdm_a, ier_a)
        resistencia_a = calcular_bloco_resistencia_pressao(fcd_res_a, egz_res_a, fri_res_a, fzc_res_a)
        overall_a = calcular_overall_unificado(consistencia_a, ataque_a, defesa_a, resistencia_a)
        im_a = calcular_im_final(cc3_a, cc5_a, geral_3_a, geral_5_a, geral_10_a, tabela_din_a)
        irc_a = calcular_irc_final(rodada_a, nota_pos_a, prospeccao_a, orgulho_a, revanche_a)
        juncao_a = calcular_juncao_unificada(overall_a, im_a, irc_a)
        
        # Cálculos Time B
        ataque_b = calcular_bloco_ataque(fvo_b, fco_b)
        defesa_b = calcular_bloco_defesa(frd_b, fcd_def_b)
        consistencia_b = calcular_bloco_consistencia(fdm_b, ier_b)
        resistencia_b = calcular_bloco_resistencia_pressao(fcd_res_b, egz_res_b, fri_res_b, fzc_res_b)
        overall_b = calcular_overall_unificado(consistencia_b, ataque_b, defesa_b, resistencia_b)
        im_b = calcular_im_final(cc3_b, cc5_b, geral_3_b, geral_5_b, geral_10_b, tabela_din_b)
        irc_b = calcular_irc_final(rodada_b, nota_pos_b, prospeccao_b, orgulho_b, revanche_b)
        juncao_b = calcular_juncao_unificada(overall_b, im_b, irc_b)
        
        # Probabilidades
        prob_a, prob_empate, prob_b = calcular_probabilidades(juncao_a, juncao_b)
        
        # Exibição
        st.header("📊 Resultado da Análise")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"🏠 {nome_time_a}", f"{juncao_a:.1f}", f"Overall: {overall_a:.1f}")
        with col2:
            st.metric("⚖️ Diferença", f"{abs(juncao_a - juncao_b):.1f}")
        with col3:
            st.metric(f"🚌 {nome_time_b}", f"{juncao_b:.1f}", f"Overall: {overall_b:.1f}")
        
        st.divider()
        st.subheader("🎯 Probabilidades")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"Vitória {nome_time_a}", f"{prob_a:.1f}%")
        with col2:
            st.metric("Empate", f"{prob_empate:.1f}%")
        with col3:
            st.metric(f"Vitória {nome_time_b}", f"{prob_b:.1f}%")
        
        # Resultado final
        if prob_a > prob_b and prob_a > prob_empate:
            st.success(f"## 🏆 Previsão: Vitória do {nome_time_a}")
        elif prob_b > prob_a and prob_b > prob_empate:
            st.success(f"## 🏆 Previsão: Vitória do {nome_time_b}")
        else:
            st.warning(f"## 🤝 Previsão: Empate")
        
        # Detalhamento
        with st.expander("🔍 Ver detalhamento completo"):
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"🏠 {nome_time_a}")
                st.write(f"Overall: {overall_a:.1f} ({classificar_intervalo_fifa(overall_a)})")
                st.write(f"Ataque: {ataque_a:.1f} | Defesa: {defesa_a:.1f}")
                st.write(f"Consistência: {consistencia_a:.1f} | Resistência: {resistencia_a:.1f}")
                st.write(f"IM (Momento): {im_a:.1f} | IRC: {irc_a:.1f}")
                st.write(f"🔹 Junção Final: {juncao_a:.1f}")
            with col2:
                st.subheader(f"🚌 {nome_time_b}")
                st.write(f"Overall: {overall_b:.1f} ({classificar_intervalo_fifa(overall_b)})")
                st.write(f"Ataque: {ataque_b:.1f} | Defesa: {defesa_b:.1f}")
                st.write(f"Consistência: {consistencia_b:.1f} | Resistência: {resistencia_b:.1f}")
                st.write(f"IM (Momento): {im_b:.1f} | IRC: {irc_b:.1f}")
                st.write(f"🔹 Junção Final: {juncao_b:.1f}")

# =========================================================================
# RODAPÉ
# =========================================================================
st.sidebar.divider()
st.sidebar.caption(f"Método FMP | {datetime.now().strftime('%d/%m/%Y')}")
