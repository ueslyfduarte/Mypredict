import streamlit as st
import pandas as pd
import os

# Importação da sua caixa de ferramentas matemática
from ferramentas_calculo import (
    calcular_fmp, calcular_bloco_ataque, calcular_bloco_defesa,
    calcular_bloco_consistencia, calcular_bloco_resistencia_pressao,
    calcular_overall_unificado, classificar_intervalo_fifa,
    calcular_pontos_retrovisor, calcular_im_final,
    calcular_irc_final, calcular_juncao_unificada
)

# Importação do seu módulo de internet original (Caso decida usar a API)
from ponte_api import buscar_dados_api

st.set_page_config(page_title="Mypredict", layout="wide")
st.title("⚽ Mypredict — Painel Híbrido Avançado")

# =========================================================================
# CHAVE SELETORA: VOCÊ ESCOLHE DE ONDE VÊM OS DADOS DO CONFRONTO
# =========================================================================
st.sidebar.header("🔌 Origem dos Dados")
modo_dados = st.sidebar.radio("Selecione a Fonte de Entrada:", ["Planilha Local (.csv)", "API-Football (Internet)"])

arquivo_csv = "jogos_historicos.csv"

# -------------------------------------------------------------------------
# MODO DE OPERAÇÃO A: PLANILHA LOCAL
# -------------------------------------------------------------------------
if modo_dados == "Planilha Local (.csv)":
    if not os.path.exists(arquivo_csv):
        st.info("📊 **Aguardando Planilha:** Crie o arquivo 'jogos_historicos.csv' no seu GitHub para rodar o modo local de graça.")
        st.stop()
        
    # CORREÇÃO AUTOMÁTICA DE SEPARADOR: Lê o arquivo mesmo que ele use espaços em vez de vírgulas
df_jogos = pd.read_csv(arquivo_csv, sep=r'\s+', engine='python')

    
    st.header("🗂️ Seleção de Confronto por Planilha")
    c1, c2 = st.columns(2)
    with c1:
        temp_sel = st.selectbox("Escolha a Temporada:", options=df_jogos["temporada"].unique().tolist())
    df_filtrado = df_jogos[df_jogos["temporada"] == temp_sel]
    
    opcoes_menu = [f"📅 {r['data']} - ({r['rodada']}) - {r['mandante']} vs {r['visitante']}" for _, r in df_filtrado.iterrows()]
    with c2:
        jogo_sel = st.selectbox("Selecione o Jogo da Lista:", options=opcoes_menu)
        
    dados_partida = df_filtrado[df_filtrado.apply(lambda r: f"📅 {r['data']} - ({r['rodada']}) - {r['mandante']} vs {r['visitante']}" == jogo_sel, axis=1)].iloc[0]
    
    time_m = dados_partida["mandante"]
    time_v = dados_partida["visitante"]
    gols_m_real = dados_partida["gols_mandante"]
    gols_v_real = dados_partida["gols_visitante"]
    
    # Captura automática dos valores vindos das colunas do seu arquivo
    fvo_m, fco_m = dados_partida.get("fvo_m", 80), dados_partida.get("fco_m", 75)
    frd_m, fcd_m = dados_partida.get("frd_m", 85), dados_partida.get("fcd_m", 70)
    fdm_m, ier_m = dados_partida.get("fdm_m", 80), dados_partida.get("ier_m", 85)
    fcd_r_m, egz_r_m, fri_r_m, fzc_r_m = dados_partida.get("fcd_r_m", 75), dados_partida.get("egz_r_m", 80), dados_partida.get("fri_r_m", 70), dados_partida.get("fzc_r_m", 85)
    cc3_m, cc5_m, g3_m, g5_m, g10_m, tab_m = dados_partida.get("cc3_m", 80), dados_partida.get("cc5_m", 75), dados_partida.get("g3_m", 85), dados_partida.get("g5_m", 80), dados_partida.get("g10_m", 75), dados_partida.get("tab_m", 70)
    pos_m, org_m, rev_m = dados_partida.get("pos_m", 10), dados_partida.get("org_m", 0), dados_partida.get("rev_m", 0)
    
    fvo_v, fco_v = dados_partida.get("fvo_v", 70), dados_partida.get("fco_v", 65)
    frd_v, fcd_v = dados_partida.get("frd_v", 72), dados_partida.get("fcd_v", 68)
    fdm_v, ier_v = dados_partida.get("fdm_v", 74), dados_partida.get("ier_v", 70)
    fcd_r_v, egz_r_v, fri_r_v, fzc_r_v = dados_partida.get("fcd_r_v", 65), dados_partida.get("egz_r_v", 70), dados_partida.get("fri_r_v", 50), dados_partida.get("fzc_r_v", 60)
    cc3_v, cc5_v, g3_v, g5_v, g10_v, tab_v = dados_partida.get("cc3_v", 55), dados_partida.get("cc5_v", 60), dados_partida.get("g3_v", 62), dados_partida.get("g5_v", 58), dados_partida.get("g10_v", 60), dados_partida.get("tab_v", 55)
    pos_v, org_v, rev_v = dados_partida.get("pos_v", 5), dados_partida.get("org_v", 0), dados_partida.get("rev_v", 0)
    rodada_atual = int(dados_partida.get("numero_rodada", 6))

# -------------------------------------------------------------------------
# MODO DE OPERAÇÃO B: API-FOOTBALL (INTERNET ATIVA)
# -------------------------------------------------------------------------
else:
    st.header("🌐 Consulta via API-Football Ativa")
    st.write("Insira os parâmetros abaixo. O app usará a função contida no seu 'ponte_api.py'.")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        id_partida_api = st.text_input("Insira o ID Real do Jogo (Fixture ID):", value="1035341")
    with col_a2:
        rodada_atual = st.number_input("Rodada Atual do Confronto:", min_value=1, max_value=38, value=6)
        
    # Valores base pré-setados para a API preencher no futuro quando destravar o Cloudflare
    time_m, time_v = "Time Mandante", "Time Visitante"
    gols_m_real, gols_v_real = "?", "?"
    fvo_m, fco_m, frd_m, fcd_m, fdm_m, ier_m = 80, 80, 80, 80, 80, 80
    fcd_r_m, egz_r_m, fri_r_m, fzc_r_m = 75, 75, 70, 70
    cc3_m, cc5_m, g3_m, g5_m, g10_m, tab_m = 75, 75, 75, 75, 75, 75
    pos_m, org_m, rev_m = 10, 0, 0
    
    fvo_v, fco_v, frd_v, fcd_v, fdm_v, ier_v = 70, 70, 70, 70, 70, 70
    fcd_r_v, egz_r_v, fri_r_v, fzc_r_v = 65, 65, 60, 60
    cc3_v, cc5_v, g3_v, g5_v, g10_v, tab_v = 65, 65, 65, 65, 65, 65
    pos_v, org_v, rev_v = 5, 0, 0

# =========================================================================
# CENTRAL DE PROCESSAMENTO DO MÉTODOS (UNIFICADO PARA AS DUAS FONTES)
# =========================================================================
# Execução das equações da Caixa de Ferramentas
atq_m = calcular_bloco_ataque(fvo_m, fco_m)
def_m = calcular_bloco_defesa(frd_m, fcd_m)
cons_m = calcular_bloco_consistencia(fdm_m, ier_m)
pres_m = calcular_bloco_resistencia_pressao(fcd_r_m, egz_r_m, fri_r_m, fzc_r_m)
overall_m = calcular_overall_unificado(cons_m, atq_m, def_m, pres_m)
im_m = calcular_im_final(cc3_m, cc5_m, g3_m, g5_m, g10_m, tab_m)
irc_m = calcular_irc_final(rodada_atual, pos_m, True, org_m, 10 if rev_m else 0)
juncao_m = calcular_juncao_unificada(overall_m, im_m, irc_m)

atq_v = calcular_bloco_ataque(fvo_v, fco_v)
def_v = calcular_bloco_defesa(frd_v, fcd_v)
cons_v = calcular_bloco_consistencia(fdm_v, ier_v)
pres_v = calcular_bloco_resistencia_pressao(fcd_r_v, egz_r_v, fri_r_v, fzc_r_v)
overall_v = calcular_overall_unificado(cons_v, atq_v, def_v, pres_v)
im_v = calcular_im_final(cc3_v, cc5_v, g3_v, g5_v, g10_v, tab_v)
irc_v = calcular_irc_final(rodada_atual, pos_v, False, org_v, 10 if rev_v else 0)
juncao_v = calcular_juncao_unificada(overall_v, im_v, irc_v)

disparidade_critica = juncao_m - juncao_v

# =========================================================================
# TELA DE APRESENTAÇÃO DO LAUDO (IDÊNTICA PARA AMBOS OS MODOS)
# =========================================================================
st.divider()
st.subheader(f"📊 Laudo Preditivo Unificado: {time_m} vs {time_v}")
st.write(f"Placar Real Identificado: **{gols_m_real} x {gols_v_real}**")

col_res_m, col_vs, col_res_v = st.columns(3)

with col_res_m:
    st.markdown(f"### 🏠 {time_m}")
    st.metric("🔰 Nota Junção Mandante", f"{juncao_m:.2f} / 100")
    st.write(f"• **Overall Final:** {overall_m:.1f} ({classificar_intervalo_fifa(overall_m)})")
    st.write(f"• **Força de Ataque:** {atq_m:.1f} | **Defesa:** {def_m:.1f}")
    st.write(f"• **Consistência:** {cons_m:.1f} | **Resistência:** {pres_m:.1f}")
    st.write(f"• **Índice Momento (ImA):** {im_m:.1f}")
    st.write(f"• **Índice Psicológico (IRC):** {irc_m:.1f}")

with col_vs:
    st.markdown("<p style='text-align: center; font-weight: bold; margin-top: 20px;'>Diferença Crítica Final</p>", unsafe_allow_html=True)
    cor_disp = "green" if disparidade_critica > 8 else "red" if disparidade_critica < -8 else "orange"
    st.markdown(f"<h2 style='text-align: center; color: {cor_disp};'>{disparidade_critica:+.2f}</h2>", unsafe_allow_html=True)
    
    fmp_atq, fmp_def = calcular_fmp("Elite", "Meio")
    st.caption(f"<p style='text-align: center;'><b>Modulação FMP:</b><br>Acertos Ofensivos: x{fmp_atq:.2f}<br>Erros Defensivos: x{fmp_def:.2f}</p>", unsafe_allow_html=True)

with col_res_v:
    st.markdown(f"### 🚀 {time_v}")
    st.metric("🔰 Nota Junção Visitante", f"{juncao_v:.2f} / 100")
    st.write(f"• **Overall Final:** {overall_v:.1f} ({classificar_intervalo_fifa(overall_v)})")
    st.write(f"• **Força de Ataque:** {atq_v:.1f} | **Defesa:** {def_v:.1f}")
    st.write(f"• **Consistência:** {cons_v:.1f} | **Resistência:** {pres_v:.1f}")
    st.write(f"• **Índice Momento (ImA):** {im_v:.1f}")
    st.write(f"• **Índice Psicológico (IRC):** {irc_v:.1f}")
