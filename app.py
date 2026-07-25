import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# =========================================================================
# CONFIGURAÇÃO DA PÁGINA - TEMA PRETO, BRANCO E AZUL
# =========================================================================
st.set_page_config(
    page_title="MyPredict by Ferry v0.3",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================================
# CSS CUSTOMIZADO
# =========================================================================
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #111111; border-right: 2px solid #1e3a5f; }
    section[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    h1, h2, h3, h4, h5, h6 { color: #4da6ff !important; font-weight: 700; }
    div[data-testid="stMetric"] { background-color: #1a1a1a; border: 1px solid #2a4a6f; border-radius: 10px; padding: 15px; color: #ffffff; }
    div[data-testid="stMetric"] label { color: #4da6ff !important; }
    div.stButton > button { background-color: #1e3a5f; color: white; border: 2px solid #4da6ff; border-radius: 8px; font-weight: bold; transition: 0.3s; }
    div.stButton > button:hover { background-color: #2a4a6f; border-color: #80c1ff; }
    .mypredict-btn { background: linear-gradient(135deg, #0a1a2f, #1e3a5f); color: white; border: 2px solid #4da6ff; border-radius: 10px; padding: 15px 40px; font-size: 20px; font-weight: bold; cursor: pointer; width: 100%; transition: 0.3s; margin: 20px 0; }
    .mypredict-btn:hover { background: linear-gradient(135deg, #1e3a5f, #2a4a6f); border-color: #80c1ff; box-shadow: 0 0 20px rgba(77, 166, 255, 0.6); }
    .welcome-card { background: linear-gradient(135deg, #0d2137, #1a1a2e); border: 1px solid #2a4a6f; border-radius: 15px; padding: 30px; margin: 20px 0; }
    .quote { font-style: italic; color: #a0c4e8; font-size: 18px; border-left: 4px solid #4da6ff; padding-left: 20px; margin: 25px 0; }
    .streamlit-expanderHeader { background-color: #1a1a1a; border: 1px solid #2a4a6f; border-radius: 8px; color: #4da6ff; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input { background-color: #1a1a1a; color: white; border: 1px solid #2a4a6f; }
    .compare-box { background-color: #111; border: 1px solid #2a4a6f; border-radius: 10px; padding: 20px; margin: 10px 0; }
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
    st.markdown("<p style='color: #4da6ff; font-size: 18px; margin-top: 0;'>v0.3 • Inteligência Estatística no Futebol</p>", unsafe_allow_html=True)

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
aba = st.sidebar.radio("", ["🔌 API (Dados Reais)", "🧮 Simulador Manual"])

# =========================================================================
# MOTOR MATEMÁTICO COMPLETO
# =========================================================================

def normalizar_por_media(valor_time, media_liga, inverter=False):
    if media_liga == 0:
        return 50.0
    razao = valor_time / media_liga
    nota = razao * 50
    if inverter:
        nota = 100 - nota
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

def calcular_fvo(estatisticas_time, medias_liga, pesos_ativos):
    if not pesos_ativos:
        return 50.0
    nota_total = 0.0
    peso_total = 0.0
    mapeamento = ['atq', 'atq_perigosos', 'chutes', 'chutes_gol', 'gols', 'xg']
    for chave in mapeamento:
        if chave in pesos_ativos and chave in estatisticas_time:
            val = estatisticas_time[chave]
            med = medias_liga.get(chave, 1)
            nota = normalizar_por_media(val, med)
            nota_total += nota * pesos_ativos[chave]
            peso_total += pesos_ativos[chave]
    return nota_total / peso_total if peso_total > 0 else 50.0

def calcular_fco(estatisticas_time, medias_liga):
    chutes_gol = estatisticas_time.get('chutes_gol')
    gols = estatisticas_time.get('gols')
    med_cg = medias_liga.get('chutes_gol', 1)
    med_gols = medias_liga.get('gols', 1)
    if not chutes_gol or not gols or chutes_gol == 0 or med_cg == 0:
        return 50.0
    media_time = chutes_gol / gols if gols > 0 else 999
    media_liga = med_cg / med_gols if med_gols > 0 else 1
    if media_time == 0:
        return 0.0
    nota = (media_liga / media_time) * 50
    return max(0.0, min(100.0, nota))

def calcular_frd(estatisticas_time, medias_liga, pesos_ativos):
    if not pesos_ativos:
        return 50.0
    nota_total = 0.0
    peso_total = 0.0
    mapeamento = ['atq_sofridos', 'atq_perigosos_sofridos', 'chutes_sofridos',
                  'chutes_gol_sofridos', 'gols_sofridos', 'xg_cedido']
    for chave in mapeamento:
        if chave in pesos_ativos and chave in estatisticas_time:
            val = estatisticas_time[chave]
            med = medias_liga.get(chave, 1)
            nota = normalizar_por_media(val, med, inverter=True)
            nota_total += nota * pesos_ativos[chave]
            peso_total += pesos_ativos[chave]
    return nota_total / peso_total if peso_total > 0 else 50.0

def calcular_fcd_defensivo(estatisticas_time, medias_liga):
    chutes_gol_sof = estatisticas_time.get('chutes_gol_sofridos')
    gols_sof = estatisticas_time.get('gols_sofridos')
    med_cgs = medias_liga.get('chutes_gol_sofridos', 1)
    med_gs = medias_liga.get('gols_sofridos', 1)
    if not chutes_gol_sof or not gols_sof or chutes_gol_sof == 0:
        return 50.0
    media_time = chutes_gol_sof / gols_sof if gols_sof > 0 else 999
    media_liga = med_cgs / med_gs if med_gs > 0 else 1
    if media_liga == 0:
        return 50.0
    nota = (media_time / media_liga) * 50
    return max(0.0, min(100.0, nota))

def calcular_bloco_consistencia(estatisticas_time, medias_liga, pesos_fdm,
                                historico_im, prat_time, prat_rival):
    if not pesos_fdm:
        fdm = 50.0
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
        else:
            fdm = 50.0

    if historico_im and len(historico_im) >= 2:
        amplitude = max(historico_im) - min(historico_im)
        ier = 100 - amplitude
        ier = max(0.0, min(100.0, ier))
    else:
        ier = 50.0

    return (fdm * 0.60) + (ier * 0.40), fdm, ier

def calcular_resistencia_pressao(estatisticas_time, medias_liga, pesos_ativos,
                                 prat_time, prat_rival):
    fcd_res = 50.0
    if 'chutes_sofridos' in pesos_ativos:
        fcd_res = normalizar_por_media(estatisticas_time.get('chutes_sofridos', 0),
                                       medias_liga.get('chutes_sofridos', 1))
    egz_res = calcular_fcd_defensivo(estatisticas_time, medias_liga) if 'chutes_gol_sofridos' in pesos_ativos else 50.0
    fri_res = estatisticas_time.get('pontos_recuperados', 50.0) if 'pontos_recuperados' in pesos_ativos else 50.0
    fzc_res = estatisticas_time.get('gols_finais', 50.0) if 'gols_finais' in pesos_ativos else 50.0

    fmp_def = calcular_fmp(prat_time, prat_rival, 'defesa')
    fmp_atk = calcular_fmp(prat_time, prat_rival, 'ataque')

    nota = (fcd_res * 0.30 * fmp_def +
            egz_res * 0.30 * fmp_def +
            fri_res * 0.20 * fmp_atk +
            fzc_res * 0.20 * fmp_atk)
    return max(0.0, min(100.0, nota)), fcd_res, egz_res, fri_res, fzc_res

def calcular_overall(estatisticas_time, medias_liga, prat_time, prat_rival,
                     pesos_ataque, pesos_defesa, pesos_fdm, pesos_resist,
                     historico_im):
    fvo = calcular_fvo(estatisticas_time, medias_liga, pesos_ataque) if pesos_ataque else 50.0
    fco = calcular_fco(estatisticas_time, medias_liga) if ('chutes_gol' in pesos_ataque and 'gols' in pesos_ataque) else 50.0
    ataque = (fvo * 0.60) + (fco * 0.40)

    frd = calcular_frd(estatisticas_time, medias_liga, pesos_defesa) if pesos_defesa else 50.0
    fcd_def = calcular_fcd_defensivo(estatisticas_time, medias_liga) if ('chutes_gol_sofridos' in pesos_defesa and 'gols_sofridos' in pesos_defesa) else 50.0
    defesa = (frd * 0.60) + (fcd_def * 0.40)

    consistencia, fdm, ier = calcular_bloco_consistencia(estatisticas_time, medias_liga,
                                                         pesos_fdm, historico_im, prat_time, prat_rival)
    resistencia, fcd_res, egz_res, fri_res, fzc_res = calcular_resistencia_pressao(
        estatisticas_time, medias_liga, pesos_resist, prat_time, prat_rival)

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
    im = max(0.0, min(100.0, im))
    return im, bloco_campo, bloco_geral, tab_din, bonus_zebra

def calcular_irc(rodada, nota_posicao, prospeccao, orgulho_ferido, revanche,
                 sequencia, pressao_torcida, importancia, desfalques):
    def fac(r):
        if r <= 10: return 0.30
        elif r <= 25: return 0.60
        elif r <= 33: return 0.85
        else: return 1.00

    fpt = -10 if (prospeccao == "Elite Absoluta" and rodada <= 10) else 0
    urgencia = nota_posicao + fpt
    fatores = urgencia + orgulho_ferido + revanche + sequencia + pressao_torcida + importancia + desfalques
    fac_valor = fac(rodada)
    nota = 50 + fatores * fac_valor
    nota = max(0.0, min(100.0, nota))
    return nota, fac_valor, urgencia, orgulho_ferido, revanche, sequencia, pressao_torcida, importancia, desfalques

def calcular_juncao(overall, im, irc):
    return (overall + im + irc) / 3

def calcular_probabilidades(nota_a, nota_b):
    diff = nota_a - nota_b
    prob_a = 35 + diff * 0.5
    prob_b = 35 - diff * 0.3
    prob_empate = 30 - abs(diff) * 0.2
    prob_a = max(5, min(85, prob_a))
    prob_b = max(5, min(85, prob_b))
    prob_empate = max(5, min(50, prob_empate))
    total = prob_a + prob_empate + prob_b
    return prob_a/total*100, prob_empate/total*100, prob_b/total*100

# =========================================================================
# ABA API
# =========================================================================
if aba == "🔌 API (Dados Reais)":
    st.header("🔌 Buscar Dados da API-Football")
    API_KEY = st.secrets.get("API_FOOTBALL_KEY", "")
    if not API_KEY:
        st.error("Chave API não encontrada nos secrets.")
    else:
        time_nome = st.text_input("Nome do time (ex: Flamengo)")
        if st.button("Buscar Time"):
            headers = {"x-rapidapi-key": API_KEY, "x-rapidapi-host": "v3.football.api-sports.io"}
            url = "https://v3.football.api-sports.io/teams"
            resp = requests.get(url, headers=headers, params={"search": time_nome})
            if resp.status_code == 200:
                dados = resp.json()
                st.json(dados)
            else:
                st.error(f"Erro {resp.status_code}")

# =========================================================================
# ABA SIMULADOR MANUAL
# =========================================================================
elif aba == "🧮 Simulador Manual":
    st.header("🧮 Simulador com Estatísticas Brutas e Momento Completo")
    st.caption("Preencha o Painel Inicial e marque as estatísticas disponíveis.")

    col1, col2 = st.columns(2)
    with col1:
        nome_a = st.text_input("Nome Time A (Mandante)", "Flamengo")
    with col2:
        nome_b = st.text_input("Nome Time B (Visitante)", "Vasco")

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

    def criar_seletores_time(prefixo, nome_time, mando):
        st.subheader(f"📈 {nome_time} ({'Mandante' if mando == 'C' else 'Visitante'})")
        
        # Inicializa tab_din com valor padrão seguro
        tab_din = 50.0
        nota_posicao = 50.0
        prospeccao = "Média"

        # ===== PAINEL INICIAL (novo) =====
        with st.expander("📋 Painel Inicial: Posicionamento e Prospecção", expanded=True):
            col_pos1, col_pos2 = st.columns(2)
            posicao_real = col_pos1.number_input("Posição Real na Tabela", 1, 20, 5, key=f"{prefixo}_pos_real")
            aprov_5j = col_pos2.slider("Aproveitamento nos Últimos 5 Jogos (%)", 0, 100, 60, key=f"{prefixo}_aprov_5j")
            prospeccao = st.selectbox("Prospecção Teórica Ideal (Prateleira)",
                                      ["Elite Absoluta", "Alta", "Média", "Baixa", "Crítica"],
                                      key=f"{prefixo}_prosp_painel")
            # Cálculo automático da Nota Posição (100 = líder)
            if posicao_real is not None:
                nota_posicao = 100.0 - (posicao_real - 1) * (100.0 / 19.0)
                nota_posicao = max(0.0, min(100.0, nota_posicao))
            # Posição momentânea baseada no aproveitamento
            pos_momentanea = 21.0 - (aprov_5j / 100.0) * 20.0
            # Multiplicador de prateleira
            if prospeccao in ["Elite Absoluta"]:
                mult_prat = 1.6
            elif prospeccao in ["Alta", "Média"]:
                mult_prat = 1.0
            else:
                mult_prat = 0.0
            tab_din = 50.0 + (posicao_real - pos_momentanea) * mult_prat
            tab_din = max(0.0, min(100.0, tab_din))
            st.caption(f"🔹 Nota Posição (IRC): {nota_posicao:.1f} | Tabela Dinâmica (IM): {tab_din:.1f}")

        estatisticas = {}
        p_atk, p_def, p_fdm, p_res = {}, {}, {}, {}

        with st.expander("⚽ Ataque", expanded=False):
            cols = st.columns(3)
            if cols[0].checkbox("Atq", key=f"{prefixo}_atq"):
                estatisticas['atq'] = cols[0].number_input("Valor", 0.0, 100.0, 15.0, key=f"{prefixo}_atq_v")
                p_atk['atq'] = 0.20
            if cols[1].checkbox("Atq Perigosos", key=f"{prefixo}_atq_per"):
                estatisticas['atq_perigosos'] = cols[1].number_input("Valor", 0.0, 100.0, 7.0, key=f"{prefixo}_atq_per_v")
                p_atk['atq_perigosos'] = 0.20
            if cols[2].checkbox("Chutes", key=f"{prefixo}_chutes"):
                estatisticas['chutes'] = cols[2].number_input("Valor", 0.0, 100.0, 16.0, key=f"{prefixo}_chutes_v")
                p_atk['chutes'] = 0.20
                p_fdm['chutes'] = 0.20
            cols2 = st.columns(3)
            if cols2[0].checkbox("Chutes Gol", key=f"{prefixo}_chutes_gol"):
                estatisticas['chutes_gol'] = cols2[0].number_input("Valor", 0.0, 100.0, 6.0, key=f"{prefixo}_chutes_gol_v")
                p_atk['chutes_gol'] = 0.20
            if cols2[1].checkbox("Gols Marcados", key=f"{prefixo}_gols"):
                estatisticas['gols'] = cols2[1].number_input("Valor", 0.0, 100.0, 2.0, key=f"{prefixo}_gols_v")
                p_atk['gols'] = 0.20
            if cols2[2].checkbox("xG", key=f"{prefixo}_xg"):
                estatisticas['xg'] = cols2[2].number_input("Valor", 0.0, 100.0, 1.8, key=f"{prefixo}_xg_v")
                p_atk['xg'] = 0.20

        with st.expander("🛡️ Defesa", expanded=False):
            cols = st.columns(3)
            if cols[0].checkbox("Atq Sofridos", key=f"{prefixo}_atq_sof"):
                estatisticas['atq_sofridos'] = cols[0].number_input("Valor", 0.0, 100.0, 8.0, key=f"{prefixo}_atq_sof_v")
                p_def['atq_sofridos'] = 0.20
            if cols[1].checkbox("Atq Perigosos Sofridos", key=f"{prefixo}_atq_per_sof"):
                estatisticas['atq_perigosos_sofridos'] = cols[1].number_input("Valor", 0.0, 100.0, 4.0, key=f"{prefixo}_atq_per_sof_v")
                p_def['atq_perigosos_sofridos'] = 0.20
            if cols[2].checkbox("Chutes Sofridos", key=f"{prefixo}_chutes_sof"):
                estatisticas['chutes_sofridos'] = cols[2].number_input("Valor", 0.0, 100.0, 10.0, key=f"{prefixo}_chutes_sof_v")
                p_def['chutes_sofridos'] = 0.20
                p_fdm['chutes_sofridos'] = 0.20
            cols2 = st.columns(3)
            if cols2[0].checkbox("Chutes Gol Sofridos", key=f"{prefixo}_chutes_gol_sof"):
                estatisticas['chutes_gol_sofridos'] = cols2[0].number_input("Valor", 0.0, 100.0, 3.0, key=f"{prefixo}_chutes_gol_sof_v")
                p_def['chutes_gol_sofridos'] = 0.20
            if cols2[1].checkbox("Gols Sofridos", key=f"{prefixo}_gols_sof"):
                estatisticas['gols_sofridos'] = cols2[1].number_input("Valor", 0.0, 100.0, 0.8, key=f"{prefixo}_gols_sof_v")
                p_def['gols_sofridos'] = 0.20
            if cols2[2].checkbox("xG Cedido", key=f"{prefixo}_xg_ced"):
                estatisticas['xg_cedido'] = cols2[2].number_input("Valor", 0.0, 100.0, 1.0, key=f"{prefixo}_xg_ced_v")
                p_def['xg_cedido'] = 0.20

        with st.expander("💪 Resistência à Pressão", expanded=False):
            cols = st.columns(2)
            if cols[0].checkbox("Pontos Recuperados (0-100)", key=f"{prefixo}_pontos_rec"):
                estatisticas['pontos_recuperados'] = cols[0].number_input("Nota", 0.0, 100.0, 60.0, key=f"{prefixo}_pontos_rec_v")
                p_res['pontos_recuperados'] = 1.0
            if cols[1].checkbox("Gols Finais (75'-90')", key=f"{prefixo}_gols_fin"):
                estatisticas['gols_finais'] = cols[1].number_input("Nota", 0.0, 100.0, 70.0, key=f"{prefixo}_gols_fin_v")
                p_res['gols_finais'] = 1.0

        # ---- MOMENTO (IM) ----
        with st.expander("📈 Índice de Momento (IM)", expanded=False):
            st.markdown("**Condição de Campo**")
            cc3 = st.slider(f"Últimos 3 jogos em { 'casa' if mando == 'C' else 'fora' }", 0, 100, 65, key=f"{prefixo}_cc3")
            cc5 = st.slider(f"Últimos 5 jogos em { 'casa' if mando == 'C' else 'fora' }", 0, 100, 60, key=f"{prefixo}_cc5")
            st.markdown("**Geral**")
            g3 = st.slider("Últimos 3 jogos gerais", 0, 100, 68, key=f"{prefixo}_g3")
            g5 = st.slider("Últimos 5 jogos gerais", 0, 100, 64, key=f"{prefixo}_g5")
            g10 = st.slider("Últimos 10 jogos gerais", 0, 100, 60, key=f"{prefixo}_g10")
            bonus_zebra = st.number_input("Bônus de Zebra (+15 se ativado)", 0, 15, 0, key=f"{prefixo}_zebra")

        # Histórico IM para IER
        with st.expander("📉 Histórico IM (últimos 5 jogos)", expanded=False):
            hist_im = []
            for i in range(5):
                hist_im.append(st.number_input(f"IM jogo {i+1}", 0.0, 100.0, 50.0, key=f"{prefixo}_im_hist{i}"))

        # Prateleira (para FMP) e IRC
        prat = st.selectbox("Prateleira do time (para FMP)",
                            ["Elite Absoluta", "Alta", "Média", "Baixa", "Crítica"],
                            key=f"{prefixo}_prat_fmp")
        with st.expander("🧠 IRC (Psicológico / Contextual)", expanded=False):
            rodada = st.number_input("Rodada", 1, 38, 20, key=f"{prefixo}_rod")
            orgulho = st.slider("Orgulho Ferido (0-30)", 0, 30, 0,
                                help="+10 derrota para inferior; +20 goleada humilhante")
            revanche = st.slider("Revanche (0-20)", 0, 20, 0,
                                 help="+10 se rival eliminou/goleou recentemente")
            st.markdown("---")
            st.markdown("**Novos Fatores**")
            sequencia = st.slider("Sequência (+/-10)", -10, 10, 0,
                                  help="+2 por vitória consecutiva (máx. +10); -2 por derrota consecutiva (mín. -10)")
            pressao = st.slider("Pressão da Torcida (-10 a +15)", -10, 15, 0,
                                help="Mandante com estádio lotado +10; visitante em clássico hostil -5")
            importancia = st.selectbox("Importância do Jogo", [0, 10, 20],
                                       help="0=normal, 10=clássico, 20=final/semifinal")
            desfalques = st.slider("Desfalques Graves (-15 a 0)", -15, 0, 0,
                                   help="Penalidade por jogadores-chave ausentes")

        im_params = (cc3, cc5, g3, g5, g10, bonus_zebra, tab_din)
        irc_params = (rodada, nota_posicao, prospeccao, orgulho, revanche,
                      sequencia, pressao, importancia, desfalques)
        return (estatisticas, p_atk, p_def, p_fdm, p_res, hist_im, prat,
                im_params, irc_params, prospeccao)

    # Time A (mandante)
    (est_a, p_atk_a, p_def_a, p_fdm_a, p_res_a, hist_im_a, prat_a,
     im_params_a, irc_params_a, prosp_a) = criar_seletores_time("a", nome_a, "C")

    st.divider()

    # Time B (visitante)
    (est_b, p_atk_b, p_def_b, p_fdm_b, p_res_b, hist_im_b, prat_b,
     im_params_b, irc_params_b, prosp_b) = criar_seletores_time("b", nome_b, "F")

    if st.button("⚡ GERAR MYPREDICT", use_container_width=True):
        # Cálculo completo com detalhamento
        res_a = calcular_overall(est_a, med_liga, prat_a, prat_b,
                                 p_atk_a, p_def_a, p_fdm_a, p_res_a, hist_im_a)
        res_b = calcular_overall(est_b, med_liga, prat_b, prat_a,
                                 p_atk_b, p_def_b, p_fdm_b, p_res_b, hist_im_b)

        im_a, bc_a, bg_a, td_a, bz_a = calcular_im(*im_params_a)
        im_b, bc_b, bg_b, td_b, bz_b = calcular_im(*im_params_b)

        irc_a, fac_a, urg_a, org_a, rev_a, seq_a, pr_a, imp_a, desf_a = calcular_irc(*irc_params_a)
        irc_b, fac_b, urg_b, org_b, rev_b, seq_b, pr_b, imp_b, desf_b = calcular_irc(*irc_params_b)

        jun_a = calcular_juncao(res_a['overall'], im_a, irc_a)
        jun_b = calcular_juncao(res_b['overall'], im_b, irc_b)

        prob_a, prob_e, prob_b = calcular_probabilidades(jun_a, jun_b)

        # =================================================================
        # EXIBIÇÃO DOS RESULTADOS (COMPARAÇÃO LADO A LADO)
        # =================================================================
        st.header("📊 Resultado MyPredict")
        col1, col2, col3 = st.columns(3)
        col1.metric(f"🏠 {nome_a}", f"{jun_a:.1f}", f"Overall: {res_a['overall']:.1f}")
        col2.metric("⚖️ Diferença", f"{abs(jun_a - jun_b):.1f}")
        col3.metric(f"🚌 {nome_b}", f"{jun_b:.1f}", f"Overall: {res_b['overall']:.1f}")

        st.subheader("🎯 Probabilidades")
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Vitória {nome_a}", f"{prob_a:.1f}%")
        c2.metric("Empate", f"{prob_e:.1f}%")
        c3.metric(f"Vitória {nome_b}", f"{prob_b:.1f}%")

        if prob_a > prob_b and prob_a > prob_e:
            st.success(f"🏆 Previsão: Vitória do {nome_a}")
        elif prob_b > prob_a and prob_b > prob_e:
            st.success(f"🏆 Previsão: Vitória do {nome_b}")
        else:
            st.warning("🤝 Previsão: Empate")

        # COMPARAÇÃO DETALHADA LADO A LADO
        st.markdown("---")
        st.subheader("🔍 Comparação Detalhada (lado a lado)")

        with st.container():
            colA, colB = st.columns(2)
            with colA:
                st.markdown(f"### 🏠 {nome_a}")
                st.write(f"**Prateleira:** {prat_a} (rival {prat_b})")
                st.write("**Overall**")
                st.write(f"- Ataque: {res_a['ataque']:.1f} (FVO: {res_a['fvo']:.1f}, FCO: {res_a['fco']:.1f})")
                st.write(f"- Defesa: {res_a['defesa']:.1f} (FRD: {res_a['frd']:.1f}, FCD Def: {res_a['fcd_def']:.1f})")
                st.write(f"- Consistência: {res_a['consistencia']:.1f} (FDM: {res_a['fdm']:.1f}, IER: {res_a['ier']:.1f})")
                st.write(f"- Resistência: {res_a['resistencia']:.1f} (FCD Res: {res_a['fcd_res']:.1f}, EGZ: {res_a['egz_res']:.1f}, FRI: {res_a['fri_res']:.1f}, FZC: {res_a['fzc_res']:.1f})")
                st.write(f"**Overall Final:** {res_a['overall']:.1f}")
                st.write("**IM**")
                st.write(f"- Cond. Campo: {bc_a:.1f} | Geral: {bg_a:.1f} | Tab. Dinâmica: {td_a:.1f} | Zebra: {bz_a:.1f}")
                st.write(f"**IM Final:** {im_a:.1f}")
                st.write("**IRC**")
                st.write(f"- FAC: {fac_a:.2f}, Urgência: {urg_a:.1f}, Orgulho: {org_a:.1f}, Revanche: {rev_a:.1f}")
                st.write(f"- Sequência: {seq_a:.1f}, Pressão: {pr_a:.1f}, Importância: {imp_a:.1f}, Desfalques: {desf_a:.1f}")
                st.write(f"**IRC Final:** {irc_a:.1f}")
                st.write(f"**Junção:** {jun_a:.1f}")

            with colB:
                st.markdown(f"### 🚌 {nome_b}")
                st.write(f"**Prateleira:** {prat_b} (rival {prat_a})")
                st.write("**Overall**")
                st.write(f"- Ataque: {res_b['ataque']:.1f} (FVO: {res_b['fvo']:.1f}, FCO: {res_b['fco']:.1f})")
                st.write(f"- Defesa: {res_b['defesa']:.1f} (FRD: {res_b['frd']:.1f}, FCD Def: {res_b['fcd_def']:.1f})")
                st.write(f"- Consistência: {res_b['consistencia']:.1f} (FDM: {res_b['fdm']:.1f}, IER: {res_b['ier']:.1f})")
                st.write(f"- Resistência: {res_b['resistencia']:.1f} (FCD Res: {res_b['fcd_res']:.1f}, EGZ: {res_b['egz_res']:.1f}, FRI: {res_b['fri_res']:.1f}, FZC: {res_b['fzc_res']:.1f})")
                st.write(f"**Overall Final:** {res_b['overall']:.1f}")
                st.write("**IM**")
                st.write(f"- Cond. Campo: {bc_b:.1f} | Geral: {bg_b:.1f} | Tab. Dinâmica: {td_b:.1f} | Zebra: {bz_b:.1f}")
                st.write(f"**IM Final:** {im_b:.1f}")
                st.write("**IRC**")
                st.write(f"- FAC: {fac_b:.2f}, Urgência: {urg_b:.1f}, Orgulho: {org_b:.1f}, Revanche: {rev_b:.1f}")
                st.write(f"- Sequência: {seq_b:.1f}, Pressão: {pr_b:.1f}, Importância: {imp_b:.1f}, Desfalques: {desf_b:.1f}")
                st.write(f"**IRC Final:** {irc_b:.1f}")
                st.write(f"**Junção:** {jun_b:.1f}")

        # Detalhamento completo expander (redundante, mas mantido)
        with st.expander("📋 Ver todas as variáveis utilizadas"):
            st.write("**Estatísticas ativas Time A:**", list(est_a.keys()) if est_a else "Nenhuma")
            st.write("**Estatísticas ativas Time B:**", list(est_b.keys()) if est_b else "Nenhuma")

# =========================================================================
# RODAPÉ
# =========================================================================
st.sidebar.divider()
st.sidebar.caption("MyPredict by Ferry v0.3")
st.sidebar.caption(f"{datetime.now().strftime('%d/%m/%Y %H:%M')}")
