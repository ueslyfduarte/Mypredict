# automatico.py — MyPredict 2.0 (lógica do modo automático)
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
from data_source_api_football import listar_ligas, listar_temporadas, get_api_usage

def inicializar_estado():
    """Garante que o estado inicial esteja criado."""
    if 'ligas_carregadas' not in st.session_state:
        st.session_state.ligas_carregadas = False
        st.session_state.lista_ligas = []
        st.session_state.temporadas = {}
        st.session_state.times_carregados = {}

def carregar_ligas():
    """Carrega a lista de ligas da API e guarda no estado."""
    if not st.session_state.ligas_carregadas:
        with st.spinner("Conectando à API-Football..."):
            try:
                ligas_dict = listar_ligas()
                st.session_state.lista_ligas = sorted(ligas_dict.keys())
                st.session_state.ligas_dict = ligas_dict
                st.session_state.ligas_carregadas = True
                st.session_state.erro_ligas = None
            except Exception as e:
                st.session_state.erro_ligas = str(e)

def buscar_temporadas(liga_nome):
    """Busca as temporadas da liga e guarda no estado."""
    if liga_nome and liga_nome in st.session_state.ligas_dict:
        liga_id = st.session_state.ligas_dict[liga_nome]
        if liga_id not in st.session_state.temporadas:
            with st.spinner("Buscando temporadas..."):
                try:
                    st.session_state.temporadas[liga_id] = listar_temporadas(liga_id)
                except:
                    st.session_state.temporadas[liga_id] = []

def buscar_times(liga_nome, temporada):
    """Busca os times da classificação e guarda no estado."""
    chave = f"{liga_nome}_{temporada}"
    if chave not in st.session_state.times_carregados:
        with st.spinner("Obtendo classificação..."):
            try:
                class_ant = classificação_anterior(liga_nome, temporada)
                if class_ant:
                    st.session_state.times_carregados[chave] = sorted(class_ant.values())
                else:
                    st.session_state.times_carregados[chave] = []
            except Exception as e:
                st.error(f"Erro ao carregar times: {e}")
                st.session_state.times_carregados[chave] = []

def executar_automatico(liga_nome, temporada, time_casa, time_fora):
    """Executa o cálculo completo e retorna (resultados, mensagem_erro)."""
    class_ant = classificação_anterior(liga_nome, temporada)
    if not class_ant:
        return None, "Classificação indisponível."

    prateleiras = gerar_prateleiras(liga_nome, temporada)

    dados_casa = obter_dados_ovrall_time(time_casa, liga_nome, temporada, class_ant)
    dados_fora = obter_dados_ovrall_time(time_fora, liga_nome, temporada, class_ant)
    if not dados_casa or not dados_fora:
        return None, "Partidas não encontradas."

    jogos_casa = obter_ultimos_jogos_com_heranca(time_casa, liga_nome, temporada, class_ant, n=20)
    rec_casa = extrair_recortes_ima(jogos_casa, True)
    jogos_fora = obter_ultimos_jogos_com_heranca(time_fora, liga_nome, temporada, class_ant, n=20)
    rec_fora = extrair_recortes_ima(jogos_fora, False)

    ima_casa = calcular_ima(time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                            rec_casa['5CF'], rec_casa['3CF'], prateleiras)
    ima_fora = calcular_ima(time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                            rec_fora['5CF'], rec_fora['3CF'], prateleiras)

    # OVRall e IC temporários (modo automático usa 50)
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
    gols_esp_casa = _gols_esperados(dados_casa.get('gols_media'), dados_fora.get('gols_sofridos_media'), MEDIA_GOLS_CASA_LIGA)
    gols_esp_fora = _gols_esperados(dados_fora.get('gols_media'), dados_casa.get('gols_sofridos_media'), MEDIA_GOLS_FORA_LIGA)
    btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)
    gol_ht = prob_gol_ht(
        dados_casa.get('gols_ht_media'), dados_fora.get('gols_ht_media'),
        dados_casa.get('gols_ht_sofridos_media'), dados_fora.get('gols_ht_sofridos_media')
    )
    esc = prob_over_escanteios(
        dados_casa.get('escanteios_media'), dados_fora.get('escanteios_media'),
        dados_casa.get('escanteios_sofridos_media'), dados_fora.get('escanteios_sofridos_media')
    )

    return {
        'time_casa': time_casa, 'time_fora': time_fora,
        'p1': p1, 'pX': pX, 'p2': p2,
        'rec_p1': (p1 is not None and p1 >= 0.60),
        'rec_p2': (p2 is not None and p2 >= 0.60),
        'over25': over25, 'btts': btts, 'gol_ht': gol_ht, 'esc': esc,
        'ima_casa': ima_casa, 'ima_fora': ima_fora,
        'mpv_casa': mpv_casa, 'mpv_fora': mpv_fora,
    }, None
