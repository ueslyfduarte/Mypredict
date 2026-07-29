# interfaces.py — MyPredict 2.0 (com MP Value destacado e detalhamento completo)
import streamlit as st
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from manual import executar_manual
from utils import para_float
from data_source_api_football import get_api_usage
from automatico import inicializar_estado, carregar_ligas, buscar_temporadas, buscar_times, executar_automatico

# Constantes do projeto para exibição educativa (não afetam o cálculo)
PRATELEIRAS_EX = {'Elite': (1,3), 'Alta': (4,7), 'Media': (8,13), 'Baixa': (14,16), 'Critica': (17,99)}
PESOS_RECORTES_EX = {'10G': 0.10, '5G': 0.15, '3G': 0.20, '5CF': 0.25, '3CF': 0.30}
PESOS_OVRALL_EX = {'Ataque': 0.25, 'Defesa': 0.25, 'MeioCampo': 0.20, 'Consistencia': 0.15, 'Resiliencia': 0.15}
PESOS_IC_EX = {'confronto_direto': 0.25, 'mesmo_escalao': 0.20, 'contra_escalao_adversario': 0.20, 'fator_casa': 0.20, 'odds': 0.15}

def injetar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: radial-gradient(ellipse at 50% 0%, #1a1a2e 0%, #0e1117 50%, #000000 100%); background-attachment: fixed; }

        .main-title { font-size: 2.8rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #ffd700, #ffaa00, #ffd700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.2rem; }
        .subtitle { text-align: center; color: #b0b0b0; font-size: 0.9rem; margin-bottom: 1.5rem; letter-spacing: 2px; }
        .gold-highlight { font-size: 2rem; font-weight: 900; background: linear-gradient(135deg, #ffd700, #ffaa00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: block; text-align: center; margin-bottom: 12px; }

        .divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(255,215,0,0.2), transparent); margin: 24px 0; }

        .stButton > button {
            background: linear-gradient(135deg, #ffd700, #ff8c00); color: #000; border: none;
            font-weight: 700; font-size: 1rem; border-radius: 12px; padding: 12px 24px;
            letter-spacing: 1px; box-shadow: 0 4px 15px rgba(255,215,0,0.3);
        }
        .stButton > button:hover { transform: scale(1.02); box-shadow: 0 8px 25px rgba(255,215,0,0.5); }

        /* Times */
        .team-block {
            border-radius: 16px; padding: 18px 14px; margin-bottom: 20px;
        }
        .team-block.home { background: linear-gradient(145deg, rgba(255,215,0,0.08), rgba(255,215,0,0.02)); border: 1px solid rgba(255,215,0,0.3); }
        .team-block.away { background: linear-gradient(145deg, rgba(192,192,192,0.08), rgba(192,192,192,0.02)); border: 1px solid rgba(192,192,192,0.3); }
        .team-title { font-size: 1.4rem; font-weight: 800; text-align: center; margin-bottom: 16px; }
        .team-title.home-title { color: #ffd700; }
        .team-title.away-title { color: #c0c0c0; }

        .section-title {
            font-size: 1.6rem; font-weight: 800; text-align: center;
            background: linear-gradient(135deg, #ffd700, #ffaa00);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin: 32px 0 16px 0;
        }
        .dimension-title { font-size: 1.1rem; font-weight: 700; color: #ffd700; margin: 12px 0 8px 0; padding-left: 8px; border-left: 3px solid #ffd700; }

        /* MP Value Hero */
        .mpv-hero {
            background: radial-gradient(circle at 50% 0%, rgba(255,215,0,0.18) 0%, transparent 75%);
            border: 2px solid #ffd700;
            border-radius: 32px;
            padding: 28px 16px;
            text-align: center;
            margin: 24px 0;
            animation: heroGlow 2s ease-in-out infinite alternate;
        }
        @keyframes heroGlow {
            from { box-shadow: 0 0 25px rgba(255,215,0,0.25); }
            to { box-shadow: 0 0 50px rgba(255,215,0,0.6), 0 0 100px rgba(255,140,0,0.3); }
        }
        .mpv-crown { font-size: 3rem; margin-bottom: 8px; }
        .mpv-main-values { display: flex; justify-content: center; align-items: center; gap: 24px; }
        .mpv-value { font-size: 5rem; font-weight: 900; line-height: 1; }
        .mpv-value.home-value { background: linear-gradient(180deg, #ffd700 0%, #ff8c00 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .mpv-value.away-value { background: linear-gradient(180deg, #c0c0c0 0%, #a0a0a0 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .mpv-vs { font-size: 1.8rem; color: #888; font-weight: 700; }
        .mpv-bar {
            height: 8px; background: #333; border-radius: 4px; margin: 16px 0 8px; overflow: hidden;
            display: flex;
        }
        .mpv-bar-fill { height: 100%; background: linear-gradient(90deg, #ffd700, #ff8c00); }
        .mpv-bar-fill.away { background: linear-gradient(90deg, #c0c0c0, #a0a0a0); }

        /* Cartões de composição */
        .comp-card {
            background: rgba(20,20,35,0.9); border-radius: 16px; padding: 16px;
            border: 1px solid rgba(255,215,0,0.25); text-align: center;
        }
        .comp-card h4 { color: #ffd700; margin-bottom: 8px; }
        .comp-card .big { font-size: 2rem; font-weight: 900; }
        .comp-card .small { font-size: 0.8rem; color: #aaa; }

        /* Tabelas de detalhe */
        .detail-table { width: 100%; border-collapse: collapse; margin: 12px 0; }
        .detail-table th { color: #ffd700; font-weight: 600; padding: 8px; border-bottom: 1px solid #333; text-align: left; }
        .detail-table td { padding: 8px; border-bottom: 1px solid #222; color: #ddd; }
    </style>
    """, unsafe_allow_html=True)

# ---------- TELA AUTOMÁTICA (mantida) ----------
def tela_automatico(lista_ligas, temporadas, times_carregados, uso_api, limite_api, msg_erro, resultados):
    st.set_page_config(page_title="MyPredict 2.0", layout="wide", page_icon="⚽")
    injetar_css()
    if uso_api is not None:
        porcentagem = uso_api / limite_api if limite_api else 0
        cor = "#00ff7f" if porcentagem < 0.5 else ("#ffaa00" if porcentagem < 0.8 else "#ff4d4d")
        st.markdown(f'<div style="display:flex;justify-content:center;"><div class="rec-card" style="display:inline-flex;align-items:center;gap:8px;padding:6px 16px;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{cor};"></span> API: {uso_api}/{limite_api}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">"O futebol não é uma questão de vida ou morte. É muito mais importante que isso." — Bill Shankly</div>', unsafe_allow_html=True)
    if msg_erro: st.error(msg_erro)
    col_liga, col_temp = st.columns([2,1])
    with col_liga: liga_nome = st.selectbox("Liga", lista_ligas or [], key="sel_liga")
    with col_temp:
        if liga_nome and liga_nome in temporadas:
            temps = temporadas[liga_nome]
            temporada = st.selectbox("Temporada", temps, key="sel_temp") if temps else st.number_input("Temporada", value=2024)
        else: temporada = st.number_input("Temporada", value=2024)
    chave = f"{liga_nome}_{temporada}"
    buscar = st.button("🔍 Buscar Times", use_container_width=True) if chave not in times_carregados else False
    if chave in times_carregados: st.info("Times carregados.")
    lista_times = times_carregados.get(chave, [])
    c1,c2 = st.columns(2)
    with c1: time_casa = st.selectbox("Casa", lista_times) if lista_times else st.text_input("Time da casa", value="")
    with c2: time_fora = st.selectbox("Fora", lista_times, index=min(1,len(lista_times)-1)) if lista_times else st.text_input("Time de fora", value="")
    gerar = st.button("⚡ Gerar MyPredict", use_container_width=True)
    if resultados:
        st.markdown(f'<div class="scoreboard"><span class="score-home">{resultados["time_casa"]}</span><span class="score-vs">vs</span><span class="score-away">{resultados["time_fora"]}</span></div>', unsafe_allow_html=True)
        c1,c2,c3=st.columns(3)
        c1.metric("🏠 Casa",f"{resultados['p1']:.1%}"); c2.metric("🤝 Empate",f"{resultados['pX']:.1%}"); c3.metric("🏟️ Fora",f"{resultados['p2']:.1%}")
        if resultados.get('rec_p1'): st.markdown('<div class="value-seal">VALUE</div>', unsafe_allow_html=True)
        if resultados.get('rec_p2'): st.markdown('<div class="value-seal">VALUE</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        c4,c5=st.columns(2)
        c4.metric("Over 2.5 Gols",f"{resultados['over25']:.1%}" if resultados['over25'] else "N/D")
        c5.metric("Ambas Marcam",f"{resultados['btts']:.1%}" if resultados['btts'] else "N/D")
        st.metric("⚡ Gol 1º Tempo",f"{resultados['gol_ht']:.1%}" if resultados['gol_ht'] else "N/D")
        st.metric("🏳️ Escanteios",f"{resultados['esc']:.1%}" if resultados['esc'] else "N/D")
    return liga_nome, temporada, time_casa, time_fora, buscar, gerar, chave

# ---------- NOVA TELA MANUAL COM MP VALUE DESTACADO ----------
def tela_manual():
    st.set_page_config(page_title="MyPredict 2.0 – Manual", layout="centered", page_icon="⚽")
    injetar_css()

    for chave, padrao in {
        'time_casa':'','time_fora':'','pos_casa':1,'pos_fora':2,
        'jogos_casa':[],'jogos_fora':[],'ovrall_casa':{},'ovrall_fora':{},
        'ic_casa':{},'ic_fora':{},'media_gols_casa':MEDIA_GOLS_CASA_LIGA,
        'media_gols_fora':MEDIA_GOLS_FORA_LIGA,'media_ht_casa':0.75,'media_ht_fora':0.65,
        'media_esc_casa':5.0,'media_esc_fora':4.5,'prateleiras_extra':{}
    }.items():
        if chave not in st.session_state: st.session_state[chave] = padrao

    st.markdown('<div class="main-title">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">ANÁLISE PREDITIVA PREMIUM</div>', unsafe_allow_html=True)

    # --- Times ---
    st.markdown('<div class="section-title">⚔️ TIMES</div>', unsafe_allow_html=True)
    col_casa, col_fora = st.columns(2)
    with col_casa:
        st.markdown('<div class="team-block home">', unsafe_allow_html=True)
        st.markdown('<div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        st.text_input("Nome do time", key="time_casa_input", value=st.session_state.time_casa, placeholder="Time da casa")
        st.number_input("Posição", 1, 20, key="pos_casa_input", value=st.session_state.pos_casa)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora:
        st.markdown('<div class="team-block away">', unsafe_allow_html=True)
        st.markdown('<div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        st.text_input("Nome do time", key="time_fora_input", value=st.session_state.time_fora, placeholder="Time de fora")
        st.number_input("Posição", 1, 20, key="pos_fora_input", value=st.session_state.pos_fora)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- IMA (últimos 10 jogos) ---
    st.markdown('<div class="section-title">📊 IMA · ÚLTIMOS 10 JOGOS</div>', unsafe_allow_html=True)
    st.markdown('<span class="gold-highlight">IMA</span>', unsafe_allow_html=True)

    jogos_casa_temp = st.session_state.jogos_casa[:10] if st.session_state.jogos_casa else [{"resultado":"","adversario":"","mandante":False} for _ in range(10)]
    jogos_fora_temp = st.session_state.jogos_fora[:10] if st.session_state.jogos_fora else [{"resultado":"","adversario":"","mandante":False} for _ in range(10)]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="team-block home">', unsafe_allow_html=True)
        st.markdown('<div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        for i in range(10):
            cols = st.columns([0.6, 2, 0.6])
            with cols[0]:
                res = st.selectbox("", ["", "V", "E", "D"], key=f"casa_res_{i}", label_visibility="collapsed",
                                   index=["", "V", "E", "D"].index(jogos_casa_temp[i]['resultado']) if jogos_casa_temp[i]['resultado'] in ["V","E","D"] else 0)
            with cols[1]:
                adv = st.text_input("", key=f"casa_adv_{i}", value=jogos_casa_temp[i]['adversario'], placeholder=f"Adversário {i+1}", label_visibility="collapsed")
            with cols[2]:
                mand = st.checkbox("Mandante", key=f"casa_mand_{i}", value=jogos_casa_temp[i]['mandante'])
            if res and adv:
                jogos_casa_temp[i] = {"resultado": res, "adversario": adv, "mandante": mand}
            else:
                jogos_casa_temp[i] = {"resultado":"","adversario":"","mandante":False}
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="team-block away">', unsafe_allow_html=True)
        st.markdown('<div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        for i in range(10):
            cols = st.columns([0.6, 2, 0.6])
            with cols[0]:
                res = st.selectbox("", ["", "V", "E", "D"], key=f"fora_res_{i}", label_visibility="collapsed",
                                   index=["", "V", "E", "D"].index(jogos_fora_temp[i]['resultado']) if jogos_fora_temp[i]['resultado'] in ["V","E","D"] else 0)
            with cols[1]:
                adv = st.text_input("", key=f"fora_adv_{i}", value=jogos_fora_temp[i]['adversario'], placeholder=f"Adversário {i+1}", label_visibility="collapsed")
            with cols[2]:
                mand = st.checkbox("Mandante", key=f"fora_mand_{i}", value=jogos_fora_temp[i]['mandante'])
            if res and adv:
                jogos_fora_temp[i] = {"resultado": res, "adversario": adv, "mandante": mand}
            else:
                jogos_fora_temp[i] = {"resultado":"","adversario":"","mandante":False}
        st.markdown('</div>', unsafe_allow_html=True)

    # --- OVRall (agrupado por dimensões) ---
    st.markdown('<div class="section-title">📈 OVRALL · MÉTRICAS DA TEMPORADA</div>', unsafe_allow_html=True)
    st.markdown('<span class="gold-highlight">OVR</span>', unsafe_allow_html=True)
    st.caption("Preencha as métricas do time. A nota OVRall é calculada a partir de 5 dimensões ponderadas.")

    ovrall_casa, ovrall_fora = {}, {}
    dimensoes = {
        "⚔️ ATAQUE": [("Gols marcados (média)","gols_media"),("xG (média)","xg_media"),
                      ("Finalizações no alvo (média)","finalizacoes_alvo_media"),("Conversão (%)","conversao")],
        "🛡️ DEFESA": [("Gols sofridos (média)","gols_sofridos_media"),("xGA (média)","xga_media"),
                       ("Finalizações no alvo sofridas (média)","finalizacoes_alvo_sofridas_media"),
                       ("Desarmes + Interceptações (média)","desarmes_intercep_media")],
        "🧩 MEIO-CAMPO": [("Posse de bola (%)","posse_media"),("Passes certos (%)","passes_certos_pct"),
                         ("Passes-chave (média)","passes_chave_media"),("Assistências (média)","assistencias_media"),
                         ("Chutes totais (média)","chutes_media")],
        "📏 CONSISTÊNCIA": [("Desvio padrão pontos","desvio_pontos"),("Desvio padrão gols pró","desvio_gols_pro"),
                           ("Desvio padrão gols sofridos","desvio_gols_sofridos"),
                           ("Jogos sem sofrer gols (%)","clean_sheets_pct")],
        "🔄 RESILIÊNCIA": [("Pontos após sair atrás","pontos_pos_desvantagem_media"),
                          ("Gols nos últimos 15 min","gols_ultimos_15min_media"),
                          ("Pontos após derrota","pontos_apos_derrota_media"),
                          ("Dif. aprovação casa-fora (%)","diff_aprov_casa_fora"),
                          ("Viradas a favor (%)","aprov_viradas_favor"),
                          ("Viradas contra (%)","aprov_viradas_contra")],
        "⚡ MERCADOS (1ºT / ESCANTEIOS)": [("Gols 1º tempo (média)","gols_ht_media"),
                                          ("Gols sofridos 1º tempo (média)","gols_ht_sofridos_media"),
                                          ("Escanteios (média)","escanteios_media"),
                                          ("Escanteios sofridos (média)","escanteios_sofridos_media")]
    }
    col_casa_ovr, col_fora_ovr = st.columns(2)
    with col_casa_ovr:
        st.markdown('<div class="team-block home">', unsafe_allow_html=True)
        st.markdown('<div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        for nome_dim, indicadores in dimensoes.items():
            st.markdown(f'<div class="dimension-title">{nome_dim}</div>', unsafe_allow_html=True)
            for label, key in indicadores:
                val = st.text_input(label, key=f"casa_ovr_{key}", placeholder=label, label_visibility="visible")
                ovrall_casa[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora_ovr:
        st.markdown('<div class="team-block away">', unsafe_allow_html=True)
        st.markdown('<div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        for nome_dim, indicadores in dimensoes.items():
            st.markdown(f'<div class="dimension-title">{nome_dim}</div>', unsafe_allow_html=True)
            for label, key in indicadores:
                val = st.text_input(label, key=f"fora_ovr_{key}", placeholder=label, label_visibility="visible")
                ovrall_fora[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)

    # --- IC ---
    st.markdown('<div class="section-title">🧠 IC · ÍNDICE DE CONTEXTO</div>', unsafe_allow_html=True)
    st.markdown('<span class="gold-highlight">IC</span>', unsafe_allow_html=True)
    ic_casa, ic_fora = {}, {}
    metricas_ic = [
        ("Confronto direto (%)","confronto_direto"),
        ("Mesmo escalão (%)","mesmo_escalao"),
        ("Contra escalão adversário (%)","contra_escalao_adversario"),
        ("Fator casa (%)","fator_casa"),
        ("Odd","odds"),
    ]
    col_casa_ic, col_fora_ic = st.columns(2)
    with col_casa_ic:
        st.markdown('<div class="team-block home">', unsafe_allow_html=True)
        st.markdown('<div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        for label, key in metricas_ic:
            val = st.text_input(label, key=f"ic_casa_{key}", placeholder=label, label_visibility="visible")
            ic_casa[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora_ic:
        st.markdown('<div class="team-block away">', unsafe_allow_html=True)
        st.markdown('<div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        for label, key in metricas_ic:
            val = st.text_input(label, key=f"ic_fora_{key}", placeholder=label, label_visibility="visible")
            ic_fora[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Médias da Liga ---
    st.markdown('<div class="section-title">📊 MÉDIAS DA LIGA</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        mgc = st.number_input("Média gols casa", value=MEDIA_GOLS_CASA_LIGA, key="mgc")
        mhtc = st.number_input("Média gols HT casa", value=0.75, key="mhtc")
        mecc = st.number_input("Média escanteios casa", value=5.0, key="mecc")
    with c2:
        mgf = st.number_input("Média gols fora", value=MEDIA_GOLS_FORA_LIGA, key="mgf")
        mhtf = st.number_input("Média gols HT fora", value=0.65, key="mhtf")
        mecf = st.number_input("Média escanteios fora", value=4.5, key="mecf")

    # --- Botão GERAR ---
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    if st.button("🔥 GERAR MYPREDICT VALUE", use_container_width=True):
        st.session_state.jogos_casa = [j for j in jogos_casa_temp if j['resultado'] and j['adversario']]
        st.session_state.jogos_fora = [j for j in jogos_fora_temp if j['resultado'] and j['adversario']]
        st.session_state.time_casa = st.session_state.time_casa_input
        st.session_state.time_fora = st.session_state.time_fora_input
        st.session_state.pos_casa = st.session_state.pos_casa_input
        st.session_state.pos_fora = st.session_state.pos_fora_input
        st.session_state.ovrall_casa = ovrall_casa
        st.session_state.ovrall_fora = ovrall_fora
        st.session_state.ic_casa = ic_casa
        st.session_state.ic_fora = ic_fora
        st.session_state.media_gols_casa = mgc; st.session_state.media_gols_fora = mgf
        st.session_state.media_ht_casa = mhtc; st.session_state.media_ht_fora = mhtf
        st.session_state.media_esc_casa = mecc; st.session_state.media_esc_fora = mecf
        dados = {k:v for k,v in st.session_state.items() if k in [
            'time_casa','time_fora','pos_casa','pos_fora','jogos_casa','jogos_fora',
            'ovrall_casa','ovrall_fora','ic_casa','ic_fora','media_gols_casa','media_gols_fora',
            'media_ht_casa','media_ht_fora','media_esc_casa','media_esc_fora','prateleiras_extra']}
        res, err = executar_manual(dados)
        if err: st.error(err)
        else: st.session_state.resultados = res; st.rerun()

    # ---------- RESULTADOS (NOVA INTERFACE) ----------
    if 'resultados' in st.session_state:
        res = st.session_state.resultados
        st.markdown(f"""
        <div style="text-align:center; margin:20px 0;">
            <span style="font-size:2rem; font-weight:900; color:#ffd700;">{res['time_casa']}</span>
            <span style="font-size:1.5rem; color:#888; margin:0 12px;">vs</span>
            <span style="font-size:2rem; font-weight:900; color:#c0c0c0;">{res['time_fora']}</span>
        </div>
        """, unsafe_allow_html=True)

        # ----- MP VALUE HERO -----
        st.markdown('<div class="mpv-hero">', unsafe_allow_html=True)
        st.markdown('<div class="mpv-crown">👑</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:1.2rem; color:#ffd700; letter-spacing:3px; margin-bottom:8px;">MYPREDICT VALUE</div>', unsafe_allow_html=True)

        # Valores lado a lado
        st.markdown(f"""
        <div class="mpv-main-values">
            <span class="mpv-value home-value">{res['mpv_casa']:.1f}</span>
            <span class="mpv-vs">×</span>
            <span class="mpv-value away-value">{res['mpv_fora']:.1f}</span>
        </div>
        """, unsafe_allow_html=True)

        # Barra comparativa
        total = res['mpv_casa'] + res['mpv_fora']
        pct_casa = (res['mpv_casa'] / total * 100) if total > 0 else 50
        pct_fora = 100 - pct_casa
        st.markdown(f"""
        <div class="mpv-bar">
            <div class="mpv-bar-fill" style="width:{pct_casa}%;"></div>
            <div class="mpv-bar-fill away" style="width:{pct_fora}%;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#aaa;">
            <span>{res['time_casa']} {res['mpv_casa']:.1f}</span>
            <span>{res['time_fora']} {res['mpv_fora']:.1f}</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ----- COMPOSIÇÃO DO MPV (três pilares) -----
        st.markdown('<div class="section-title">🧱 COMPOSIÇÃO DO MP VALUE</div>', unsafe_allow_html=True)
        col_ima, col_ovr, col_ic = st.columns(3)
        with col_ima:
            st.markdown(f"""
            <div class="comp-card">
                <h4>⚡ IMA</h4>
                <div class="big" style="color:#ffd700;">{res['ima_casa']:.1f} <span style="font-size:0.8rem;">vs</span> {res['ima_fora']:.1f}</div>
                <div class="small">Peso: {PESOS_RECORTES_EX['10G']+PESOS_RECORTES_EX['5G']+PESOS_RECORTES_EX['3G']+PESOS_RECORTES_EX['5CF']+PESOS_RECORTES_EX['3CF']:.0%} (1/3)</div>
                <div class="small">Contribuição: Casa {res['ima_casa']/3:.2f} | Fora {res['ima_fora']/3:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_ovr:
            st.markdown(f"""
            <div class="comp-card">
                <h4>📈 OVRall</h4>
                <div class="big" style="color:#ffd700;">{res['ovrall_casa']:.1f} <span style="font-size:0.8rem;">vs</span> {res['ovrall_fora']:.1f}</div>
                <div class="small">Peso: 1/3</div>
                <div class="small">Contribuição: Casa {res['ovrall_casa']/3:.2f} | Fora {res['ovrall_fora']/3:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_ic:
            st.markdown(f"""
            <div class="comp-card">
                <h4>🧠 IC</h4>
                <div class="big" style="color:#ffd700;">{res['ic_casa']:.1f} <span style="font-size:0.8rem;">vs</span> {res['ic_fora']:.1f}</div>
                <div class="small">Peso: 1/3</div>
                <div class="small">Contribuição: Casa {res['ic_casa']/3:.2f} | Fora {res['ic_fora']/3:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

        # ----- DETALHAMENTO EXPANDÍVEL -----
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        with st.expander("🔍 COMO O MP VALUE É CALCULADO?", expanded=False):
            st.markdown("**MP Value = (IMA × 1/3) + (OVRall × 1/3) + (IC × 1/3)**")
            st.markdown("Abaixo, cada componente é detalhado com seus subfatores e pesos.")

            # IMA detalhamento
            st.markdown("### ⚡ IMA (Índice de Momentum Atual)")
            st.markdown("Pesos dos recortes: 10G=0.10, 5G=0.15, 3G=0.20, 5CF=0.25, 3CF=0.30")
            for lado, time, ima, detalhes in [('Casa', res['time_casa'], res['ima_casa'], res['detalhes_ima']['casa']),
                                              ('Fora', res['time_fora'], res['ima_fora'], res['detalhes_ima']['fora'])]:
                st.write(f"**{time}** (IMA={ima:.1f})")
                dados_recortes = []
                for recorte, jogos in detalhes.items():
                    if jogos:
                        media = sum(j['pontos'] for j in jogos) / len(jogos)
                        peso = PESOS_RECORTES_EX[recorte]
                        contrib = media * peso
                        dados_recortes.append((recorte, peso, media, contrib))
                if dados_recortes:
                    st.markdown("<table class='detail-table'><tr><th>Recorte</th><th>Peso</th><th>Média Pontos</th><th>Contrib.</th></tr>", unsafe_allow_html=True)
                    for rec, p, m, c in dados_recortes:
                        st.markdown(f"<tr><td>{rec}</td><td>{p:.2f}</td><td>{m:.2f}</td><td>{c:.2f}</td></tr>", unsafe_allow_html=True)
                    st.markdown("</table>", unsafe_allow_html=True)
                    soma_contrib = sum(c for _,_,_,c in dados_recortes)
                    st.caption(f"Soma das contribuições: {soma_contrib:.2f} (após piso/teto = {ima:.1f})")
                else:
                    st.write("Sem dados.")

            # OVRall detalhamento
            st.markdown("### 📈 OVRall")
            st.markdown("Pesos das dimensões: Ataque=0.25, Defesa=0.25, MeioCampo=0.20, Consistencia=0.15, Resiliencia=0.15")
            for lado, time, ovr, notas in [('Casa', res['time_casa'], res['ovrall_casa'], res['notas_casa']),
                                           ('Fora', res['time_fora'], res['ovrall_fora'], res['notas_fora'])]:
                st.write(f"**{time}** (OVRall={ovr:.1f})")
                rows = []
                for dim, peso in PESOS_OVRALL_EX.items():
                    nota = notas.get(dim, 0)
                    contrib = nota * peso
                    rows.append((dim, peso, nota, contrib))
                st.markdown("<table class='detail-table'><tr><th>Dimensão</th><th>Peso</th><th>Nota (0-100)</th><th>Contrib.</th></tr>", unsafe_allow_html=True)
                for dim, p, n, c in rows:
                    st.markdown(f"<tr><td>{dim}</td><td>{p:.2f}</td><td>{n:.1f}</td><td>{c:.2f}</td></tr>", unsafe_allow_html=True)
                st.markdown("</table>", unsafe_allow_html=True)
                soma_contrib = sum(c for _,_,_,c in rows)
                st.caption(f"Soma das contribuições: {soma_contrib:.2f} (OVRall final = {ovr:.1f})")

            # IC detalhamento
            st.markdown("### 🧠 IC (Índice de Contexto)")
            st.markdown("Pesos: Confronto direto=0.25, Mesmo escalão=0.20, Contra escalão adversário=0.20, Fator casa=0.20, Odds=0.15")
            for lado, time, ic_val, ic_dict in [('Casa', res['time_casa'], res['ic_casa'], st.session_state.ic_casa),
                                                 ('Fora', res['time_fora'], res['ic_fora'], st.session_state.ic_fora)]:
                st.write(f"**{time}** (IC={ic_val:.1f})")
                rows = []
                for nome, chave in metricas_ic:
                    peso = PESOS_IC_EX[chave]
                    valor = ic_dict.get(chave, None)
                    if valor is not None:
                        contrib = valor * peso
                        rows.append((nome, peso, valor, contrib))
                    else:
                        rows.append((nome, peso, '-', '-'))
                st.markdown("<table class='detail-table'><tr><th>Componente</th><th>Peso</th><th>Valor</th><th>Contrib.</th></tr>", unsafe_allow_html=True)
                for nome, p, v, c in rows:
                    v_str = f"{v:.1f}" if isinstance(v, (int,float)) else v
                    c_str = f"{c:.2f}" if isinstance(c, (int,float)) else c
                    st.markdown(f"<tr><td>{nome}</td><td>{p:.2f}</td><td>{v_str}</td><td>{c_str}</td></tr>", unsafe_allow_html=True)
                st.markdown("</table>", unsafe_allow_html=True)
                if rows and isinstance(rows[0][3], (int,float)):
                    soma_contrib = sum(c for _,_,_,c in rows if isinstance(c, (int,float)))
                    st.caption(f"Soma das contribuições: {soma_contrib:.2f} (IC final = {ic_val:.1f})")

            st.markdown("---")
            st.markdown("**Bônus assimétricos** (aplicados automaticamente conforme prateleiras):")
            st.markdown("- Vitória de Crítico sobre Elite: +2.0  \n- Vitória de Baixa sobre Elite: +0.5  \n- Derrota de Elite para Crítico: -2.0  \n- Empate Crítico vs Elite: +2.0 (Crítico) / -1.0 (Elite)")
            st.caption("As prateleiras são definidas pela posição: Elite (1-3), Alta (4-7), Média (8-13), Baixa (14-16), Crítica (17+).")

        # ----- PROBABILIDADES E MERCADOS (secundário) -----
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.subheader("📊 PROBABILIDADES 1X2")
        col1, col2, col3 = st.columns(3)
        col1.metric("🏠 Casa", f"{res['p1']:.1%}")
        col2.metric("🤝 Empate", f"{res['pX']:.1%}")
        col3.metric("🏟️ Fora", f"{res['p2']:.1%}")

        st.subheader("🎯 RECOMENDAÇÕES DE MERCADO")
        mercados = [
            ("Over 2.5 Gols", res.get('over25')),
            ("Ambas Marcam", res.get('btts')),
            ("Gol no 1º Tempo", res.get('gol_ht')),
            ("Over Escanteios", res.get('esc')),
        ]
        cols = st.columns(len(mercados))
        for col, (nome, prob) in zip(cols, mercados):
            with col:
                if prob is not None:
                    rec = "VALUE" if prob >= 0.60 else ("FAVORITO" if prob >= 0.50 else "NÃO RECOMENDADO")
                    border = "2px solid #ffd700" if rec=="VALUE" else ("1px solid #888" if rec=="NÃO RECOMENDADO" else "1px solid #aaa")
                    st.markdown(f"""
                    <div style="background:rgba(20,20,35,0.9); border-radius:14px; padding:14px; border:{border}; text-align:center;">
                        <div style="color:#aaa; font-size:0.8rem;">{nome}</div>
                        <strong style="color:#ffd700; font-size:1.2rem;">{prob:.1%}</strong>
                        <div style="color:#ffd700; font-size:0.7rem; margin-top:4px;">{rec}</div>
                    </div>
                    """, unsafe_allow_html=True)
