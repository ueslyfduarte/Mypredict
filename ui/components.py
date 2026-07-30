# ui/components.py — MyPredict 2.0 (completo: métricas originais + MPV Dye)
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from config import THRESHOLD_GOLD, THRESHOLD_VALUE, THRESHOLD_FAVORITO, MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

# ------------------------------------------------------------
# FUNÇÕES AUXILIARES (ORIGINAIS)
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# RADAR CHART
# ------------------------------------------------------------
def radar_chart(casa_scores, fora_scores):
    labels = [dim for dim in casa_scores.keys() if dim in fora_scores.keys()]
    if not labels:
        return None
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    values_casa = [casa_scores.get(dim, 50) for dim in labels]
    values_casa += values_casa[:1]
    values_fora = [fora_scores.get(dim, 50) for dim in labels]
    values_fora += values_fora[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.set_facecolor('#0E1117')
    fig.patch.set_facecolor('#0E1117')
    
    ax.plot(angles, values_casa, 'o-', color='#FFD700', linewidth=2, label='Casa')
    ax.fill(angles, values_casa, alpha=0.1, color='#FFD700')
    ax.plot(angles, values_fora, 'o-', color='#00B4D8', linewidth=2, label='Fora')
    ax.fill(angles, values_fora, alpha=0.1, color='#00B4D8')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='white', fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80])
    ax.set_yticklabels(['20', '40', '60', '80'], color='white', fontsize=7)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), facecolor='#1a1e2b', edgecolor='#FFD700', labelcolor='white')
    ax.grid(True, color='#333')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close()
    return img_base64

# ------------------------------------------------------------
# MAPA DE CALOR ANOTADO
# ------------------------------------------------------------
def field_heatmap_annotated(deltas, critical_routes=None):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 68)
    ax.set_facecolor('#1a472a')
    
    # Desenho do campo
    ax.plot([0, 0, 100, 100, 0], [0, 68, 68, 0, 0], color='white', linewidth=2)
    ax.plot([50, 50], [0, 68], color='white', linewidth=1.5)
    ax.plot([0, 16.5], [13.84, 13.84], color='white'); ax.plot([16.5, 16.5], [13.84, 54.16], color='white')
    ax.plot([0, 16.5], [54.16, 54.16], color='white')
    ax.plot([83.5, 100], [13.84, 13.84], color='white'); ax.plot([83.5, 83.5], [13.84, 54.16], color='white')
    ax.plot([83.5, 100], [54.16, 54.16], color='white')
    ax.add_patch(plt.Circle((50, 34), 9.15, fill=False, color='white'))
    ax.add_patch(plt.Circle((11, 34), 0.5, color='white'))
    ax.add_patch(plt.Circle((89, 34), 0.5, color='white'))
    
    zones = {
        'ataque_posicional': (70, 20, 30, 28, "Ataque Posicional"),
        'ataque_transicao': (40, 15, 30, 38, "Transição"),
        'defesa_organizada': (0, 20, 30, 28, "Defesa Organizada"),
        'bola_parada_ofensiva': (85, 0, 15, 68, "Bola Parada Of."),
        'controle_meio_campo': (30, 15, 40, 38, "Meio-Campo"),
        'pressao_alta': (60, 0, 40, 68, "Pressão Alta"),
        'resistencia_pressao': (0, 0, 30, 68, "Resist. Pressão"),
    }
    
    for dim, delta in deltas.items():
        if dim in zones:
            x, y, w, h, label = zones[dim]
            intensity = min(abs(delta) / 30, 1.0)
            color = 'blue' if delta > 0 else 'red'
            rect = plt.Rectangle((x, y), w, h, color=color, alpha=intensity * 0.6)
            ax.add_patch(rect)
            ax.text(x + w/2, y + h/2, f"{label}\n{delta:+.1f}", 
                    ha='center', va='center', fontsize=7, color='white', fontweight='bold')
    
    if critical_routes:
        for i, (dim, delta, _) in enumerate(critical_routes[:3]):
            if dim in zones:
                x, y, w, h, _ = zones[dim]
                ax.annotate('', xy=(x + w/2, y + h/2), xytext=(50, 34),
                            arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
                ax.text(x + w/2 + 2, y + h/2 + 2, f"Rota {i+1}", fontsize=6, color='yellow')
    
    ax.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close()
    return img_base64

# ------------------------------------------------------------
# AUTO‑INSIGHT (DUAS NOTAS)
# ------------------------------------------------------------
def generate_refined_insight(res):
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']
    tactical = res.get('tactical')
    nota_casa = res.get('mpv_score_casa', 5.0)
    nota_fora = res.get('mpv_score_fora', 5.0)
    
    if not tactical:
        return "Dados táticos insuficientes."
    
    dims_casa = tactical['dimensions_casa']
    dims_fora = tactical['dimensions_fora']
    deltas = tactical['deltas']
    routes = tactical.get('critical_routes', [])
    
    atk_casa = np.mean([dims_casa.get(d, 50) for d in ['ataque_posicional','ataque_transicao','bola_parada_ofensiva']])
    def_casa = np.mean([dims_casa.get(d, 50) for d in ['defesa_organizada','defesa_transicao','bola_parada_defensiva']])
    atk_fora = np.mean([dims_fora.get(d, 50) for d in ['ataque_posicional','ataque_transicao','bola_parada_ofensiva']])
    def_fora = np.mean([dims_fora.get(d, 50) for d in ['defesa_organizada','defesa_transicao','bola_parada_defensiva']])
    
    insights = []
    
    # Favoritismo
    if nota_casa >= nota_fora + 1.5:
        insights.append(f"🏆 Favoritismo do **{nome_casa}** (MP Value {nota_casa} vs {nota_fora}).")
    elif nota_fora >= nota_casa + 1.5:
        insights.append(f"🔻 Favoritismo do **{nome_fora}** (MP Value {nota_fora} vs {nota_casa}).")
    else:
        insights.append(f"⚖️ Confronto equilibrado (MP Value {nota_casa} – {nota_fora}).")
    
    soma_ataques = atk_casa + atk_fora
    soma_defesas = def_casa + def_fora
    
    if soma_ataques > soma_defesas + 20:
        insights.append("🔥 Os ataques dominam as defesas. **Over 2.5 Gols** e **BTTS** favorecidos.")
        mercado_gols = "Over / BTTS"
    elif soma_defesas > soma_ataques + 20:
        insights.append("❄️ As defesas são mais fortes que os ataques. **Under 2.5 Gols** e **Ambas Não Marcam** ganham força.")
        mercado_gols = "Under / Ambas Não Marcam"
    else:
        insights.append("⚖️ Equilíbrio entre setores. Análise cautelosa dos mercados de gols.")
        mercado_gols = "Neutro"
    
    if routes:
        top_dim, top_delta, _ = routes[0]
        if abs(top_delta) > 15:
            if top_delta > 0:
                insights.append(f"🎯 A grande vantagem do **{nome_casa}** em **{top_dim}** (+{top_delta:.1f}) sugere explorar o mercado de gols a favor do mandante.")
            else:
                insights.append(f"🧱 O **{nome_fora}** tem um muro em **{top_dim}** ({top_delta:.1f}). Isso favorece **Under** e pode anular o ataque adversário.")
    
    return "### 🧠 Análise Tática\n" + "\n".join(f"- {item}" for item in insights)

# ------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE RESULTADOS (COMPLETA)
# ------------------------------------------------------------
def show_results_manual(res):
    # Dados da sessão
    ovr_casa = st.session_state.get('ovrall_casa', {})
    ovr_fora = st.session_state.get('ovrall_fora', {})
    jogos_casa = st.session_state.get('jogos_casa', [])
    jogos_fora = st.session_state.get('jogos_fora', [])
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']
    media_gols_casa = st.session_state.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA)
    media_gols_fora = st.session_state.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)

    # ================================================================
    # MP VALUE 10.0 (DUAS NOTAS INDEPENDENTES)
    # ================================================================
    try:
        ima_casa = res['ima_casa']
        ima_fora = res['ima_fora']
        superacao_casa = res.get('superacao_casa', 0)
        superacao_fora = res.get('superacao_fora', 0)
        
        if 'tactical' in res and res['tactical'] is not None:
            dims_casa = res['tactical']['dimensions_casa']
            dims_fora = res['tactical']['dimensions_fora']
            deltas = res['tactical']['deltas']
        else:
            dims_casa = {}
            dims_fora = {}
            deltas = {}
        
        atk_casa = np.mean([dims_casa.get(d, 50) for d in ['ataque_posicional','ataque_transicao','bola_parada_ofensiva']])
        def_casa = np.mean([dims_casa.get(d, 50) for d in ['defesa_organizada','defesa_transicao','bola_parada_defensiva']])
        atk_fora = np.mean([dims_fora.get(d, 50) for d in ['ataque_posicional','ataque_transicao','bola_parada_ofensiva']])
        def_fora = np.mean([dims_fora.get(d, 50) for d in ['defesa_organizada','defesa_transicao','bola_parada_defensiva']])
        
        vantagem_casa = sum([delta for delta in deltas.values() if delta > 0])
        vantagem_fora = sum([-delta for delta in deltas.values() if delta < 0])
        
        mpv_tatico_casa = np.mean(list(dims_casa.values())) if dims_casa else 50
        mpv_tatico_fora = np.mean(list(dims_fora.values())) if dims_fora else 50
        
        def calc_nota(atk, def_adv, ima, superacao, vantagem, mpv_tatico):
            a = atk / 100
            d = (100 - def_adv) / 100
            i = ima / 100
            s = (superacao + 10) / 20
            v = min(vantagem, 30) / 30
            m = mpv_tatico / 100
            raw = (0.25 * a + 0.20 * d + 0.15 * i + 0.10 * s + 0.10 * v + 0.20 * m) * 10
            return max(0, min(10, raw))
        
        nota_casa = calc_nota(atk_casa, def_fora, ima_casa, superacao_casa, vantagem_casa, mpv_tatico_casa)
        nota_fora = calc_nota(atk_fora, def_casa, ima_fora, superacao_fora, vantagem_fora, mpv_tatico_fora)
        nota_casa = round(nota_casa, 1)
        nota_fora = round(nota_fora, 1)
    except Exception as e:
        nota_casa = 5.0
        nota_fora = 5.0
    
    res['mpv_score_casa'] = nota_casa
    res['mpv_score_fora'] = nota_fora
    
    col_score1, col_score2 = st.columns(2)
    with col_score1:
        cor = "#FFD700" if nota_casa >= nota_fora else "#00B4D8"
        st.markdown(f"""
        <div style="background:linear-gradient(145deg, #1a1e2b 0%, #121621 100%); border:2px solid {cor}; 
                    border-radius:20px; padding:20px; text-align:center;">
            <div style="font-size:1.2rem; color:#aaa;">{nome_casa}</div>
            <div style="font-size:4rem; font-weight:900; color:{cor};">{nota_casa}</div>
            <div style="color:#aaa;">MP Value 10.0</div>
        </div>
        """, unsafe_allow_html=True)
    with col_score2:
        cor = "#FFD700" if nota_fora >= nota_casa else "#00B4D8"
        st.markdown(f"""
        <div style="background:linear-gradient(145deg, #1a1e2b 0%, #121621 100%); border:2px solid {cor}; 
                    border-radius:20px; padding:20px; text-align:center;">
            <div style="font-size:1.2rem; color:#aaa;">{nome_fora}</div>
            <div style="font-size:4rem; font-weight:900; color:{cor};">{nota_fora}</div>
            <div style="color:#aaa;">MP Value 10.0</div>
        </div>
        """, unsafe_allow_html=True)

    # ================================================================
    # SEÇÃO DO CONTRASTE TÁTICO (MPV Dye)
    # ================================================================
    if 'tactical' in res and res['tactical'] is not None:
        st.markdown("## 🧪 Contraste Tático (MPV Dye)")
        tactical = res['tactical']

        col_radar, col_mapa = st.columns([2, 1])
        with col_radar:
            st.markdown("### 📡 Radar de Perfil Tático")
            try:
                radar_img = radar_chart(tactical['dimensions_casa'], tactical['dimensions_fora'])
                if radar_img:
                    st.image(f"data:image/png;base64,{radar_img}", use_container_width=True,
                             caption="Dourado = Casa, Azul = Fora")
                else:
                    st.warning("Dimensões insuficientes para gerar o radar.")
            except Exception as e:
                st.warning("Não foi possível gerar o radar.")
        with col_mapa:
            st.markdown("### 🗺️ Mapa de Calor Tático")
            try:
                heat = field_heatmap_annotated(tactical['deltas'], tactical.get('critical_routes', []))
                st.image(f"data:image/png;base64,{heat}", use_container_width=True,
                         caption="Azul = Vantagem Casa, Vermelho = Vantagem Fora. Textos indicam os deltas.")
            except:
                st.info("Mapa de calor não disponível.")

        # Rotas Críticas
        st.markdown("### 🎯 Rotas Críticas")
        if 'critical_routes' in tactical and tactical['critical_routes']:
            for dim, delta, interpretation in tactical['critical_routes']:
                if delta > 0:
                    st.success(f"**{interpretation}**")
                else:
                    st.error(f"**{interpretation}**")
        else:
            st.info("Nenhuma rota crítica com diferença significativa.")

        # Tabela de Deltas
        st.markdown("### 📊 Diferencial por Dimensão")
        deltas_df = pd.DataFrame(tactical['deltas'].items(), columns=['Dimensão', 'Δ (Casa - Fora)'])
        def interpretar(delta):
            if delta > 10: return "🟢 Vantagem Casa"
            elif delta > 3: return "🟡 Leve Vantagem Casa"
            elif delta < -10: return "🔴 Vantagem Fora"
            elif delta < -3: return "🟠 Leve Vantagem Fora"
            else: return "⚪ Equilíbrio"
        deltas_df['Interpretação'] = deltas_df['Δ (Casa - Fora)'].apply(interpretar)
        deltas_df = deltas_df.sort_values('Δ (Casa - Fora)', key=abs, ascending=False)
        st.dataframe(deltas_df, use_container_width=True, hide_index=True)

        # Auto‑Insight Refinado
        refined = generate_refined_insight(res)
        st.markdown(refined)

    # ================================================================
    # CABEÇALHO DO CONFRONTO
    # ================================================================
    st.markdown(f"""
    <div style="text-align:center; margin:20px 0;">
        <span style="font-size:2rem; font-weight:900; color:#ffd700;">{nome_casa}</span>
        <span style="font-size:1.5rem; color:#888; margin:0 12px;">vs</span>
        <span style="font-size:2rem; font-weight:900; color:#c0c0c0;">{nome_fora}</span>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"🔺 {nome_casa}: {res.get('prat_proj_casa','?')} → {res.get('prat_real_casa','?')} ({res.get('superacao_casa', 0):+.1f} pts) | 🔺 {nome_fora}: {res.get('prat_proj_fora','?')} → {res.get('prat_real_fora','?')} ({res.get('superacao_fora', 0):+.1f} pts)")

    # MPV Hero (antigo)
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

    # ================================================================
    # ANÁLISE COMPLETA DETALHADA (TODAS AS SEÇÕES ORIGINAIS)
    # ================================================================
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

    # Expanders com detalhamentos
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
