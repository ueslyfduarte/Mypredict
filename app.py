import streamlit as st

# =========================================================================
# CONEXÃO REAL COM OS SEUS MÓDULOS EXTERNOS (A MÁGICA RODA AQUI)
# =========================================================================
from ferramentas_calculo import (
    calcular_fmp, calcular_bloco_ataque, calcular_bloco_defesa,
    calcular_bloco_consistencia, calcular_bloco_resistencia_pressao,
    calcular_overall_unificado, classificar_intervalo_fifa,
    calcular_im_final, calcular_pontos_retrovisor
)
from ponte_api import buscar_dados_api

st.set_page_config(page_title="Método Analítico Unificado", layout="wide")
st.title("🏆 Painel Analítico Modularizado")
st.write("Interface principal conectada com sucesso às suas caixas de ferramentas.")

# =========================================================================
# CONFIGURAÇÃO VISUAL: DUAS COLUNAS MANDANTE E VISITANTE
# =========================================================================
col_m, col_v = st.columns(2)

with col_m:
    st.markdown("### 🏠 Configuração do Mandante")
    prat_m = st.selectbox("Prateleira Inicial Mandante:", ["Elite", "Meio", "Baixo"], key="pratm")
    prat_rival_m = st.selectbox("Prateleira do Rival para o Mandante:", ["Elite (Top 4)", "Meio de Tabela", "Z-4", "Igual"], key="prat_rival_m")
    
    st.markdown("**A) Sub-Bloco de Ataque (Proporção: 25%)**")
    fvo_m = st.slider("FVO (Força de Volume Ofensivo) - 60% do bloco:", 0.0, 100.0, 80.0, key="fvom")
    fco_m = st.slider("FCO (Fator de Conversão) - 40% do bloco:", 0.0, 100.0, 75.0, key="fcom")
    
    st.markdown("**B) Sub-Bloco de Defesa (Proporção: 25%)**")
    frd_m = st.slider("FRD (Força de Resiliência Defensiva) - 60% do bloco:", 0.0, 100.0, 85.0, key="frdm")
    fcd_m = st.slider("FCD (Fator de Conversão Defensiva) - 40% do bloco:", 0.0, 100.0, 70.0, key="fcdm")
    
    st.markdown("**C) Sub-Bloco de Consistência (Proporção: 35%)**")
    fdm_m = st.slider("FDM (Fator Desvio da Mediana) - 60% do bloco:", 0.0, 100.0, 82.0, key="fdmm")
    ier_m = st.slider("IER (Índice de Estabilidade) - 40% do bloco:", 0.0, 100.0, 78.0, key="ierm")
    
    st.markdown("**D) Bloco de Resistência à Pressão (Proporção: 15%)**")
    fcd_r_m = st.slider("FCD (Vol Chutes vs xG) - Peso 30%:", 0.0, 100.0, 75.0, key="fcdrm")
    egz_r_m = st.slider("EGZ (Taxa Conversão Cedida) - Peso 30%:", 0.0, 100.0, 80.0, key="egzrm")
    fri_r_m = st.slider("FRI (% Pontos Recuperados) - Peso 20%:", 0.0, 100.0, 65.0, key="frirm")
    fzc_r_m = st.slider("FZC (Minuto 75' ao 90'+) - Peso 20%:", 0.0, 100.0, 85.0, key="fzcrm")
    
    st.markdown("**📈 Configuração do Índice de Momento (ImA)**")
    cc3_m = st.slider("Aproveitamento últimos 3 jogos em casa (Peso 65%):", 0.0, 100.0, 80.0, key="cc3m")
    cc5_m = st.slider("Aproveitamento últimos 5 jogos em casa (Peso 35%):", 0.0, 100.0, 70.0, key="cc5m")
    g3_m = st.slider("Aproveitamento últimos 3 gerais (Peso 50%):", 0.0, 100.0, 85.0, key="g3m")
    g5_m = st.slider("Aproveitamento últimos 5 gerais (Peso 35%):", 0.0, 100.0, 75.0, key="g5m")
    g10_m = st.slider("Aproveitamento últimos 10 gerais (Peso 15%):", 0.0, 100.0, 70.0, key="g10m")
    tab_m = st.slider("Tabela Dinâmica (Aproveitamento últimos 5) - Proporção 20%:", 0.0, 100.0, 65.0, key="tabm")

with col_v:
    st.markdown("### 🚀 Configuração do Visitante")
    prat_v = st.selectbox("Prateleira Inicial Visitante:", ["Elite", "Meio", "Baixo"], key="pratv")
    prat_rival_v = st.selectbox("Prateleira do Rival para o Visitante:", ["Elite (Top 4)", "Meio de Tabela", "Z-4", "Igual"], key="prat_rival_v")
    
    st.markdown("**A) Sub-Bloco de Ataque (Proporção: 25%)**")
    fvo_v = st.slider("FVO (Força de Volume Ofensivo) - 60% do bloco:", 0.0, 100.0, 70.0, key="fvov")
    fco_v = st.slider("FCO (Fator de Conversão) - 40% do bloco:", 0.0, 100.0, 65.0, key="fcov")
    
    st.markdown("**B) Sub-Bloco de Defesa (Proporção: 25%)**")
    frd_v = st.slider("FRD (Força de Resiliência Defensiva) - 60% do bloco:", 0.0, 100.0, 75.0, key="frdv")
    fcd_v = st.slider("FCD (Fator de Conversão Defensiva) - 40% do bloco:", 0.0, 100.0, 60.0, key="fcdv")
    
    st.markdown("**C) Sub-Bloco de Consistência (Proporção: 35%)**")
    fdm_v = st.slider("FDM (Fator Desvio da Mediana) - 60% do bloco:", 0.0, 100.0, 70.0, key="fdmv")
    ier_v = st.slider("IER (Índice de Estabilidade) - 40% do bloco:", 0.0, 100.0, 68.0, key="ierv")
    
    st.markdown("**D) Bloco de Resistência à Pressão (Proporção: 15%)**")
    fcd_r_v = st.slider("FCD (Vol Chutes vs xG) - Peso 30%:", 0.0, 100.0, 65.0, key="fcdrv")
    egz_r_v = st.slider("EGZ (Taxa Conversão Cedida) - Peso 30%:", 0.0, 100.0, 70.0, key="egzrv")
    fri_r_v = st.slider("FRI (% Pontos Recuperados) - Peso 20%:", 0.0, 100.0, 50.0, key="frirv")
    fzc_r_v = st.slider("FZC (Minuto 75' ao 90'+) - Peso 20%:", 0.0, 100.0, 60.0, key="fzcrv")
    
    st.markdown("**📈 Configuração do Índice de Momento (ImA)**")
    cc3_v = st.slider("Aproveitamento últimos 3 jogos fora (Peso 65%):", 0.0, 100.0, 50.0, key="cc3v")
    cc5_v = st.slider("Aproveitamento últimos 5 jogos fora (Peso 35%):", 0.0, 100.0, 55.0, key="cc5v")
    g3_v = st.slider("Aproveitamento últimos 3 gerais (Peso 50%):", 0.0, 100.0, 60.0, key="g3v")
    g5_v = st.slider("Aproveitamento últimos 5 gerais (Peso 35%):", 0.0, 100.0, 58.0, key="g5v")
    g10_v = st.slider("Aproveitamento últimos 10 gerais (Peso 15%):", 0.0, 100.0, 62.0, key="g10v")
    tab_v = st.slider("Tabela Dinâmica (Aproveitamento últimos 5) - Proporção 20%:", 0.0, 100.0, 55.0, key="tabv")

# =========================================================================
# CHAMA AS FUNÇÕES DO SEU ARQUIVO ferramentas_calculo.py
# =========================================================================
# Processamento Mandante
nota_atq_m = calcular_bloco_ataque(fvo_m, fco_m)
nota_def_m = calcular_bloco_defesa(frd_m, fcd_m)
nota_cons_m = calcular_bloco_consistencia(fdm_m, ier_m)
nota_pres_m = calcular_bloco_resistencia_pressao(fcd_r_m, egz_r_m, fri_r_m, fzc_r_m)
overall_m = calcular_overall_unificado(nota_cons_m, nota_atq_m, nota_def_m, nota_pres_m)
im_m = calcular_im_final(cc3_m, cc5_m, g3_m, g5_m, g10_m, tab_m)

# Processamento Visitante
nota_atq_v = calcular_bloco_ataque(fvo_v, fco_v)
nota_def_v = calcular_bloco_defesa(frd_v, fcd_v)
nota_cons_v = calcular_bloco_consistencia(fdm_v, ier_v)
nota_pres_v = calcular_bloco_resistencia_pressao(fcd_r_v, egz_r_v, fri_r_v, fzc_r_v)
overall_v = calcular_overall_unificado(nota_cons_v, nota_atq_v, nota_def_v, nota_pres_v)
im_v = calcular_im_final(cc3_v, cc5_v, g3_v, g5_v, g10_v, tab_v)

# =========================================================================
# APRESENTAÇÃO COMPARATIVA FINAL NA TELA
# =========================================================================
st.divider()
st.header("🎯 Diagnóstico Unificado do Confronto")

col_res_m, col_fmp, col_res_v = st.columns(3)

with col_res_m:
    st.subheader("🔰 Diagnóstico Mandante")
    st.metric("🛡️ Overall Final (Passo 1)", f"{overall_m:.1f} / 100")
    st.write(f"• **Escalão FIFA:** {classificar_intervalo_fifa(overall_m)}")
    st.write(f"• Nota do Bloco Ataque: {nota_atq_m:.1f}")
    st.write(f"• Nota do Bloco Defesa: {nota_def_m:.1f}")
    st.write(f"• Nota de Consistência: {nota_cons_m:.1f}")
    st.write(f"• Nota de Pressão: {nota_pres_m:.1f}")
    st.metric("📈 Índice de Momento (ImA)", f"{im_m:.1f} / 100")

with col_fmp:
    st.markdown("<p style='text-align: center; font-weight: bold;'>Moduladores Ativos</p>", unsafe_allow_html=True)
    fmp_atq, fmp_def = calcular_fmp(prat_m, prat_v)
    st.write(f"• **FMP Acertos Ofensivos:** x{fmp_atq:.2f}")
    st.write(f"• **FMP Erros Defensivos:** x{fmp_def:.2f}")
    st.write("---")
    pts_emp_m = calcular_pontos_retrovisor("MANDANTE", "EMPATE", prat_rival_m)
    pts_emp_v = calcular_pontos_retrovisor("VISITANTE", "EMPATE", prat_rival_v)
    st.write(f"• **Empate Histórico Mandante:** {pts_emp_m:.2f} pts")
    st.write(f"• **Empate Histórico Visitante:** {pts_emp_v:.2f} pts")

with col_res_v:
    st.subheader("🚀 Diagnóstico Visitante")
    st.metric("🛡️ Overall Final (Passo 1)", f"{overall_v:.1f} / 100")
    st.write(f"• **Escalão FIFA:** {classificar_intervalo_fifa(overall_v)}")
    st.write(f"• Nota do Bloco Ataque: {nota_atq_v:.1f}")
    st.write(f"• Nota do Bloco Defesa: {nota_def_v:.1f}")
    st.write(f"• Nota de Consistência: {nota_cons_v:.1f}")
    st.write(f"• Nota de Pressão: {nota_pres_v:.1f}")
    st.metric("📈 Índice de Momento (ImA)", f"{im_v:.1f} / 100")
