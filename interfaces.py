# interfaces.py — MyPredict 2.0 (processamento direto na interface)
import streamlit as st
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from manual import processar_texto_ia

def para_float(valor_str):
    if valor_str is None or valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        return None

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

def tela_automatico(lista_ligas, temporadas, times_carregados, uso_api, limite_api, msg_erro, resultados):
    st.set_page_config(page_title="MyPredict 2.0", layout="wide")
    injetar_css()

    if uso_api is not None:
        porcentagem = uso_api / limite_api if limite_api else 0
        if porcentagem < 0.5: cor = "#00ff7f"
        elif porcentagem < 0.8: cor = "#ffaa00"
        else: cor = "#ff4d4d"
        st.markdown(f"""
        <div style="display: flex; justify-content: center;">
            <div class="usage-badge">
                <span class="usage-dot" style="background-color: {cor};"></span>
                API: {uso_api}/{limite_api} requisições restantes hoje
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='main-title'>⚽ MyPredict 2.0</div>", unsafe_allow_html=True)
    st.markdown("<div class='quote'>“O futebol é a única coisa que me emociona mais do que a ciência.”<br>— Albert Einstein (adaptado)</div>", unsafe_allow_html=True)

    if msg_erro:
        st.error(msg_erro)

    col_liga, col_temp = st.columns([2, 1])
    with col_liga:
        liga_nome = st.selectbox("Selecione a liga", lista_ligas or [], key="sel_liga")
    with col_temp:
        if liga_nome and liga_nome in temporadas:
            temps = temporadas[liga_nome]
            if not temps:
                st.warning("Nenhuma temporada disponível")
                temporada = st.number_input("Temporada", value=2024)
            else:
                temporada = st.selectbox("Temporada", temps, key="sel_temp")
        else:
            temporada = st.number_input("Temporada", value=2024)

    chave_times = f"{liga_nome}_{temporada}"
    if chave_times not in times_carregados:
        buscar = st.button("🔍 Buscar Times", use_container_width=True)
    else:
        st.info("Times carregados do cache.")
        buscar = False

    lista_times = times_carregados.get(chave_times, [])
    col1, col2 = st.columns(2)
    with col1:
        if lista_times: time_casa = st.selectbox("Time da casa", lista_times)
        else: time_casa = st.text_input("Time da casa", value="Arsenal")
    with col2:
        if lista_times: time_fora = st.selectbox("Time de fora", lista_times, index=min(1, len(lista_times)-1))
        else: time_fora = st.text_input("Time de fora", value="Manchester United")

    gerar = st.button("⚡ Gerar MyPredict", use_container_width=True)

    if resultados:
        st.markdown(f"<h2 style='text-align: center; color: #ffd700;'>{resultados['time_casa']} x {resultados['time_fora']}</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitória Casa", f"{resultados['p1']:.1%}")
            if resultados.get('rec_p1'): st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
        with col2:
            st.metric("Empate", f"{resultados['pX']:.1%}")
        with col3:
            st.metric("Vitória Fora", f"{resultados['p2']:.1%}")
            if resultados.get('rec_p2'): st.markdown('<div class="selo-ouro">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)

        st.markdown("---")
        col4, col5 = st.columns(2)
        with col4:
            st.metric("Over 2.5 gols", f"{resultados['over25']:.1%}" if resultados['over25'] else "N/D")
            st.metric("Gol no 1º tempo", f"{resultados['gol_ht']:.1%}" if resultados['gol_ht'] else "N/D")
        with col5:
            st.metric("Ambas Marcam", f"{resultados['btts']:.1%}" if resultados['btts'] else "N/D")
            st.metric("Over Escanteios", f"{resultados['esc']:.1%}" if resultados['esc'] else "N/D")

        with st.expander("📊 Métricas detalhadas"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{resultados['time_casa']}**")
                st.write(f"IMA: {resultados['ima_casa']:.1f}")
                st.write(f"MPV: {resultados['mpv_casa']:.1f}")
            with c2:
                st.markdown(f"**{resultados['time_fora']}**")
                st.write(f"IMA: {resultados['ima_fora']:.1f}")
                st.write(f"MPV: {resultados['mpv_fora']:.1f}")

    return liga_nome, temporada, time_casa, time_fora, buscar, gerar, chave_times

def tela_manual(dados_state):
    st.set_page_config(page_title="MyPredict 2.0 – Manual", layout="centered")
    injetar_css()
    st.title("MyPredict 2.0 – Modo Manual")

    entrada = st.radio("Método de entrada", ["Preenchimento Manual", "Colar resposta da IA"], key="modo_manual")

    if entrada == "Colar resposta da IA":
        st.subheader("📥 Cole aqui a resposta completa da IA")
        texto = st.text_area("Resposta da IA", height=300, key="widget_ia")
        processar = st.button("Processar dados")
        if processar:
            if texto.strip():
                dados = processar_texto_ia(texto)
                for chave, valor in dados.items():
                    st.session_state[chave] = valor
                st.success("Dados processados! Agora clique em 'Calcular MyPredict Manual'.")
            else:
                st.error("Por favor, cole a resposta da IA.")

        if dados_state.get('jogos_casa') and dados_state.get('jogos_fora'):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="time-box time-casa"><h3 style="color:#ffd700;">🏠 {dados_state["time_casa"]}</h3>', unsafe_allow_html=True)
                st.write(f"**Posição:** {dados_state['pos_casa']}")
                for j in dados_state['jogos_casa'][:10]:
                    st.write(f"{j['resultado']} x {j['adversario']} {'(C)' if j['mandante'] else '(F)'}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="time-box time-fora"><h3 style="color:#c0c0c0;">🏟️ {dados_state["time_fora"]}</h3>', unsafe_allow_html=True)
                st.write(f"**Posição:** {dados_state['pos_fora']}")
                for j in dados_state['jogos_fora'][:10]:
                    st.write(f"{j['resultado']} x {j['adversario']} {'(C)' if j['mandante'] else '(F)'}")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        c1, c2 = st.columns(2)
        with c1: st.text_input("Time da Casa", value=dados_state.get('time_casa', 'Flamengo'), key="time_casa")
        with c2: st.text_input("Time da Fora", value=dados_state.get('time_fora', 'Palmeiras'), key="time_fora")

        st.subheader("🏷 Projeção de Prateleiras")
        st.number_input("Posição do time da casa", 1, 20, value=dados_state.get('pos_casa', 1), key="pos_casa")
        st.number_input("Posição do time da fora", 1, 20, value=dados_state.get('pos_fora', 2), key="pos_fora")

        st.subheader("📊 IMA – Últimos 10 jogos")
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            st.text_area("Time da casa", height=200, key="jogos_casa_manual")
        with col_j2:
            st.text_area("Time da fora", height=200, key="jogos_fora_manual")

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
            st.number_input("Média gols casa", value=dados_state.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA), key="media_gols_casa")
            st.number_input("Média gols HT casa", value=dados_state.get('media_ht_casa', 0.75), key="media_ht_casa")
            st.number_input("Média escanteios casa", value=dados_state.get('media_esc_casa', 5.0), key="media_esc_casa")
        with c2:
            st.number_input("Média gols fora", value=dados_state.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA), key="media_gols_fora")
            st.number_input("Média gols HT fora", value=dados_state.get('media_ht_fora', 0.65), key="media_ht_fora")
            st.number_input("Média escanteios fora", value=dados_state.get('media_esc_fora', 4.5), key="media_esc_fora")

    calcular = st.button("Calcular MyPredict Manual")
    return entrada, calcular
