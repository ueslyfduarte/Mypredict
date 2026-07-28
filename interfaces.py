# interfaces.py — MyPredict 2.0 (central de interfaces)
import streamlit as st
import json
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from data_loader import (
    gerar_prateleiras, obter_ultimos_jogos_com_heranca, extrair_recortes_ima,
    obter_dados_ovrall_time, classificação_anterior
)
from data_source_api_football import listar_ligas, listar_temporadas, get_api_usage

# ------------------------------------------------------------
# CSS compartilhado (usado por ambas as interfaces)
# ------------------------------------------------------------
def injetar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background: radial-gradient(ellipse at top, #1a1a2e 0%, #0e1117 70%); }
        h1, h2, h3, h4 { color: #ffd700 !important; letter-spacing: 0.5px; }
        .main-title { font-size: 3rem; font-weight: 700; background: linear-gradient(135deg, #ffd700, #ffaa00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0; }
        .quote { color: #c0c0c0; font-style: italic; text-align: center; font-size: 1.2rem; margin-top: -10px; margin-bottom: 20px; }
        div[data-testid="metric-container"] { background: rgba(30, 30, 30, 0.8); border: 1px solid #333; border-radius: 16px; padding: 24px 16px; backdrop-filter: blur(10px); transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
        div[data-testid="metric-container"]:hover { border-color: #ffd700; box-shadow: 0 8px 24px rgba(255,215,0,0.2); }
        div[data-testid="metric-container"] label { color: #c0c0c0 !important; font-size: 0.9rem; text-transform: uppercase; }
        div.stButton > button { background: linear-gradient(135deg, #ffd700, #ffaa00); color: #0e1117; border: none; font-weight: 700; font-size: 1.2rem; border-radius: 12px; padding: 14px; transition: all 0.3s ease; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(255,215,0,0.3); }
        div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(255,215,0,0.5); }
        .selo-ouro { background: linear-gradient(145deg, #ffd700, #b8860b); color: #0e1117; font-weight: 900; text-align: center; border-radius: 50%; width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; margin: 20px auto 0; font-size: 14px; box-shadow: 0 0 35px #ffd700; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { box-shadow: 0 0 15px #ffd700; } 50% { box-shadow: 0 0 40px #ffd700, 0 0 80px #ffaa00; } 100% { box-shadow: 0 0 15px #ffd700; } }
        .stSelectbox [data-baseweb="select"] { background: rgba(30,30,30,0.9); border: 1px solid #444; border-radius: 10px; color: #ffd700; }
        .usage-badge { background: rgba(30,30,30,0.8); border: 1px solid #ffd700; border-radius: 20px; padding: 4px 16px; display: inline-flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #ffd700; margin-bottom: 20px; }
        .usage-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
        .time-box { background: #1a1a1a; border-radius: 12px; padding: 16px; margin: 10px 0; }
        .time-casa { border: 2px solid #ffd700; }
        .time-fora { border: 2px solid #c0c0c0; }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# Função auxiliar para converter string com vírgula
# ------------------------------------------------------------
def para_float(valor_str):
    if valor_str is None or valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        return None

# ------------------------------------------------------------
# Função auxiliar para extrair jogos de texto (linha única ou múltiplas)
# ------------------------------------------------------------
def extrair_jogos(texto):
    jogos = []
    for linha in texto.split('\n'):
        linha = linha.strip()
        if not linha: continue
        partes = [p.strip() for p in linha.split(',')]
        if len(partes) == 3 and partes[0] in ('V','E','D') and partes[2].upper() in ('S','N'):
            jogos.append({"resultado": partes[0], "adversario": partes[1], "mandante": partes[2].upper() == 'S'})
    if len(jogos) >= 10: return jogos
    for linha in texto.split('\n'):
        linha = linha.strip()
        if not linha: continue
        partes = [p.strip() for p in linha.split(',')]
        if len(partes) >= 30:
            for i in range(0, len(partes)-2, 3):
                res = partes[i]; adv = partes[i+1]; mand = partes[i+2]
                if res in ('V','E','D') and mand.upper() in ('S','N'):
                    jogos.append({"resultado": res, "adversario": adv, "mandante": mand.upper() == 'S'})
            break
    return jogos

# ------------------------------------------------------------
# INTERFACE AUTOMÁTICA
# ------------------------------------------------------------
def show_automatico():
    st.set_page_config(page_title="MyPredict 2.0", layout="wide")
    injetar_css()

    # Estado inicial das ligas
    if 'ligas_carregadas' not in st.session_state:
        st.session_state.ligas_carregadas = False
        st.session_state.lista_ligas = []
        st.session_state.temporadas = {}
        st.session_state.times_carregados = {}

    if not st.session_state.ligas_carregadas:
        with st.spinner("Conectando à API-Football..."):
            try:
                ligas_dict = listar_ligas()
                st.session_state.lista_ligas = sorted(ligas_dict.keys())
                st.session_state.ligas_dict = ligas_dict
                st.session_state.ligas_carregadas = True
            except Exception as e:
                st.error(f"Erro ao carregar ligas: {e}")
                st.stop()

    # Indicador de uso da API
    uso, limite = get_api_usage()
    porcentagem = uso / limite
    if porcentagem < 0.5: cor = "#00ff7f"
    elif porcentagem < 0.8: cor = "#ffaa00"
    else: cor = "#ff4d4d"
    st.markdown(f"""
    <div style="display: flex; justify-content: center;">
        <div class="usage-badge">
            <span class="usage-dot" style="background-color: {cor};"></span>
            API: {uso}/{limite} requisições restantes hoje
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-title'>⚽ MyPredict 2.0</div>", unsafe_allow_html=True)
    st.markdown("<div class='quote'>“O futebol é a única coisa que me emociona mais do que a ciência.”<br>— Albert Einstein (adaptado)</div>", unsafe_allow_html=True)

    col_liga, col_temp = st.columns([2, 1])
    with col_liga:
        liga_nome = st.selectbox("Selecione a liga", st.session_state.lista_ligas, key="sel_liga")
    with col_temp:
        if liga_nome:
            liga_id = st.session_state.ligas_dict[liga_nome]
            if liga_id not in st.session_state.temporadas:
                with st.spinner("Buscando temporadas..."):
                    try: st.session_state.temporadas[liga_id] = listar_temporadas(liga_id)
                    except: st.session_state.temporadas[liga_id] = []
            temporadas = st.session_state.temporadas.get(liga_id, [])
            if not temporadas:
                st.warning("Nenhuma temporada disponível")
                temporada = st.number_input("Temporada", value=2024)
            else:
                temporada = st.selectbox("Temporada", temporadas, key="sel_temp")
        else:
            temporada = st.number_input("Temporada", value=2024)

    chave_times = f"{liga_nome}_{temporada}"
    if chave_times not in st.session_state.times_carregados:
        buscar = st.button("🔍 Buscar Times", use_container_width=True)
        if buscar:
            with st.spinner("Obtendo classificação..."):
                try:
                    class_ant = classificação_anterior(liga_nome, temporada)
                    if class_ant: st.session_state.times_carregados[chave_times] = sorted(class_ant.values())
                    else: st.session_state.times_carregados[chave_times] = []
                except Exception as e:
                    st.error(f"Erro ao carregar times: {e}")
                    st.session_state.times_carregados[chave_times] = []
    else:
        st.info("Times carregados do cache. Para atualizar, troque de temporada ou liga.")

    lista_times = st.session_state.times_carregados.get(chave_times, [])
    col1, col2 = st.columns(2)
    with col1:
        if lista_times: time_casa = st.selectbox("Time da casa", lista_times)
        else: time_casa = st.text_input("Time da casa", value="Arsenal")
    with col2:
        if lista_times: time_fora = st.selectbox("Time de fora", lista_times, index=min(1, len(lista_times)-1))
        else: time_fora = st.text_input("Time de fora", value="Manchester United")

    gerar = st.button("⚡ Gerar MyPredict", use_container_width=True)

    if gerar:
        with st.spinner("Calculando..."):
            try:
                if chave_times not in st.session_state.times_carregados:
                    class_ant = classificação_anterior(liga_nome, temporada)
                else:
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

                def recomendado(prob): return prob is not None and prob >= 0.60

                st.markdown(f"<h2 style='text-align: center; color: #ffd700;'>{time_casa} x {time_fora}</h2>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Vitória Casa", f"{p1:.1%}")
                    if recomendado(p1): st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
                with col2:
                    st.metric("Empate", f"{pX:.1%}")
                    if recomendado(pX): st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
                with col3:
                    st.metric("Vitória Fora", f"{p2:.1%}")
                    if recomendado(p2): st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)

                st.markdown("---")
                col4, col5 = st.columns(2)
                with col4:
                    st.metric("Over 2.5 gols", f"{over25:.1%}" if over25 else "N/D")
                    if recomendado(over25): st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
                    st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")
                    if recomendado(gol_ht): st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
                with col5:
                    st.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")
                    if recomendado(btts): st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
                    st.metric("Over Escanteios", f"{esc:.1%}" if esc else "N/D")
                    if recomendado(esc): st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)

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

# ------------------------------------------------------------
# INTERFACE MANUAL
# ------------------------------------------------------------
def show_manual():
    st.set_page_config(page_title="MyPredict 2.0 – Manual", layout="centered")
    injetar_css()

    # Inicializa estado
    defaults = {
        'time_casa': "Flamengo", 'time_fora': "Palmeiras",
        'pos_casa': 1, 'pos_fora': 2,
        'jogos_casa': [], 'jogos_fora': [],
        'ovrall_casa': {}, 'ovrall_fora': {},
        'ic_casa': {}, 'ic_fora': {},
        'media_gols_casa': MEDIA_GOLS_CASA_LIGA, 'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
        'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
        'media_esc_casa': 5.0, 'media_esc_fora': 4.5,
        'prateleiras_extra': {}
    }
    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

    st.title("MyPredict 2.0 – Modo Manual")
    entrada = st.radio("Método de entrada", ["Preenchimento Manual", "Colar resposta da IA"])

    if entrada == "Colar resposta da IA":
        st.subheader("📥 Cole aqui a resposta completa da IA")
        texto = st.text_area("Resposta da IA", height=300, key="ia_text")
        if st.button("Processar dados"):
            if not texto.strip():
                st.error("Por favor, cole a resposta da IA.")
            else:
                # Tenta JSON primeiro
                try:
                    dados = json.loads(texto)
                    for chave, valor in dados.items():
                        st.session_state[chave] = valor
                    # Converte mandante para bool nos jogos
                    for j in st.session_state.jogos_casa:
                        j['mandante'] = bool(j['mandante'])
                    for j in st.session_state.jogos_fora:
                        j['mandante'] = bool(j['mandante'])
                    st.success("JSON carregado com sucesso!")
                    st.rerun()
                except json.JSONDecodeError:
                    pass

                # Se não é JSON, faz o parsing de texto
                jogos_casa = []; jogos_fora = []
                ovrall_casa = {}; ovrall_fora = {}
                ic_casa = {}; ic_fora = {}
                medias = {
                    'media_gols_casa': MEDIA_GOLS_CASA_LIGA, 'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
                    'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
                    'media_esc_casa': 5.0, 'media_esc_fora': 4.5
                }
                prateleiras = {}
                time_casa = "Flamengo"; time_fora = "Palmeiras"
                pos_casa = 1; pos_fora = 2

                blocos = texto.strip().split('\n\n')
                for bloco in blocos:
                    linhas = bloco.strip().split('\n')
                    if not linhas: continue
                    primeira = linhas[0].strip()
                    if primeira.startswith('Time da casa:'): time_casa = primeira.split(':',1)[1].strip()
                    elif primeira.startswith('Time da fora:'): time_fora = primeira.split(':',1)[1].strip()
                    elif 'Posições:' in primeira:
                        for l in linhas[1:]:
                            if l.startswith('Casa:'):
                                try: pos_casa = int(l.split(':')[1].strip())
                                except: pass
                            elif l.startswith('Fora:'):
                                try: pos_fora = int(l.split(':')[1].strip())
                                except: pass
                    elif 'Últimos 10 jogos do time da casa' in primeira:
                        jogos_casa = extrair_jogos('\n'.join(linhas[1:]))
                    elif 'Últimos 10 jogos do time da fora' in primeira:
                        jogos_fora = extrair_jogos('\n'.join(linhas[1:]))
                    elif 'Métricas OVRall do time da casa' in primeira:
                        chaves = ["gols_media","gols_sofridos_media","xg_media","xga_media",
                                  "finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media",
                                  "chutes_media","desarmes_intercep_media","posse_media",
                                  "passes_certos_pct","passes_chave_media","assistencias_media",
                                  "conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro",
                                  "desvio_gols_sofridos","pontos_pos_desvantagem_media",
                                  "gols_ultimos_15min_media","pontos_apos_derrota_media",
                                  "diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
                        vals = [para_float(x) for x in linhas[-1].split(',')]
                        if len(vals) == 23: ovrall_casa = {chaves[i]: vals[i] for i in range(23)}
                    elif 'Métricas OVRall do time da fora' in primeira:
                        chaves = ["gols_media","gols_sofridos_media","xg_media","xga_media",
                                  "finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media",
                                  "chutes_media","desarmes_intercep_media","posse_media",
                                  "passes_certos_pct","passes_chave_media","assistencias_media",
                                  "conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro",
                                  "desvio_gols_sofridos","pontos_pos_desvantagem_media",
                                  "gols_ultimos_15min_media","pontos_apos_derrota_media",
                                  "diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
                        vals = [para_float(x) for x in linhas[-1].split(',')]
                        if len(vals) == 23: ovrall_fora = {chaves[i]: vals[i] for i in range(23)}
                    elif 'Métricas IC do time da casa' in primeira:
                        chaves = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
                        vals = [para_float(x) for x in linhas[-1].split(',')]
                        if len(vals) == 5: ic_casa = {chaves[i]: vals[i] for i in range(5)}
                    elif 'Métricas IC do time da fora' in primeira:
                        chaves = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
                        vals = [para_float(x) for x in linhas[-1].split(',')]
                        if len(vals) == 5: ic_fora = {chaves[i]: vals[i] for i in range(5)}
                    elif 'Médias da Liga' in primeira:
                        for l in linhas[1:]:
                            if 'casa:' in l: medias['media_gols_casa'] = para_float(l.split(':')[1])
                            elif 'fora:' in l: medias['media_gols_fora'] = para_float(l.split(':')[1])
                            elif '1º tempo casa:' in l: medias['media_ht_casa'] = para_float(l.split(':')[1])
                            elif '1º tempo fora:' in l: medias['media_ht_fora'] = para_float(l.split(':')[1])
                            elif 'escanteios casa:' in l: medias['media_esc_casa'] = para_float(l.split(':')[1])
                            elif 'escanteios fora:' in l: medias['media_esc_fora'] = para_float(l.split(':')[1])
                    elif 'Prateleiras' in primeira:
                        for l in linhas[1:]:
                            if ':' in l:
                                adv, prat = l.split(':',1)
                                prateleiras[adv.strip()] = prat.strip()

                if len(jogos_casa) < 10 or len(jogos_fora) < 10:
                    todos_jogos = extrair_jogos(texto)
                    if len(todos_jogos) >= 20:
                        jogos_casa = todos_jogos[:10]
                        jogos_fora = todos_jogos[10:20]

                st.session_state.time_casa = time_casa
                st.session_state.time_fora = time_fora
                st.session_state.pos_casa = pos_casa
                st.session_state.pos_fora = pos_fora
                st.session_state.jogos_casa = jogos_casa
                st.session_state.jogos_fora = jogos_fora
                st.session_state.ovrall_casa = ovrall_casa
                st.session_state.ovrall_fora = ovrall_fora
                st.session_state.ic_casa = ic_casa
                st.session_state.ic_fora = ic_fora
                for k, v in medias.items():
                    st.session_state[k] = v
                st.session_state.prateleiras_extra = prateleiras

                if len(jogos_casa) >= 10 and len(jogos_fora) >= 10 and ovrall_casa and ovrall_fora:
                    st.success("Dados processados com sucesso!")
                else:
                    st.warning(f"Extração parcial: {len(jogos_casa)} jogos casa, {len(jogos_fora)} jogos fora, "
                               f"OVRall casa: {'OK' if ovrall_casa else 'Faltando'}, OVRall fora: {'OK' if ovrall_fora else 'Faltando'}.")
                st.rerun()

        if st.session_state.get('jogos_casa') and st.session_state.get('jogos_fora'):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="time-box time-casa"><h3 style="color:#ffd700;">🏠 {st.session_state.time_casa}</h3>', unsafe_allow_html=True)
                st.write(f"**Posição:** {st.session_state.pos_casa}")
                for j in st.session_state.jogos_casa[:10]:
                    st.write(f"{j['resultado']} x {j['adversario']} {'(C)' if j['mandante'] else '(F)'}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="time-box time-fora"><h3 style="color:#c0c0c0;">🏟️ {st.session_state.time_fora}</h3>', unsafe_allow_html=True)
                st.write(f"**Posição:** {st.session_state.pos_fora}")
                for j in st.session_state.jogos_fora[:10]:
                    st.write(f"{j['resultado']} x {j['adversario']} {'(C)' if j['mandante'] else '(F)'}")
                st.markdown('</div>', unsafe_allow_html=True)

    else:
        # MODO MANUAL (preenchimento campo a campo)
        c1, c2 = st.columns(2)
        with c1: st.session_state.time_casa = st.text_input("Time da Casa", value=st.session_state.time_casa)
        with c2: st.session_state.time_fora = st.text_input("Time da Fora", value=st.session_state.time_fora)

        st.subheader("🏷 Projeção de Prateleiras")
        st.session_state.pos_casa = st.number_input("Posição do time da casa", 1, 20, st.session_state.pos_casa)
        st.session_state.pos_fora = st.number_input("Posição do time da fora", 1, 20, st.session_state.pos_fora)

        st.subheader("📊 IMA – Últimos 10 jogos")
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            txt_casa = st.text_area("Time da casa", height=200, key="jogos_casa_manual")
        with col_j2:
            txt_fora = st.text_area("Time da fora", height=200, key="jogos_fora_manual")

        def parse_jogos(texto):
            jogos = []
            for linha in texto.strip().split('\n'):
                partes = [p.strip() for p in linha.split(',')]
                if len(partes) == 3 and partes[0] in ('V','E','D') and partes[2].upper() in ('S','N'):
                    jogos.append({"resultado": partes[0], "adversario": partes[1], "mandante": partes[2].upper() == 'S'})
            return jogos

        st.session_state.jogos_casa = parse_jogos(txt_casa)
        st.session_state.jogos_fora = parse_jogos(txt_fora)

        st.subheader("📈 OVRall – Métricas da Temporada")
        def metrica(label, key_casa, key_fora):
            c1, c2 = st.columns(2)
            vc = para_float(c1.text_input(label, key=f"{key_casa}_val"))
            vf = para_float(c2.text_input(label, key=f"{key_fora}_val"))
            return vc, vf

        ovrall_casa = {}
        ovrall_fora = {}
        for label, key in [
            ("Gols marcados (média)", "gols_media"),
            ("Gols sofridos (média)", "gols_sofridos_media"),
            ("xG (média)", "xg_media"),
            ("xGA (média)", "xga_media"),
            ("Finalizações no alvo (média)", "finalizacoes_alvo_media"),
            ("Finalizações no alvo sofridas (média)", "finalizacoes_alvo_sofridas_media"),
            ("Chutes totais (média)", "chutes_media"),
            ("Desarmes + Interceptações (média)", "desarmes_intercep_media"),
            ("Posse de bola (%)", "posse_media"),
            ("Passes certos (%)", "passes_certos_pct"),
            ("Passes-chave (média)", "passes_chave_media"),
            ("Assistências (média)", "assistencias_media"),
            ("Conversão de finalizações (%)", "conversao"),
            ("Jogos sem sofrer gols (%)", "clean_sheets_pct"),
            ("Desvio padrão dos pontos", "desvio_pontos"),
            ("Desvio padrão gols marcados", "desvio_gols_pro"),
            ("Desvio padrão gols sofridos", "desvio_gols_sofridos"),
            ("Pontos após sair atrás (média)", "pontos_pos_desvantagem_media"),
            ("Gols nos últimos 15 min (média)", "gols_ultimos_15min_media"),
            ("Pontos após derrota (média)", "pontos_apos_derrota_media"),
            ("Diferença aprovação casa-fora (%)", "diff_aprov_casa_fora"),
            ("Aproveitamento viradas a favor (%)", "aprov_viradas_favor"),
            ("Aproveitamento viradas contra (%)", "aprov_viradas_contra"),
        ]:
            vc, vf = metrica(label, f"casa_{key}", f"fora_{key}")
            ovrall_casa[key] = vc
            ovrall_fora[key] = vf
        st.session_state.ovrall_casa = ovrall_casa
        st.session_state.ovrall_fora = ovrall_fora

        st.subheader("🧠 IC – Fatores Contextuais")
        ic_casa = {}
        ic_fora = {}
        for label, key in [
            ("Confronto direto (%)", "confronto_direto"),
            ("Mesmo escalão (%)", "mesmo_escalao"),
            ("Contra escalão adversário (%)", "contra_escalao_adversario"),
            ("Fator casa (%)", "fator_casa"),
            ("Odd", "odds"),
        ]:
            vc, vf = metrica(label, f"ic_casa_{key}", f"ic_fora_{key}")
            ic_casa[key] = vc
            ic_fora[key] = vf
        st.session_state.ic_casa = ic_casa
        st.session_state.ic_fora = ic_fora

        st.subheader("📊 Médias da Liga")
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.media_gols_casa = st.number_input("Média gols casa", value=st.session_state.media_gols_casa)
            st.session_state.media_ht_casa = st.number_input("Média gols HT casa", value=st.session_state.media_ht_casa)
            st.session_state.media_esc_casa = st.number_input("Média escanteios casa", value=st.session_state.media_esc_casa)
        with c2:
            st.session_state.media_gols_fora = st.number_input("Média gols fora", value=st.session_state.media_gols_fora)
            st.session_state.media_ht_fora = st.number_input("Média gols HT fora", value=st.session_state.media_ht_fora)
            st.session_state.media_esc_fora = st.number_input("Média escanteios fora", value=st.session_state.media_esc_fora)

    # ---------- CÁLCULO (comum a ambos os submodos manuais) ----------
    if st.button("Calcular MyPredict Manual"):
        if len(st.session_state.jogos_casa) < 10 or len(st.session_state.jogos_fora) < 10:
            st.error(f"Foram encontrados {len(st.session_state.jogos_casa)} jogos para o time da casa e {len(st.session_state.jogos_fora)} para o time da fora. São necessários 10 de cada.")
            st.stop()
        if not st.session_state.ovrall_casa or not st.session_state.ovrall_fora:
            st.error("Métricas OVRall não encontradas.")
            st.stop()

        prat_casa = obter_prateleira(st.session_state.pos_casa)
        prat_fora = obter_prateleira(st.session_state.pos_fora)
        prateleiras = {st.session_state.time_casa: prat_casa, st.session_state.time_fora: prat_fora}
        for j in st.session_state.jogos_casa + st.session_state.jogos_fora:
            if j['adversario'] not in prateleiras:
                prateleiras[j['adversario']] = "Media"
        for adv, prat in st.session_state.prateleiras_extra.items():
            if adv in prateleiras:
                prateleiras[adv] = prat

        rec_casa = {
            '10G': st.session_state.jogos_casa[:10], '5G': st.session_state.jogos_casa[:5], '3G': st.session_state.jogos_casa[:3],
            '5CF': [j for j in st.session_state.jogos_casa if j['mandante']][:5],
            '3CF': [j for j in st.session_state.jogos_casa if j['mandante']][:3],
        }
        rec_fora = {
            '10G': st.session_state.jogos_fora[:10], '5G': st.session_state.jogos_fora[:5], '3G': st.session_state.jogos_fora[:3],
            '5CF': [j for j in st.session_state.jogos_fora if j['mandante']][:5],
            '3CF': [j for j in st.session_state.jogos_fora if j['mandante']][:3],
        }

        ima_casa = calcular_ima(st.session_state.time_casa,
                                rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                                rec_casa['5CF'], rec_casa['3CF'], prateleiras)
        ima_fora = calcular_ima(st.session_state.time_fora,
                                rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                                rec_fora['5CF'], rec_fora['3CF'], prateleiras)

        dados_liga = {k: [st.session_state.ovrall_casa.get(k, 0) or 0, st.session_state.ovrall_fora.get(k, 0) or 0] for k in set(st.session_state.ovrall_casa) | set(st.session_state.ovrall_fora)}
        ovrall_val_casa = calcular_ovrall(st.session_state.ovrall_casa, dados_liga)
        ovrall_val_fora = calcular_ovrall(st.session_state.ovrall_fora, dados_liga)

        ic_val_casa = calcular_ic(st.session_state.ic_casa)
        ic_val_fora = calcular_ic(st.session_state.ic_fora)

        mpv_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
        mpv_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

        bonus_casa = calcular_bonus_casa(st.session_state.ovrall_casa.get('diff_aprov_casa_fora') or 0)
        p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

        over25 = prob_over_2_5(
            st.session_state.ovrall_casa.get('gols_media'), st.session_state.ovrall_fora.get('gols_media'),
            st.session_state.ovrall_casa.get('gols_sofridos_media'), st.session_state.ovrall_fora.get('gols_sofridos_media'),
            media_casa=st.session_state.media_gols_casa, media_fora=st.session_state.media_gols_fora
        )

        gols_esp_casa = _gols_esperados(st.session_state.ovrall_casa.get('gols_media'),
                                        st.session_state.ovrall_fora.get('gols_sofridos_media'),
                                        st.session_state.media_gols_casa)
        gols_esp_fora = _gols_esperados(st.session_state.ovrall_fora.get('gols_media'),
                                        st.session_state.ovrall_casa.get('gols_sofridos_media'),
                                        st.session_state.media_gols_fora)
        btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)

        gol_ht = prob_gol_ht(
            st.session_state.ovrall_casa.get('gols_ht_media', 0.5) or 0.5,
            st.session_state.ovrall_fora.get('gols_ht_media', 0.5) or 0.5,
            st.session_state.ovrall_casa.get('gols_ht_sofridos_media', 0.5) or 0.5,
            st.session_state.ovrall_fora.get('gols_ht_sofridos_media', 0.5) or 0.5,
            media_ht_casa=st.session_state.media_ht_casa, media_ht_fora=st.session_state.media_ht_fora
        )

        esc = prob_over_escanteios(
            st.session_state.ovrall_casa.get('escanteios_media', 5.0) or 5.0,
            st.session_state.ovrall_fora.get('escanteios_media', 5.0) or 5.0,
            st.session_state.ovrall_casa.get('escanteios_sofridos_media', 5.0) or 5.0,
            st.session_state.ovrall_fora.get('escanteios_sofridos_media', 5.0) or 5.0,
            media_casa=st.session_state.media_esc_casa, media_fora=st.session_state.media_esc_fora
        )

        st.subheader("📊 Resultados")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitória Casa", f"{p1:.1%}")
        with col2:
            st.metric("Empate", f"{pX:.1%}")
        with col3:
            st.metric("Vitória Fora", f"{p2:.1%}")

        st.markdown("---")
        col4, col5 = st.columns(2)
        with col4:
            st.metric("Over 2.5 gols", f"{over25:.1%}" if over25 else "N/D")
        with col5:
            st.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")

        st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")
        st.metric("Over Escanteios", f"{esc:.1%}" if esc else "N/D")

        with st.expander("📊 Métricas detalhadas"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{st.session_state.time_casa}**")
                st.write(f"IMA: {ima_casa:.1f}")
                st.write(f"OVRall: {ovrall_val_casa:.1f}")
                st.write(f"IC: {ic_val_casa:.1f}")
                st.write(f"MPV: {mpv_casa:.1f}")
            with c2:
                st.markdown(f"**{st.session_state.time_fora}**")
                st.write(f"IMA: {ima_fora:.1f}")
                st.write(f"OVRall: {ovrall_val_fora:.1f}")
                st.write(f"IC: {ic_val_fora:.1f}")
                st.write(f"MPV: {mpv_fora:.1f}")
