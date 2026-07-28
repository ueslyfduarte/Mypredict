# app.py — MyPredict 2.0 (sem busca automática, contador de uso, layout premium)
import streamlit as st
from data_loader import (
    gerar_prateleiras, obter_ultimos_jogos_com_heranca, extrair_recortes_ima,
    obter_dados_ovrall_time, classificação_anterior
)
from ratings import calcular_ima, calcular_mpv
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from data_source_football_api import listar_ligas, listar_temporadas, get_api_usage

# ------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------
st.set_page_config(page_title="MyPredict 2.0", layout="wide")

# ------------------------------------------------------------
# CSS premium (preto, prata, dourado com cartões e sombras)
# ------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: radial-gradient(ellipse at top, #1a1a2e 0%, #0e1117 70%); }
    h1, h2, h3, h4 { color: #ffd700 !important; letter-spacing: 0.5px; }
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #ffd700, #ffaa00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }
    .quote {
        color: #c0c0c0;
        font-style: italic;
        text-align: center;
        font-size: 1.2rem;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    div[data-testid="metric-container"] {
        background: rgba(30, 30, 30, 0.8);
        border: 1px solid #333;
        border-radius: 16px;
        padding: 24px 16px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    div[data-testid="metric-container"]:hover {
        border-color: #ffd700;
        box-shadow: 0 8px 24px rgba(255,215,0,0.2);
    }
    div[data-testid="metric-container"] label { color: #c0c0c0 !important; font-size: 0.9rem; text-transform: uppercase; }
    div.stButton > button {
        background: linear-gradient(135deg, #ffd700, #ffaa00);
        color: #0e1117;
        border: none;
        font-weight: 700;
        font-size: 1.2rem;
        border-radius: 12px;
        padding: 14px;
        transition: all 0.3s ease;
        letter-spacing: 1px;
        box-shadow: 0 4px 15px rgba(255,215,0,0.3);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255,215,0,0.5);
    }
    .selo-ouro {
        background: linear-gradient(145deg, #ffd700, #b8860b);
        color: #0e1117;
        font-weight: 900;
        text-align: center;
        border-radius: 50%;
        width: 120px;
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto 0;
        font-size: 14px;
        box-shadow: 0 0 35px #ffd700;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 15px #ffd700; }
        50% { box-shadow: 0 0 40px #ffd700, 0 0 80px #ffaa00; }
        100% { box-shadow: 0 0 15px #ffd700; }
    }
    .stSelectbox [data-baseweb="select"] {
        background: rgba(30,30,30,0.9);
        border: 1px solid #444;
        border-radius: 10px;
        color: #ffd700;
    }
    .stTextInput > div > div > input {
        background: rgba(30,30,30,0.9);
        border: 1px solid #444;
        border-radius: 10px;
        color: #c0c0c0;
    }
    .usage-badge {
        background: rgba(30,30,30,0.8);
        border: 1px solid #ffd700;
        border-radius: 20px;
        padding: 4px 16px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        color: #ffd700;
        margin-bottom: 20px;
    }
    .usage-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Controle de estado para ligas (carregar apenas uma vez)
# ------------------------------------------------------------
if 'ligas_carregadas' not in st.session_state:
    st.session_state.ligas_carregadas = False
    st.session_state.lista_ligas = []
    st.session_state.temporadas = {}

if not st.session_state.ligas_carregadas:
    with st.spinner("Conectando à API football-data.org..."):
        try:
            ligas_dict = listar_ligas()
            st.session_state.lista_ligas = sorted(ligas_dict.keys())
            st.session_state.ligas_dict = ligas_dict
            st.session_state.ligas_carregadas = True
        except Exception as e:
            st.error(f"Erro ao carregar ligas: {e}")
            st.stop()

# ------------------------------------------------------------
# Indicador de uso da API
# ------------------------------------------------------------
uso, limite = get_api_usage()
porcentagem = uso / limite

# Cor do indicador: verde (>50% restante), amarelo (20-50%), vermelho (<20%)
if porcentagem < 0.5:
    cor = "#00ff7f"
elif porcentagem < 0.8:
    cor = "#ffaa00"
else:
    cor = "#ff4d4d"

st.markdown(f"""
<div style="display: flex; justify-content: center;">
    <div class="usage-badge">
        <span class="usage-dot" style="background-color: {cor};"></span>
        API: {uso}/{limite} requisições neste minuto
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Título e frase
# ------------------------------------------------------------
st.markdown("<div class='main-title'>⚽ MyPredict 2.0</div>", unsafe_allow_html=True)
st.markdown("<div class='quote'>“O futebol é a única coisa que me emociona mais do que a ciência.”<br>— Albert Einstein (adaptado)</div>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Seletores (agora apenas interface, sem chamadas à API)
# ------------------------------------------------------------
col_liga, col_temp = st.columns([2, 1])
with col_liga:
    liga_nome = st.selectbox("Selecione a liga", st.session_state.lista_ligas, key="sel_liga")
with col_temp:
    # Temporadas carregadas sob demanda para a liga escolhida
    if liga_nome:
        codigo = st.session_state.ligas_dict[liga_nome]
        if codigo not in st.session_state.temporadas:
            with st.spinner("Buscando temporadas..."):
                try:
                    st.session_state.temporadas[codigo] = listar_temporadas(codigo)
                except:
                    st.session_state.temporadas[codigo] = []
        temporadas = st.session_state.temporadas.get(codigo, [])
        if not temporadas:
            st.warning("Nenhuma temporada disponível")
            temporada = st.number_input("Temporada", value=2024)
        else:
            temporada = st.selectbox("Temporada", temporadas, key="sel_temp")
    else:
        temporada = st.number_input("Temporada", value=2024)

# Times: campos de texto (sem busca automática)
col1, col2 = st.columns(2)
with col1:
    time_casa = st.text_input("Time da casa", value="Flamengo")
with col2:
    time_fora = st.text_input("Time de fora", value="Palmeiras")

# ------------------------------------------------------------
# Botão de ação – sempre visível
# ------------------------------------------------------------
gerar = st.button("⚡ Gerar MyPredict", use_container_width=True)

# ------------------------------------------------------------
# Execução da análise (apenas ao clicar)
# ------------------------------------------------------------
if gerar:
    with st.spinner("Calculando..."):
        try:
            # Agora sim, buscamos a classificação e os dados
            class_ant = classificação_anterior(liga_nome, temporada)
            if not class_ant:
                st.error(f"Classificação não disponível para {liga_nome} {temporada}.")
                st.stop()
            prateleiras = gerar_prateleiras(liga_nome, temporada)

            dados_casa = obter_dados_ovrall_time(time_casa, liga_nome, temporada, class_ant)
            dados_fora = obter_dados_ovrall_time(time_fora, liga_nome, temporada, class_ant)
            if not dados_casa or not dados_fora:
                st.error("Partidas não encontradas para um dos times.")
                st.stop()

            jogos_casa = obter_ultimos_jogos_com_heranca(time_casa, liga_nome, temporada, class_ant, n=20)
            rec_casa = extrair_recortes_ima(jogos_casa, True)
            jogos_fora = obter_ultimos_jogos_com_heranca(time_fora, liga_nome, temporada, class_ant, n=20)
            rec_fora = extrair_recortes_ima(jogos_fora, False)

            ima_casa = calcular_ima(time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                                    rec_casa['5CF'], rec_casa['3CF'], prateleiras)
            ima_fora = calcular_ima(time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                                    rec_fora['5CF'], rec_fora['3CF'], prateleiras)

            ovrall_casa, ovrall_fora = 50.0, 50.0
            ic_casa, ic_fora = 50.0, 50.0
            mpv_casa = calcular_mpv(ima_casa, ovrall_casa, ic_casa)
            mpv_fora = calcular_mpv(ima_fora, ovrall_fora, ic_fora)
            bonus_casa = calcular_bonus_casa(dados_casa.get('diff_aprov_casa_fora'))

            p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

            over25 = prob_over_2_5(
                dados_casa.get('gols_media'), dados_fora.get('gols_media'),
                dados_casa.get('gols_sofridos_media'), dados_fora.get('gols_sofridos_media')
            )

            gols_esp_casa = _gols_esperados(dados_casa.get('gols_media'),
                                            dados_fora.get('gols_sofridos_media'),
                                            MEDIA_GOLS_CASA_LIGA)
            gols_esp_fora = _gols_esperados(dados_fora.get('gols_media'),
                                            dados_casa.get('gols_sofridos_media'),
                                            MEDIA_GOLS_FORA_LIGA)
            btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora) if gols_esp_casa and gols_esp_fora else None

            gol_ht = prob_gol_ht(
                dados_casa.get('gols_ht_media'), dados_fora.get('gols_ht_media'),
                dados_casa.get('gols_ht_sofridos_media'), dados_fora.get('gols_ht_sofridos_media')
            )

            esc = prob_over_escanteios(
                dados_casa.get('escanteios_media'), dados_fora.get('escanteios_media'),
                dados_casa.get('escanteios_sofridos_media'), dados_fora.get('escanteios_sofridos_media')
            )

            def recomendado(prob):
                return prob is not None and prob >= 0.60

            st.markdown(f"<h2 style='text-align: center; color: #ffd700;'>{time_casa} x {time_fora}</h2>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Vitória Casa", f"{p1:.1%}")
                if recomendado(p1):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
            with col2:
                st.metric("Empate", f"{pX:.1%}")
                if recomendado(pX):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
            with col3:
                st.metric("Vitória Fora", f"{p2:.1%}")
                if recomendado(p2):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)

            st.markdown("---")
            col4, col5 = st.columns(2)
            with col4:
                st.metric("Over 2.5 gols", f"{over25:.1%}" if over25 else "N/D")
                if recomendado(over25):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
                st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")
                if recomendado(gol_ht):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
            with col5:
                st.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")
                if recomendado(btts):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
                st.metric("Over Escanteios", f"{esc:.1%}" if esc else "N/D")
                if recomendado(esc):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)

            with st.expander("📊 Métricas detalhadas"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**{time_casa}**")
                    st.write(f"IMA: {ima_casa:.1f}")
                    st.write(f"MPV: {mpv_casa:.1f}")
                with c2:
                    st.markdown(f"**{time_fora}**")
                    st.write(f"IMA: {ima_fora:.1f}")
                    st.write(f"MPV: {mpv_fora:.1f}")

        except Exception as e:
            st.error(f"Erro: {str(e)}")
