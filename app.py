import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# =========================================================================
# CONFIGURAÇÃO DA PÁGINA - TEMA PRETO E DOURADO
# =========================================================================
st.set_page_config(
    page_title="MyPredict by Ferry v1.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# CSS CUSTOMIZADO (COM BOTÃO GRANDE E DESTAQUE DOURADO)
# =========================================================================
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #ffffff; }
    section[data-testid="stSidebar"] { background-color: #0d0d0d; border-right: 2px solid #ffd700; }
    section[data-testid="stSidebar"] * { color: #ffffff !important; }
    h1, h2, h3 { color: #ffd700 !important; font-weight: 700; letter-spacing: 1px; }
    h2 { border-bottom: 2px solid #ffd700; padding-bottom: 8px; }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a00, #2a2a00);
        border: 1px solid #ffd700;
        border-radius: 15px;
        padding: 20px;
        color: #ffffff;
        box-shadow: 0 4px 15px rgba(255,215,0,0.2);
        transition: 0.3s;
    }
    div[data-testid="stMetric"]:hover { border-color: #ffea80; box-shadow: 0 6px 25px rgba(255,215,0,0.5); }
    div[data-testid="stMetric"] label { color: #ffd700 !important; font-weight: 600; }
    /* Botão MyPredict gigante e dourado */
    div.stButton > button {
        background: linear-gradient(135deg, #b8860b, #ffd700);
        color: #000000;
        border: 3px solid #ffd700;
        border-radius: 15px;
        font-weight: bold;
        font-size: 28px;
        padding: 18px 40px;
        transition: 0.3s;
        letter-spacing: 2px;
        width: 100%;
        box-shadow: 0 0 30px rgba(255,215,0,0.7);
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #ffd700, #ffea80);
        border-color: #ffffff;
        box-shadow: 0 0 50px rgba(255,215,0,1);
        transform: scale(1.03);
    }
    .welcome-card {
        background: linear-gradient(135deg, #1a1a00, #0d0d0d);
        border: 1px solid #ffd700;
        border-radius: 15px;
        padding: 30px;
        margin: 20px 0;
        box-shadow: 0 8px 20px rgba(255,215,0,0.2);
    }
    .quote {
        font-style: italic;
        color: #ffd700;
        font-size: 20px;
        border-left: 5px solid #ffd700;
        padding-left: 25px;
        margin: 30px 0;
        background: rgba(255,215,0,0.05);
        padding: 15px 25px;
        border-radius: 0 10px 10px 0;
    }
    .analysis-box {
        background: linear-gradient(135deg, #1a1a00, #0d0d0d);
        border: 1px solid #ffd700;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: #e0e0e0;
        line-height: 1.6;
    }
    .analysis-box h4 { color: #ffd700; margin-top: 0; }
    /* Cartão de IMP em destaque */
    .imp-highlight {
        background: linear-gradient(135deg, #2a1a00, #4d3e00);
        border: 2px solid #ffd700;
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 0 40px rgba(255,215,0,0.6);
    }
    .imp-highlight h2 { color: #ffd700; font-size: 48px; margin: 0; }
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #1a1a00, #0d0d0d);
        border: 1px solid #ffd700;
        border-radius: 10px;
        color: #ffd700;
        font-weight: 600;
    }
    .streamlit-expanderHeader:hover { border-color: #ffea80; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>textarea {
        background-color: #1a1a00;
        color: white;
        border: 1px solid #ffd700;
        border-radius: 8px;
    }
    .stDataFrame {
        background-color: #0d0d0d;
        border: 1px solid #ffd700;
        border-radius: 10px;
        overflow: hidden;
    }
    .stDataFrame thead th { background-color: #ffd700 !important; color: #0a0a0a !important; font-weight: bold; }
    .stDataFrame tbody td { background-color: #1a1a00; color: #ffffff; border-bottom: 1px solid #2a2a00; }
    .stDataFrame tbody tr:hover td { background-color: #2a2a00 !important; color: #ffd700 !important; }
    .result-banner {
        padding: 20px; border-radius: 15px; text-align: center; font-size: 24px;
        font-weight: bold; margin: 20px 0; box-shadow: 0 8px 25px rgba(255,215,0,0.4);
    }
    .result-win { background: linear-gradient(135deg, #0a3d0a, #1a5c1a); border: 2px solid #ffd700; color: #a5d6a7; }
    .result-draw { background: linear-gradient(135deg, #3d3500, #5c5200); border: 2px solid #ffd700; color: #ffe082; }
    .market-card {
        background: linear-gradient(135deg, #1a1a00, #2a2a00);
        border: 1px solid #ffd700; border-radius: 10px; padding: 15px; margin: 8px 0;
        text-align: center; color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================================
# CABEÇALHO
# =========================================================================
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("<div style='font-size: 60px; text-align: center;'>⚽</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin-bottom: 0;'>MyPredict by Ferry</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #ffd700; font-size: 18px; margin-top: 0;'>v1.0 • Inteligência Estatística no Futebol</p>", unsafe_allow_html=True)

st.markdown("<div class='welcome-card'>", unsafe_allow_html=True)
st.markdown("""
### 👋 Bem-vindo ao MyPredict!

O **MyPredict** é um sistema avançado de análise e previsão de partidas de futebol baseado no **Método FMP (Fator de Modulação de Prateleira)**.  
Ele cruza estatísticas brutas com um motor matemático que avalia força ofensiva, defensiva, consistência e resposta psicológica, gerando probabilidades para diversos mercados.
""")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='quote'>\"O futebol é a coisa mais importante entre as menos importantes.\"<br>— <b>Arrigo Sacchi</b></div>", unsafe_allow_html=True)

# =========================================================================
# MENU LATERAL
# =========================================================================
st.sidebar.title("⚙️ Navegação")
aba = st.sidebar.radio("", ["🧮 Simulador Manual"])

# =========================================================================
# FUNÇÕES AUXILIARES
# =========================================================================
def processar_lista_estatistica(texto_lista):
    if not texto_lista or not texto_lista.strip():
        return None, None, None
    try:
        valores = [float(x.strip()) for x in texto_lista.split(",") if x.strip()]
        if not valores:
            return None, None, None
        media = np.mean(valores)
        mediana = np.median(valores)
        return media, mediana, valores
    except:
        return None, None, None

def sequencia_para_pontos(seq):
    if not seq or not seq.strip():
        return 50.0, 50.0, 50.0
    seq = seq.strip().upper()
    resultados = [c for c in seq if c in 'VED']
    if not resultados:
        return 50.0, 50.0, 50.0
    def calc_aprov(lista):
        if not lista: return 50.0
        pts = sum(3 if r == 'V' else 1 if r == 'E' else 0 for r in lista)
        return (pts / (len(lista) * 3)) * 100
    cc3 = calc_aprov(resultados[:3]) if len(resultados) >= 3 else calc_aprov(resultados)
    cc5 = calc_aprov(resultados[:5]) if len(resultados) >= 5 else calc_aprov(resultados)
    geral = calc_aprov(resultados[:10])
    return cc3, cc5, geral

# =========================================================================
# MOTOR MATEMÁTICO COMPLETO (FMP)
# =========================================================================
def normalizar_por_media(valor_time, referencia, inverter=False):
    if referencia == 0: return 50.0
    razao = valor_time / referencia
    nota = razao * 50
    if inverter: nota = 100 - nota
    return max(0.0, min(100.0, nota))

def calcular_fmp(prat_time, prat_rival, tipo):
    elite = ["Elite Absoluta"]
    media_alta = ["Alta", "Média"]
    baixa = ["Baixa", "Crítica"]
    if prat_time in elite and prat_rival in media_alta + baixa:
        return 0.60 if tipo == "ataque" else 1.40
    elif prat_time in baixa and prat_rival in elite:
        return 1.30 if tipo == "ataque" else 0.70
    elif prat_time in media_alta and prat_rival in elite:
        return 1.30 if tipo == "ataque" else 0.70
    else:
        return 1.00

def classificar_prateleira(overall):
    if overall >= 86: return "Elite Absoluta"
    elif overall >= 78: return "Alta"
    elif overall >= 70: return "Média"
    elif overall >= 60: return "Baixa"
    else: return "Crítica"

def calcular_fvo(estatisticas_time, medias_liga, medianas_time, pesos_ativos):
    if not pesos_ativos: return 50.0
    nota_total, peso_total = 0.0, 0.0
    mapeamento = ['atq', 'atq_perigosos', 'chutes', 'chutes_gol', 'gols', 'xg']
    for chave in mapeamento:
        if chave in pesos_ativos and chave in estatisticas_time:
            val = estatisticas_time[chave]
            ref = medianas_time.get(chave) if (medianas_time and chave in medianas_time and medianas_time[chave] > 0) else medias_liga.get(chave, 1)
            nota = normalizar_por_media(val, ref)
            nota_total += nota * pesos_ativos[chave]
            peso_total += pesos_ativos[chave]
    return nota_total / peso_total if peso_total > 0 else 50.0

def calcular_fco(estatisticas_time, medias_liga, medianas_time=None):
    chutes_gol = estatisticas_time.get('chutes_gol')
    gols = estatisticas_time.get('gols')
    ref_cg = medianas_time.get('chutes_gol') if (medianas_time and 'chutes_gol' in medianas_time and medianas_time['chutes_gol'] > 0) else medias_liga.get('chutes_gol', 1)
    ref_gols = medianas_time.get('gols') if (medianas_time and 'gols' in medianas_time and medianas_time['gols'] > 0) else medias_liga.get('gols', 1)
    if not chutes_gol or not gols or chutes_gol == 0 or ref_cg == 0: return 50.0
    media_time = chutes_gol / gols if gols > 0 else 999
    media_liga = ref_cg / ref_gols if ref_gols > 0 else 1
    if media_time == 0: return 0.0
    nota = (media_liga / media_time) * 50
    return max(0.0, min(100.0, nota))

def calcular_frd(estatisticas_time, medias_liga, medianas_time, pesos_ativos):
    if not pesos_ativos: return 50.0
    nota_total, peso_total = 0.0, 0.0
    mapeamento = ['atq_sofridos', 'atq_perigosos_sofridos', 'chutes_sofridos', 'chutes_gol_sofridos', 'gols_sofridos', 'xg_cedido']
    for chave in mapeamento:
        if chave in pesos_ativos and chave in estatisticas_time:
            val = estatisticas_time[chave]
            ref = medianas_time.get(chave) if (medianas_time and chave in medianas_time and medianas_time[chave] > 0) else medias_liga.get(chave, 1)
            nota = normalizar_por_media(val, ref, inverter=True)
            nota_total += nota * pesos_ativos[chave]
            peso_total += pesos_ativos[chave]
    return nota_total / peso_total if peso_total > 0 else 50.0

def calcular_fcd_defensivo(estatisticas_time, medias_liga, medianas_time=None):
    chutes_gol_sof = estatisticas_time.get('chutes_gol_sofridos')
    gols_sof = estatisticas_time.get('gols_sofridos')
    ref_cgs = medianas_time.get('chutes_gol_sofridos') if (medianas_time and 'chutes_gol_sofridos' in medianas_time and medianas_time['chutes_gol_sofridos'] > 0) else medias_liga.get('chutes_gol_sofridos', 1)
    ref_gs = medianas_time.get('gols_sofridos') if (medianas_time and 'gols_sofridos' in medianas_time and medianas_time['gols_sofridos'] > 0) else medias_liga.get('gols_sofridos', 1)
    if not chutes_gol_sof or not gols_sof or chutes_gol_sof == 0: return 50.0
    media_time = chutes_gol_sof / gols_sof if gols_sof > 0 else 999
    media_liga = ref_cgs / ref_gs if ref_gs > 0 else 1
    if media_liga == 0: return 50.0
    nota = (media_time / media_liga) * 50
    return max(0.0, min(100.0, nota))

def calcular_bloco_consistencia(estatisticas_time, medias_liga, pesos_fdm, historico_im, prat_time, prat_rival):
    if not pesos_fdm: fdm = 50.0
    else:
        desvios = []
        fmp_mod = calcular_fmp(prat_time, prat_rival, 'defesa')
        for chave in pesos_fdm:
            if chave in estatisticas_time and chave in medias_liga:
                nota = normalizar_por_media(estatisticas_time[chave], medias_liga[chave])
                desvios.append(nota)
        if desvios:
            desvio_padrao = np.std(desvios)
            fdm = 100 - (desvio_padrao * 2 * fmp_mod)
            fdm = max(0.0, min(100.0, fdm))
        else: fdm = 50.0
    if historico_im and len(historico_im) >= 2:
        amplitude = max(historico_im) - min(historico_im)
        ier = 100 - amplitude
        ier = max(0.0, min(100.0, ier))
    else: ier = 50.0
    return (fdm * 0.60) + (ier * 0.40), fdm, ier

def calcular_resistencia_pressao(estatisticas_time, medias_liga, pesos_ativos, prat_time, prat_rival):
    fcd_res = 50.0
    if 'chutes_sofridos' in pesos_ativos: fcd_res = normalizar_por_media(estatisticas_time.get('chutes_sofridos', 0), medias_liga.get('chutes_sofridos', 1))
    egz_res = calcular_fcd_defensivo(estatisticas_time, medias_liga) if 'chutes_gol_sofridos' in pesos_ativos else 50.0
    fri_res = estatisticas_time.get('pontos_recuperados', 50.0) if 'pontos_recuperados' in pesos_ativos else 50.0
    fzc_res = estatisticas_time.get('gols_finais', 50.0) if 'gols_finais' in pesos_ativos else 50.0
    fmp_def = calcular_fmp(prat_time, prat_rival, 'defesa'); fmp_atk = calcular_fmp(prat_time, prat_rival, 'ataque')
    nota = (fcd_res * 0.30 * fmp_def + egz_res * 0.30 * fmp_def + fri_res * 0.20 * fmp_atk + fzc_res * 0.20 * fmp_atk)
    return max(0.0, min(100.0, nota)), fcd_res, egz_res, fri_res, fzc_res

def calcular_overall(estatisticas_time, medias_liga, prat_time, prat_rival,
                     pesos_ataque, pesos_defesa, pesos_fdm, pesos_resist,
                     historico_im, medianas_time=None):
    fvo = calcular_fvo(estatisticas_time, medias_liga, medianas_time, pesos_ataque) if pesos_ataque else 50.0
    fco = calcular_fco(estatisticas_time, medias_liga, medianas_time) if ('chutes_gol' in pesos_ataque and 'gols' in pesos_ataque) else 50.0
    ataque = (fvo * 0.60) + (fco * 0.40)
    frd = calcular_frd(estatisticas_time, medias_liga, medianas_time, pesos_defesa) if pesos_defesa else 50.0
    fcd_def = calcular_fcd_defensivo(estatisticas_time, medias_liga, medianas_time) if ('chutes_gol_sofridos' in pesos_defesa and 'gols_sofridos' in pesos_defesa) else 50.0
    defesa = (frd * 0.60) + (fcd_def * 0.40)
    consistencia, fdm, ier = calcular_bloco_consistencia(estatisticas_time, medias_liga, pesos_fdm, historico_im, prat_time, prat_rival)
    resistencia, fcd_res, egz_res, fri_res, fzc_res = calcular_resistencia_pressao(estatisticas_time, medias_liga, pesos_resist, prat_time, prat_rival)
    overall = (consistencia * 0.35) + (ataque * 0.25) + (defesa * 0.25) + (resistencia * 0.15)
    overall = max(0.0, min(100.0, overall))
    return {
        'overall': overall,
        'ataque': ataque, 'fvo': fvo, 'fco': fco,
        'defesa': defesa, 'frd': frd, 'fcd_def': fcd_def,
        'consistencia': consistencia, 'fdm': fdm, 'ier': ier,
        'resistencia': resistencia, 'fcd_res': fcd_res, 'egz_res': egz_res,
        'fri_res': fri_res, 'fzc_res': fzc_res
    }

def calcular_im(cc3, cc5, geral_3, geral_5, geral_10, bonus_zebra, tab_din):
    bloco_campo = (cc3 * 0.65) + (cc5 * 0.35)
    bloco_geral = (geral_3 * 0.50) + (geral_5 * 0.35) + (geral_10 * 0.15)
    im = (bloco_campo * 0.45) + (bloco_geral * 0.35) + (tab_din * 0.20) + bonus_zebra
    return max(0.0, min(100.0, im)), bloco_campo, bloco_geral, tab_din, bonus_zebra

def calcular_irc(rodada, nota_posicao, prospeccao, orgulho_ferido, revanche,
                 sequencia, pressao_torcida, importancia, desfalques, fatores_empiricos=None):
    def fac(r):
        if r <= 10: return 0.30
        elif r <= 25: return 0.60
        elif r <= 33: return 0.85
        else: return 1.00
    fpt = -10 if (prospeccao == "Elite Absoluta" and rodada <= 10) else 0
    urgencia = nota_posicao + fpt
    fatores = urgencia + orgulho_ferido + revanche + sequencia + pressao_torcida + importancia + desfalques
    if fatores_empiricos:
        fatores += fatores_empiricos.get('if_val', 0) + fatores_empiricos.get('fcf_val', 0) + fatores_empiricos.get('vcd_val', 0)
    nota = 50 + fatores * fac(rodada)
    return max(0.0, min(100.0, nota)), fac(rodada), urgencia, orgulho_ferido, revanche, sequencia, pressao_torcida, importancia, desfalques

def calcular_imp(overall, im, irc): return (overall + im + irc) / 3

def calcular_probabilidades(nota_a, nota_b):
    diff = nota_a - nota_b
    prob_a = 35 + diff * 0.5; prob_b = 35 - diff * 0.3; prob_empate = 30 - abs(diff) * 0.2
    prob_a = max(5, min(85, prob_a)); prob_b = max(5, min(85, prob_b)); prob_empate = max(5, min(50, prob_empate))
    total = prob_a + prob_empate + prob_b
    return prob_a/total*100, prob_empate/total*100, prob_b/total*100

# =========================================================================
# ABA SIMULADOR MANUAL (COMPLETA COM TODOS OS CAMPOS)
# =========================================================================
if aba == "🧮 Simulador Manual":
    st.header("🧮 Simulador com Estatísticas Brutas e Momento Completo")
    st.caption("Preencha o Painel Inicial e as sequências de resultados. Insira as estatísticas médias por jogo e os dados de mercados.")

    col1, col2 = st.columns(2)
    with col1:
        nome_a = st.text_input("Nome Time A (Mandante)", "Flamengo")
    with col2:
        nome_b = st.text_input("Nome Time B (Visitante)", "Vasco")

    # Painel Inicial reformulado
    with st.expander("📋 Painel Inicial: Posicionamento e Forma Recente", expanded=True):
        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"**{nome_a}**")
            pos_real_a = st.number_input(f"Posição Real na Tabela ({nome_a})", 1, 20, 5, key="pos_a")
            seq_a = st.text_input(f"Sequência últimos jogos ({nome_a}) - ex: V,E,D,V,V", value="V,E,D,V,V", key="seq_a",
                                  help="Insira os resultados dos últimos jogos (V=Vitória, E=Empate, D=Derrota). O sistema calculará o momento automaticamente.")
            prosp_a = st.selectbox(f"Prospecção ({nome_a})", ["Elite Absoluta", "Alta", "Média", "Baixa", "Crítica"], key="prosp_a")
        with colB:
            st.markdown(f"**{nome_b}**")
            pos_real_b = st.number_input(f"Posição Real na Tabela ({nome_b})", 1, 20, 8, key="pos_b")
            seq_b = st.text_input(f"Sequência últimos jogos ({nome_b}) - ex: V,E,D,V,V", value="D,V,E,D,V", key="seq_b",
                                  help="Insira os resultados dos últimos jogos (V=Vitória, E=Empate, D=Derrota).")
            prosp_b = st.selectbox(f"Prospecção ({nome_b})", ["Elite Absoluta", "Alta", "Média", "Baixa", "Crítica"], key="prosp_b")

        # Cálculo automático das notas de posição e momento (IM) a partir das sequências
        nota_pos_a = 100.0 - (pos_real_a - 1) * (100.0 / 19.0)
        nota_pos_b = 100.0 - (pos_real_b - 1) * (100.0 / 19.0)
        cc3_a, cc5_a, geral_a = sequencia_para_pontos(seq_a)
        cc3_b, cc5_b, geral_b = sequencia_para_pontos(seq_b)
        aprov_a = geral_a
        aprov_b = geral_b
        pos_mom_a = 21.0 - (aprov_a / 100.0) * 20.0
        pos_mom_b = 21.0 - (aprov_b / 100.0) * 20.0
        mult_prat_a = 1.6 if prosp_a in ["Elite Absoluta"] else (1.0 if prosp_a in ["Alta", "Média"] else 0.0)
        mult_prat_b = 1.6 if prosp_b in ["Elite Absoluta"] else (1.0 if prosp_b in ["Alta", "Média"] else 0.0)
        tab_din_a = 50.0 + (pos_real_a - pos_mom_a) * mult_prat_a
        tab_din_b = 50.0 + (pos_real_b - pos_mom_b) * mult_prat_b
        tab_din_a = max(0.0, min(100.0, tab_din_a))
        tab_din_b = max(0.0, min(100.0, tab_din_b))
        st.caption(f"🔹 Nota Posição (IRC): {nome_a} {nota_pos_a:.1f} | {nome_b} {nota_pos_b:.1f}")
        st.caption(f"🔹 Momento (IM) automático: CC3/CC5/Geral {nome_a}: {cc3_a:.0f}/{cc5_a:.0f}/{geral_a:.0f} | {nome_b}: {cc3_b:.0f}/{cc5_b:.0f}/{geral_b:.0f}")

    # Médias da Liga
    with st.expander("📊 Médias da Liga (Referência)", expanded=False):
        cols = st.columns(6)
        med_liga = {}
        med_liga['atq'] = cols[0].number_input("Atq", 0.0, 100.0, 12.0)
        med_liga['atq_perigosos'] = cols[1].number_input("Atq Perigosos", 0.0, 100.0, 6.0)
        med_liga['chutes'] = cols[2].number_input("Chutes", 0.0, 100.0, 14.0)
        med_liga['chutes_gol'] = cols[3].number_input("Chutes Gol", 0.0, 100.0, 5.0)
        med_liga['gols'] = cols[4].number_input("Gols Marcados", 0.0, 100.0, 1.4)
        med_liga['xg'] = cols[5].number_input("xG", 0.0, 100.0, 1.5)
        cols2 = st.columns(6)
        med_liga['atq_sofridos'] = cols2[0].number_input("Atq Sofridos", 0.0, 100.0, 10.0)
        med_liga['atq_perigosos_sofridos'] = cols2[1].number_input("Atq Perigosos Sofridos", 0.0, 100.0, 5.0)
        med_liga['chutes_sofridos'] = cols2[2].number_input("Chutes Sofridos", 0.0, 100.0, 12.0)
        med_liga['chutes_gol_sofridos'] = cols2[3].number_input("Chutes Gol Sofridos", 0.0, 100.0, 4.0)
        med_liga['gols_sofridos'] = cols2[4].number_input("Gols Sofridos", 0.0, 100.0, 1.2)
        med_liga['xg_cedido'] = cols2[5].number_input("xG Cedido", 0.0, 100.0, 1.3)

    # ========== COLETA TIME A ==========
    st.subheader(f"📈 {nome_a} (Mandante)")
    est_a, med_a, p_atk_a, p_def_a, p_fdm_a, p_res_a = {}, {}, {}, {}, {}, {}

    with st.expander("⚽ Ataque (médias por jogo)", expanded=False):
        usar_lista_a = st.checkbox("Usar listas de valores (últimos 10 jogos)", key="a_list_ataque")
        cols = st.columns(3)
        if cols[0].checkbox("Atq", key="a_atq"):
            if usar_lista_a:
                txt = st.text_area("Lista Atq", "12,15,10,14,13,11,16,14,15,12", key="a_atq_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['atq'] = media; med_a['atq'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['atq'] = cols[0].number_input("Média", 0.0, 100.0, 15.0, key="a_atq_v")
            p_atk_a['atq'] = 0.20
        if cols[1].checkbox("Atq Perigosos", key="a_atq_per"):
            if usar_lista_a:
                txt = st.text_area("Lista Atq Perigosos", "6,7,5,8,6,7,5,9,6,7", key="a_atq_per_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['atq_perigosos'] = media; med_a['atq_perigosos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['atq_perigosos'] = cols[1].number_input("Média", 0.0, 100.0, 7.0, key="a_atq_per_v")
            p_atk_a['atq_perigosos'] = 0.20
        if cols[2].checkbox("Chutes", key="a_chutes"):
            if usar_lista_a:
                txt = st.text_area("Lista Chutes", "16,14,18,15,17,13,19,16,14,15", key="a_chutes_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['chutes'] = media; med_a['chutes'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['chutes'] = cols[2].number_input("Média", 0.0, 100.0, 16.0, key="a_chutes_v")
            p_atk_a['chutes'] = 0.20; p_fdm_a['chutes'] = 0.20
        cols2 = st.columns(3)
        if cols2[0].checkbox("Chutes Gol", key="a_chutes_gol"):
            if usar_lista_a:
                txt = st.text_area("Lista Chutes Gol", "5,6,4,7,5,6,4,8,5,6", key="a_chutes_gol_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['chutes_gol'] = media; med_a['chutes_gol'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['chutes_gol'] = cols2[0].number_input("Média", 0.0, 100.0, 6.0, key="a_chutes_gol_v")
            p_atk_a['chutes_gol'] = 0.20
        if cols2[1].checkbox("Gols Marcados", key="a_gols"):
            if usar_lista_a:
                txt = st.text_area("Lista Gols", "2,1,3,0,2,2,1,4,2,1", key="a_gols_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['gols'] = media; med_a['gols'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['gols'] = cols2[1].number_input("Média", 0.0, 100.0, 2.0, key="a_gols_v")
            p_atk_a['gols'] = 0.20
        if cols2[2].checkbox("xG", key="a_xg"):
            if usar_lista_a:
                txt = st.text_area("Lista xG", "1.8,1.5,2.2,0.8,1.9,2.0,1.3,2.5,1.7,1.4", key="a_xg_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['xg'] = media; med_a['xg'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['xg'] = cols2[2].number_input("Média", 0.0, 100.0, 1.8, key="a_xg_v")
            p_atk_a['xg'] = 0.20

    with st.expander("🛡️ Defesa (médias por jogo)", expanded=False):
        usar_lista_d_a = st.checkbox("Usar listas de valores", key="a_list_def")
        cols = st.columns(3)
        if cols[0].checkbox("Atq Sofridos", key="a_atq_sof"):
            if usar_lista_d_a:
                txt = st.text_area("Lista Atq Sofridos", "8,6,10,7,9,5,11,8,7,9", key="a_atq_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['atq_sofridos'] = media; med_a['atq_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['atq_sofridos'] = cols[0].number_input("Média", 0.0, 100.0, 8.0, key="a_atq_sof_v")
            p_def_a['atq_sofridos'] = 0.20
        if cols[1].checkbox("Atq Perigosos Sofridos", key="a_atq_per_sof"):
            if usar_lista_d_a:
                txt = st.text_area("Lista Atq Perigosos Sofridos", "3,4,2,5,3,4,2,6,3,4", key="a_atq_per_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['atq_perigosos_sofridos'] = media; med_a['atq_perigosos_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['atq_perigosos_sofridos'] = cols[1].number_input("Média", 0.0, 100.0, 4.0, key="a_atq_per_sof_v")
            p_def_a['atq_perigosos_sofridos'] = 0.20
        if cols[2].checkbox("Chutes Sofridos", key="a_chutes_sof"):
            if usar_lista_d_a:
                txt = st.text_area("Lista Chutes Sofridos", "10,8,12,9,11,7,13,10,9,11", key="a_chutes_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['chutes_sofridos'] = media; med_a['chutes_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['chutes_sofridos'] = cols[2].number_input("Média", 0.0, 100.0, 10.0, key="a_chutes_sof_v")
            p_def_a['chutes_sofridos'] = 0.20; p_fdm_a['chutes_sofridos'] = 0.20
        cols2 = st.columns(3)
        if cols2[0].checkbox("Chutes Gol Sofridos", key="a_chutes_gol_sof"):
            if usar_lista_d_a:
                txt = st.text_area("Lista Chutes Gol Sofridos", "3,2,4,1,3,2,4,3,2,3", key="a_chutes_gol_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['chutes_gol_sofridos'] = media; med_a['chutes_gol_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['chutes_gol_sofridos'] = cols2[0].number_input("Média", 0.0, 100.0, 3.0, key="a_chutes_gol_sof_v")
            p_def_a['chutes_gol_sofridos'] = 0.20
        if cols2[1].checkbox("Gols Sofridos", key="a_gols_sof"):
            if usar_lista_d_a:
                txt = st.text_area("Lista Gols Sofridos", "0,1,0,2,1,0,1,1,0,1", key="a_gols_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['gols_sofridos'] = media; med_a['gols_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['gols_sofridos'] = cols2[1].number_input("Média", 0.0, 100.0, 0.8, key="a_gols_sof_v")
            p_def_a['gols_sofridos'] = 0.20
        if cols2[2].checkbox("xG Cedido", key="a_xg_ced"):
            if usar_lista_d_a:
                txt = st.text_area("Lista xG Cedido", "0.8,1.0,0.5,1.2,0.9,0.7,1.1,1.0,0.6,0.9", key="a_xg_ced_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_a['xg_cedido'] = media; med_a['xg_cedido'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_a['xg_cedido'] = cols2[2].number_input("Média", 0.0, 100.0, 1.0, key="a_xg_ced_v")
            p_def_a['xg_cedido'] = 0.20

    with st.expander("💪 Resistência à Pressão", expanded=False):
        cols = st.columns(2)
        if cols[0].checkbox("Pontos Recuperados (0-100)", key="a_pontos_rec"):
            est_a['pontos_recuperados'] = cols[0].number_input("Nota", 0.0, 100.0, 60.0, key="a_pontos_rec_v")
            p_res_a['pontos_recuperados'] = 1.0
        if cols[1].checkbox("Gols Finais (75'-90')", key="a_gols_fin"):
            est_a['gols_finais'] = cols[1].number_input("Nota", 0.0, 100.0, 70.0, key="a_gols_fin_v")
            p_res_a['gols_finais'] = 1.0

    hist_im_a = [50.0]*5
    prat_a = prosp_a

    with st.expander("🧠 IRC (Psicológico / Contextual)", expanded=False):
        rod_a = st.number_input("Rodada A", 1, 38, 20, key="rod_a")
        org_a = st.slider("Orgulho Ferido A", 0, 30, 0, key="org_a")
        rev_a = st.slider("Revanche A", 0, 20, 0, key="rev_a")
        seq_a_irc = st.slider("Sequência A", -10, 10, 0, key="seq_a_irc")
        press_a = st.slider("Pressão Torcida A", -10, 15, 0, key="press_a")
        imp_a = st.selectbox("Importância A", [0,10,20], key="imp_a")
        desf_a = st.slider("Desfalques A", -15, 0, 0, key="desf_a")
        usar_emp_a = st.checkbox("Fatores Empíricos A", True, key="emp_a")
        if usar_emp_a:
            if_val_a = (geral_a - 50) * 0.3
            fcf_val_a = (cc3_a - 50) * 0.25
            vcd_a = st.number_input("Vitórias Confronto Direto A", 0,5,2, key="vcd_a")
            vcd_val_a = max(-15, min(15, (vcd_a*6) - ((5-vcd_a)*4)))
            fatores_emp_a = {'if_val': if_val_a, 'fcf_val': fcf_val_a, 'vcd_val': vcd_val_a}
        else:
            fatores_emp_a = None

    with st.expander("🎲 Mercados (últimos 10 jogos)", expanded=False):
        n_jogos_a = st.number_input("Total de jogos A", 1,50,10, key="nj_a")
        mkt_a = {
            'n_jogos': n_jogos_a,
            'over05ht': st.number_input("Over 0.5 HT A", 0,n_jogos_a,6, key="o05a"),
            'over15ht': st.number_input("Over 1.5 HT A", 0,n_jogos_a,4, key="o15hta"),
            'over15ft': st.number_input("Over 1.5 FT A", 0,n_jogos_a,7, key="o15a"),
            'over25ft': st.number_input("Over 2.5 FT A", 0,n_jogos_a,5, key="o25a"),
            'ambas': st.number_input("Ambas Marcam A", 0,n_jogos_a,4, key="bta"),
            'escanteios': st.number_input("Média Escanteios A", 0.0,20.0,5.2, key="esca")
        }

    # ========== COLETA TIME B ==========
    st.subheader(f"📈 {nome_b} (Visitante)")
    est_b, med_b, p_atk_b, p_def_b, p_fdm_b, p_res_b = {}, {}, {}, {}, {}, {}

    with st.expander("⚽ Ataque (médias por jogo)", expanded=False):
        usar_lista_b = st.checkbox("Usar listas", key="b_list_ataque")
        cols = st.columns(3)
        if cols[0].checkbox("Atq", key="b_atq"):
            if usar_lista_b:
                txt = st.text_area("Lista Atq", "10,12,8,9,11,13,10,9,12,8", key="b_atq_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['atq'] = media; med_b['atq'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['atq'] = cols[0].number_input("Média", 0.0, 100.0, 10.0, key="b_atq_v")
            p_atk_b['atq'] = 0.20
        if cols[1].checkbox("Atq Perigosos", key="b_atq_per"):
            if usar_lista_b:
                txt = st.text_area("Lista Atq Perigosos", "4,5,3,6,4,5,4,7,5,4", key="b_atq_per_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['atq_perigosos'] = media; med_b['atq_perigosos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['atq_perigosos'] = cols[1].number_input("Média", 0.0, 100.0, 5.0, key="b_atq_per_v")
            p_atk_b['atq_perigosos'] = 0.20
        if cols[2].checkbox("Chutes", key="b_chutes"):
            if usar_lista_b:
                txt = st.text_area("Lista Chutes", "12,14,10,13,11,15,12,13,10,14", key="b_chutes_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['chutes'] = media; med_b['chutes'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['chutes'] = cols[2].number_input("Média", 0.0, 100.0, 12.0, key="b_chutes_v")
            p_atk_b['chutes'] = 0.20; p_fdm_b['chutes'] = 0.20
        cols2 = st.columns(3)
        if cols2[0].checkbox("Chutes Gol", key="b_chutes_gol"):
            if usar_lista_b:
                txt = st.text_area("Lista Chutes Gol", "3,4,2,5,3,4,3,5,4,3", key="b_chutes_gol_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['chutes_gol'] = media; med_b['chutes_gol'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['chutes_gol'] = cols2[0].number_input("Média", 0.0, 100.0, 4.0, key="b_chutes_gol_v")
            p_atk_b['chutes_gol'] = 0.20
        if cols2[1].checkbox("Gols Marcados", key="b_gols"):
            if usar_lista_b:
                txt = st.text_area("Lista Gols", "1,2,0,1,1,2,1,2,1,0", key="b_gols_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['gols'] = media; med_b['gols'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['gols'] = cols2[1].number_input("Média", 0.0, 100.0, 1.2, key="b_gols_v")
            p_atk_b['gols'] = 0.20
        if cols2[2].checkbox("xG", key="b_xg"):
            if usar_lista_b:
                txt = st.text_area("Lista xG", "1.2,1.4,0.9,1.3,1.1,1.6,1.2,1.5,1.3,1.0", key="b_xg_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['xg'] = media; med_b['xg'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['xg'] = cols2[2].number_input("Média", 0.0, 100.0, 1.3, key="b_xg_v")
            p_atk_b['xg'] = 0.20

    with st.expander("🛡️ Defesa (médias por jogo)", expanded=False):
        usar_lista_d_b = st.checkbox("Usar listas", key="b_list_def")
        cols = st.columns(3)
        if cols[0].checkbox("Atq Sofridos", key="b_atq_sof"):
            if usar_lista_d_b:
                txt = st.text_area("Lista Atq Sofridos", "10,12,8,11,9,13,10,11,9,12", key="b_atq_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['atq_sofridos'] = media; med_b['atq_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['atq_sofridos'] = cols[0].number_input("Média", 0.0, 100.0, 10.0, key="b_atq_sof_v")
            p_def_b['atq_sofridos'] = 0.20
        if cols[1].checkbox("Atq Perigosos Sofridos", key="b_atq_per_sof"):
            if usar_lista_d_b:
                txt = st.text_area("Lista Atq Perigosos Sofridos", "5,6,4,7,5,6,5,7,6,5", key="b_atq_per_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['atq_perigosos_sofridos'] = media; med_b['atq_perigosos_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['atq_perigosos_sofridos'] = cols[1].number_input("Média", 0.0, 100.0, 5.0, key="b_atq_per_sof_v")
            p_def_b['atq_perigosos_sofridos'] = 0.20
        if cols[2].checkbox("Chutes Sofridos", key="b_chutes_sof"):
            if usar_lista_d_b:
                txt = st.text_area("Lista Chutes Sofridos", "14,12,16,13,15,11,14,13,12,14", key="b_chutes_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['chutes_sofridos'] = media; med_b['chutes_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['chutes_sofridos'] = cols[2].number_input("Média", 0.0, 100.0, 14.0, key="b_chutes_sof_v")
            p_def_b['chutes_sofridos'] = 0.20; p_fdm_b['chutes_sofridos'] = 0.20
        cols2 = st.columns(3)
        if cols2[0].checkbox("Chutes Gol Sofridos", key="b_chutes_gol_sof"):
            if usar_lista_d_b:
                txt = st.text_area("Lista Chutes Gol Sofridos", "5,4,6,5,4,5,5,6,4,5", key="b_chutes_gol_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['chutes_gol_sofridos'] = media; med_b['chutes_gol_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['chutes_gol_sofridos'] = cols2[0].number_input("Média", 0.0, 100.0, 5.0, key="b_chutes_gol_sof_v")
            p_def_b['chutes_gol_sofridos'] = 0.20
        if cols2[1].checkbox("Gols Sofridos", key="b_gols_sof"):
            if usar_lista_d_b:
                txt = st.text_area("Lista Gols Sofridos", "1,0,2,1,1,2,1,0,1,1", key="b_gols_sof_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['gols_sofridos'] = media; med_b['gols_sofridos'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['gols_sofridos'] = cols2[1].number_input("Média", 0.0, 100.0, 1.0, key="b_gols_sof_v")
            p_def_b['gols_sofridos'] = 0.20
        if cols2[2].checkbox("xG Cedido", key="b_xg_ced"):
            if usar_lista_d_b:
                txt = st.text_area("Lista xG Cedido", "1.1,1.3,0.8,1.2,1.0,1.4,1.1,1.3,1.2,1.0", key="b_xg_ced_list")
                media, mediana, _ = processar_lista_estatistica(txt)
                if media:
                    est_b['xg_cedido'] = media; med_b['xg_cedido'] = mediana
                    st.caption(f"Média: {media:.1f} | Mediana: {mediana:.1f}")
            else:
                est_b['xg_cedido'] = cols2[2].number_input("Média", 0.0, 100.0, 1.1, key="b_xg_ced_v")
            p_def_b['xg_cedido'] = 0.20

    with st.expander("💪 Resistência à Pressão", expanded=False):
        cols = st.columns(2)
        if cols[0].checkbox("Pontos Recuperados (0-100)", key="b_pontos_rec"):
            est_b['pontos_recuperados'] = cols[0].number_input("Nota", 0.0, 100.0, 40.0, key="b_pontos_rec_v")
            p_res_b['pontos_recuperados'] = 1.0
        if cols[1].checkbox("Gols Finais (75'-90')", key="b_gols_fin"):
            est_b['gols_finais'] = cols[1].number_input("Nota", 0.0, 100.0, 50.0, key="b_gols_fin_v")
            p_res_b['gols_finais'] = 1.0

    hist_im_b = [50.0]*5
    prat_b = prosp_b

    with st.expander("🧠 IRC (Psicológico / Contextual)", expanded=False):
        rod_b = st.number_input("Rodada B", 1, 38, 20, key="rod_b")
        org_b = st.slider("Orgulho Ferido B", 0, 30, 0, key="org_b")
        rev_b = st.slider("Revanche B", 0, 20, 0, key="rev_b")
        seq_b_irc = st.slider("Sequência B", -10, 10, 0, key="seq_b_irc")
        press_b = st.slider("Pressão Torcida B", -10, 15, 0, key="press_b")
        imp_b = st.selectbox("Importância B", [0,10,20], key="imp_b")
        desf_b = st.slider("Desfalques B", -15, 0, 0, key="desf_b")
        usar_emp_b = st.checkbox("Fatores Empíricos B", True, key="emp_b")
        if usar_emp_b:
            if_val_b = (geral_b - 50) * 0.3
            fcf_val_b = (cc3_b - 50) * 0.25
            vcd_b = st.number_input("Vitórias Confronto Direto B", 0,5,2, key="vcd_b")
            vcd_val_b = max(-15, min(15, (vcd_b*6) - ((5-vcd_b)*4)))
            fatores_emp_b = {'if_val': if_val_b, 'fcf_val': fcf_val_b, 'vcd_val': vcd_val_b}
        else:
            fatores_emp_b = None

    with st.expander("🎲 Mercados (últimos 10 jogos)", expanded=False):
        n_jogos_b = st.number_input("Total de jogos B", 1,50,10, key="nj_b")
        mkt_b = {
            'n_jogos': n_jogos_b,
            'over05ht': st.number_input("Over 0.5 HT B", 0,n_jogos_b,5, key="o05b"),
            'over15ht': st.number_input("Over 1.5 HT B", 0,n_jogos_b,3, key="o15htb"),
            'over15ft': st.number_input("Over 1.5 FT B", 0,n_jogos_b,6, key="o15b"),
            'over25ft': st.number_input("Over 2.5 FT B", 0,n_jogos_b,4, key="o25b"),
            'ambas': st.number_input("Ambas Marcam B", 0,n_jogos_b,3, key="btb"),
            'escanteios': st.number_input("Média Escanteios B", 0.0,20.0,4.8, key="escb")
        }

    # ========== BOTÃO GERAR MYPREDICT ==========
    if st.button("⚡ GERAR MYPREDICT", use_container_width=True):
        # Cálculos
        res_a = calcular_overall(est_a, med_liga, prat_a, prat_b,
                                 p_atk_a, p_def_a, p_fdm_a, p_res_a, hist_im_a, med_a)
        res_b = calcular_overall(est_b, med_liga, prat_b, prat_a,
                                 p_atk_b, p_def_b, p_fdm_b, p_res_b, hist_im_b, med_b)
        im_a, bc_a, bg_a, td_a, bz_a = calcular_im(cc3_a, cc5_a, geral_a, geral_a, geral_a, 0, tab_din_a)
        im_b, bc_b, bg_b, td_b, bz_b = calcular_im(cc3_b, cc5_b, geral_b, geral_b, geral_b, 0, tab_din_b)
        irc_a, fac_a, urg_a, org_a, rev_a, seq_a, pr_a, imp_a, desf_a = calcular_irc(
            rod_a, nota_pos_a, prosp_a, org_a, rev_a, seq_a_irc, press_a, imp_a, desf_a, fatores_emp_a
        )
        irc_b, fac_b, urg_b, org_b, rev_b, seq_b, pr_b, imp_b, desf_b = calcular_irc(
            rod_b, nota_pos_b, prosp_b, org_b, rev_b, seq_b_irc, press_b, imp_b, desf_b, fatores_emp_b
        )
        imp_a = calcular_imp(res_a['overall'], im_a, irc_a)
        imp_b = calcular_imp(res_b['overall'], im_b, irc_b)
        prob_a, prob_e, prob_b = calcular_probabilidades(imp_a, imp_b)
        diff = imp_a - imp_b

        # Análise descritiva
        st.markdown("---")
        st.header("📋 Análise Pré‑Confronto")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 🏠 {nome_a}")
            st.markdown(f"""
            <div class='analysis-box'>
            <h4>Posicionamento</h4>
            <p><b>Posição atual:</b> {pos_real_a}º<br>
            <b>Prospecção:</b> {prosp_a}<br>
            <b>Forma recente:</b> {seq_a} (IM automático: {im_a:.1f})</p>
            <h4>Desempenho</h4>
            <p><b>Overall:</b> {res_a['overall']:.1f} (Ataque {res_a['ataque']:.1f}, Defesa {res_a['defesa']:.1f})<br>
            <b>Consistência:</b> {res_a['consistencia']:.1f}, <b>Resistência:</b> {res_a['resistencia']:.1f}<br>
            <b>IRC:</b> {irc_a:.1f}</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"### 🚌 {nome_b}")
            st.markdown(f"""
            <div class='analysis-box'>
            <h4>Posicionamento</h4>
            <p><b>Posição atual:</b> {pos_real_b}º<br>
            <b>Prospecção:</b> {prosp_b}<br>
            <b>Forma recente:</b> {seq_b} (IM automático: {im_b:.1f})</p>
            <h4>Desempenho</h4>
            <p><b>Overall:</b> {res_b['overall']:.1f} (Ataque {res_b['ataque']:.1f}, Defesa {res_b['defesa']:.1f})<br>
            <b>Consistência:</b> {res_b['consistencia']:.1f}, <b>Resistência:</b> {res_b['resistencia']:.1f}<br>
            <b>IRC:</b> {irc_b:.1f}</p>
            </div>
            """, unsafe_allow_html=True)

        # IMP em destaque
        st.markdown("---")
        st.header("🏆 Índice MyPredict (IMP)")
        col_imp1, col_imp2, col_imp3 = st.columns(3)
        with col_imp1:
            st.markdown(f"""
            <div class='imp-highlight'>
                <h4>🏠 {nome_a}</h4>
                <h2>{imp_a:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col_imp2:
            st.markdown(f"""
            <div class='imp-highlight'>
                <h4>⚖️ Diferença</h4>
                <h2>{diff:+.1f}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col_imp3:
            st.markdown(f"""
            <div class='imp-highlight'>
                <h4>🚌 {nome_b}</h4>
                <h2>{imp_b:.1f}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Probabilidades
        st.subheader("🎯 Probabilidades de Resultado")
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Vitória {nome_a}", f"{prob_a:.1f}%")
        c2.metric("Empate", f"{prob_e:.1f}%")
        c3.metric(f"Vitória {nome_b}", f"{prob_b:.1f}%")

        # Descrição baseada na diferença
        if diff > 10:
            st.success(f"🏆 {nome_a} é amplamente favorito. A diferença de {diff:.1f} pontos indica superioridade técnica e de momento. Espera-se um domínio claro.")
        elif diff > 5:
            st.info(f"📈 {nome_a} leva vantagem, mas o confronto é competitivo. A diferença de {diff:.1f} pontos sugere um jogo disputado, com leve pendor para o mandante.")
        elif diff > -5:
            st.warning(f"⚖️ Equilíbrio total. A diferença de {diff:.1f} pontos indica um duelo muito parelho, onde detalhes como fator casa e psicológico podem decidir.")
        elif diff > -10:
            st.info(f"📈 {nome_b} leva vantagem, mesmo atuando fora. A diferença de {diff:.1f} pontos aponta um visitante mais forte, mas sem grande margem.")
        else:
            st.success(f"🏆 {nome_b} é amplamente favorito. A diferença de {diff:.1f} pontos revela superioridade técnica e de momento, com expectativa de vitória visitante.")

        # Tabela comparativa lado a lado
        st.markdown("---")
        st.subheader("📋 Tabela Comparativa")
        df_comp = pd.DataFrame({
            'Métrica': ['Overall', 'Ataque', 'Defesa', 'Consistência', 'Resistência', 'IM', 'IRC', 'IMP'],
            nome_a: [f"{res_a['overall']:.1f}", f"{res_a['ataque']:.1f}", f"{res_a['defesa']:.1f}",
                     f"{res_a['consistencia']:.1f}", f"{res_a['resistencia']:.1f}", f"{im_a:.1f}", f"{irc_a:.1f}", f"{imp_a:.1f}"],
            nome_b: [f"{res_b['overall']:.1f}", f"{res_b['ataque']:.1f}", f"{res_b['defesa']:.1f}",
                     f"{res_b['consistencia']:.1f}", f"{res_b['resistencia']:.1f}", f"{im_b:.1f}", f"{irc_b:.1f}", f"{imp_b:.1f}"]
        })
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

        # Cruzamentos Ataque vs Defesa
        st.subheader("⚔️ Confronto Direto: Ataque vs Defesa")
        col_cruz1, col_cruz2 = st.columns(2)
        with col_cruz1:
            atk_a_vs_def_b = (res_a['ataque'] + (100 - res_b['defesa'])) / 2
            st.metric(f"Ataque {nome_a} vs Defesa {nome_b}", f"{atk_a_vs_def_b:.1f}",
                      help="Média entre o ataque do mandante e a fragilidade defensiva do visitante.")
        with col_cruz2:
            atk_b_vs_def_a = (res_b['ataque'] + (100 - res_a['defesa'])) / 2
            st.metric(f"Ataque {nome_b} vs Defesa {nome_a}", f"{atk_b_vs_def_a:.1f}",
                      help="Média entre o ataque do visitante e a fragilidade defensiva do mandante.")

        # Mercados
        st.markdown("---")
        st.subheader("🎲 Probabilidades de Mercados")
        def prob(ocorrencias, total):
            return ocorrencias/total*100 if total > 0 else 0
        colm1, colm2 = st.columns(2)
        with colm1:
            st.write(f"**{nome_a}**")
            st.write(f"Over 0.5 HT: {prob(mkt_a['over05ht'], n_jogos_a):.0f}%")
            st.write(f"Over 1.5 HT: {prob(mkt_a['over15ht'], n_jogos_a):.0f}%")
            st.write(f"Over 1.5 FT: {prob(mkt_a['over15ft'], n_jogos_a):.0f}%")
            st.write(f"Over 2.5 FT: {prob(mkt_a['over25ft'], n_jogos_a):.0f}%")
            st.write(f"Ambas Marcam: {prob(mkt_a['ambas'], n_jogos_a):.0f}%")
            st.write(f"Escanteios: {mkt_a['escanteios']:.1f}")
        with colm2:
            st.write(f"**{nome_b}**")
            st.write(f"Over 0.5 HT: {prob(mkt_b['over05ht'], n_jogos_b):.0f}%")
            st.write(f"Over 1.5 HT: {prob(mkt_b['over15ht'], n_jogos_b):.0f}%")
            st.write(f"Over 1.5 FT: {prob(mkt_b['over15ft'], n_jogos_b):.0f}%")
            st.write(f"Over 2.5 FT: {prob(mkt_b['over25ft'], n_jogos_b):.0f}%")
            st.write(f"Ambas Marcam: {prob(mkt_b['ambas'], n_jogos_b):.0f}%")
            st.write(f"Escanteios: {mkt_b['escanteios']:.1f}")

        # Combinação simples (média)
        st.write("**Médias Combinadas**")
        comb = {}
        comb['Over 0.5 HT'] = (prob(mkt_a['over05ht'], n_jogos_a) + prob(mkt_b['over05ht'], n_jogos_b))/2
        comb['Over 1.5 HT'] = (prob(mkt_a['over15ht'], n_jogos_a) + prob(mkt_b['over15ht'], n_jogos_b))/2
        comb['Over 1.5 FT'] = (prob(mkt_a['over15ft'], n_jogos_a) + prob(mkt_b['over15ft'], n_jogos_b))/2
        comb['Over 2.5 FT'] = (prob(mkt_a['over25ft'], n_jogos_a) + prob(mkt_b['over25ft'], n_jogos_b))/2
        comb['Ambas Marcam'] = (prob(mkt_a['ambas'], n_jogos_a) + prob(mkt_b['ambas'], n_jogos_b))/2
        comb['Escanteios'] = (mkt_a['escanteios'] + mkt_b['escanteios'])/2
        for k, v in comb.items():
            st.metric(k, f"{v:.1f}%" if k != 'Escanteios' else f"{v:.1f}")

# =========================================================================
# RODAPÉ
# =========================================================================
st.sidebar.divider()
st.sidebar.caption("MyPredict by Ferry v1.0")
st.sidebar.caption(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
