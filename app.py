import streamlit as st

# Importação Integral das Fórmulas da sua Caixa de Ferramentas Externa
from ferramentas_calculo import (
    calcular_fmp, calcular_bloco_ataque, calcular_bloco_defesa,
    calcular_bloco_consistencia, calcular_bloco_resistencia_pressao,
    calcular_overall_unificado, classificar_intervalo_fifa,
    calcular_pontos_retrovisor, calcular_im_final,
    calcular_irc_final, calcular_juncao_unificada
)

st.set_page_config(page_title="Mypredict", layout="wide")
st.title("⚽ Mypredict — Validador de Métodos Combinados")
st.write("Cálculo integrado do Passo 1 (Overall), Passo 2/3 (Momento) e Índice Psicológico (IRC).")

# =========================================================================
# CONFIGURAÇÃO DE ENTRADA GRÁFICA SEM ENXERTOS
# =========================================================================
st.sidebar.header("⚙️ Contexto Geral do Confronto")
rodada_atual = st.sidebar.number_input("Número da Rodada Atual (1 a 38):", min_value=1, max_value=38, value=6)

st.header("⚔️ Tela de Confronto Direto")
col_m, col_v = st.columns(2)

with col_m:
    st.markdown("### 🏠 Equipe Mandante")
    time_m = st.text_input("Nome do Mandante:", value="Arsenal")
    prat_m = st.selectbox("Prateleira Estrutural Mandante (FMP):", ["Elite", "Meio", "Baixo"], key="pratm")
    ancora_m = st.selectbox("⚓ Âncora de Realidade Mandante (Tabela):", ["Escalão A (Elite)", "Escalão B (Meio)", "Escalão C (Risco)"], key="ancm")
    
    # Passo 1: Inputs de Atributos do Overall
    fvo_m = st.slider("FVO (Volume Ofensivo Mandante):", 0.0, 100.0, 85.0)
    fco_m = st.slider("FCO (Fator de Conversão Mandante):", 0.0, 100.0, 80.0)
    frd_m = st.slider("FRD (Resiliência Defensiva Mandante):", 0.0, 100.0, 90.0)
    fcd_m = st.slider("FCD (Conversão Defensiva Mandante):", 0.0, 100.0, 75.0)
    fdm_m = st.slider("FDM (Desvio da Mediana Mandante):", 0.0, 100.0, 82.0)
    ier_m = st.slider("IER (Índice de Estabilidade Mandante):", 0.0, 100.0, 88.0)
    
    # Bloco D: Resistência à Pressão
    st.markdown("**🥊 Resistência à Pressão (Sub-Bloco D):**")
    fcd_r_m = st.slider("FCD (Vol Chutes vs xG) Mandante:", 0.0, 100.0, 80.0)
    egz_r_m = st.slider("EGZ (Conversão Cedida) Mandante:", 0.0, 100.0, 75.0)
    fri_r_m = st.slider("FRI (% Pontos Recuperados) Mandante:", 0.0, 100.0, 70.0)
    fzc_r_m = st.slider("FZC (Minuto 75' ao 90'+) Mandante:", 0.0, 100.0, 85.0)
    
    # Passo 2: Inputs de Atributos do IM
    st.markdown("**📈 Desempenho de Momento (ImA):**")
    cc3_m = st.slider("CC3 (Últimos 3 Casa Mandante):", 0.0, 100.0, 80.0)
    cc5_m = st.slider("CC5 (Últimos 5 Casa Mandante):", 0.0, 100.0, 70.0)
    g3_m = st.slider("G3 (Últimos 3 Gerais Mandante):", 0.0, 100.0, 90.0)
    g5_m = st.slider("G5 (Últimos 5 Gerais Mandante):", 0.0, 100.0, 75.0)
    g10_m = st.slider("G10 (Últimos 10 Gerais Mandante):", 0.0, 100.0, 65.0)
    tab_m = st.slider("Tabela Dinâmica Mandante:", 0.0, 100.0, 70.0)
    
    # Gatilhos Psicológicos IRC
    st.markdown("**🧠 Fatores de Resposta Competitiva (IRC):**")
    pos_m = st.number_input("Nota Posição Atual Mandante (-30 a 30):", value=15, key="posm")
    elite_teorica_m = st.checkbox("Time tem Prospecção Teórica de 'Elite'? (FPT)", value=True, key="elitem")
    orgulho_m = st.selectbox("Orgulho Ferido Mandante:", [0, 10, 20], format_func=lambda x: "Não (+0)" if x==0 else "Derrota prateleira inferior (+10)" if x==10 else "Goleada Humilhante (+20)", key="orgm")
    revanche_m = st.checkbox("Jogo é uma Revanche recente Mandante? (+10)", value=False, key="revm")

with col_v:
    st.markdown("### 🚀 Equipe Visitante")
    time_v = st.text_input("Nome do Visitante:", value="Chelsea")
    prat_v = st.selectbox("Prateleira Estrutural Visitante (FMP):", ["Elite", "Meio", "Baixo"], key="pratv")
    ancora_v = st.selectbox("⚓ Âncora de Realidade Visitante (Tabela):", ["Escalão A (Elite)", "Escalão B (Meio)", "Escalão C (Risco)"], key="ancv")
    
    # Passo 1: Inputs de Atributos do Overall
    fvo_v = st.slider("FVO (Volume Ofensivo Visitante):", 0.0, 100.0, 75.0)
    fco_v = st.slider("FCO (Fator de Conversão Visitante):", 0.0, 100.0, 70.0)
    frd_v = st.slider("FRD (Resiliência Defensiva Visitante):", 0.0, 100.0, 70.0)
    fcd_v = st.slider("FCD (Conversão Defensiva Visitante):", 0.0, 100.0, 65.0)
    fdm_v = st.slider("FDM (Desvio da Mediana Visitante):", 0.0, 100.0, 74.0)
    ier_v = st.slider("IER (Índice de Estabilidade Visitante):", 0.0, 100.0, 70.0)
    
    # Bloco D: Resistência à Pressão
    st.markdown("**🥊 Resistência à Pressão (Sub-Bloco D):**")
    fcd_r_v = st.slider("FCD (Vol Chutes vs xG) Visitante:", 0.0, 100.0, 70.0)
    egz_r_v = st.slider("EGZ (Conversão Cedida) Visitante:", 0.0, 100.0, 60.0)
    fri_r_v = st.slider("FRI (% Pontos Recuperados) Visitante:", 0.0, 100.0, 50.0)
    fzc_r_v = st.slider("FZC (Minuto 75' ao 90'+) Visitante:", 0.0, 100.0, 60.0)
    
    # Passo 2: Inputs de Atributos do IM
    st.markdown("**📈 Desempenho de Momento (ImA):**")
    cc3_v = st.slider("CC3 (Últimos 3 Fora Visitante):", 0.0, 100.0, 40.0)
    cc5_v = st.slider("CC5 (Últimos 5 Fora Visitante):", 0.0, 100.0, 50.0)
    g3_v = st.slider("G3 (Últimos 3 Gerais Visitante):", 0.0, 100.0, 60.0)
    g5_v = st.slider("G5 (Últimos 5 Gerais Visitante):", 0.0, 100.0, 55.0)
    g10_v = st.slider("G10 (Últimos 10 Gerais Visitante):", 0.0, 100.0, 60.0)
    tab_v = st.slider("Tabela Dinâmica Visitante:", 0.0, 100.0, 50.0)
    
    # Gatilhos Psicológicos IRC
    st.markdown("**🧠 Fatores de Resposta Competitiva (IRC):**")
    pos_v = st.number_input("Nota Posição Atual Visitante (-30 a 30):", value=5, key="posv")
    elite_teorica_v = st.checkbox("Time tem Prospecção Teórica de 'Elite'? (FPT)", value=False, key="elitev")
    orgulho_v = st.selectbox("Orgulho Ferido Visitante:", [0, 10, 20], format_func=lambda x: "Não (+0)" if x==0 else "Derrota prateleira inferior (+10)" if x==10 else "Goleada Humilhante (+20)", key="orgv")
    revanche_v = st.checkbox("Jogo é uma Revanche recente Visitante? (+10)", value=True, key="revv")

# =========================================================================
# MAQUINA DE PROCESSAMENTO CENTRALIZADO (MOURA DOS DADOS)
# =========================================================================
# Processamento Mandante
atq_m = calcular_bloco_ataque(fvo_m, fco_m)
def_m = calcular_bloco_defesa(frd_m, fcd_m)
cons_m = calcular_bloco_consistencia(fdm_m, ier_m)
pres_m = calcular_bloco_resistencia_pressao(fcd_r_m, egz_r_m, fri_r_m, fzc_r_m)
overall_m = calcular_overall_unificado(cons_m, atq_m, def_m, pres_m)
im_m = calcular_im_final(cc3_m, cc5_m, g3_m, g5_m, g10_m, tab_m)
irc_m = calcular_irc_final(rodada_atual, pos_m, elite_teorica_m, orgulho_m, 10 if revanche_m else 0)
juncao_m = calcular_juncao_unificado(overall_m, im_m, irc_m)

# Processamento Visitante
atq_v = calcular_bloco_ataque(fvo_v, fco_v)
def_v = calcular_bloco_defesa(frd_v, fcd_v)
cons_v = calcular_bloco_consistencia(fdm_v, ier_v)
pres_v = calcular_bloco_resistencia_pressao(fcd_r_v, egz_r_v, fri_r_v, fzc_r_v)
overall_v = calcular_overall_unificado(cons_v, atq_v, def_v, pres_v)
im_v = calcular_im_final(cc3_v, cc5_v, g3_v, g5_v, g10_v, tab_v)
irc_v = calcular_irc_final(rodada_atual, pos_v, elite_teorica_v, orgulho_v, 10 if revanche_v else 0)
juncao_v = calcular_juncao_unificado(overall_v, im_v, irc_v)

# Cálculo da Disparidade Crítica Final (Passo 4)
disparidade_critica = juncao_m - juncao_v

# =========================================================================
# APRESENTAÇÃO DOS RESULTADOS COMPARATIVOS
# =========================================================================
st.divider()
st.header("🎯 PASSO 4: Diagnóstico de Confronto Direto e Disparidade")

col_res_m, col_vs, col_res_v = st.columns(3)

with col_res_m:
    st.subheader(f"🏠 {time_m}")
    st.metric("🔰 Nota Junção Mandante", f"{juncao_m:.2f} / 100")
    st.write(f"• **Overall Estrutural:** {overall_m:.1f} ({classificar_intervalo_fifa(overall_m)})")
    st.write(f"• **Índice Momento (IM):** {im_m:.1f}")
    st.write(f"• **Resposta Psicológica (IRC):** {irc_m:.1f}")
    st.write("---")
    st.write(f"• Força de Ataque: {atq_m:.1f} | Defesa: {def_m:.1f}")
    st.write(f"• Consistência: {cons_m:.1f} | Pressão: {pres_m:.1f}")

with col_vs:
    st.markdown("<p style='text-align: center; font-weight: bold; margin-top: 20px;'>Diferença Crítica Final</p>", unsafe_allow_html=True)
    cor_disp = "green" if disparidade_critica > 8 else "red" if disparidade_critica < -8 else "orange"
    st.markdown(f"<h2 style='text-align: center; color: {cor_disp};'>{disparidade_critica:+.2f}</h2>", unsafe_allow_html=True)
    
    # Exibe os Moduladores de Prateleira Dinâmicos (FMP) ativos
    fmp_atq, fmp_def = calcular_fmp(prat_m, prat_v)
    st.caption(f"<p style='text-align: center;'><b>Modulação FMP:</b><br>Acertos Ofensivos: x{fmp_atq:.2f}<br>Erros Defensivos: x{fmp_def:.2f}</p>", unsafe_allow_html=True)
    st.write("---")
    # Consulta Ponderada do Passo 3 de Empates
    pts_emp_m = calcular_pontos_retrovisor("MANDANTE", "EMPATE", ancora_v)
    pts_emp_v = calcular_pontos_retrovisor("VISITANTE", "EMPATE", ancora_m)
    st.caption(f"<p style='text-align: center;'><b>Peso de Empate (Passo 3):</b><br>Para o Mandante vale {pts_emp_m:.2f} pts<br>Para o Visitante vale {pts_emp_v:.2f} pts</p>", unsafe_allow_html=True)

with col_res_v:
    st.subheader(f"🚀 {time_v}")
    st.metric("🔰 Nota Junção Visitante", f"{juncao_v:.2f} / 100")
    st.write(f"• **Overall Estrutural:** {overall_v:.1f} ({classificar_intervalo_fifa(overall_v)})")
    st.write(f"• **Índice Momento (IM):** {im_v:.1f}")
    st.write(f"• **Resposta Psicológica (IRC):** {irc_v:.1f}")
    st.write("---")
    st.write(f"• Força de Ataque: {atq_v:.1f} | Defesa: {def_v:.1f}")
    st.write(f"• Consistência: {cons_v:.1f} | Pressão: {pres_v:.1f}")

