# interfaces.py — MyPredict 2.0 (Visual refinado, sem placeholders)
import streamlit as st
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from manual import executar_manual
from utils import para_float, extrair_jogos
from data_source_api_football import get_api_usage
from automatico import inicializar_estado, carregar_ligas, buscar_temporadas, buscar_times, executar_automatico

def injetar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .stApp { background: radial-gradient(ellipse at 50% 0%, #1a1a2e 0%, #0e1117 50%, #000000 100%); background-attachment: fixed; }
        .main-title { font-size: 3.5rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #ffd700 0%, #ffaa00 30%, #ffd700 60%, #ff8c00 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.3rem; letter-spacing: 2px; }
        .subtitle { text-align: center; color: #b0b0b0; font-size: 1rem; margin-bottom: 1.5rem; font-weight: 300; letter-spacing: 1px; }
        .quote-box { background: linear-gradient(135deg, rgba(255,215,0,0.05) 0%, rgba(255,215,0,0.02) 100%); border-left: 3px solid #ffd700; border-radius: 0 12px 12px 0; padding: 16px 20px; margin: 20px 0; text-align: center; }
        .quote-text { color: #d0d0d0; font-style: italic; font-size: 1rem; line-height: 1.6; }
        .quote-author { color: #ffd700; font-size: 0.85rem; margin-top: 8px; }
        .team-card { background: linear-gradient(145deg, rgba(20,20,35,0.95) 0%, rgba(15,15,25,0.98) 100%); border-radius: 20px; padding: 20px; margin: 10px 0; border: 1px solid rgba(255,215,0,0.3); box-shadow: 0 8px 32px rgba(0,0,0,0.4); transition: all 0.3s ease; }
        .team-card:hover { border-color: #ffd700; box-shadow: 0 12px 40px rgba(255,215,0,0.15); transform: translateY(-2px); }
        .team-name { font-size: 1.4rem; font-weight: 700; color: #ffd700; text-align: center; margin-bottom: 8px; }
        .metric-compare { display: flex; align-items: center; margin: 4px 0; padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid rgba(255,215,0,0.15); }
        .metric-bar { height: 4px; border-radius: 2px; margin: 2px 0; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,215,0,0.1); }
        .metric-fill-gold { height: 100%; border-radius: 2px; background: linear-gradient(90deg, #ffd700, #ffaa00); box-shadow: 0 0 6px rgba(255,215,0,0.3); }
        .metric-fill-silver { height: 100%; border-radius: 2px; background: linear-gradient(90deg, #c0c0c0, #a0a0a0); }
        .gold-text { color: #ffd700 !important; font-weight: 700; }
        .silver-text { color: #c0c0c0 !important; font-weight: 600; }
        .value-seal { background: linear-gradient(145deg, #ffd700 0%, #ff8c00 50%, #b8860b 100%); color: #000; font-weight: 900; text-align: center; border-radius: 50%; width: 90px; height: 90px; display: flex; align-items: center; justify-content: center; margin: 15px auto; font-size: 0.8rem; letter-spacing: 1px; box-shadow: 0 0 30px rgba(255,215,0,0.5); animation: sealPulse 2s ease-in-out infinite; }
        @keyframes sealPulse { 0%, 100% { box-shadow: 0 0 20px rgba(255,215,0,0.4); } 50% { box-shadow: 0 0 40px rgba(255,215,0,0.7), 0 0 80px rgba(255,140,0,0.4); } }
        .stButton > button { background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%); color: #000; border: none; font-weight: 700; font-size: 1.1rem; border-radius: 14px; padding: 14px 28px; letter-spacing: 1px; box-shadow: 0 4px 20px rgba(255,215,0,0.3); transition: all 0.3s ease; text-transform: uppercase; }
        .stButton > button:hover { transform: scale(1.03); box-shadow: 0 8px 30px rgba(255,215,0,0.5); }
        .divider-gold { height: 1px; background: linear-gradient(90deg, transparent, rgba(255,215,0,0.3), transparent); margin: 20px 0; }
        .stTextInput > div > div > input, .stTextArea > div > div > textarea { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; color: #e0e0e0; }
        .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus { border-color: #ffd700; }
        .stats-table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        .stats-table td, .stats-table th { padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); text-align: center; }
        .stats-table th { color: #ffd700; font-weight: 600; font-size: 0.9rem; }
        .stats-table td { color: #d0d0d0; font-size: 0.9rem; }
        .scoreboard { background: linear-gradient(180deg, rgba(0,0,0,0.6) 0%, rgba(20,20,30,0.8) 100%); border: 2px solid rgba(255,215,0,0.4); border-radius: 20px; padding: 20px; text-align: center; margin: 20px 0; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
        .score-home, .score-away { font-size: 2.5rem; font-weight: 900; color: #ffd700; }
        .score-vs { font-size: 1.2rem; color: #888; margin: 0 15px; }
    </style>
    """, unsafe_allow_html=True)

# ---------- TELA AUTOMÁTICA (mantida para compatibilidade) ----------
def tela_automatico(lista_ligas, temporadas, times_carregados, uso_api, limite_api, msg_erro, resultados):
    st.set_page_config(page_title="MyPredict 2.0", layout="wide", page_icon="⚽")
    injetar_css()
    if uso_api is not None:
        porcentagem = uso_api / limite_api if limite_api else 0
        cor = "#00ff7f" if porcentagem < 0.5 else ("#ffaa00" if porcentagem < 0.8 else "#ff4d4d")
        st.markdown(f'<div style="display:flex;justify-content:center;"><div class="api-badge"><span class="api-dot" style="background-color:{cor};"></span> API: {uso_api}/{limite_api}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-title">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="quote-box"><div class="quote-text">"O futebol não é uma questão de vida ou morte. É muito mais importante que isso."</div><div class="quote-author">— Bill Shankly</div></div>', unsafe_allow_html=True)
    if msg_erro: st.error(msg_erro)
    col_liga, col_temp = st.columns([2,1])
    with col_liga: liga_nome = st.selectbox("Selecione a liga", lista_ligas or [], key="sel_liga")
    with col_temp:
        if liga_nome and liga_nome in temporadas:
            temps = temporadas[liga_nome]
            temporada = st.selectbox("Temporada", temps, key="sel_temp") if temps else st.number_input("Temporada", value=2024)
        else: temporada = st.number_input("Temporada", value=2024)
    chave_times = f"{liga_nome}_{temporada}"
    buscar = st.button("🔍 Buscar Times", use_container_width=True) if chave_times not in times_carregados else False
    if chave_times in times_carregados: st.info("Times carregados do cache.")
    lista_times = times_carregados.get(chave_times, [])
    col1, col2 = st.columns(2)
    with col1: time_casa = st.selectbox("Time da casa", lista_times) if lista_times else st.text_input("Time da casa", value="")
    with col2: time_fora = st.selectbox("Time de fora", lista_times, index=min(1,len(lista_times)-1)) if lista_times else st.text_input("Time de fora", value="")
    gerar = st.button("⚡ Gerar MyPredict", use_container_width=True)
    if resultados:
        st.markdown(f'<div class="scoreboard"><span class="score-home">{resultados["time_casa"]}</span><span class="score-vs">vs</span><span class="score-away">{resultados["time_fora"]}</span></div>', unsafe_allow_html=True)
        col1,col2,col3=st.columns(3)
        col1.metric("🏠 Casa",f"{resultados['p1']:.1%}"); col2.metric("🤝 Empate",f"{resultados['pX']:.1%}"); col3.metric("🏟️ Fora",f"{resultados['p2']:.1%}")
        if resultados.get('rec_p1'): st.markdown('<div class="value-seal">VALUE</div>', unsafe_allow_html=True)
        if resultados.get('rec_p2'): st.markdown('<div class="value-seal">VALUE</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
        col4,col5=st.columns(2)
        col4.metric("Over 2.5 Gols",f"{resultados['over25']:.1%}" if resultados['over25'] else "N/D")
        col5.metric("Ambas Marcam",f"{resultados['btts']:.1%}" if resultados['btts'] else "N/D")
        st.metric("⚡ Gol 1º Tempo",f"{resultados['gol_ht']:.1%}" if resultados['gol_ht'] else "N/D")
        st.metric("🏳️ Escanteios",f"{resultados['esc']:.1%}" if resultados['esc'] else "N/D")
    return liga_nome, temporada, time_casa, time_fora, buscar, gerar, chave_times

# ---------- TELA MANUAL (Refinada) ----------
def tela_manual():
    st.set_page_config(page_title="MyPredict 2.0 – Premium", layout="centered", page_icon="⚽")
    injetar_css()

    for chave, padrao in {
        'time_casa': '', 'time_fora': '', 'pos_casa': 1, 'pos_fora': 2,
        'jogos_casa': [], 'jogos_fora': [], 'ovrall_casa': {}, 'ovrall_fora': {},
        'ic_casa': {}, 'ic_fora': {}, 'media_gols_casa': MEDIA_GOLS_CASA_LIGA,
        'media_gols_fora': MEDIA_GOLS_FORA_LIGA, 'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
        'media_esc_casa': 5.0, 'media_esc_fora': 4.5, 'prateleiras_extra': {}
    }.items():
        if chave not in st.session_state: st.session_state[chave] = padrao

    st.markdown('<div class="main-title">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">ANÁLISE PREDITIVA PREMIUM · TRADE ESPORTIVO</div>', unsafe_allow_html=True)
    st.markdown('<div class="quote-box"><div class="quote-text">"O futebol é a arte de prever o imprevisível. Nós apenas tentamos ser um pouco menos surpreendidos."</div><div class="quote-author">— MyPredict Philosophy</div></div>', unsafe_allow_html=True)

    # Times
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.text_input("Time da Casa", key="time_casa_input", value=st.session_state.time_casa, placeholder="Ex: Flamengo")
        st.number_input("Posição", 1, 20, key="pos_casa_input", value=st.session_state.pos_casa)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="team-card">', unsafe_allow_html=True)
        st.text_input("Time da Fora", key="time_fora_input", value=st.session_state.time_fora, placeholder="Ex: Palmeiras")
        st.number_input("Posição", 1, 20, key="pos_fora_input", value=st.session_state.pos_fora)
        st.markdown('</div>', unsafe_allow_html=True)

    # IMA
    st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
    st.subheader("📊 IMA · Índice de Momento Atual")
    st.caption("Formato: `V, Adversário, S` (uma linha por jogo)")
    col_j1, col_j2 = st.columns(2)
    with col_j1:
        txt_casa = st.text_area("Últimos 10 jogos - Casa", height=180, key="jogos_casa_input",
                               value="\n".join([f"{j['resultado']}, {j['adversario']}, {'S' if j['mandante'] else 'N'}" for j in st.session_state.jogos_casa]))
    with col_j2:
        txt_fora = st.text_area("Últimos 10 jogos - Fora", height=180, key="jogos_fora_input",
                               value="\n".join([f"{j['resultado']}, {j['adversario']}, {'S' if j['mandante'] else 'N'}" for j in st.session_state.jogos_fora]))

    # OVRall
    st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
    st.subheader("📈 OVRall · Força Geral da Temporada")
    st.caption("Deixe em branco para ignorar a métrica. Use vírgula como separador decimal.")
    def metrica(label, key_casa, key_fora):
        c1, c2 = st.columns(2)
        vc = para_float(c1.text_input(label, key=f"{key_casa}_val"))
        vf = para_float(c2.text_input(label, key=f"{key_fora}_val"))
        return vc, vf

    ovrall_casa, ovrall_fora = {}, {}
    for label, key in [
        ("Gols marcados (média)", "gols_media"), ("Gols sofridos (média)", "gols_sofridos_media"),
        ("xG (média)", "xg_media"), ("xGA (média)", "xga_media"),
        ("Finalizações no alvo (média)", "finalizacoes_alvo_media"),
        ("Finalizações no alvo sofridas (média)", "finalizacoes_alvo_sofridas_media"),
        ("Chutes totais (média)", "chutes_media"),
        ("Desarmes + Interceptações (média)", "desarmes_intercep_media"),
        ("Posse de bola (%)", "posse_media"), ("Passes certos (%)", "passes_certos_pct"),
        ("Passes-chave (média)", "passes_chave_media"), ("Assistências (média)", "assistencias_media"),
        ("Conversão de finalizações (%)", "conversao"), ("Jogos sem sofrer gols (%)", "clean_sheets_pct"),
        ("Desvio padrão dos pontos", "desvio_pontos"), ("Desvio padrão gols marcados", "desvio_gols_pro"),
        ("Desvio padrão gols sofridos", "desvio_gols_sofridos"),
        ("Pontos após sair atrás (média)", "pontos_pos_desvantagem_media"),
        ("Gols nos últimos 15 min (média)", "gols_ultimos_15min_media"),
        ("Pontos após derrota (média)", "pontos_apos_derrota_media"),
        ("Diferença aprovação casa-fora (%)", "diff_aprov_casa_fora"),
        ("Aproveitamento viradas a favor (%)", "aprov_viradas_favor"),
        ("Aproveitamento viradas contra (%)", "aprov_viradas_contra"),
    ]:
        vc, vf = metrica(label, f"casa_{key}", f"fora_{key}")
        if vc is not None: ovrall_casa[key] = vc
        if vf is not None: ovrall_fora[key] = vf

    # IC
    st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
    st.subheader("🧠 IC · Índice de Contexto")
    ic_casa, ic_fora = {}, {}
    for label, key in [
        ("Confronto direto (%)", "confronto_direto"), ("Mesmo escalão (%)", "mesmo_escalao"),
        ("Contra escalão adversário (%)", "contra_escalao_adversario"),
        ("Fator casa (%)", "fator_casa"), ("Odd", "odds"),
    ]:
        vc, vf = metrica(label, f"ic_casa_{key}", f"ic_fora_{key}")
        if vc is not None: ic_casa[key] = vc
        if vf is not None: ic_fora[key] = vf

    # Médias da Liga
    st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
    st.subheader("📊 Médias da Liga")
    c1, c2 = st.columns(2)
    with c1:
        mgc = st.number_input("Média gols casa", value=MEDIA_GOLS_CASA_LIGA, key="mgc")
        mhtc = st.number_input("Média gols HT casa", value=0.75, key="mhtc")
        mecc = st.number_input("Média escanteios casa", value=5.0, key="mecc")
    with c2:
        mgf = st.number_input("Média gols fora", value=MEDIA_GOLS_FORA_LIGA, key="mgf")
        mhtf = st.number_input("Média gols HT fora", value=0.65, key="mhtf")
        mecf = st.number_input("Média escanteios fora", value=4.5, key="mecf")

    # Botão
    st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
    if st.button("🔥 GERAR MYPREDICT VALUE", use_container_width=True):
        st.session_state.time_casa = st.session_state.time_casa_input
        st.session_state.time_fora = st.session_state.time_fora_input
        st.session_state.pos_casa = st.session_state.pos_casa_input
        st.session_state.pos_fora = st.session_state.pos_fora_input
        st.session_state.jogos_casa = extrair_jogos(txt_casa) if txt_casa else []
        st.session_state.jogos_fora = extrair_jogos(txt_fora) if txt_fora else []
        st.session_state.ovrall_casa = ovrall_casa
        st.session_state.ovrall_fora = ovrall_fora
        st.session_state.ic_casa = ic_casa
        st.session_state.ic_fora = ic_fora
        st.session_state.media_gols_casa = mgc
        st.session_state.media_gols_fora = mgf
        st.session_state.media_ht_casa = mhtc
        st.session_state.media_ht_fora = mhtf
        st.session_state.media_esc_casa = mecc
        st.session_state.media_esc_fora = mecf

        dados_calc = {k: v for k, v in st.session_state.items() if k in [
            'time_casa','time_fora','pos_casa','pos_fora','jogos_casa','jogos_fora',
            'ovrall_casa','ovrall_fora','ic_casa','ic_fora','media_gols_casa','media_gols_fora',
            'media_ht_casa','media_ht_fora','media_esc_casa','media_esc_fora','prateleiras_extra']}
        res, err = executar_manual(dados_calc)
        if err: st.error(err)
        else:
            st.session_state.resultados = res
            st.rerun()

    # Resultados
    if 'resultados' in st.session_state:
        res = st.session_state.resultados
        
        st.markdown(f"""
        <div class="scoreboard">
            <span class="score-home">{res['time_casa']}</span>
            <span class="score-vs">vs</span>
            <span class="score-away">{res['time_fora']}</span>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("🏠 Casa", f"{res['p1']:.1%}")
            if res['p1'] >= 0.60: st.markdown('<div class="value-seal">VALUE</div>', unsafe_allow_html=True)
        with c2: st.metric("🤝 Empate", f"{res['pX']:.1%}")
        with c3:
            st.metric("🏟️ Fora", f"{res['p2']:.1%}")
            if res['p2'] >= 0.60: st.markdown('<div class="value-seal">VALUE</div>', unsafe_allow_html=True)

        st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
        st.subheader("📊 Comparação de Métricas")

        def card_metric(titulo, vc, vf, tc, tf, fmt=".1f", max_val=100):
            maior_casa = vc >= vf
            cc = "gold-text" if maior_casa else "silver-text"
            cf = "gold-text" if not maior_casa else "silver-text"
            pct_c = min(vc / max_val, 1.0) * 100 if max_val else 0
            pct_f = min(vf / max_val, 1.0) * 100 if max_val else 0
            st.markdown(f"""
            <div class="metric-compare">
                <div style="width:35%; text-align:right; padding-right:10px;">
                    <div style="font-size:0.7rem; color:#888;">{tc}</div>
                    <div class="{cc}" style="font-size:1.1rem;">{vc:{fmt}}</div>
                    <div class="metric-bar"><div class="metric-fill-gold" style="width:{pct_c}%;"></div></div>
                </div>
                <div style="width:30%; text-align:center;">
                    <div style="color:#ffd700; font-weight:600; font-size:0.8rem;">{titulo}</div>
                </div>
                <div style="width:35%; text-align:left; padding-left:10px;">
                    <div style="font-size:0.7rem; color:#888;">{tf}</div>
                    <div class="{cf}" style="font-size:1.1rem;">{vf:{fmt}}</div>
                    <div class="metric-bar"><div class="metric-fill-silver" style="width:{pct_f}%;"></div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        card_metric("IMA", res['ima_casa'], res['ima_fora'], res['time_casa'], res['time_fora'])
        card_metric("MPV", res['mpv_casa'], res['mpv_fora'], res['time_casa'], res['time_fora'])
        if 'notas_casa' in res:
            for dim in ['Ataque', 'Defesa', 'MeioCampo', 'Consistencia', 'Resiliencia']:
                card_metric(dim, res['notas_casa'].get(dim,0), res['notas_fora'].get(dim,0), 
                          res['time_casa'], res['time_fora'])

        # Tabela de estatísticas lado a lado
        st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
        st.subheader("📋 Estatísticas Completas")
        st.markdown(f"""
        <table class="stats-table">
            <tr><th>Indicador</th><th>{res['time_casa']}</th><th>{res['time_fora']}</th></tr>
            <tr><td>Gols marcados (média)</td><td class="{'gold-text' if res['ovrall_casa'] >= res['ovrall_fora'] else 'silver-text'}">{res['ovrall_casa']:.1f}</td><td class="{'gold-text' if res['ovrall_fora'] >= res['ovrall_casa'] else 'silver-text'}">{res['ovrall_fora']:.1f}</td></tr>
            <tr><td>Gols sofridos (média)</td><td>{res['ovrall_casa']:.1f}</td><td>{res['ovrall_fora']:.1f}</td></tr>
            <tr><td>Posse de bola (%)</td><td>{res['ovrall_casa']:.1f}</td><td>{res['ovrall_fora']:.1f}</td></tr>
            <tr><td>Passes certos (%)</td><td>{res['ovrall_casa']:.1f}</td><td>{res['ovrall_fora']:.1f}</td></tr>
            <tr><td>Finalizações alvo (média)</td><td>{res['ovrall_casa']:.1f}</td><td>{res['ovrall_fora']:.1f}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        st.markdown('<div class="divider-gold"></div>', unsafe_allow_html=True)
        st.subheader("🎯 Mercados")
        c4, c5 = st.columns(2)
        with c4:
            st.metric("Over 2.5 Gols", f"{res['over25']:.1%}" if res['over25'] else "N/D")
            if res['over25'] and res['over25'] >= 0.60: st.markdown('<div class="value-seal">VALUE</div>', unsafe_allow_html=True)
        with c5:
            st.metric("Ambas Marcam", f"{res['btts']:.1%}" if res['btts'] else "N/D")
            if res['btts'] and res['btts'] >= 0.60: st.markdown('<div class="value-seal">VALUE</div>', unsafe_allow_html=True)
        st.metric("⚡ Gol no 1º Tempo", f"{res['gol_ht']:.1%}" if res['gol_ht'] else "N/D")
        st.metric("🏳️ Over Escanteios", f"{res['esc']:.1%}" if res['esc'] else "N/D")

        # Rastreio
        with st.expander("🔎 RASTREIO COMPLETO"):
            st.markdown("### 1. IMA")
            for lado, time, ima, det in [('casa', res['time_casa'], res['ima_casa'], res['detalhes_ima']['casa']),
                                         ('fora', res['time_fora'], res['ima_fora'], res['detalhes_ima']['fora'])]:
                st.markdown(f"**{time}** → {ima:.1f}")
                for recorte, jogos in det.items():
                    if not jogos: continue
                    st.write(f"*{recorte}*:")
                    for j in jogos:
                        st.write(f"  {j['jogo']} → {j['pontos']:.2f} pts ({j['prateleira_time']} vs {j['prateleira_adv']})")
            st.markdown("### 2. OVRall")
            for nome, det in res.get('detalhes_ovr', {}).items():
                st.markdown(f"**{nome}**")
                for ind, valor, perc in det['casa']:
                    st.write(f"  {ind}: {valor} → nota {perc:.1f}")
            st.markdown("### 3. IC")
            st.write(f"Casa: {res['ic_casa']:.1f} / Fora: {res['ic_fora']:.1f}")
            st.markdown("### 4. MPV")
            st.write(f"Casa: {res['mpv_casa']:.1f} / Fora: {res['mpv_fora']:.1f}")
