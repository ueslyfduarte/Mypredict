# interfaces.py — MyPredict 2.0 (com OVRall completo e intuitivo)
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

        .main-title { font-size: 2.8rem; font-weight: 900; text-align: center; background: linear-gradient(135deg, #ffd700, #ffaa00, #ffd700); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.2rem; }
        .subtitle { text-align: center; color: #b0b0b0; font-size: 0.9rem; margin-bottom: 1.5rem; letter-spacing: 2px; }
        .gold-highlight { font-size: 2rem; font-weight: 900; background: linear-gradient(135deg, #ffd700, #ffaa00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: block; text-align: center; margin-bottom: 12px; }

        .divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(255,215,0,0.2), transparent); margin: 24px 0; }

        .value-seal {
            background: linear-gradient(145deg, #ffd700, #ff8c00, #b8860b);
            color: #000; font-weight: 900; text-align: center; border-radius: 50%;
            width: 70px; height: 70px; display: flex; align-items: center; justify-content: center;
            font-size: 0.7rem; letter-spacing: 1px; box-shadow: 0 0 25px rgba(255,215,0,0.5);
            animation: sealPulse 2s ease-in-out infinite; margin: 10px auto;
        }
        @keyframes sealPulse { 0%,100%{box-shadow:0 0 15px rgba(255,215,0,0.4);} 50%{box-shadow:0 0 30px rgba(255,215,0,0.8);} }

        .rec-card {
            background: rgba(20,20,35,0.9); border-radius: 14px; padding: 14px;
            border: 1px solid rgba(255,215,0,0.2); text-align: center; margin: 6px 0;
        }
        .rec-card strong { color: #ffd700; font-size: 1.2rem; }

        .stButton > button {
            background: linear-gradient(135deg, #ffd700, #ff8c00); color: #000; border: none;
            font-weight: 700; font-size: 1rem; border-radius: 12px; padding: 12px 24px;
            letter-spacing: 1px; box-shadow: 0 4px 15px rgba(255,215,0,0.3);
        }
        .stButton > button:hover { transform: scale(1.02); box-shadow: 0 8px 25px rgba(255,215,0,0.5); }

        .scoreboard {
            background: linear-gradient(180deg, rgba(0,0,0,0.5), rgba(20,20,30,0.8));
            border: 2px solid rgba(255,215,0,0.4); border-radius: 20px;
            padding: 16px; text-align: center; margin: 16px 0;
        }
        .score-home, .score-away { font-size: 2rem; font-weight: 900; color: #ffd700; }
        .score-vs { font-size: 1rem; color: #888; margin: 0 12px; }

        .team-block {
            border-radius: 16px;
            padding: 18px 14px;
            margin-bottom: 20px;
        }
        .team-block.home {
            background: linear-gradient(145deg, rgba(255,215,0,0.08), rgba(255,215,0,0.02));
            border: 1px solid rgba(255,215,0,0.3);
        }
        .team-block.away {
            background: linear-gradient(145deg, rgba(192,192,192,0.08), rgba(192,192,192,0.02));
            border: 1px solid rgba(192,192,192,0.3);
        }

        .team-title {
            font-size: 1.4rem;
            font-weight: 800;
            text-align: center;
            margin-bottom: 16px;
        }
        .team-title.home-title { color: #ffd700; }
        .team-title.away-title { color: #c0c0c0; }

        .section-title {
            font-size: 1.6rem; font-weight: 800; text-align: center;
            background: linear-gradient(135deg, #ffd700, #ffaa00);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin: 32px 0 16px 0;
        }

        .dimension-title {
            font-size: 1.1rem; font-weight: 700; color: #ffd700;
            margin: 12px 0 8px 0; padding-left: 8px; border-left: 3px solid #ffd700;
        }

        /* Cartões comparativos */
        .big-metric {
            text-align: center; padding: 20px 10px;
            background: rgba(20,20,35,0.9); border-radius: 20px;
            border: 1px solid rgba(255,215,0,0.3);
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        .big-metric .metric-value {
            font-size: 2.8rem; font-weight: 900;
            background: linear-gradient(135deg, #ffd700, #ffaa00);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .big-metric .metric-label {
            font-size: 0.9rem; color: #ffd700; font-weight: 600; letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .big-metric.giant .metric-value { font-size: 4rem; }
        .big-metric.giant {
            border-color: #ffd700;
            box-shadow: 0 0 30px rgba(255,215,0,0.3), 0 0 60px rgba(255,140,0,0.15);
        }
    </style>
    """, unsafe_allow_html=True)

# ---------- TELA AUTOMÁTICA ----------
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

# ---------- TELA MANUAL (com OVRall intuitivo e completo) ----------
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

    # --- Times e Posições ---
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

    # --- IMA ---
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

    # --- OVRall (intuitivo por dimensões) ---
    st.markdown('<div class="section-title">📈 OVRALL · MÉTRICAS DA TEMPORADA</div>', unsafe_allow_html=True)
    st.markdown('<span class="gold-highlight">OVR</span>', unsafe_allow_html=True)
    st.caption("Preencha as métricas do time. Deixe em branco para ignorar. A nota OVRall é calculada a partir de 5 dimensões (Ataque, Defesa, Meio-Campo, Consistência, Resiliência).")

    ovrall_casa, ovrall_fora = {}, {}

    # Dimensões e indicadores (conforme manual.py)
    dimensoes = {
        "⚔️ ATAQUE": [
            ("Gols marcados (média)", "gols_media"),
            ("xG (média)", "xg_media"),
            ("Finalizações no alvo (média)", "finalizacoes_alvo_media"),
            ("Conversão (%)", "conversao"),
        ],
        "🛡️ DEFESA": [
            ("Gols sofridos (média)", "gols_sofridos_media"),
            ("xGA (média)", "xga_media"),
            ("Finalizações no alvo sofridas (média)", "finalizacoes_alvo_sofridas_media"),
            ("Desarmes + Interceptações (média)", "desarmes_intercep_media"),
        ],
        "🧩 MEIO-CAMPO": [
            ("Posse de bola (%)", "posse_media"),
            ("Passes certos (%)", "passes_certos_pct"),
            ("Passes-chave (média)", "passes_chave_media"),
            ("Assistências (média)", "assistencias_media"),
            ("Chutes totais (média)", "chutes_media"),
        ],
        "📏 CONSISTÊNCIA": [
            ("Desvio padrão pontos", "desvio_pontos"),
            ("Desvio padrão gols pró", "desvio_gols_pro"),
            ("Desvio padrão gols sofridos", "desvio_gols_sofridos"),
            ("Jogos sem sofrer gols (%)", "clean_sheets_pct"),
        ],
        "🔄 RESILIÊNCIA": [
            ("Pontos após sair atrás", "pontos_pos_desvantagem_media"),
            ("Gols nos últimos 15 min", "gols_ultimos_15min_media"),
            ("Pontos após derrota", "pontos_apos_derrota_media"),
            ("Dif. aprovação casa-fora (%)", "diff_aprov_casa_fora"),
            ("Viradas a favor (%)", "aprov_viradas_favor"),
            ("Viradas contra (%)", "aprov_viradas_contra"),
        ],
        # Métricas extras para mercados (não entram no OVRall, mas necessárias)
        "⚡ MERCADOS (1ºT / ESCANTEIOS)": [
            ("Gols 1º tempo (média)", "gols_ht_media"),
            ("Gols sofridos 1º tempo (média)", "gols_ht_sofridos_media"),
            ("Escanteios (média)", "escanteios_media"),
            ("Escanteios sofridos (média)", "escanteios_sofridos_media"),
        ]
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

    # --- Botão de calcular ---
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

    # --- RESULTADOS (idêntico ao anterior, com resumo individual e comparativo) ---
    if 'resultados' in st.session_state:
        res = st.session_state.resultados
        st.markdown(f'<div class="scoreboard"><span class="score-home">{res["time_casa"]}</span><span class="score-vs">vs</span><span class="score-away">{res["time_fora"]}</span></div>', unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)
        with c1: st.metric("🏠 Casa", f"{res['p1']:.1%}")
        with c2: st.metric("🤝 Empate", f"{res['pX']:.1%}")
        with c3: st.metric("🏟️ Fora", f"{res['p2']:.1%}")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.subheader("🏆 COMPARATIVO DE FORÇA")
        cols = st.columns([1, 1, 1.5])
        with cols[0]:
            vc = res['ima_casa']; vf = res['ima_fora']
            maior = vc >= vf
            cc = "gold-text" if maior else "silver-text"
            cf = "gold-text" if not maior else "silver-text"
            st.markdown(f"""
            <div class="big-metric">
                <div class="metric-label">⚡ IMA</div>
                <div style="display:flex;justify-content:space-between;padding:0 10px;">
                    <span class="{cc}" style="font-size:1.2rem;">{vc:.1f}</span>
                    <span style="color:#888;">vs</span>
                    <span class="{cf}" style="font-size:1.2rem;">{vf:.1f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with cols[1]:
            vc = res['ovrall_casa']; vf = res['ovrall_fora']
            maior = vc >= vf
            cc = "gold-text" if maior else "silver-text"
            cf = "gold-text" if not maior else "silver-text"
            st.markdown(f"""
            <div class="big-metric">
                <div class="metric-label">📈 OVRall</div>
                <div style="display:flex;justify-content:space-between;padding:0 10px;">
                    <span class="{cc}" style="font-size:1.2rem;">{vc:.1f}</span>
                    <span style="color:#888;">vs</span>
                    <span class="{cf}" style="font-size:1.2rem;">{vf:.1f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with cols[2]:
            vc = res['mpv_casa']; vf = res['mpv_fora']
            maior = vc >= vf
            cc = "gold-text" if maior else "silver-text"
            cf = "gold-text" if not maior else "silver-text"
            st.markdown(f"""
            <div class="big-metric giant">
                <div class="metric-label">🏆 MPV</div>
                <div style="display:flex;justify-content:space-between;padding:0 10px;">
                    <span class="{cc}" style="font-size:1.6rem;">{vc:.1f}</span>
                    <span style="color:#888;">vs</span>
                    <span class="{cf}" style="font-size:1.6rem;">{vf:.1f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        col_res_casa, col_res_fora = st.columns(2)
        with col_res_casa:
            st.markdown('<div class="team-block home">', unsafe_allow_html=True)
            st.markdown(f'<div class="team-title home-title">🏠 {res["time_casa"]}</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div style="font-size:1.5rem; font-weight:900; color:#ffd700;">IMA: {res['ima_casa']:.1f}</div>
                <div style="font-size:1.2rem; color:#ffaa00;">OVRall: {res['ovrall_casa']:.1f}</div>
                <div style="font-size:1.4rem; color:#ffd700;">MPV: {res['mpv_casa']:.1f}</div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_res_fora:
            st.markdown('<div class="team-block away">', unsafe_allow_html=True)
            st.markdown(f'<div class="team-title away-title">🏟️ {res["time_fora"]}</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div style="font-size:1.5rem; font-weight:900; color:#c0c0c0;">IMA: {res['ima_fora']:.1f}</div>
                <div style="font-size:1.2rem; color:#aaaaaa;">OVRall: {res['ovrall_fora']:.1f}</div>
                <div style="font-size:1.4rem; color:#c0c0c0;">MPV: {res['mpv_fora']:.1f}</div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.subheader("🔬 DIMENSÕES DO OVRALL")
        if 'notas_casa' in res:
            for dim in ['Ataque','Defesa','MeioCampo','Consistencia','Resiliencia']:
                vc = res['notas_casa'].get(dim,0); vf = res['notas_fora'].get(dim,0)
                maior = vc >= vf
                cc = "gold-text" if maior else "silver-text"; cf = "gold-text" if not maior else "silver-text"
                pct_c = min(vc/100,1.0)*100; pct_f = min(vf/100,1.0)*100
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;padding:2px 0;">
                    <span style="width:80px;font-size:0.8rem;color:#aaa;">{dim}</span>
                    <span class="{cc}" style="width:40px;text-align:right;font-size:0.9rem;">{vc:.1f}</span>
                    <div style="flex:1;height:3px;background:rgba(255,255,255,0.06);border-radius:2px;border:1px solid rgba(255,215,0,0.06);">
                        <div style="width:{pct_c}%;height:100%;background:linear-gradient(90deg,#ffd700,#ffaa00);border-radius:2px;"></div>
                    </div>
                    <span style="font-size:0.8rem;color:#ffd700;width:20px;text-align:center;">VS</span>
                    <div style="flex:1;height:3px;background:rgba(255,255,255,0.06);border-radius:2px;border:1px solid rgba(255,215,0,0.06);">
                        <div style="width:{pct_f}%;height:100%;background:linear-gradient(90deg,#c0c0c0,#a0a0a0);border-radius:2px;"></div>
                    </div>
                    <span class="{cf}" style="width:40px;text-align:left;font-size:0.9rem;">{vf:.1f}</span>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
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
                    rec = ""
                    if prob >= 0.60: rec = "VALUE"
                    elif prob >= 0.50: rec = "FAVORITO"
                    else: rec = "NÃO RECOMENDADO"
                    border = "border:2px solid #ffd700;" if rec=="VALUE" else ("border:1px solid #888;" if rec=="NÃO RECOMENDADO" else "border:1px solid #aaa;")
                    st.markdown(f"""
                    <div class="rec-card" style="{border}">
                        <div style="font-size:0.8rem;color:#aaa;">{nome}</div>
                        <strong>{prob:.1%}</strong>
                        <div style="font-size:0.7rem;color:#ffd700;margin-top:4px;">{rec}</div>
                    </div>
                    """, unsafe_allow_html=True)

        with st.expander("🔎 RASTREIO COMPLETO"):
            st.markdown("### IMA")
            for lado, time, ima, det in [('casa',res['time_casa'],res['ima_casa'],res['detalhes_ima']['casa']),
                                         ('fora',res['time_fora'],res['ima_fora'],res['detalhes_ima']['fora'])]:
                st.write(f"**{time}**: {ima:.1f}")
                for recorte, jogos in det.items():
                    if jogos:
                        st.write(f"*{recorte}*: {sum(j['pontos'] for j in jogos)/len(jogos):.2f} média")
            st.markdown("### OVRall")
            for nome, det in res.get('detalhes_ovr',{}).items():
                st.write(f"**{nome}**: Casa {res['notas_casa'][nome]:.1f} / Fora {res['notas_fora'][nome]:.1f}")
            st.markdown("### IC e MPV")
            st.write(f"IC: Casa {res['ic_casa']:.1f} / Fora {res['ic_fora']:.1f}")
            st.write(f"MPV: Casa {res['mpv_casa']:.1f} / Fora {res['mpv_fora']:.1f}")
