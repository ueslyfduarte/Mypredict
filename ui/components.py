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
# FUNÇÕES AUXILIARES (mantidas)
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
# RADAR CHART (mantido)
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
# MAPA DE CALOR ANOTADO (mantido)
# ------------------------------------------------------------
def field_heatmap_annotated(deltas, critical_routes=None):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 68)
    ax.set_facecolor('#1a472a')
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
            ax.text(x + w/2, y + h/2, f"{label}\n{delta:+.1f}", ha='center', va='center', fontsize=7, color='white', fontweight='bold')
    if critical_routes:
        for i, (dim, delta, _) in enumerate(critical_routes[:3]):
            if dim in zones:
                x, y, w, h, _ = zones[dim]
                ax.annotate('', xy=(x + w/2, y + h/2), xytext=(50, 34), arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
                ax.text(x + w/2 + 2, y + h/2 + 2, f"Rota {i+1}", fontsize=6, color='yellow')
    ax.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close()
    return img_base64

# ------------------------------------------------------------
# AUTO‑INSIGHT (mantido)
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
    if nota_casa >= nota_fora + 1.5:
        insights.append(f"🏆 Favoritismo do **{nome_casa}** (MP Value {nota_casa} vs {nota_fora}).")
    elif nota_fora >= nota_casa + 1.5:
        insights.append(f"🔻 Favoritismo do **{nome_fora}** (MP Value {nota_fora} vs {nota_casa}).")
    else:
        insights.append(f"⚖️ Confronto equilibrado (MP Value {nota_casa} – {nota_fora}).")
    soma_ataques = atk_casa + atk_fora
    soma_defesas = def_casa + def_fora
    if soma_ataques > soma_defesas + 20:
        insights.append("🔥 Os ataques dominam as defesas. **Over 2.5 Gols** e **BTTS** são favorecidos.")
    elif soma_defesas > soma_ataques + 20:
        insights.append("❄️ As defesas são mais fortes que os ataques. **Under 2.5 Gols** e **Ambas Não Marcam** ganham força.")
    else:
        insights.append("⚖️ Equilíbrio entre setores. Mercados de gols devem ser analisados com cuidado.")
    if routes:
        top_dim, top_delta, _ = routes[0]
        if abs(top_delta) > 15:
            if top_delta > 0:
                insights.append(f"🎯 A grande vantagem do **{nome_casa}** em **{top_dim}** (+{top_delta:.1f}) sugere explorar o mercado de gols a favor do mandante.")
            else:
                insights.append(f"🧱 O **{nome_fora}** tem um muro em **{top_dim}** ({top_delta:.1f}). Isso favorece **Under** e pode anular o ataque adversário.")
    return "### 🧠 Análise Tática e Padrões para Apostas\n" + "\n".join(f"- {item}" for item in insights)

# ------------------------------------------------------------
# FUNÇÃO PRINCIPAL (ORDEM REVISADA)
# ------------------------------------------------------------
def show_results_manual(res):
    # ---- Dados da sessão ----
    ovr_casa = st.session_state.get('ovrall_casa', {})
    ovr_fora = st.session_state.get('ovrall_fora', {})
    jogos_casa = st.session_state.get('jogos_casa', [])
    jogos_fora = st.session_state.get('jogos_fora', [])
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']
    media_gols_casa = st.session_state.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA)
    media_gols_fora = st.session_state.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)

    # ---- SEÇÃO 1: ANÁLISE MYPREDICT (antigo MPV Hero) ----
    st.markdown("## ⚽ Análise MyPredict")
    st.markdown(f"""
    <div style="text-align:center; margin:20px 0;">
        <span style="font-size:2rem; font-weight:900; color:#ffd700;">{nome_casa}</span>
        <span style="font-size:1.5rem; color:#888; margin:0 12px;">vs</span>
        <span style="font-size:2rem; font-weight:900; color:#c0c0c0;">{nome_fora}</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"🔺 {nome_casa}: {res.get('prat_proj_casa','?')} → {res.get('prat_real_casa','?')} ({res.get('superacao_casa', 0):+.1f} pts) | 🔺 {nome_fora}: {res.get('prat_proj_fora','?')} → {res.get('prat_real_fora','?')} ({res.get('superacao_fora', 0):+.1f} pts)")
    st.markdown('<div class="mpv-hero">', unsafe_allow_html=True)
    st.markdown('<div class="mpv-crown">👑</div>', unsafe_allow_html=True)
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

    # ---- SEÇÃO 2: INDICADORES DESTACADOS (IMA, OVRall, IC) ----
    st.markdown("---")
    st.markdown("## 📊 Indicadores de Força")
    col_esq, col_dir = st.columns(2)
    with col_esq:
        st.markdown(f"### 🏠 {nome_casa}")
        # IMA
        st.markdown(f"**⚡ IMA (Momento):** {res['ima_casa']:.1f}")
        st.progress(res['ima_casa'] / 100)
        # OVRall (barra de força)
        st.markdown("**📈 OVRall (Força Estrutural)**")
        st.markdown(f"""
        <div style="background:#2d3242; border-radius:10px; height:20px; width:100%; margin:5px 0;">
            <div style="background:linear-gradient(90deg, #FFD700, #FFA500); border-radius:10px; height:20px; width:{res['ovrall_casa']}%;"></div>
        </div>
        <small>{res['ovrall_casa']:.1f} / 100</small>
        """, unsafe_allow_html=True)
        # IC (painel)
        st.markdown("**🧠 IC (Contexto)**")
        st.markdown(f"""
        <div style="border:1px solid #FFD700; border-radius:10px; padding:8px; background:rgba(255,215,0,0.05);">
            <span style="font-size:1.2rem; font-weight:bold;">{res['ic_casa']:.1f} / 100</span><br>
            <small>Fatores: Confronto direto, Fator casa, etc.</small>
        </div>
        """, unsafe_allow_html=True)
    with col_dir:
        st.markdown(f"### 🏟️ {nome_fora}")
        st.markdown(f"**⚡ IMA (Momento):** {res['ima_fora']:.1f}")
        st.progress(res['ima_fora'] / 100)
        st.markdown("**📈 OVRall (Força Estrutural)**")
        st.markdown(f"""
        <div style="background:#2d3242; border-radius:10px; height:20px; width:100%; margin:5px 0;">
            <div style="background:linear-gradient(90deg, #00B4D8, #0096c7); border-radius:10px; height:20px; width:{res['ovrall_fora']}%;"></div>
        </div>
        <small>{res['ovrall_fora']:.1f} / 100</small>
        """, unsafe_allow_html=True)
        st.markdown("**🧠 IC (Contexto)**")
        st.markdown(f"""
        <div style="border:1px solid #00B4D8; border-radius:10px; padding:8px; background:rgba(0,180,216,0.05);">
            <span style="font-size:1.2rem; font-weight:bold;">{res['ic_fora']:.1f} / 100</span><br>
            <small>Fatores: Confronto direto, Fator visitante, etc.</small>
        </div>
        """, unsafe_allow_html=True)

    # ---- SEÇÃO 3: MP VALUE 10.0 (DUAS NOTAS) ----
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
            dims_casa, dims_fora, deltas = {}, {}, {}
        atk_casa = np.mean([dims_casa.get(d, 50) for d in ['ataque_posicional','ataque_transicao','bola_parada_ofensiva']])
        def_casa = np.mean([dims_casa.get(d, 50) for d in ['defesa_organizada','defesa_transicao','bola_parada_defensiva']])
        atk_fora = np.mean([dims_fora.get(d, 50) for d in ['ataque_posicional','ataque_transicao','bola_parada_ofensiva']])
        def_fora = np.mean([dims_fora.get(d, 50) for d in ['defesa_organizada','defesa_transicao','bola_parada_defensiva']])
        vantagem_casa = sum([d for d in deltas.values() if d > 0])
        vantagem_fora = sum([-d for d in deltas.values() if d < 0])
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
        nota_casa = round(calc_nota(atk_casa, def_fora, ima_casa, superacao_casa, vantagem_casa, mpv_tatico_casa), 1)
        nota_fora = round(calc_nota(atk_fora, def_casa, ima_fora, superacao_fora, vantagem_fora, mpv_tatico_fora), 1)
    except:
        nota_casa, nota_fora = 5.0, 5.0
    res['mpv_score_casa'] = nota_casa
    res['mpv_score_fora'] = nota_fora
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        cor = "#FFD700" if nota_casa >= nota_fora else "#00B4D8"
        st.markdown(f"""
        <div style="border:2px solid {cor}; border-radius:20px; padding:15px; text-align:center; background:linear-gradient(145deg, #1a1e2b, #121621);">
            <div style="color:#aaa;">{nome_casa}</div>
            <div style="font-size:3rem; font-weight:900; color:{cor};">{nota_casa}</div>
            <div style="color:#aaa;">MP Value 10.0</div>
        </div>
        """, unsafe_allow_html=True)
    with col_n2:
        cor = "#FFD700" if nota_fora >= nota_casa else "#00B4D8"
        st.markdown(f"""
        <div style="border:2px solid {cor}; border-radius:20px; padding:15px; text-align:center; background:linear-gradient(145deg, #1a1e2b, #121621);">
            <div style="color:#aaa;">{nome_fora}</div>
            <div style="font-size:3rem; font-weight:900; color:{cor};">{nota_fora}</div>
            <div style="color:#aaa;">MP Value 10.0</div>
        </div>
        """, unsafe_allow_html=True)

    # ---- SEÇÃO 4: CONTRASTE TÁTICO (MPV Dye) ----
    if 'tactical' in res and res['tactical'] is not None:
        st.markdown("---")
        st.markdown("## 🧪 Contraste Tático (MPV Dye)")
        tactical = res['tactical']
        col_radar, col_mapa = st.columns([2, 1])
        with col_radar:
            st.markdown("### 📡 Radar de Perfil Tático")
            try:
                radar_img = radar_chart(tactical['dimensions_casa'], tactical['dimensions_fora'])
                if radar_img:
                    st.image(f"data:image/png;base64,{radar_img}", use_container_width=True, caption="Dourado = Casa, Azul = Fora")
                else:
                    st.warning("Dimensões insuficientes para gerar o radar.")
            except Exception as e:
                st.warning("Não foi possível gerar o radar.")
        with col_mapa:
            st.markdown("### 🗺️ Mapa de Calor Tático")
            try:
                heat = field_heatmap_annotated(tactical['deltas'], tactical.get('critical_routes', []))
                st.image(f"data:image/png;base64,{heat}", use_container_width=True, caption="Azul = Vantagem Casa, Vermelho = Vantagem Fora")
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

    # ---- SEÇÃO 5: ANÁLISE TÁTICA E PADRÕES PARA APOSTAS ----
    st.markdown("---")
    insight_text = generate_refined_insight(res)
    st.markdown(insight_text)

    # ---- SEÇÃO 6: PROBABILIDADES 1X2 ----
    st.markdown("---")
    st.subheader("📊 PROBABILIDADES 1X2")
    col1, col2, col3 = st.columns(3)
    col1.metric("🏠 Casa", f"{res['p1']:.1%}")
    col2.metric("🤝 Empate", f"{res['pX']:.1%}")
    col3.metric("🏟️ Fora", f"{res['p2']:.1%}")

    # ---- SEÇÃO 7: RECOMENDAÇÕES DE MERCADO ----
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

    # ---- SEÇÃO 8: ANÁLISE COMPLETA DETALHADA (todo o restante) ----
    st.markdown("---")
    st.markdown("## 📊 Análise Completa Detalhada")

    # (Mantenha as seções 1 a 10 conforme o código anterior: comparativo real, confrontos, últimos jogos, etc.)
    # ... (todo o restante do código existente, a partir de "### 📋 Comparativo Real")
