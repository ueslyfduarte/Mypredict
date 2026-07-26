import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# =========================================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================================
st.set_page_config(
    page_title="Previsão Esportiva - Método FMP",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Previsão Esportiva - Método FMP")
st.caption("FMP = Fator de Modulação de Prateleira")

# =========================================================================
# CAIXA DE FERRAMENTAS MATEMÁTICA (CORRIGIDA)
# =========================================================================

# Constantes dos pesos
PESO_FVO = 0.60
PESO_FCO = 0.40
PESO_FRD = 0.60
PESO_FCD_DEF = 0.40
PESO_FDM = 0.60
PESO_IER = 0.40
PESO_CONSISTENCIA = 0.35
PESO_ATAQUE = 0.25
PESO_DEFESA = 0.25
PESO_RESISTENCIA = 0.15

def validar_nota(valor, nome):
    """Garante que o valor está entre 0 e 100"""
    if valor is None:
        raise ValueError(f"❌ {nome} está vazio.")
    if not (0 <= valor <= 100):
        raise ValueError(f"❌ {nome} = {valor} fora do intervalo 0-100.")
    return float(valor)

def definir_prateleira(overall):
    """Define prateleira baseado no Overall"""
    if overall >= 78:
        return "Elite"
    elif overall >= 70:
        return "Meio"
    else:
        return "Baixo"

def calcular_fmp(prateleira_time, prateleira_rival):
    """Fator de Modulação de Prateleira Dinâmico"""
    if prateleira_time == "Elite" and prateleira_rival in ["Meio", "Baixo"]:
        return 0.60, 1.40
    elif prateleira_time in ["Meio", "Baixo"] and prateleira_rival == "Elite":
        return 1.30, 0.70
    else:
        return 1.00, 1.00

def calcular_bloco_ataque(fvo, fco):
    """Nota Final de Ataque (0-100)"""
    fvo = validar_nota(fvo, "FVO")
    fco = validar_nota(fco, "FCO")
    return min(100.0, max(0.0, (fvo * PESO_FVO) + (fco * PESO_FCO)))

def calcular_bloco_defesa(frd, fcd_defensivo):
    """Nota Final de Defesa (0-100)"""
    frd = validar_nota(frd, "FRD")
    fcd_defensivo = validar_nota(fcd_defensivo, "FCD Defensivo")
    return min(100.0, max(0.0, (frd * PESO_FRD) + (fcd_defensivo * PESO_FCD_DEF)))

def calcular_bloco_consistencia(fdm, ier):
    """Nota Final de Consistência"""
    fdm = validar_nota(fdm, "FDM")
    ier = validar_nota(ier, "IER")
    return (fdm * PESO_FDM) + (ier * PESO_IER)

def calcular_bloco_resistencia_pressao(fcd_res, egz_res, fri_res, fzc_res):
    """Bloco de Resistência à Pressão"""
    return (fcd_res * 0.30) + (egz_res * 0.30) + (fri_res * 0.20) + (fzc_res * 0.20)

def calcular_overall_unificado(consistencia, ataque, defesa, resistencia_pressao):
    """Overall Final (0-100)"""
    return (consistencia * PESO_CONSISTENCIA) + (ataque * PESO_ATAQUE) + (defesa * PESO_DEFESA) + (resistencia_pressao * PESO_RESISTENCIA)

def classificar_intervalo_fifa(nota):
    """Classificação FIFA"""
    if nota >= 86: return "Elite (86-99)"
    if nota >= 78: return "Alto (78-85)"
    if nota >= 70: return "Médio (70-77)"
    if nota >= 60: return "Baixo (60-69)"
    return "Crítico (<60)"

def calcular_pontos_retrovisor(mando, resultado, escalao_rival):
    """Cálculo de pontos ponderados para empates"""
    if resultado == "VITÓRIA": return 3.0
    if resultado == "DERROTA": return 0.0
    
    if mando == "VISITANTE":
        if escalao_rival == "Elite":
            return 3.0 * 0.666
        else:
            return 3.0 * 1.000
    else:
        if escalao_rival == "Elite":
            return 3.0 * 0.666
        elif escalao_rival == "Meio":
            return 3.0 * 0.333
        elif escalao_rival == "Baixo":
            return 3.0 * 0.000
    return 1.0

def calcular_im_final(cc3, cc5, geral_3, geral_5, geral_10, tabela_dinamica):
    """Índice de Momento (0-100)"""
    sub_campo = (cc3 * 0.65) + (cc5 * 0.35)
    sub_geral = (geral_3 * 0.50) + (geral_5 * 0.35) + (geral_10 * 0.15)
    return (sub_campo * 0.45) + (sub_geral * 0.35) + (tabela_dinamica * 0.20)

def calcular_fac(rodada):
    """Fator de Altura da Competição"""
    if 1 <= rodada <= 10: return 0.30
    if 11 <= rodada <= 25: return 0.60
    if 26 <= rodada <= 33: return 0.85
    return 1.00

def calcular_irc_final(rodada, nota_posicao, prospeccao_elite, orgulho_ferido, revanche):
    """Índice de Resposta Competitiva (0-100)"""
    fac = calcular_fac(rodada)
    fpt = -10 if (1 <= rodada <= 10 and prospeccao_elite) else 0
    urgencia_real = nota_posicao + fpt
    nota_irc = 50 + (urgencia_real + orgulho_ferido + revanche) * fac
    return max(0.0, min(100.0, nota_irc))

def calcular_juncao_unificada(overall, im, irc):
    """Junção Final"""
    return (overall + im + irc) / 3

def calcular_probabilidades(nota_time_a, nota_time_b):
    """Converte notas em probabilidades de resultado"""
    diff = nota_time_a - nota_time_b
    
    # Base neutra
    prob_vitoria_a = 35
    prob_empate = 30
    prob_vitoria_b = 35
    
    # Ajuste pela diferença
    if diff > 0:
        prob_vitoria_a += diff * 0.5
        prob_vitoria_b -= diff * 0.3
        prob_empate -= diff * 0.2
    else:
        prob_vitoria_b += abs(diff) * 0.5
        prob_vitoria_a -= abs(diff) * 0.3
        prob_empate -= abs(diff) * 0.2
    
    # Garante limites
    prob_vitoria_a = max(5, min(85, prob_vitoria_a))
    prob_empate = max(5, min(50, prob_empate))
    prob_vitoria_b = max(5, min(85, prob_vitoria_b))
    
    # Normaliza para 100%
    total = prob_vitoria_a + prob_empate + prob_vitoria_b
    return prob_vitoria_a/total*100, prob_empate/total*100, prob_vitoria_b/total*100

# =========================================================================
# INTERFACE DO USUÁRIO
# =========================================================================

st.sidebar.header("⚙️ Configuração da Partida")

# Escolha do modo
modo = st.sidebar.radio(
    "Modo de Entrada:",
    ["🎮 Manual (Simulador)", "🔌 API (Em breve)"]
)

if modo == "🎮 Manual (Simulador)":
    
    # Dados do Time A (Mandante)
    st.sidebar.divider()
    st.sidebar.subheader("🏠 Time A (Mandante)")
    nome_time_a = st.sidebar.text_input("Nome do Time A", "Time A")
    
    with st.sidebar.expander("📊 Notas do Time A"):
        fvo_a = st.slider("FVO - Força Ofensiva", 0, 100, 75, key="fvo_a")
        fco_a = st.slider("FCO - Força Coletiva Ofensiva", 0, 100, 72, key="fco_a")
        frd_a = st.slider("FRD - Força de Resistência Defensiva", 0, 100, 70, key="frd_a")
        fcd_def_a = st.slider("FCD Defensivo", 0, 100, 68, key="fcd_def_a")
        fdm_a = st.slider("FDM - Força Dinâmica do Meio", 0, 100, 73, key="fdm_a")
        ier_a = st.slider("IER - Índice de Efetividade Real", 0, 100, 71, key="ier_a")
        fcd_res_a = st.slider("FCD Resistência", 0, 100, 70, key="fcd_res_a")
        egz_res_a = st.slider("EGZ Resistência", 0, 100, 68, key="egz_res_a")
        fri_res_a = st.slider("FRI Resistência", 0, 100, 72, key="fri_res_a")
        fzc_res_a = st.slider("FZC Resistência", 0, 100, 69, key="fzc_res_a")
    
    with st.sidebar.expander("📈 Momento do Time A"):
        cc3_a = st.slider("CC3 - Últimos 3 jogos em casa", 0, 100, 65, key="cc3_a")
        cc5_a = st.slider("CC5 - Últimos 5 jogos em casa", 0, 100, 62, key="cc5_a")
        geral_3_a = st.slider("Geral 3 jogos", 0, 100, 68, key="geral_3_a")
        geral_5_a = st.slider("Geral 5 jogos", 0, 100, 64, key="geral_5_a")
        geral_10_a = st.slider("Geral 10 jogos", 0, 100, 60, key="geral_10_a")
        tabela_din_a = st.slider("Tabela Dinâmica", 0, 100, 55, key="tabela_din_a")
    
    with st.sidebar.expander("🧠 IRC do Time A"):
        rodada_a = st.number_input("Rodada atual", 1, 38, 20, key="rodada_a")
        nota_pos_a = st.slider("Nota Posição", 0, 100, 60, key="nota_pos_a")
        prospeccao_a = st.checkbox("Prospecção Elite", False, key="prosp_a")
        orgulho_a = st.slider("Orgulho Ferido", -30, 30, 0, key="orgulho_a")
        revanche_a = st.slider("Revanche", 0, 20, 0, key="revanche_a")
    
    st.sidebar.divider()
    st.sidebar.subheader("🚌 Time B (Visitante)")
    nome_time_b = st.sidebar.text_input("Nome do Time B", "Time B")
    
    with st.sidebar.expander("📊 Notas do Time B"):
        fvo_b = st.slider("FVO - Força Ofensiva", 0, 100, 65, key="fvo_b")
        fco_b = st.slider("FCO - Força Coletiva Ofensiva", 0, 100, 63, key="fco_b")
        frd_b = st.slider("FRD - Força de Resistência Defensiva", 0, 100, 68, key="frd_b")
        fcd_def_b = st.slider("FCD Defensivo", 0, 100, 66, key="fcd_def_b")
        fdm_b = st.slider("FDM - Força Dinâmica do Meio", 0, 100, 62, key="fdm_b")
        ier_b = st.slider("IER - Índice de Efetividade Real", 0, 100, 64, key="ier_b")
        fcd_res_b = st.slider("FCD Resistência", 0, 100, 65, key="fcd_res_b")
        egz_res_b = st.slider("EGZ Resistência", 0, 100, 63, key="egz_res_b")
        fri_res_b = st.slider("FRI Resistência", 0, 100, 66, key="fri_res_b")
        fzc_res_b = st.slider("FZC Resistência", 0, 100, 64, key="fzc_res_b")
    
    with st.sidebar.expander("📈 Momento do Time B"):
        cc3_b = st.slider("CC3 - Últimos 3 jogos fora", 0, 100, 55, key="cc3_b")
        cc5_b = st.slider("CC5 - Últimos 5 jogos fora", 0, 100, 52, key="cc5_b")
        geral_3_b = st.slider("Geral 3 jogos", 0, 100, 58, key="geral_3_b")
        geral_5_b = st.slider("Geral 5 jogos", 0, 100, 54, key="geral_5_b")
        geral_10_b = st.slider("Geral 10 jogos", 0, 100, 50, key="geral_10_b")
        tabela_din_b = st.slider("Tabela Dinâmica", 0, 100, 48, key="tabela_din_b")
    
    with st.sidebar.expander("🧠 IRC do Time B"):
        rodada_b = st.number_input("Rodada atual", 1, 38, 20, key="rodada_b")
        nota_pos_b = st.slider("Nota Posição", 0, 100, 50, key="nota_pos_b")
        prospeccao_b = st.checkbox("Prospecção Elite", False, key="prosp_b")
        orgulho_b = st.slider("Orgulho Ferido", -30, 30, 0, key="orgulho_b")
        revanche_b = st.slider("Revanche", 0, 20, 0, key="revanche_b")
    
    # =========================================================================
    # BOTÃO PARA CALCULAR
    # =========================================================================
    if st.sidebar.button("🧮 CALCULAR PREVISÃO", type="primary", use_container_width=True):
        
        # Cálculo Time A
        ataque_a = calcular_bloco_ataque(fvo_a, fco_a)
        defesa_a = calcular_bloco_defesa(frd_a, fcd_def_a)
        consistencia_a = calcular_bloco_consistencia(fdm_a, ier_a)
        resistencia_a = calcular_bloco_resistencia_pressao(fcd_res_a, egz_res_a, fri_res_a, fzc_res_a)
        overall_a = calcular_overall_unificado(consistencia_a, ataque_a, defesa_a, resistencia_a)
        
        im_a = calcular_im_final(cc3_a, cc5_a, geral_3_a, geral_5_a, geral_10_a, tabela_din_a)
        irc_a = calcular_irc_final(rodada_a, nota_pos_a, prospeccao_a, orgulho_a, revanche_a)
        juncao_a = calcular_juncao_unificada(overall_a, im_a, irc_a)
        
        # Cálculo Time B
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
        
        # Determina favorito
        if prob_a > prob_b and prob_a > prob_empate:
            resultado_previsto = f"🏆 Vitória do {nome_time_a}"
        elif prob_b > prob_a and prob_b > prob_empate:
            resultado_previsto = f"🏆 Vitória do {nome_time_b}"
        else:
            resultado_previsto = "🤝 Empate"
        
        # =========================================================================
        # EXIBIÇÃO DOS RESULTADOS
        # =========================================================================
        st.header("📊 Resultado da Análise")
        
        # Cards principais
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"🏠 {nome_time_a}", f"{juncao_a:.1f}", f"Overall: {overall_a:.1f}")
        with col2:
            st.metric("⚖️ Comparativo", f"Dif: {abs(juncao_a - juncao_b):.1f}")
        with col3:
            st.metric(f"🚌 {nome_time_b}", f"{juncao_b:.1f}", f"Overall: {overall_b:.1f}")
        
        st.divider()
        
        # Probabilidades
        st.subheader("🎯 Probabilidades de Resultado")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"Vitória {nome_time_a}", f"{prob_a:.1f}%")
        with col2:
            st.metric("Empate", f"{prob_empate:.1f}%")
        with col3:
            st.metric(f"Vitória {nome_time_b}", f"{prob_b:.1f}%")
        
        # Barra de probabilidade visual
        st.progress(prob_a / 100)
        st.caption(f"{nome_time_a} ← → {nome_time_b}")
        
        st.divider()
        
        # Resultado previsto
        st.subheader("📢 Previsão Final")
        if "Vitória" in resultado_previsto:
            st.success(f"## {resultado_previsto}")
        else:
            st.warning(f"## {resultado_previsto}")
        
        # Detalhamento
        with st.expander("🔍 Detalhamento Completo"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"🏠 {nome_time_a}")
                st.write(f"**Overall:** {overall_a:.1f} ({classificar_intervalo_fifa(overall_a)})")
                st.write(f"**Ataque:** {ataque_a:.1f} | **Defesa:** {defesa_a:.1f}")
                st.write(f"**Consistência:** {consistencia_a:.1f}")
                st.write(f"**Resistência:** {resistencia_a:.1f}")
                st.write(f"**IM (Momento):** {im_a:.1f}")
                st.write(f"**IRC (Resposta):** {irc_a:.1f}")
                st.write(f"**Junção Final:** {juncao_a:.1f}")
            
            with col2:
                st.subheader(f"🚌 {nome_time_b}")
                st.write(f"**Overall:** {overall_b:.1f} ({classificar_intervalo_fifa(overall_b)})")
                st.write(f"**Ataque:** {ataque_b:.1f} | **Defesa:** {defesa_b:.1f}")
                st.write(f"**Consistência:** {consistencia_b:.1f}")
                st.write(f"**Resistência:** {resistencia_b:.1f}")
                st.write(f"**IM (Momento):** {im_b:.1f}")
                st.write(f"**IRC (Resposta):** {irc_b:.1f}")
                st.write(f"**Junção Final:** {juncao_b:.1f}")

elif modo == "🔌 API (Em breve)":
    st.info("🏗️ Módulo API em desenvolvimento. Crie sua conta na API-Football para liberar.")

# =========================================================================
# RODAPÉ
# =========================================================================
st.sidebar.divider()
st.sidebar.caption("Método FMP v2.0 | Previsão Esportiva")
st.sidebar.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
