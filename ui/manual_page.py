# ui/manual_page.py (versão final)
import streamlit as st
from ui.styles import injetar_css
from ui.components import show_results_manual
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from utils import extrair_jogos, para_float
from core.calculations import executar_manual

PESOS_RECORTES_EX = {'10G': 0.10, '5G': 0.15, '3G': 0.20, '5CF': 0.25, '3CF': 0.30}
PESOS_OVRALL_EX = {'Ataque': 0.25, 'Defesa': 0.25, 'MeioCampo': 0.20, 'Consistencia': 0.15, 'Resiliencia': 0.15}
PESOS_IC_EX = {'confronto_direto': 0.25, 'mesmo_escalao': 0.20, 'contra_escalao_adversario': 0.20, 'fator_casa': 0.20, 'odds': 0.15}

def render_manual():
    injetar_css()
    st.markdown('<div class="main-title">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">ANÁLISE PREDITIVA PREMIUM</div>', unsafe_allow_html=True)

    # Inicializar sessão
    for chave, padrao in {
        'time_casa':'','time_fora':'','pos_casa':1,'pos_fora':2,
        'jogos_casa':[],'jogos_fora':[],'ovrall_casa':{},'ovrall_fora':{},
        'ic_casa':{},'ic_fora':{},'media_gols_casa':MEDIA_GOLS_CASA_LIGA,
        'media_gols_fora':MEDIA_GOLS_FORA_LIGA,'media_ht_casa':0.75,'media_ht_fora':0.65,
        'media_esc_casa':5.0,'media_esc_fora':4.5,'prateleiras_extra':{}
    }.items():
        if chave not in st.session_state:
            st.session_state[chave] = padrao

    # Determinar qual time está melhor classificado (posição menor = melhor)
    melhor = 'casa' if st.session_state.pos_casa < st.session_state.pos_fora else 'fora'

    # --- Times ---
    st.markdown('<div class="section-title">⚔️ TIMES</div>', unsafe_allow_html=True)
    col_casa, col_fora = st.columns(2)
    with col_casa:
        classe_casa = "team-block home" + (" gold-highlight" if melhor == 'casa' else "")
        st.markdown(f'<div class="{classe_casa}">', unsafe_allow_html=True)
        st.markdown('<div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        st.text_input("Nome", key="time_casa_input", value=st.session_state.time_casa, placeholder="Time da casa")
        st.number_input("Posição", 1, 20, key="pos_casa_input", value=st.session_state.pos_casa)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora:
        classe_fora = "team-block away" + (" gold-highlight" if melhor == 'fora' else "")
        st.markdown(f'<div class="{classe_fora}">', unsafe_allow_html=True)
        st.markdown('<div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        st.text_input("Nome", key="time_fora_input", value=st.session_state.time_fora, placeholder="Time de fora")
        st.number_input("Posição", 1, 20, key="pos_fora_input", value=st.session_state.pos_fora)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- IMA com seletores coloridos ---
    st.markdown('<div class="section-title">⚡ IMA</div>', unsafe_allow_html=True)
    st.caption("Últimos 10 jogos. Selecione resultado (V/E/D), digite o adversário e marque se foi mandante.")

    def cor_resultado(res):
        if res == 'V': return '🟢'
        elif res == 'E': return '🟡'
        elif res == 'D': return '🔴'
        return '⚪'

    col_jogos_casa, col_jogos_fora = st.columns(2)
    with col_jogos_casa:
        st.markdown("**🏠 Casa**")
        for i in range(10):
            jogo_atual = st.session_state.jogos_casa[i] if i < len(st.session_state.jogos_casa) else {}
            cols = st.columns([0.8, 2, 0.8])
            res = cols[0].selectbox("", ["", "V", "E", "D"], 
                                    key=f"man_casa_res_{i}",
                                    index=["", "V", "E", "D"].index(jogo_atual.get('resultado', '')) if jogo_atual.get('resultado') in ["V","E","D"] else 0,
                                    label_visibility="collapsed")
            # Exibe bolinha colorida ao lado
            cols[0].markdown(f'<span style="font-size:1.2rem;">{cor_resultado(res)}</span>', unsafe_allow_html=True)
            adv = cols[1].text_input("", value=jogo_atual.get('adversario',''), key=f"man_casa_adv_{i}", placeholder="Adversário", label_visibility="collapsed")
            mand = cols[2].checkbox("Mandante", value=jogo_atual.get('mandante', False), key=f"man_casa_mand_{i}")
            if res and adv:
                if i >= len(st.session_state.jogos_casa):
                    st.session_state.jogos_casa.append({"resultado": res, "adversario": adv, "mandante": mand})
                else:
                    st.session_state.jogos_casa[i] = {"resultado": res, "adversario": adv, "mandante": mand}
    with col_jogos_fora:
        st.markdown("**🏟️ Fora**")
        for i in range(10):
            jogo_atual = st.session_state.jogos_fora[i] if i < len(st.session_state.jogos_fora) else {}
            cols = st.columns([0.8, 2, 0.8])
            res = cols[0].selectbox("", ["", "V", "E", "D"], 
                                    key=f"man_fora_res_{i}",
                                    index=["", "V", "E", "D"].index(jogo_atual.get('resultado', '')) if jogo_atual.get('resultado') in ["V","E","D"] else 0,
                                    label_visibility="collapsed")
            cols[0].markdown(f'<span style="font-size:1.2rem;">{cor_resultado(res)}</span>', unsafe_allow_html=True)
            adv = cols[1].text_input("", value=jogo_atual.get('adversario',''), key=f"man_fora_adv_{i}", placeholder="Adversário", label_visibility="collapsed")
            mand = cols[2].checkbox("Mandante", value=jogo_atual.get('mandante', False), key=f"man_fora_mand_{i}")
            if res and adv:
                if i >= len(st.session_state.jogos_fora):
                    st.session_state.jogos_fora.append({"resultado": res, "adversario": adv, "mandante": mand})
                else:
                    st.session_state.jogos_fora[i] = {"resultado": res, "adversario": adv, "mandante": mand}

    # --- OVRall (dimensões, sem a antiga aba "mercados", agora "Estatísticas Globais") ---
    st.markdown('<div class="section-title">📈 OVRall</div>', unsafe_allow_html=True)
    st.caption("Preencha as métricas da temporada. Deixe em branco se não disponível.")
    dimensoes = {
        "⚔️ ATAQUE": [("Gols marcados", "gols_media"), ("xG", "xg_media"),
                      ("Finalizações alvo", "finalizacoes_alvo_media"), ("Conversão %", "conversao")],
        "🛡️ DEFESA": [("Gols sofridos", "gols_sofridos_media"), ("xGA", "xga_media"),
                       ("Finalizações alvo sofridas", "finalizacoes_alvo_sofridas_media"),
                       ("Desarmes+Intercept.", "desarmes_intercep_media")],
        "🧩 MEIO-CAMPO": [("Posse %", "posse_media"), ("Passes certos %", "passes_certos_pct"),
                         ("Passes-chave", "passes_chave_media"), ("Assistências", "assistencias_media"),
                         ("Chutes totais", "chutes_media")],
        "📏 CONSISTÊNCIA": [("Desvio padrão pontos", "desvio_pontos"), ("Desvio gols pró", "desvio_gols_pro"),
                           ("Desvio gols sofridos", "desvio_gols_sofridos"),
                           ("Jogos sem sofrer gol %", "clean_sheets_pct")],
        "🔄 RESILIÊNCIA": [("Pontos após sair atrás", "pontos_pos_desvantagem_media"),
                          ("Gols últimos 15 min", "gols_ultimos_15min_media"),
                          ("Pontos após derrota", "pontos_apos_derrota_media"),
                          ("Dif. aprovação casa-fora %", "diff_aprov_casa_fora"),
                          ("Viradas a favor %", "aprov_viradas_favor"),
                          ("Viradas contra %", "aprov_viradas_contra")],
        "🌐 ESTATÍSTICAS GLOBAIS": [("Gols 1º tempo (média)", "gols_ht_media"),
                                    ("Gols sofridos 1º tempo", "gols_ht_sofridos_media"),
                                    ("Escanteios (média)", "escanteios_media"),
                                    ("Escanteios sofridos", "escanteios_sofridos_media")]
    }
    col_casa_ovr, col_fora_ovr = st.columns(2)
    with col_casa_ovr:
        st.markdown('<div class="team-block home">', unsafe_allow_html=True)
        st.markdown('<div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        for nome_dim, indicadores in dimensoes.items():
            st.markdown(f'<div class="dimension-title">{nome_dim}</div>', unsafe_allow_html=True)
            for label, key in indicadores:
                val = st.text_input(label, key=f"casa_ovr_{key}", placeholder=label, label_visibility="visible")
                st.session_state.ovrall_casa[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora_ovr:
        st.markdown('<div class="team-block away">', unsafe_allow_html=True)
        st.markdown('<div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        for nome_dim, indicadores in dimensoes.items():
            st.markdown(f'<div class="dimension-title">{nome_dim}</div>', unsafe_allow_html=True)
            for label, key in indicadores:
                val = st.text_input(label, key=f"fora_ovr_{key}", placeholder=label, label_visibility="visible")
                st.session_state.ovrall_fora[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)

    # --- IC ---
    st.markdown('<div class="section-title">🧠 IC</div>', unsafe_allow_html=True)
    st.caption("Índice de Contexto. Preencha se tiver informações adicionais.")
    metricas_ic = [
        ("Confronto direto %", "confronto_direto"),
        ("Mesmo escalão %", "mesmo_escalao"),
        ("Contra escalão adversário %", "contra_escalao_adversario"),
        ("Fator casa %", "fator_casa"),
        ("Odds (decimal)", "odds"),
    ]
    col_casa_ic, col_fora_ic = st.columns(2)
    with col_casa_ic:
        st.markdown('<div class="team-block home"><div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        for label, key in metricas_ic:
            val = st.text_input(label, key=f"ic_casa_{key}", placeholder=label, label_visibility="visible")
            st.session_state.ic_casa[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora_ic:
        st.markdown('<div class="team-block away"><div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        for label, key in metricas_ic:
            val = st.text_input(label, key=f"ic_fora_{key}", placeholder=label, label_visibility="visible")
            st.session_state.ic_fora[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Médias da Liga (em uma linha) ---
    st.markdown('<div class="section-title">📊 MÉDIAS DA LIGA</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        mgc = st.number_input("Gols casa", value=MEDIA_GOLS_CASA_LIGA, key="mgc")
        mhtc = st.number_input("Gols HT casa", value=0.75, key="mhtc")
        mecc = st.number_input("Escanteios casa", value=5.0, key="mecc")
    with c2:
        mgf = st.number_input("Gols fora", value=MEDIA_GOLS_FORA_LIGA, key="mgf")
        mhtf = st.number_input("Gols HT fora", value=0.65, key="mhtf")
        mecf = st.number_input("Escanteios fora", value=4.5, key="mecf")
    # (terceira coluna vazia para balancear)

    # --- Botão GERAR ---
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    if st.button("🔥 GERAR MYPREDICT VALUE", use_container_width=True):
        st.session_state.time_casa = st.session_state.time_casa_input
        st.session_state.time_fora = st.session_state.time_fora_input
        st.session_state.pos_casa = st.session_state.pos_casa_input
        st.session_state.pos_fora = st.session_state.pos_fora_input
        st.session_state.media_gols_casa = mgc; st.session_state.media_gols_fora = mgf
        st.session_state.media_ht_casa = mhtc; st.session_state.media_ht_fora = mhtf
        st.session_state.media_esc_casa = mecc; st.session_state.media_esc_fora = mecf

        dados = {k:v for k,v in st.session_state.items() if k in [
            'time_casa','time_fora','pos_casa','pos_fora','jogos_casa','jogos_fora',
            'ovrall_casa','ovrall_fora','ic_casa','ic_fora','media_gols_casa','media_gols_fora',
            'media_ht_casa','media_ht_fora','media_esc_casa','media_esc_fora','prateleiras_extra']}
        res, err = executar_manual(dados)
        if err:
            st.error(err)
        else:
            st.session_state.resultados = res
            st.rerun()

    # Exibir resultados
    if 'resultados' in st.session_state and st.session_state.resultados is not None:
        show_results_manual(st.session_state.resultados)
