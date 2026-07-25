import streamlit as st
import pandas as pd
import os

# Importação Integral das Fórmulas da sua Caixa de Ferramentas Externa
from ferramentas_calculo import (
    calcular_fmp, calcular_bloco_ataque, calcular_bloco_defesa,
    calcular_bloco_consistencia, calcular_bloco_resistencia_pressao,
    calcular_overall_unificado, classificar_intervalo_fifa,
    calcular_pontos_retrovisor, calcular_im_final,
    calcular_irc_final, calcular_juncao_unificada
)

st.set_page_config(page_title="Mypredict", layout="wide")
st.title("⚽ Mypredict — Painel Híbrido Automático")

# Chave Seletora de Origem de Dados
st.sidebar.header("🔌 Origem dos Dados")
modo_dados = st.sidebar.radio("Selecione a Fonte de Entrada:", ["Planilha Local (.csv)", "API-Football (Acesso Direto)"])

arquivo_csv = "jogos_historicos.csv"

# -------------------------------------------------------------------------
# MODO AUTOMÁTICO 1: LEITURA VIA PLANILHA HISTÓRICA LOCAL
# -------------------------------------------------------------------------
if modo_dados == "Planilha Local (.csv)":
    if not os.path.exists(arquivo_csv):
        st.info("📊 **Aguardando Planilha:** O arquivo 'jogos_historicos.csv' não foi localizado na raiz do seu GitHub.")
        st.stop()
        
    try:
        # CORREÇÃO DEFINITIVA (VÍRGULA): on_bad_lines='skip' ignora qualquer linha desalinhada e carrega o arquivo liso
        df_jogos = pd.read_csv(arquivo_csv, sep=',', on_bad_lines='skip', engine='python')
        
        st.header("🗂️ Seleção de Confronto por Planilha")
        
        # Monta as opções do menu usando os títulos oficiais em inglês do Football-Data
        opcoes_menu = []
        for idx, r in df_jogos.iterrows():
            # Evita erros se a linha contiver células em branco
            if pd.notna(r.get('Date')) and pd.notna(r.get('HomeTeam')) and pd.notna(r.get('AwayTeam')):
                texto = f"📅 {r['Date']} - {r['HomeTeam']} vs {r['AwayTeam']}"
                opcoes_menu.append(texto)
        
        if not opcoes_menu:
            st.warning("⚠️ Planilha carregada, mas nenhuma linha válida foi identificada.")
            st.stop()
            
        jogo_sel = st.selectbox("Selecione o Jogo da Lista:", options=opcoes_menu)
        
        # Separa os dados da linha selecionada de forma isolada
        linha_filtrada = df_jogos[df_jogos.apply(lambda r: f"📅 {r.get('Date')} - {r.get('HomeTeam')} vs {r.get('AwayTeam')}" == jogo_sel if pd.notna(r.get('Date')) else False, axis=1)]
        
        if linha_filtrada.empty:
            st.error("Erro ao isolar os dados do confronto selecionado.")
            st.stop()
            
        dados_partida = linha_filtrada.iloc[0]
        
        # Preenchimento Automático Baseado nas Colunas Oficiais da Planilha Real
        time_m = dados_partida["HomeTeam"]
        time_v = dados_partida["AwayTeam"]
        gols_m_real = dados_partida.get("FTHG", "?") 
        gols_v_real = dados_partida.get("FTAG", "?") 
        rodada_atual = 6
        
        # Definição automática de prateleiras baseadas nas equipes selecionadas
        grandes = ["Liverpool", "Man City", "Arsenal", "Man United", "Chelsea", "Tottenham"]
        prat_m = "Elite" if time_m in grandes else "Meio"
        prat_v = "Elite" if time_v in grandes else "Meio"
        ancora_m = "Escalão A (Elite)" if prat_m == "Elite" else "Escalão B (Meio)"
        ancora_v = "Escalão A (Elite)" if prat_v == "Elite" else "Escalão B (Meio)"
        
        # Valores estruturais padrão de desenvolvimento alimentando as equações
        fvo_m, fco_m, frd_m, fcd_m, fdm_m, ier_m = 80.0, 80.0, 80.0, 80.0, 80.0, 80.0
        fcd_r_m, egz_r_m, fri_r_m, fzc_r_m = 75.0, 75.0, 70.0, 70.0
        cc3_m, cc5_m, g3_m, g5_m, g10_m, tab_m = 75.0, 75.0, 75.0, 75.0, 75.0, 75.0
        pos_m, elite_m, org_m, rev_m = 10, True, 0, 0
        
        fvo_v, fco_v, frd_v, fcd_v, fdm_v, ier_v = 70.0, 70.0, 70.0, 70.0, 70.0, 70.0
        fcd_r_v, egz_r_v, fri_r_v, fzc_r_v = 65.0, 65.0, 60.0, 60.0
        cc3_v, cc5_v, g3_v, g5_v, g10_v, tab_v = 65.0, 65.0, 65.0, 65.0, 65.0, 65.0
        pos_v, elite_v, org_v, rev_v = 5, False, 0, 0
        
    except Exception as e:
        st.error(f"❌ Erro de processamento na planilha (Item 9): {e}")
        st.stop()

# -------------------------------------------------------------------------
# MODO AUTOMÁTICO 2: PREPARAÇÃO COMPLETA PARA ENTRADA VIA API
# -------------------------------------------------------------------------
else:
    st.header("🌐 Consulta via API-Football Ativa")
    st.write("Layout estruturado. Os valores abaixo representam a blueprint pronta para recepção de dados via ID.")
    
    id_partida_api = st.text_input("Insira o ID Real do Jogo (Fixture ID):", value="1035341")
    rodada_atual = st.number_input("Número da Rodada Atual:", min_value=1, max_value=38, value=6)
    
    time_m, time_v = "Time Mandante (API)", "Time Visitante (API)"
    gols_m_real, gols_v_real = "?", "?"
    prat_m, prat_v, ancora_m, ancora_v = "Elite", "Meio", "Escalão A (Elite)", "Escalão B (Meio)"
    fvo_m, fco_m, frd_m, fcd_m, fdm_m, ier_m = 80.0, 80.0, 80.0, 80.0, 80.0, 80.0
    fcd_r_m, egz_r_m, fri_r_m, fzc_r_m = 75.0, 75.0, 70.0, 70.0
    cc3_m, cc5_m, g3_m, g5_m, g10_m, tab_m = 75.0, 75.0, 75.0, 75.0, 75.0, 75.0
    pos_m, elite_m, org_m, rev_m = 10, True, 0, 0
    
    fvo_v, fco_v, frd_v, fcd_v, fdm_v, ier_v = 70.0, 70.0, 70.0, 70.0, 70.0, 70.0
    fcd_r_v, egz_r_v, fri_r_v, fzc_r_v = 65.0, 65.0, 60.0, 60.0
    cc3_v, cc5_v, g3_v, g5_v, g10_v, tab_v = 65.0, 65.0, 65.0, 65.0, 65.0, 65.0
    pos_v, elite_v, org_v, rev_v = 5, False, 0, 10

# =========================================================================
# PROCESSAMENTO CENTRALIZADO (MOTOR MATEMÁTICO INTEGRAL)
# =========================================================================
# Garante que as variáveis numéricas sejam floats puros para as equações da Caixa de Ferramentas
fvo_m, fco_m, frd_m, fcd_m = float(fvo_m), float(fco_m), float(frd_m), float(fcd_m)
fdm_m, ier_m, fcd_r_m, egz_r_m = float(fdm_m), float(ier_m), float(fcd_r_m), float(egz_r_m)
fri_r_m, fzc_r_m, cc3_m, cc5_m = float(fri_r_m), float(fzc_r_m), float(cc3_m), float(cc5_m)
g3_m, g5_m, g10_m, tab_m = float(g3_m), float(g5_m), float(g10_m), float(tab_m)

fvo_v, fco_v, frd_v, fcd_v = float(fvo_v), float(fco_v), float(frd_v), float(fcd_v)
fdm_v, ier_v, fcd_r_v, egz_r_v = float(fdm_v), float(ier_v), float(fcd_r_v), float(egz_r_v)
fri_r_v, fzc_r_v, cc3_v, cc5_v = float(fri_r_v), float(fzc_r_v), float(cc3_v), float(cc5_v)
g3_v, g5_v, g10_v, tab_v = float(g3_v), float(g5_v), float(g10_v), float(tab_v)

# Execução das equações importadas
atq_m = calcular_bloco_ataque(fvo_m, fco_m)
def_m = calcular_bloco_defesa(frd_m, fcd_m)
cons_m = calcular_bloco_consistencia(fdm_m, ier_m)
pres_m = calcular_bloco_resistencia_pressao(fcd_r_m, egz_r_m, fri_r_m, fzc_r_m)
overall_m = calcular_overall_unificado(cons_m, atq_m, def_m, pres_m)
im_m = calcular_im_final(cc3_m, cc5_m, g3_m, g5_m, g10_m, tab_m)
irc_m = calcular_irc_final(rodada_atual, int(pos_m), elite_m, int(org_m), int(rev_m))
juncao_m = calcular_juncao_unificada(overall_m, im_m, irc_m)

atq_v = calcular_bloco_ataque(fvo_v, fco_v)
def_v = calcular_bloco_defesa(frd_v, fcd_v)
cons_v = calcular_bloco_consistencia(fdm_v, ier_v)
pres_v = calcular_bloco_resistencia_pressao(fcd_r_v, egz_r_v, fri_r_v, fzc_r_v)
overall_v = calcular_overall_unificado(cons_v, atq_v, def_v, pres_v)
im_v = calcular_im_final(cc3_v, cc5_v, g3_v, g5_v, g10_v, tab_v)
irc_v = calcular_irc_final(rodada_atual, int(pos_v), elite_v, int(org_v), int(rev_v))
juncao_v = calcular_juncao_unificada(overall_v, im_v, irc_v)

disparidade_critica = juncao_m - juncao_v

# =========================================================================
# LAYOUT DE EXIBIÇÃO: LAUDO TÉCNICO COMPREENSÍVEL DO MYPREDICT
# =========================================================================
st.divider()
st.subheader(f"📊 Laudo Preditivo Unificado: {time_m} vs {time_v}")
st.write(f"Placar Oficial Ocorrido no Dia: **{gols_m_real} x {gols_v_real}**")

col_res_m, col_vs, col_res_v = st.columns(3)

with col_res_m:
    st.markdown(f"### 🏠 {time_m}")
    st.metric("🔰 Nota Junção Mandante", f"{juncao_m:.2f} / 100")
    st.write(f"• **Overall Final (Passo 1):** {overall_m:.1f} ({classificar_intervalo_fifa(overall_m)})")
    st.write(f"• ⚔️ **Força de Ataque:** {atq_m:.1f} | 🛡️ **Defesa:** {def_m:.1f}")
    st.write(f"• 📐 **Consistência Tática:** {cons_m:.1f} | 🥊 **Resistência:** {pres_m:.1f}")
    st.write(f"• **Índice Momento (IM):** {im_m:.1f}")
    st.write(f"• **Índice Psicológico (IRC):** {irc_m:.1f}")

with col_vs:
    st.markdown("<p style='text-align: center; font-weight: bold; margin-top: 20px;'>Diferença Crítica Final</p>", unsafe_allow_html=True)
    cor_disp = "green" if disparidade_critica > 8 else "red" if disparidade_critica < -8 else "orange"
    st.markdown(f"<h2 style='text-align: center; color: {cor_disp};'>{disparidade_critica:+.2f}</h2>", unsafe_allow_html=True)
    
    fmp_atq, fmp_def = calcular_fmp(prat_m, prat_v)
    st.caption(f"<p style='text-align: center;'><b>Modulação FMP:</b><br>Acertos Ofensivos: x{fmp_atq:.2f}<br>Erros Defensivos: x{fmp_def:.2f}</p>", unsafe_allow_html=True)
    st.write("---")
    pts_emp_m = calcular_pontos_retrovisor("MANDANTE", "EMPATE", ancora_v)
    pts_emp_v = calcular_pontos_retrovisor("VISITANTE", "EMPATE", ancora_m)
    st.caption(f"<p style='text-align: center;'><b>Peso de Empate (Passo 3):</b><br>Mandante: {pts_emp_m:.2f} pts | Visitante: {pts_emp_v:.2f} pts</p>", unsafe_allow_html=True)

with col_res_v:
    st.markdown(f"### 🚀 {time_v}")
    st.metric("🔰 Nota Junção Visitante", f"{juncao_v:.2f} / 100")
    st.write(f"• **Overall Final (Passo 1):** {overall_v:.1f} ({classificar_intervalo_fifa(overall_v)})")
    st.write(f"• ⚔️ **Força de Ataque:** {atq_v:.1f} | 🛡️ **Defesa:** {def_v:.1f}")
    st.write(f"• 📐 Consistência Tática: {cons_v:.1f} | 🥊 Resistência: {pres_v:.1f}")
    st.write(f"• Índice Momento (IM): {im_v:.1f}")
    st.write(f"• Índice Psicológico (IRC): {irc_v:.1f}")
