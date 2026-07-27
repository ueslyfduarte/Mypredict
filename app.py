# app.py — MyPredict 2.0 (Interface centralizada, seletor de ligas e times)
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
from data_source_fbref_stats import obter_codigo_fbref
import json
from pathlib import Path

# ------------------------------------------------------------
# Carregar lista de ligas do arquivo config/league_dict.json
# ------------------------------------------------------------
def carregar_ligas():
    league_dict_file = Path('config') / 'league_dict.json'
    if league_dict_file.exists():
        with open(league_dict_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Fallback mínimo se o arquivo não existir
    return {
        "Brasileirão": 24,
        "Premier League": 9,
        "La Liga": 12,
        "Bundesliga": 20,
        "Serie A": 11,
        "Ligue 1": 13,
        "Eredivisie": 23,
        "Primeira Liga": 32,
        "MLS": 22,
    }

LIGAS_DICT = carregar_ligas()
LISTA_LIGAS = sorted(LIGAS_DICT.keys())

# ------------------------------------------------------------
# Configuração da página
# ------------------------------------------------------------
st.set_page_config(page_title="MyPredict 2.0", layout="centered")

# ------------------------------------------------------------
# CSS personalizado (preto, prata, dourado)
# ------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #c0c0c0; }
    h1, h2, h3 { color: #ffd700 !important; }
    div[data-testid="metric-container"] {
        background-color: #1e1e1e; border: 1px solid #333;
        border-radius: 10px; padding: 10px; color: #ffd700 !important;
    }
    div[data-testid="metric-container"] label { color: #c0c0c0 !important; }
    div.stButton > button {
        background-color: #ffd700; color: #0e1117;
        border: none; font-weight: bold; border-radius: 8px;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #ffed4a; box-shadow: 0px 0px 15px #ffd700;
    }
    .selo-ouro {
        background: linear-gradient(145deg, #ffd700, #b8860b);
        color: #0e1117; font-weight: 900; text-align: center;
        border-radius: 50%; width: 120px; height: 120px;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto; font-size: 14px;
        box-shadow: 0px 0px 25px #ffd700; animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 10px #ffd700; }
        50% { box-shadow: 0 0 30px #ffd700; }
        100% { box-shadow: 0 0 10px #ffd700; }
    }
    .stSelectbox [data-baseweb="select"] {
        background-color: #1e1e1e;
        color: #ffd700;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Título e frase
# ------------------------------------------------------------
st.markdown("<h1 style='text-align: center;'>⚽ MyPredict 2.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #c0c0c0;'>"
            "“O futebol é a única coisa que me emociona mais do que a ciência.”<br>"
            "— Albert Einstein (adaptado)</p>", unsafe_allow_html=True)

# ------------------------------------------------------------
# Seleção de liga e temporada
# ------------------------------------------------------------
liga_selecionada = st.selectbox("Selecione a liga", LISTA_LIGAS, index=0)
temporada = st.number_input("Temporada", min_value=2015, max_value=2026, value=2024)

# Carregar classificação para preencher times
try:
    liga_codigo = LIGAS_DICT[liga_selecionada]
    class_ant = classificação_anterior(liga_codigo, temporada)
    if class_ant:
        lista_times = sorted(class_ant.values())
    else:
        lista_times = []
        st.warning("Não foi possível carregar a classificação desta liga/temporada.")
except Exception as e:
    lista_times = []
    st.error(f"Erro ao carregar dados da liga: {e}")

# ------------------------------------------------------------
# Seleção dos times
# ------------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    if lista_times:
        time_casa = st.selectbox("Time da casa", lista_times)
    else:
        time_casa = st.text_input("Time da casa", "Flamengo")
with col2:
    if lista_times:
        time_fora = st.selectbox("Time de fora", lista_times, index=min(1, len(lista_times)-1))
    else:
        time_fora = st.text_input("Time de fora", "Palmeiras")

# ------------------------------------------------------------
# Botão de ação
# ------------------------------------------------------------
gerar = st.button("⚡ Gerar MyPredict", use_container_width=True)

# ------------------------------------------------------------
# Execução da análise
# ------------------------------------------------------------
if gerar:
    with st.spinner("Calculando..."):
        try:
            if not class_ant:
                st.error("Classificação indisponível.")
                st.stop()
            prateleiras = gerar_prateleiras(liga_codigo, temporada)

            dados_casa = obter_dados_ovrall_time(time_casa, liga_codigo, temporada, class_ant)
            dados_fora = obter_dados_ovrall_time(time_fora, liga_codigo, temporada, class_ant)
            if not dados_casa or not dados_fora:
                st.error("Partidas não encontradas para um dos times.")
                st.stop()

            # IMA
            jogos_casa = obter_ultimos_jogos_com_heranca(time_casa, liga_codigo, temporada, class_ant, n=20)
            rec_casa = extrair_recortes_ima(jogos_casa, True)
            jogos_fora = obter_ultimos_jogos_com_heranca(time_fora, liga_codigo, temporada, class_ant, n=20)
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

            st.markdown(f"<h2 style='text-align: center;'>{time_casa} x {time_fora}</h2>",
                        unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Vitória Casa", f"{p1:.1%}")
                if recomendado(p1):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>',
                                unsafe_allow_html=True)
            with col2:
                st.metric("Empate", f"{pX:.1%}")
                if recomendado(pX):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>',
                                unsafe_allow_html=True)
            with col3:
                st.metric("Vitória Fora", f"{p2:.1%}")
                if recomendado(p2):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>',
                                unsafe_allow_html=True)

            st.markdown("---")
            col4, col5 = st.columns(2)
            with col4:
                st.metric("Over 2.5 gols", f"{over25:.1%}" if over25 else "N/D")
                if recomendado(over25):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>',
                                unsafe_allow_html=True)
                st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")
                if recomendado(gol_ht):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>',
                                unsafe_allow_html=True)
            with col5:
                st.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")
                if recomendado(btts):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>',
                                unsafe_allow_html=True)
                st.metric("Over Escanteios", f"{esc:.1%}" if esc else "N/D")
                if recomendado(esc):
                    st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>',
                                unsafe_allow_html=True)

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

            avancados = any(
                dados_casa.get(k) for k in ['xg_media', 'posse_media']
            ) or any(
                dados_fora.get(k) for k in ['xg_media', 'posse_media']
            )
            st.caption(
                "📡 Dados avançados (FBref): " +
                ("✅ carregados" if avancados else "⚠️ apenas dados básicos (gols/HT)")
            )

        except Exception as e:
            st.error(f"Erro: {str(e)}")
