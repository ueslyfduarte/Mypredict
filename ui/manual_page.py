# ui/manual_page.py — Painel EA Sports com Prateleira Projetada
import streamlit as st
from ui.styles import injetar_css
from ui.components import show_results_manual
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from core.calculations import executar_manual
from core.ratings import obter_prateleira

PRATELEIRAS = ["Elite", "Alta", "Media", "Baixa", "Critica"]

def render_manual():
    injetar_css()
    st.markdown('<div class="main-title">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Painel de Análise Tática</div>', unsafe_allow_html=True)

    # Inicializar estado
    defaults = {
        'time_casa': '', 'time_fora': '',
        'pos_casa': 1, 'pos_fora': 2,
        'prat_casa': 'Media', 'prat_fora': 'Media',  # Prateleira Projetada
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

    # --- CONFRONTO (Cards) ---
    prat_real_casa = obter_prateleira(st.session_state.pos_casa)
    prat_real_fora = obter_prateleira(st.session_state.pos_fora)

    st.markdown('<div class="confronto-container">', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="time-card {"destaque" if prat_real_casa in ["Elite","Alta"] else ""}">
            <div class="time-nome">{st.session_state.time_casa or "Time da Casa"}</div>
            <div class="time-detalhe">Posição: {st.session_state.pos_casa} | Real: {prat_real_casa}</div>
            <div class="time-detalhe">Projetada: {st.session_state.prat_casa}</div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('<div class="vs-divider">VS</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="time-card {"destaque" if prat_real_fora in ["Elite","Alta"] else ""}">
            <div class="time-nome">{st.session_state.time_fora or "Time Visitante"}</div>
            <div class="time-detalhe">Posição: {st.session_state.pos_fora} | Real: {prat_real_fora}</div>
            <div class="time-detalhe">Projetada: {st.session_state.prat_fora}</div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Edição rápida
    with st.expander("⚙️ Editar Times", expanded=False):
        col_casa, col_fora = st.columns(2)
        with col_casa:
            st.text_input("Nome", key="time_casa_input", value=st.session_state.time_casa, placeholder="Time da Casa")
            st.number_input("Posição", 1, 20, value=st.session_state.pos_casa, key="pos_casa_input")
            st.selectbox("Prateleira Projetada", PRATELEIRAS,
                         index=PRATELEIRAS.index(st.session_state.prat_casa), key="prat_casa_input")
        with col_fora:
            st.text_input("Nome", key="time_fora_input", value=st.session_state.time_fora, placeholder="Time Visitante")
            st.number_input("Posição", 1, 20, value=st.session_state.pos_fora, key="pos_fora_input")
            st.selectbox("Prateleira Projetada", PRATELEIRAS,
                         index=PRATELEIRAS.index(st.session_state.prat_fora), key="prat_fora_input")

    # --- PAINEL DE ATRIBUTOS (OVRall) ---
    st.markdown('<div class="section-title">📊 ATRIBUTOS DA TEMPORADA</div>', unsafe_allow_html=True)

    def pegar_valor(dic, chave, padrao):
        v = dic.get(chave)
        return v if v is not None else padrao

    atributos_casa = {
        "ATAQUE": pegar_valor(st.session_state.ovrall_casa, 'gols_media', 1.5) * 20,
        "DEFESA": (2.5 - pegar_valor(st.session_state.ovrall_casa, 'gols_sofridos_media', 1.2)) * 25,
        "MEIO-CAMPO": pegar_valor(st.session_state.ovrall_casa, 'posse_media', 50),
        "CONSISTÊNCIA": max(0, 80 - pegar_valor(st.session_state.ovrall_casa, 'desvio_pontos', 0.5)*30),
        "RESILIÊNCIA": pegar_valor(st.session_state.ovrall_casa, 'pontos_pos_desvantagem_media', 1.0) * 25,
        "GLOBAL": pegar_valor(st.session_state.ovrall_casa, 'escanteios_media', 5.0) * 10,
    }
    atributos_fora = {
        "ATAQUE": pegar_valor(st.session_state.ovrall_fora, 'gols_media', 1.5) * 20,
        "DEFESA": (2.5 - pegar_valor(st.session_state.ovrall_fora, 'gols_sofridos_media', 1.2)) * 25,
        "MEIO-CAMPO": pegar_valor(st.session_state.ovrall_fora, 'posse_media', 50),
        "CONSISTÊNCIA": max(0, 80 - pegar_valor(st.session_state.ovrall_fora, 'desvio_pontos', 0.5)*30),
        "RESILIÊNCIA": pegar_valor(st.session_state.ovrall_fora, 'pontos_pos_desvantagem_media', 1.0) * 25,
        "GLOBAL": pegar_valor(st.session_state.ovrall_fora, 'escanteios_media', 5.0) * 10,
    }

    for dic in [atributos_casa, atributos_fora]:
        for k in dic:
            dic[k] = max(0, min(100, dic[k]))

    col_att_casa, col_att_fora = st.columns(2)
    for col, atts, nome_time in [
        (col_att_casa, atributos_casa, st.session_state.time_casa or "Casa"),
        (col_att_fora, atributos_fora, st.session_state.time_fora or "Fora")
    ]:
        with col:
            st.markdown(f'<h3 style="color:#fff; text-align:center;">{nome_time}</h3>', unsafe_allow_html=True)
            for nome, valor in atts.items():
                cor_classe = {
                    "ATAQUE": "ataque", "DEFESA": "defesa", "MEIO-CAMPO": "meio",
                    "CONSISTÊNCIA": "cons", "RESILIÊNCIA": "res", "GLOBAL": "global"
                }.get(nome, "ataque")
                st.markdown(f'''
                <div class="atributo-card">
                    <div class="atributo-header">
                        <span class="atributo-nome">{nome}</span>
                        <span class="atributo-valor">{int(valor)}</span>
                    </div>
                    <div class="atributo-barra">
                        <div class="atributo-barra-preenchimento {cor_classe}" style="width:{valor}%;"></div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

    # Edição detalhada OVRall
    with st.expander("✏️ Ajustar Atributos Detalhados", expanded=False):
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
                st.markdown(f'**{lado}**')
                for nome_dim, indicadores in dimensoes.items():
                    st.caption(nome_dim)
                    for label, key, padrao in indicadores:
                        val = st.session_state[time_key].get(key, padrao)
                        novo = st.number_input(label, value=float(val), step=0.1,
                                               key=f"{time_key}_{key}", label_visibility="visible")
                        st.session_state[time_key][key] = novo

    # --- ÚLTIMOS JOGOS (IMA) ---
    st.markdown('<div class="section-title">⚡ ÚLTIMOS JOGOS (IMA)</div>', unsafe_allow_html=True)
    col_jogos_casa, col_jogos_fora = st.columns(2)
    for lado, chave_jogos in [('🏠 Casa', 'jogos_casa'), ('🏟️ Fora', 'jogos_fora')]:
        with col_jogos_casa if chave_jogos == 'jogos_casa' else col_jogos_fora:
            st.markdown(f'<h4 style="color:#fff;">{lado}</h4>', unsafe_allow_html=True)
            jogos = st.session_state[chave_jogos]
            html = '<table class="jogos-tabela"><tr><th>Res.</th><th>Prat. Adv.</th><th>Mandante</th></tr>'
            for i in range(10):
                j = jogos[i] if i < len(jogos) else {}
                res = j.get('resultado', '-')
                prat_adv = j.get('prateleira_adv', '-')
                mand = 'Sim' if j.get('mandante') else 'Não'
                html += f'<tr><td class="resultado-{res}">{res}</td><td>{prat_adv}</td><td>{mand}</td></tr>'
            html += '</table>'
            st.markdown(html, unsafe_allow_html=True)
            if st.button(f"Editar {lado}", key=f"edit_{chave_jogos}"):
                st.session_state[f"editando_{chave_jogos}"] = True
            if st.session_state.get(f"editando_{chave_jogos}"):
                with st.form(key=f"form_{chave_jogos}"):
                    novos_jogos = []
                    for i in range(10):
                        j = jogos[i] if i < len(jogos) else {}
                        c1, c2, c3 = st.columns([1, 2, 1])
                        res = c1.selectbox("Res.", ["", "V", "E", "D"],
                                           index=["", "V", "E", "D"].index(j.get('resultado', '')) if j.get('resultado') in ["V","E","D"] else 0,
                                           key=f"{chave_jogos}_{i}_res")
                        prat_adv = c2.selectbox("Prat. adv.", PRATELEIRAS,
                                                index=PRATELEIRAS.index(j.get('prateleira_adv', 'Media')),
                                                key=f"{chave_jogos}_{i}_prat")
                        mand = c3.checkbox("Mandante", value=j.get('mandante', False), key=f"{chave_jogos}_{i}_mand")
                        if res:
                            novos_jogos.append({"resultado": res, "prateleira_adv": prat_adv, "mandante": mand})
                    if st.form_submit_button("Salvar"):
                        st.session_state[chave_jogos] = novos_jogos
                        st.session_state[f"editando_{chave_jogos}"] = False
                        st.rerun()

    # --- IC ---
    with st.expander("🧠 Índice de Contexto (IC)", expanded=False):
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
                st.markdown(f'**{lado}**')
                for label, key, padrao in metricas_ic:
                    val = st.session_state[time_key].get(key, padrao)
                    novo = st.number_input(label, value=float(val), step=1.0 if key != 'odds' else 0.1,
                                           key=f"{time_key}_{key}", label_visibility="visible")
                    st.session_state[time_key][key] = novo

    # --- Médias da Liga ---
    with st.expander("📊 Médias da Liga", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.number_input("Gols casa", value=st.session_state.media_gols_casa, key="mgc")
            st.number_input("Gols HT casa", value=st.session_state.media_ht_casa, key="mhtc")
            st.number_input("Escanteios casa", value=st.session_state.media_esc_casa, key="mecc")
        with c2:
            st.number_input("Gols fora", value=st.session_state.media_gols_fora, key="mgf")
            st.number_input("Gols HT fora", value=st.session_state.media_ht_fora, key="mhtf")
            st.number_input("Escanteios fora", value=st.session_state.media_esc_fora, key="mecf")

    # --- GERAR ---
    st.markdown('<div style="margin: 30px 0;"></div>', unsafe_allow_html=True)
    if st.button("🔥 GERAR ANÁLISE COMPLETA", use_container_width=True):
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
            'time_casa', 'time_fora', 'pos_casa', 'pos_fora', 'prat_casa', 'prat_fora',
            'jogos_casa', 'jogos_fora', 'ovrall_casa', 'ovrall_fora', 'ic_casa', 'ic_fora',
            'media_gols_casa', 'media_gols_fora', 'media_ht_casa', 'media_ht_fora',
            'media_esc_casa', 'media_esc_fora', 'prateleiras_extra'
        ]}
        res, err = executar_manual(dados)
        if err:
            st.error(err)
        else:
            st.session_state.resultados = res
            st.rerun()

    if 'resultados' in st.session_state and st.session_state.resultados is not None:
        show_results_manual(st.session_state.resultados)
