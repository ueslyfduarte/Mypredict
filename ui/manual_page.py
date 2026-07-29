# ui/manual_page.py — Modo Manual (com prateleiras e sem dados obrigatórios)
import streamlit as st
from ui.styles import injetar_css
from ui.components import show_results_manual
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from core.calculations import executar_manual

PRATELEIRAS = ["Elite", "Alta", "Media", "Baixa", "Critica"]

def render_manual():
    injetar_css()
    st.markdown('<div class="main-title">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">ANÁLISE PREDITIVA PREMIUM</div>', unsafe_allow_html=True)

    # Inicializar estado com padrões neutros ou vazios
    defaults = {
        'time_casa': '', 'time_fora': '',
        'pos_casa': 1, 'pos_fora': 2,
        'prat_casa': 'Media', 'prat_fora': 'Media',
        'jogos_casa': [], 'jogos_fora': [],
        'ovrall_casa': {}, 'ovrall_fora': {},
        'ic_casa': {}, 'ic_fora': {},
        'media_gols_casa': MEDIA_GOLS_CASA_LIGA,
        'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
        'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
        'media_esc_casa': 5.0, 'media_esc_fora': 4.5,
        'prateleiras_extra': {}
    }
    for chave, padrao in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = padrao

    # --- Times ---
    st.markdown('<div class="section-title">⚔️ TIMES</div>', unsafe_allow_html=True)
    col_casa, col_fora = st.columns(2)
    with col_casa:
        st.markdown('<div class="team-block home">', unsafe_allow_html=True)
        st.markdown('<div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        st.text_input("Nome", key="time_casa_input", value=st.session_state.time_casa, placeholder="Time da Casa")
        st.number_input("Posição", 1, 20, value=st.session_state.pos_casa, key="pos_casa_input")
        st.selectbox("Prateleira", PRATELEIRAS, index=PRATELEIRAS.index(st.session_state.prat_casa), key="prat_casa_input")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora:
        st.markdown('<div class="team-block away">', unsafe_allow_html=True)
        st.markdown('<div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        st.text_input("Nome", key="time_fora_input", value=st.session_state.time_fora, placeholder="Time Visitante")
        st.number_input("Posição", 1, 20, value=st.session_state.pos_fora, key="pos_fora_input")
        st.selectbox("Prateleira", PRATELEIRAS, index=PRATELEIRAS.index(st.session_state.prat_fora), key="prat_fora_input")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- IMA (com prateleira do adversário) ---
    st.markdown('<div class="section-title">⚡ IMA</div>', unsafe_allow_html=True)
    st.caption("Preencha os últimos 10 jogos. Deixe em branco se não quiser usar (IMA neutro = 50).")

    def cor_resultado(res):
        if res == 'V': return '🟢 V'
        elif res == 'E': return '🟡 E'
        elif res == 'D': return '🔴 D'
        return '⚪'

    col_jogos_casa, col_jogos_fora = st.columns(2)
    for lado, chave_jogos in [('🏠 Casa', 'jogos_casa'), ('🏟️ Fora', 'jogos_fora')]:
        with col_jogos_casa if chave_jogos == 'jogos_casa' else col_jogos_fora:
            st.markdown(f"**{lado}**")
            jogos = st.session_state[chave_jogos]
            for i in range(10):
                jogo_atual = jogos[i] if i < len(jogos) else {}
                c1, c2, c3, c4 = st.columns([1, 2, 1.5, 1])
                # Resultado
                res_atual = jogo_atual.get('resultado', '')
                res_idx = ["", "V", "E", "D"].index(res_atual) if res_atual in ["V","E","D"] else 0
                res = c1.selectbox("", ["", "V", "E", "D"], index=res_idx,
                                   key=f"man_{chave_jogos}_res_{i}", label_visibility="collapsed")
                c1.markdown(f'<span style="font-size:1.2rem;">{cor_resultado(res)}</span>', unsafe_allow_html=True)
                # Prateleira do adversário
                prat_idx = PRATELEIRAS.index(jogo_atual.get('prateleira_adv', 'Media'))
                prat_adv = c2.selectbox("Prat. adv.", PRATELEIRAS, index=prat_idx,
                                        key=f"man_{chave_jogos}_prat_{i}", label_visibility="collapsed")
                # Mandante
                mand = c3.checkbox("Mandante", value=jogo_atual.get('mandante', False),
                                   key=f"man_{chave_jogos}_mand_{i}")
                # Nome adversário (opcional)
                adv_nome = c4.text_input("Adv.", value=jogo_atual.get('adversario', ''),
                                         key=f"man_{chave_jogos}_adv_{i}", placeholder="Nome",
                                         label_visibility="collapsed")
                if res and res != "":
                    novo = {"resultado": res, "prateleira_adv": prat_adv, "mandante": mand, "adversario": adv_nome}
                    if i < len(jogos):
                        jogos[i] = novo
                    else:
                        jogos.append(novo)
            # Ajustar tamanho da lista
            st.session_state[chave_jogos] = [j for j in jogos if j.get('resultado')][:10]

    # --- OVRall (com valores padrão da liga) ---
    st.markdown('<div class="section-title">📈 OVRall</div>', unsafe_allow_html=True)
    st.caption("Ajuste as métricas com os botões +/-. Valores padrão da liga já preenchidos.")

    dimensoes = {
        "⚔️ ATAQUE": [("Gols marcados", "gols_media", 1.5), ("xG", "xg_media", 1.2),
                      ("Finalizações alvo", "finalizacoes_alvo_media", 4.0), ("Conversão %", "conversao", 12.0)],
        "🛡️ DEFESA": [("Gols sofridos", "gols_sofridos_media", 1.2), ("xGA", "xga_media", 1.1),
                       ("Finalizações alvo sofridas", "finalizacoes_alvo_sofridas_media", 3.5),
                       ("Desarmes+Intercept.", "desarmes_intercep_media", 15.0)],
        "🧩 MEIO-CAMPO": [("Posse %", "posse_media", 50.0), ("Passes certos %", "passes_certos_pct", 80.0),
                         ("Passes-chave", "passes_chave_media", 2.0), ("Assistências", "assistencias_media", 1.5),
                         ("Chutes totais", "chutes_media", 12.0)],
        "📏 CONSISTÊNCIA": [("Desvio padrão pontos", "desvio_pontos", 0.5), ("Desvio gols pró", "desvio_gols_pro", 0.4),
                           ("Desvio gols sofridos", "desvio_gols_sofridos", 0.4),
                           ("Jogos sem sofrer gol %", "clean_sheets_pct", 35.0)],
        "🔄 RESILIÊNCIA": [("Pontos após sair atrás", "pontos_pos_desvantagem_media", 1.2),
                          ("Gols últimos 15 min", "gols_ultimos_15min_media", 0.3),
                          ("Pontos após derrota", "pontos_apos_derrota_media", 1.0),
                          ("Dif. aprovação casa-fora %", "diff_aprov_casa_fora", 15.0),
                          ("Viradas a favor %", "aprov_viradas_favor", 12.0),
                          ("Viradas contra %", "aprov_viradas_contra", 10.0)],
        "🌐 ESTATÍSTICAS GLOBAIS": [("Gols 1º tempo (média)", "gols_ht_media", 0.6),
                                    ("Gols sofridos 1º tempo", "gols_ht_sofridos_media", 0.4),
                                    ("Escanteios (média)", "escanteios_media", 5.5),
                                    ("Escanteios sofridos", "escanteios_sofridos_media", 4.5)]
    }

    col_casa_ovr, col_fora_ovr = st.columns(2)
    for time_key, lado in [('ovrall_casa', '🏠 CASA'), ('ovrall_fora', '🏟️ FORA')]:
        with col_casa_ovr if time_key == 'ovrall_casa' else col_fora_ovr:
            st.markdown(f'<div class="team-block {"home" if time_key == "ovrall_casa" else "away"}">', unsafe_allow_html=True)
            st.markdown(f'<div class="team-title {"home-title" if time_key == "ovrall_casa" else "away-title"}">{lado}</div>', unsafe_allow_html=True)
            for nome_dim, indicadores in dimensoes.items():
                st.markdown(f'<div class="dimension-title">{nome_dim}</div>', unsafe_allow_html=True)
                for label, key, padrao in indicadores:
                    val = st.session_state[time_key].get(key, padrao)
                    novo = st.number_input(label, value=float(val), step=0.1,
                                           key=f"{time_key}_{key}", label_visibility="visible")
                    st.session_state[time_key][key] = novo
            st.markdown('</div>', unsafe_allow_html=True)

    # --- IC (com padrões neutros) ---
    st.markdown('<div class="section-title">🧠 IC</div>', unsafe_allow_html=True)
    st.caption("Índice de Contexto. Valores padrão neutros (50%).")

    metricas_ic = [
        ("Confronto direto %", "confronto_direto", 50.0),
        ("Mesmo escalão %", "mesmo_escalao", 50.0),
        ("Contra escalão adversário %", "contra_escalao_adversario", 50.0),
        ("Fator casa %", "fator_casa", 50.0),
        ("Odds (decimal)", "odds", 2.0),
    ]
    col_casa_ic, col_fora_ic = st.columns(2)
    for time_key, lado in [('ic_casa', '🏠 CASA'), ('ic_fora', '🏟️ FORA')]:
        with col_casa_ic if time_key == 'ic_casa' else col_fora_ic:
            st.markdown(f'<div class="team-block {"home" if time_key == "ic_casa" else "away"}">', unsafe_allow_html=True)
            st.markdown(f'<div class="team-title {"home-title" if time_key == "ic_casa" else "away-title"}">{lado}</div>', unsafe_allow_html=True)
            for label, key, padrao in metricas_ic:
                val = st.session_state[time_key].get(key, padrao)
                novo = st.number_input(label, value=float(val), step=1.0 if key != 'odds' else 0.1,
                                       key=f"{time_key}_{key}", label_visibility="visible")
                st.session_state[time_key][key] = novo
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Médias da Liga ---
    st.markdown('<div class="section-title">📊 MÉDIAS DA LIGA</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.number_input("Gols casa", value=st.session_state.media_gols_casa, key="mgc")
        st.number_input("Gols HT casa", value=st.session_state.media_ht_casa, key="mhtc")
        st.number_input("Escanteios casa", value=st.session_state.media_esc_casa, key="mecc")
    with c2:
        st.number_input("Gols fora", value=st.session_state.media_gols_fora, key="mgf")
        st.number_input("Gols HT fora", value=st.session_state.media_ht_fora, key="mhtf")
        st.number_input("Escanteios fora", value=st.session_state.media_esc_fora, key="mecf")

    # --- Gerar ---
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    if st.button("🔥 GERAR MYPREDICT VALUE", use_container_width=True):
        # Transferir valores da interface para o estado
        st.session_state.time_casa = st.session_state.time_casa_input or "Time da Casa"
        st.session_state.time_fora = st.session_state.time_fora_input or "Time Visitante"
        st.session_state.pos_casa = st.session_state.pos_casa_input
        st.session_state.pos_fora = st.session_state.pos_fora_input
        st.session_state.prat_casa = st.session_state.prat_casa_input
        st.session_state.prat_fora = st.session_state.prat_fora_input
        st.session_state.media_gols_casa = st.session_state.mgc
        st.session_state.media_gols_fora = st.session_state.mgf
        st.session_state.media_ht_casa = st.session_state.mhtc
        st.session_state.media_ht_fora = st.session_state.mhtf
        st.session_state.media_esc_casa = st.session_state.mecc
        st.session_state.media_esc_fora = st.session_state.mecf

        dados = {k: v for k, v in st.session_state.items() if k in [
            'time_casa', 'time_fora', 'pos_casa', 'pos_fora',
            'prat_casa', 'prat_fora',
            'jogos_casa', 'jogos_fora',
            'ovrall_casa', 'ovrall_fora', 'ic_casa', 'ic_fora',
            'media_gols_casa', 'media_gols_fora',
            'media_ht_casa', 'media_ht_fora',
            'media_esc_casa', 'media_esc_fora',
            'prateleiras_extra'
        ]}

        res, err = executar_manual(dados)
        if err:
            st.error(err)
        else:
            st.session_state.resultados = res
            st.rerun()

    # Exibir resultados
    if 'resultados' in st.session_state and st.session_state.resultados is not None:
        show_results_manual(st.session_state.resultados)
