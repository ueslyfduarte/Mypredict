# ui/components.py — Componentes reutilizáveis da interface (com análise completa detalhada)
import streamlit as st
import pandas as pd
from config import THRESHOLD_GOLD, THRESHOLD_VALUE, THRESHOLD_FAVORITO, MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

def show_api_usage(uso, limite):
    if uso is not None:
        porcentagem = uso / limite if limite else 0
        cor = "#00ff7f" if porcentagem < 0.5 else ("#ffaa00" if porcentagem < 0.8 else "#ff4d4d")
        st.markdown(f'<div style="display:flex;justify-content:center;"><div style="display:inline-flex;align-items:center;gap:8px;padding:6px 16px;background:rgba(20,20,35,0.9);border-radius:20px;"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{cor};"></span> API: {uso}/{limite}</div></div>', unsafe_allow_html=True)

def get_selo(prob):
    if prob is None:
        return ""
    if prob >= THRESHOLD_GOLD:
        return "🥇 MyPredict GOLD"
    elif prob >= THRESHOLD_VALUE:
        return "✅ Value"
    elif prob >= THRESHOLD_FAVORITO:
        return "🔵 Favorito"
    else:
        return ""

# Funções auxiliares (mesmas do manual_page, agora replicadas para a análise)
def pegar_valor(dic, chave, padrao):
    v = dic.get(chave)
    return v if v is not None else padrao

def resumo_ultimos_5(jogos):
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

def show_results_manual(res):
    # Resgatar dados da sessão para enriquecer a análise
    # Seção do Contraste Tático
if 'tactical' in res:
    st.markdown("## 🧪 Contraste Tático (MPV Dye)")
    
    tactical = res['tactical']
    
    # Mapa de calor
    st.image(f"data:image/png;base64,{tactical['heatmap']}", 
             caption="Zonas de Desequilíbrio — Azul: Vantagem Casa, Vermelho: Vantagem Fora",
             use_container_width=True)
    
    # Rotas Críticas
    st.markdown("### 🎯 Rotas Críticas do Jogo")
    for dim, delta, interpretation in tactical['critical_routes']:
        if delta > 0:
            st.success(interpretation)
        else:
            st.error(interpretation)
    
    # Tabela de Deltas
    st.markdown("### 📊 Diferencial por Dimensão")
    deltas_df = pd.DataFrame(
        tactical['deltas'].items(), 
        columns=['Dimensão', 'Δ (Casa - Fora)']
    ).sort_values('Δ (Casa - Fora)', key=abs, ascending=False)
    
    st.dataframe(deltas_df, use_container_width=True)
    ovr_casa = st.session_state.get('ovrall_casa', {})
    ovr_fora = st.session_state.get('ovrall_fora', {})
    jogos_casa = st.session_state.get('jogos_casa', [])
    jogos_fora = st.session_state.get('jogos_fora', [])
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']
    media_gols_casa = st.session_state.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA)
    media_gols_fora = st.session_state.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)

    # Cabeçalho do confronto
    st.markdown(f"""
    <div style="text-align:center; margin:20px 0;">
        <span style="font-size:2rem; font-weight:900; color:#ffd700;">{nome_casa}</span>
        <span style="font-size:1.5rem; color:#888; margin:0 12px;">vs</span>
        <span style="font-size:2rem; font-weight:900; color:#c0c0c0;">{nome_fora}</span>
    </div>
    """, unsafe_allow_html=True)

    # Indicadores de superação
    st.caption(f"🔺 {nome_casa}: {res.get('prat_proj_casa','?')} → {res.get('prat_real_casa','?')} ({res.get('superacao_casa', 0):+.1f} pts) | 🔺 {nome_fora}: {res.get('prat_proj_fora','?')} → {res.get('prat_real_fora','?')} ({res.get('superacao_fora', 0):+.1f} pts)")

    # MPV Hero (mantido)
    st.markdown('<div class="mpv-hero">', unsafe_allow_html=True)
    st.markdown('<div class="mpv-crown">👑</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:1.2rem; color:#ffd700; letter-spacing:3px; margin-bottom:8px;">MYPREDICT VALUE</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="mpv-main-values">
        <span class="mpv-value home-value">{res['mpv_casa']:.1f}</span>
        <span class="mpv-vs">×</span>
        <span class="mpv-value away-value">{res['mpv_fora']:.1f}</span>
    </div>
    """, unsafe_allow_html=True)
    total = res['mpv_casa'] + res['mpv_fora']
    pct_casa = (res['mpv_casa'] / total * 100) if total > 0 else 50
    pct_fora = 100 - pct_casa
    st.markdown(f"""
    <div class="mpv-bar">
        <div class="mpv-bar-fill" style="width:{pct_casa}%;"></div>
        <div class="mpv-bar-fill away" style="width:{pct_fora}%;"></div>
    </div>
    <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:#aaa;">
        <span>{nome_casa} {res['mpv_casa']:.1f}</span>
        <span>{nome_fora} {res['mpv_fora']:.1f}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Composição (IMA, OVRall, IC)
    st.markdown('<div class="section-title">🧱 COMPOSIÇÃO DO MP VALUE</div>', unsafe_allow_html=True)
    col_ima, col_ovr, col_ic = st.columns(3)
    with col_ima:
        st.markdown(f"""
        <div class="comp-card">
            <h4>⚡ IMA</h4>
            <div class="big" style="color:#ffd700;">{res['ima_casa']:.1f} <span style="font-size:0.8rem;">vs</span> {res['ima_fora']:.1f}</div>
            <div class="small">Peso 1/3</div>
        </div>
        """, unsafe_allow_html=True)
    with col_ovr:
        st.markdown(f"""
        <div class="comp-card">
            <h4>📈 OVRall</h4>
            <div class="big" style="color:#ffd700;">{res['ovrall_casa']:.1f} <span style="font-size:0.8rem;">vs</span> {res['ovrall_fora']:.1f}</div>
            <div class="small">Peso 1/3</div>
        </div>
        """, unsafe_allow_html=True)
    with col_ic:
        st.markdown(f"""
        <div class="comp-card">
            <h4>🧠 IC</h4>
            <div class="big" style="color:#ffd700;">{res['ic_casa']:.1f} <span style="font-size:0.8rem;">vs</span> {res['ic_fora']:.1f}</div>
            <div class="small">Peso 1/3</div>
        </div>
        """, unsafe_allow_html=True)

    # Probabilidades 1X2
    st.subheader("📊 PROBABILIDADES 1X2")
    col1, col2, col3 = st.columns(3)
    col1.metric("🏠 Casa", f"{res['p1']:.1%}")
    col2.metric("🤝 Empate", f"{res['pX']:.1%}")
    col3.metric("🏟️ Fora", f"{res['p2']:.1%}")

    # Mercados com selos
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
                selo = get_selo(prob)
                border = "2px solid gold" if selo.startswith("🥇") else (
                    "1px solid #4CAF50" if "✅" in selo else (
                        "1px solid #2196F3" if "🔵" in selo else "1px solid #888"
                    )
                )
                st.markdown(f"""
                <div style="background:rgba(20,20,35,0.9); border-radius:14px; padding:14px; 
                     border:{border}; text-align:center;">
                    <div style="color:#aaa; font-size:0.8rem;">{nome}</div>
                    <strong style="color:#ffd700; font-size:1.2rem;">{prob:.1%}</strong>
                    <div style="color:#ffd700; font-size:0.7rem; margin-top:4px;">{selo}</div>
                </div>
                """, unsafe_allow_html=True)

    # ========== SEÇÕES MASSIVAS DE ESTATÍSTICAS ==========
    st.markdown("---")
    st.markdown("## 📊 ANÁLISE COMPLETA DETALHADA")
    
    # 1. COMPARATIVO REAL
    st.markdown("### 📋 Comparativo Real")
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
        val_casa = pegar_valor(ovr_casa, chave, padrao)
        val_fora = pegar_valor(ovr_fora, chave, padrao)
        with col_r1 if i % 3 == 0 else (col_r2 if i % 3 == 1 else col_r3):
            st.metric(label=label, value=f"{val_casa:.1f}" if val_casa is not None else "-", delta=f"vs {val_fora:.1f}" if val_fora is not None else None)

    # 2. CONFRONTOS DIRETOS DE FORÇA
    st.markdown("### ⚔️ Confrontos Diretos de Força")
    gols_casa = pegar_valor(ovr_casa, 'gols_media', 1.5)
    gols_sofridos_casa = pegar_valor(ovr_casa, 'gols_sofridos_media', 1.2)
    gols_fora = pegar_valor(ovr_fora, 'gols_media', 1.2)
    gols_sofridos_fora = pegar_valor(ovr_fora, 'gols_sofridos_media', 1.5)

    def calc_confronto(atk_casa, def_fora, atk_fora, def_casa):
        casa_force = atk_casa * (def_fora / media_gols_fora) if def_fora else 0
        fora_force = atk_fora * (def_casa / media_gols_casa) if def_casa else 0
        return casa_force, fora_force

    atk_vs_def = calc_confronto(gols_casa, gols_sofridos_fora, gols_fora, gols_sofridos_casa)
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("Ataque Casa vs Defesa Fora", f"{atk_vs_def[0]:.2f}")
    with col_f2:
        st.metric("Defesa Casa vs Ataque Fora", f"{atk_vs_def[1]:.2f}")
    with col_f3:
        posse_casa = pegar_valor(ovr_casa, 'posse_media', 50)
        posse_fora = pegar_valor(ovr_fora, 'posse_media', 50)
        st.metric("Meio-Campo (Posse)", f"{posse_casa:.0f}%", delta=f"vs {posse_fora:.0f}%")

    # 3. ÚLTIMOS 5 JOGOS
    st.markdown("### ⏳ Últimos 5 Jogos (Médias Móveis)")
    resumo_casa = resumo_ultimos_5(jogos_casa)
    resumo_fora = resumo_ultimos_5(jogos_fora)
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.write(f"**{nome_casa}**")
        if resumo_casa:
            st.metric("Gols Marcados", f"{resumo_casa['media_gols']:.2f}")
            st.metric("Gols Sofridos", f"{resumo_casa['media_sofridos']:.2f}")
            st.metric("BTTS %", f"{resumo_casa['btts']:.0%}")
            st.metric("Over 2.5 %", f"{resumo_casa['over25']:.0%}")
            st.metric("Aproveitamento", f"{resumo_casa['aproveitamento']:.0f}%")
        else:
            st.caption("Dados insuficientes.")
    with col_u2:
        st.write(f"**{nome_fora}**")
        if resumo_fora:
            st.metric("Gols Marcados", f"{resumo_fora['media_gols']:.2f}")
            st.metric("Gols Sofridos", f"{resumo_fora['media_sofridos']:.2f}")
            st.metric("BTTS %", f"{resumo_fora['btts']:.0%}")
            st.metric("Over 2.5 %", f"{resumo_fora['over25']:.0%}")
            st.metric("Aproveitamento", f"{resumo_fora['aproveitamento']:.0f}%")
        else:
            st.caption("Dados insuficientes.")

    # 4. PLACAR PROVÁVEL
    gols_esp_casa = gols_casa * (gols_sofridos_fora / media_gols_fora)
    gols_esp_fora = gols_fora * (gols_sofridos_casa / media_gols_casa)
    st.markdown("### 🎯 Placar Provável")
    st.markdown(f"<h2 style='text-align:center; color:#ffd700;'>{gols_esp_casa:.2f} - {gols_esp_fora:.2f}</h2>", unsafe_allow_html=True)

    # 5. CONSISTÊNCIA & RESILIÊNCIA
    st.markdown("### 📈 Consistência & Resiliência")
    col_cons1, col_cons2 = st.columns(2)
    with col_cons1:
        desv_casa = pegar_valor(ovr_casa, 'desvio_pontos', 0.5)
        if desv_casa < 0.4:
            st.success(f"{nome_casa}: muito consistente (desvio baixo)")
        elif desv_casa < 0.8:
            st.info(f"{nome_casa}: consistência moderada")
        else:
            st.warning(f"{nome_casa}: irregular (desvio alto)")
        res_casa = pegar_valor(ovr_casa, 'pontos_pos_desvantagem_media', 1.0)
        if res_casa > 1.5:
            st.success("Boa recuperação quando sai atrás")
        elif res_casa < 0.5:
            st.error("Dificuldade em reagir após desvantagem")
    with col_cons2:
        desv_fora = pegar_valor(ovr_fora, 'desvio_pontos', 0.5)
        if desv_fora < 0.4:
            st.success(f"{nome_fora}: muito consistente")
        elif desv_fora < 0.8:
            st.info(f"{nome_fora}: consistência moderada")
        else:
            st.warning(f"{nome_fora}: irregular")
        res_fora = pegar_valor(ovr_fora, 'pontos_pos_desvantagem_media', 1.0)
        if res_fora > 1.5:
            st.success("Boa recuperação quando sai atrás")
        elif res_fora < 0.5:
            st.error("Dificuldade em reagir")

    # 6. MOMENTUM
    st.markdown("### 📈 Momentum (IMA Recente)")
    mom_casa = momentum_simples(jogos_casa)
    mom_fora = momentum_simples(jogos_fora)
    col_mom1, col_mom2 = st.columns(2)
    with col_mom1:
        st.write(f"{nome_casa}: {mom_casa if mom_casa else 'Indisponível'}")
    with col_mom2:
        st.write(f"{nome_fora}: {mom_fora if mom_fora else 'Indisponível'}")

    # 7. LINHA DO TEMPO
    st.markdown("### ⚡ Linha do Tempo de Resultados")
    def render_linha_tempo(jogos, nome):
        if len(jogos) < 10:
            st.caption(f"{nome}: dados insuficientes.")
            return
        resultados = [j['resultado'] for j in jogos[:10]]
        pts_ultimos5 = sum(3 if r=='V' else (1 if r=='E' else 0) for r in resultados[:5])
        pts_anteriores5 = sum(3 if r=='V' else (1 if r=='E' else 0) for r in resultados[5:10])
        bolas = ' '.join(['🟢' if r=='V' else ('🟡' if r=='E' else '🔴') for r in resultados])
        st.markdown(f"**{nome}**  {bolas}")
        st.write(f"Últimos 5: **{pts_ultimos5} pts** | Anteriores: **{pts_anteriores5} pts**")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        render_linha_tempo(jogos_casa, nome_casa)
    with col_l2:
        render_linha_tempo(jogos_fora, nome_fora)

    # 8. COMPARAÇÃO COM A MÉDIA DA LIGA
    st.markdown("### 📈 Comparação com a Média da Liga")
    medias_liga = {
        "gols_media": (MEDIA_GOLS_CASA_LIGA + MEDIA_GOLS_FORA_LIGA)/2,
        "gols_sofridos_media": (MEDIA_GOLS_CASA_LIGA + MEDIA_GOLS_FORA_LIGA)/2,
        "posse_media": 50.0,
        "finalizacoes_alvo_media": 4.0,
        "xg_media": 1.2,
        "chutes_media": 12.0,
    }
    col_comp1, col_comp2 = st.columns(2)
    for col, time_key, nome in [(col_comp1, 'ovrall_casa', nome_casa), (col_comp2, 'ovrall_fora', nome_fora)]:
        ovr = st.session_state.get(time_key, {})
        with col:
            st.write(f"**{nome}**")
            for metrica, media in medias_liga.items():
                valor_time = pegar_valor(ovr, metrica, media)
                if valor_time is not None:
                    diff = valor_time - media
                    if metrica == "gols_sofridos_media":
                        diff = -diff
                    if diff > 0.1:
                        st.success(f"{metrica}: {valor_time:.1f} (+{diff:.1f})")
                    elif diff < -0.1:
                        st.error(f"{metrica}: {valor_time:.1f} ({diff:.1f})")
                    else:
                        st.info(f"{metrica}: {valor_time:.1f} (na média)")

    # 9. GRÁFICO DE ATRIBUTOS
    st.markdown("### 📊 Gráfico Comparativo dos Atributos")
    atributos_casa = {
        "ATAQUE": pegar_valor(ovr_casa, 'gols_media', 1.5) * 20,
        "DEFESA": (2.5 - pegar_valor(ovr_casa, 'gols_sofridos_media', 1.2)) * 25,
        "MEIO-CAMPO": pegar_valor(ovr_casa, 'posse_media', 50),
        "CONSISTÊNCIA": max(0, 80 - pegar_valor(ovr_casa, 'desvio_pontos', 0.5)*30),
        "RESILIÊNCIA": pegar_valor(ovr_casa, 'pontos_pos_desvantagem_media', 1.0) * 25,
        "GLOBAL": pegar_valor(ovr_casa, 'escanteios_media', 5.0) * 10,
    }
    atributos_fora = {
        "ATAQUE": pegar_valor(ovr_fora, 'gols_media', 1.5) * 20,
        "DEFESA": (2.5 - pegar_valor(ovr_fora, 'gols_sofridos_media', 1.2)) * 25,
        "MEIO-CAMPO": pegar_valor(ovr_fora, 'posse_media', 50),
        "CONSISTÊNCIA": max(0, 80 - pegar_valor(ovr_fora, 'desvio_pontos', 0.5)*30),
        "RESILIÊNCIA": pegar_valor(ovr_fora, 'pontos_pos_desvantagem_media', 1.0) * 25,
        "GLOBAL": pegar_valor(ovr_fora, 'escanteios_media', 5.0) * 10,
    }
    for dic in [atributos_casa, atributos_fora]:
        for k in dic:
            dic[k] = max(0, min(100, dic[k]))
    categorias = list(atributos_casa.keys())
    df_comp = pd.DataFrame({
        'Categoria': categorias,
        nome_casa: [atributos_casa[c] for c in categorias],
        nome_fora: [atributos_fora[c] for c in categorias]
    })
    st.bar_chart(df_comp.set_index('Categoria'))

    # 10. RESUMO EXECUTIVO
    st.markdown("### 📝 Resumo Executivo")
    def gerar_resumo():
        frases = []
        if gols_casa > gols_sofridos_fora + 0.3:
            frases.append(f"O ataque do {nome_casa} ({gols_casa:.1f} gols/jogo) deve explorar a defesa frágil do {nome_fora} ({gols_sofridos_fora:.1f} sofridos).")
        elif gols_casa < gols_sofridos_fora - 0.3:
            frases.append(f"O ataque do {nome_casa} pode ter dificuldades contra a sólida defesa do {nome_fora}.")
        if gols_fora > gols_sofridos_casa + 0.3:
            frases.append(f"O {nome_fora} possui ataque eficiente ({gols_fora:.1f} gols/jogo) que pode castigar a defesa do {nome_casa}.")
        if posse_casa > posse_fora + 5:
            frases.append(f"O {nome_casa} deve controlar a posse ({posse_casa:.0f}% vs {posse_fora:.0f}%).")
        if desv_casa < 0.4:
            frases.append(f"O {nome_casa} é muito consistente.")
        if res_casa > 1.5:
            frases.append(f"O {nome_casa} é resiliente em desvantagem.")
        if not frases:
            return "Preencha mais dados para um resumo automático."
        return " ".join(frases)
    st.write(gerar_resumo())

    # Expanders com detalhamentos internos do MPV (mantidos)
    with st.expander("⚡ Como o IMA foi calculado?"):
        if 'detalhes_ima' in res:
            st.write("**Casa:**")
            for recorte, jogos in res['detalhes_ima']['casa'].items():
                if jogos:
                    st.write(f"**{recorte}** (média: {sum(j['pontos'] for j in jogos)/len(jogos):.2f})")
            st.write("**Fora:**")
            for recorte, jogos in res['detalhes_ima']['fora'].items():
                if jogos:
                    st.write(f"**{recorte}** (média: {sum(j['pontos'] for j in jogos)/len(jogos):.2f})")
        else:
            st.write("Detalhamento não disponível.")

    with st.expander("📈 Como o OVRall foi calculado?"):
        if 'notas_casa' in res:
            st.write("**Casa:**")
            st.write(res['notas_casa'])
            st.write("**Fora:**")
            st.write(res['notas_fora'])
        else:
            st.write("Detalhamento não disponível.")

    with st.expander("🧠 Como o IC foi calculado?"):
        st.write("O IC é a média ponderada dos fatores fornecidos (confronto direto, fator casa, etc.).")
        st.write(f"Casa: {res['ic_casa']:.1f}")
        st.write(f"Fora: {res['ic_fora']:.1f}")
