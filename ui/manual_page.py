# ui/manual_page.py — Painel EA Sports completo com comparativos e alertas
import streamlit as st
import pandas as pd
import math
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
        'time_casa_input': '', 'time_fora_input': '',
        'pos_casa': 1, 'pos_fora': 2,
        'pos_casa_input': 1, 'pos_fora_input': 2,
        'prat_casa': 'Media', 'prat_fora': 'Media',
        'prat_casa_input': 'Media', 'prat_fora_input': 'Media',
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
    prat_real_casa = obter_prateleira(st.session_state.pos_casa_input)
    prat_real_fora = obter_prateleira(st.session_state.pos_fora_input)

    st.markdown('<div class="confronto-container">', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="time-card {"destaque" if prat_real_casa in ["Elite","Alta"] else ""}">
            <div class="time-nome">{st.session_state.time_casa_input or "Time da Casa"}</div>
            <div class="time-detalhe">Posição: {st.session_state.pos_casa_input} | Real: {prat_real_casa}</div>
            <div class="time-detalhe">Projetada: {st.session_state.prat_casa_input}</div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('<div class="vs-divider">VS</div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="time-card {"destaque" if prat_real_fora in ["Elite","Alta"] else ""}">
            <div class="time-nome">{st.session_state.time_fora_input or "Time Visitante"}</div>
            <div class="time-detalhe">Posição: {st.session_state.pos_fora_input} | Real: {prat_real_fora}</div>
            <div class="time-detalhe">Projetada: {st.session_state.prat_fora_input}</div>
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
        (col_att_casa, atributos_casa, st.session_state.time_casa_input or "Casa"),
        (col_att_fora, atributos_fora, st.session_state.time_fora_input or "Fora")
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

    # ====================== NOVAS SEÇÕES ANALÍTICAS ======================

    # 1. COMPARATIVO REAL (valores absolutos)
    st.markdown('<div class="section-title">📋 COMPARATIVO REAL</div>', unsafe_allow_html=True)
    col_r1, col_r2, col_r3 = st.columns(3)
    metricas_reais = [
        ("Gols Marcados (média)", "gols_media", 1.5),
        ("Gols Sofridos (média)", "gols_sofridos_media", 1.2),
        ("Posse de Bola (%)", "posse_media", 50.0),
        ("Finalizações Alvo (média)", "finalizacoes_alvo_media", 4.0),
        ("xG (média)", "xg_media", 1.2),
        ("Chutes Totais (média)", "chutes_media", 12.0),
    ]
    for i, (label, chave, padrao) in enumerate(metricas_reais):
        val_casa = pegar_valor(st.session_state.ovrall_casa, chave, padrao)
        val_fora = pegar_valor(st.session_state.ovrall_fora, chave, padrao)
        with col_r1 if i % 3 == 0 else (col_r2 if i % 3 == 1 else col_r3):
            st.metric(label=label, value=f"{val_casa:.1f}" if val_casa is not None else "-", delta=f"vs {val_fora:.1f}" if val_fora is not None else None)

    # 2. COMPARATIVOS DIRETOS (Ataque vs Defesa, etc.)
    st.markdown('<div class="section-title">⚔️ CONFRONTOS DIRETOS DE FORÇA</div>', unsafe_allow_html=True)
    def calc_confronto(nome, atk_casa, def_fora, atk_fora, def_casa):
        casa_force = atk_casa * (def_fora / MEDIA_GOLS_FORA_LIGA) if def_fora else 0
        fora_force = atk_fora * (def_casa / MEDIA_GOLS_CASA_LIGA) if def_casa else 0
        return f"{casa_force:.2f} vs {fora_force:.2f}"

    gols_casa = pegar_valor(st.session_state.ovrall_casa, 'gols_media', 1.5)
    gols_sofridos_casa = pegar_valor(st.session_state.ovrall_casa, 'gols_sofridos_media', 1.2)
    gols_fora = pegar_valor(st.session_state.ovrall_fora, 'gols_media', 1.2)
    gols_sofridos_fora = pegar_valor(st.session_state.ovrall_fora, 'gols_sofridos_media', 1.5)

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown("**Ataque Casa vs Defesa Fora**")
        st.metric("", calc_confronto("", gols_casa, gols_sofridos_fora, gols_fora, gols_sofridos_casa).split(" vs ")[0])
    with col_f2:
        st.markdown("**Defesa Casa vs Ataque Fora**")
        st.metric("", calc_confronto("", gols_casa, gols_sofridos_fora, gols_fora, gols_sofridos_casa).split(" vs ")[1])
    with col_f3:
        st.markdown("**Meio‑Campo**")
        posse_casa = pegar_valor(st.session_state.ovrall_casa, 'posse_media', 50)
        posse_fora = pegar_valor(st.session_state.ovrall_fora, 'posse_media', 50)
        st.metric("Posse", f"{posse_casa:.0f}%", delta=f"vs {posse_fora:.0f}%")

    # 3. RESUMO ÚLTIMOS 5 JOGOS
    st.markdown('<div class="section-title">⏳ ÚLTIMOS 5 JOGOS (Médias Móveis)</div>', unsafe_allow_html=True)
    def resumo_ultimos_5(jogos, eh_mandante=True):
        if len(jogos) < 5:
            return None
        ultimos = jogos[:5]
        gols_pro = [j.get('gols_pro', 0) for j in ultimos]
        gols_contra = [j.get('gols_contra', 0) for j in ultimos]
        media_gols = sum(gols_pro) / 5
        media_sofridos = sum(gols_contra) / 5
        btts = sum(1 for gp, gc in zip(gols_pro, gols_contra) if gp > 0 and gc > 0) / 5
        over25 = sum(1 for gp, gc in zip(gols_pro, gols_contra) if gp + gc > 2.5) / 5
        pontos = sum(3 if gp > gc else (1 if gp == gc else 0) for gp, gc in zip(gols_pro, gols_contra))
        aprov = pontos / 15 * 100
        return {
            'media_gols': media_gols,
            'media_sofridos': media_sofridos,
            'btts': btts,
            'over25': over25,
            'aproveitamento': aprov
        }

    resumo_casa = resumo_ultimos_5(st.session_state.jogos_casa)
    resumo_fora = resumo_ultimos_5(st.session_state.jogos_fora)

    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.markdown("**Casa**")
        if resumo_casa:
            st.metric("Gols Marcados", f"{resumo_casa['media_gols']:.2f}")
            st.metric("Gols Sofridos", f"{resumo_casa['media_sofridos']:.2f}")
            st.metric("BTTS %", f"{resumo_casa['btts']:.0%}")
            st.metric("Over 2.5 %", f"{resumo_casa['over25']:.0%}")
            st.metric("Aproveitamento", f"{resumo_casa['aproveitamento']:.0f}%")
        else:
            st.caption("Dados insuficientes.")
    with col_u2:
        st.markdown("**Fora**")
        if resumo_fora:
            st.metric("Gols Marcados", f"{resumo_fora['media_gols']:.2f}")
            st.metric("Gols Sofridos", f"{resumo_fora['media_sofridos']:.2f}")
            st.metric("BTTS %", f"{resumo_fora['btts']:.0%}")
            st.metric("Over 2.5 %", f"{resumo_fora['over25']:.0%}")
            st.metric("Aproveitamento", f"{resumo_fora['aproveitamento']:.0f}%")
        else:
            st.caption("Dados insuficientes.")

    # 4. PLACAR PROVÁVEL
    st.markdown('<div class="section-title">🎯 PLACAR PROVÁVEL</div>', unsafe_allow_html=True)
    gols_esp_casa = gols_casa * (gols_sofridos_fora / MEDIA_GOLS_FORA_LIGA)
    gols_esp_fora = gols_fora * (gols_sofridos_casa / MEDIA_GOLS_CASA_LIGA)
    st.markdown(f"<h2 style='text-align:center; color:#ffd700;'>{gols_esp_casa:.2f} - {gols_esp_fora:.2f}</h2>", unsafe_allow_html=True)

    # 5. INDICADORES DE CONSISTÊNCIA E RESILIÊNCIA
    st.markdown('<div class="section-title">📈 CONSISTÊNCIA & RESILIÊNCIA</div>', unsafe_allow_html=True)
    col_cons1, col_cons2 = st.columns(2)
    with col_cons1:
        desv_casa = pegar_valor(st.session_state.ovrall_casa, 'desvio_pontos', 0.5)
        if desv_casa < 0.4:
            st.success("Casa: muito consistente (desvio baixo)")
        elif desv_casa < 0.8:
            st.info("Casa: consistência moderada")
        else:
            st.warning("Casa: irregular (desvio alto)")
        res_casa = pegar_valor(st.session_state.ovrall_casa, 'pontos_pos_desvantagem_media', 1.0)
        if res_casa > 1.5:
            st.success("Boa recuperação quando sai atrás")
        elif res_casa < 0.5:
            st.error("Dificuldade em reagir após desvantagem")
    with col_cons2:
        desv_fora = pegar_valor(st.session_state.ovrall_fora, 'desvio_pontos', 0.5)
        if desv_fora < 0.4:
            st.success("Fora: muito consistente")
        elif desv_fora < 0.8:
            st.info("Fora: consistência moderada")
        else:
            st.warning("Fora: irregular")
        res_fora = pegar_valor(st.session_state.ovrall_fora, 'pontos_pos_desvantagem_media', 1.0)
        if res_fora > 1.5:
            st.success("Boa recuperação quando sai atrás")
        elif res_fora < 0.5:
            st.error("Dificuldade em reagir")

    # 6. MOMENTUM (seta de evolução)
    st.markdown('<div class="section-title">📈 MOMENTUM (IMA Recente)</div>', unsafe_allow_html=True)
    # Nota: o IMA ainda não está calculado (só após GERAR). Podemos usar uma estimativa simples baseada nos últimos 3 jogos.
    def momentum_simples(jogos):
        if len(jogos) < 3:
            return None
        pts_ultimos3 = sum(3 if j['resultado']=='V' else (1 if j['resultado']=='E' else 0) for j in jogos[:3])
        pts_anteriores3 = sum(3 if j['resultado']=='V' else (1 if j['resultado']=='E' else 0) for j in jogos[3:6]) if len(jogos)>=6 else 4.5
        if pts_ultimos3 > pts_anteriores3 + 1:
            return "⬆️ Em alta"
        elif pts_ultimos3 < pts_anteriores3 - 1:
            return "⬇️ Em queda"
        else:
            return "➡️ Estável"
    mom_casa = momentum_simples(st.session_state.jogos_casa)
    mom_fora = momentum_simples(st.session_state.jogos_fora)
    col_mom1, col_mom2 = st.columns(2)
    with col_mom1:
        st.write(f"Casa: {mom_casa if mom_casa else 'Indisponível'}")
    with col_mom2:
        st.write(f"Fora: {mom_fora if mom_fora else 'Indisponível'}")

    # 7. GRÁFICO RADAR (expandível)
    with st.expander("📡 Gráfico Radar dos Atributos", expanded=False):
        # Preparar dados para radar
        categorias = list(atributos_casa.keys())
        valores_casa = [atributos_casa[c] for c in categorias]
        valores_fora = [atributos_fora[c] for c in categorias]
        df_casa = pd.DataFrame({'Categoria': categorias, 'Valor': valores_casa, 'Time': 'Casa'})
        df_fora = pd.DataFrame({'Categoria': categorias, 'Valor': valores_fora, 'Time': 'Fora'})
        df_radar = pd.concat([df_casa, df_fora])
        radar_chart = alt.Chart(df_radar).mark_line(point=True).encode(
            theta=alt.Theta('Categoria:N', stack=True),
            radius=alt.Radius('Valor:Q', scale=alt.Scale(zero=True, domain=[0,100])),
            color='Time:N'
        ).properties(width=200, height=200).facet(column='Time:N').resolve_scale(radius='independent')
        st.altair_chart(radar_chart, use_container_width=True)
        st.caption("Valores próximos a 100 indicam força máxima na categoria.")

    # Edição detalhada OVRall (mantida)
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
