# ui/components.py — Componentes reutilizáveis da interface (com Radar Tático)
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
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

# ============================================================
# Função para gerar o Radar Chart (Spider)
# ============================================================
def radar_chart(casa_scores, fora_scores, dimensions):
    """Gera um gráfico de radar comparando dois times e retorna imagem base64."""
    labels = list(dimensions.keys())
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # fechar o polígono

    # Valores (escala 0-100)
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

# ============================================================
# Função para gerar mapa de calor real (campo)
# ============================================================
def field_heatmap(deltas):
    """Gera um campo de futebol com zonas coloridas baseado nos deltas."""
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 68)
    ax.set_facecolor('#1a472a')
    
    # Desenhar linhas do campo
    ax.plot([0, 0, 100, 100, 0], [0, 68, 68, 0, 0], color='white', linewidth=2)
    ax.plot([50, 50], [0, 68], color='white', linewidth=1.5)
    ax.plot([0, 16.5], [13.84, 13.84], color='white'); ax.plot([16.5, 16.5], [13.84, 54.16], color='white')
    ax.plot([0, 16.5], [54.16, 54.16], color='white')
    ax.plot([83.5, 100], [13.84, 13.84], color='white'); ax.plot([83.5, 83.5], [13.84, 54.16], color='white')
    ax.plot([83.5, 100], [54.16, 54.16], color='white')
    ax.add_patch(plt.Circle((50, 34), 9.15, fill=False, color='white'))
    ax.add_patch(plt.Circle((11, 34), 0.5, color='white'))
    ax.add_patch(plt.Circle((89, 34), 0.5, color='white'))
    
    # Zonas de calor baseadas nos deltas (exemplo simplificado)
    zones = {
        'ataque_posicional': (70, 20, 30, 28),
        'ataque_transicao': (40, 15, 30, 38),
        'defesa_organizada': (0, 20, 30, 28),
        'bola_parada_ofensiva': (85, 0, 15, 68),
        'controle_meio_campo': (30, 15, 40, 38),
        'pressao_alta': (60, 0, 40, 68),
        'resistencia_pressao': (0, 0, 30, 68),
    }
    
    for dim, delta in deltas.items():
        if dim in zones:
            x, y, w, h = zones[dim]
            intensity = min(abs(delta) / 30, 1.0)
            color = 'blue' if delta > 0 else 'red'
            rect = plt.Rectangle((x, y), w, h, color=color, alpha=intensity * 0.6)
            ax.add_patch(rect)
    
    ax.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close()
    return img_base64

# ============================================================
# Função principal de exibição dos resultados (com Radar Chart)
# ============================================================
def show_results_manual(res):
    # Resgatar dados da sessão
    ovr_casa = st.session_state.get('ovrall_casa', {})
    ovr_fora = st.session_state.get('ovrall_fora', {})
    jogos_casa = st.session_state.get('jogos_casa', [])
    jogos_fora = st.session_state.get('jogos_fora', [])
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']
    media_gols_casa = st.session_state.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA)
    media_gols_fora = st.session_state.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)

    # Seção do Contraste Tático (nova e turbinada)
    if 'tactical' in res and res['tactical'] is not None:
        st.markdown("## 🧪 Contraste Tático (MPV Dye)")
        tactical = res['tactical']

        # Gráfico de Radar + Mapa de Calor
        col_radar, col_mapa = st.columns([2, 1])
        with col_radar:
            st.markdown("### 📡 Radar de Perfil Tático")
            try:
                radar_img = radar_chart(tactical['dimensions_casa'], tactical['dimensions_fora'],
                                        list(tactical['dimensions_casa'].keys()))
                st.image(f"data:image/png;base64,{radar_img}", use_container_width=True,
                         caption="Comparação das dimensões táticas (Casa = Dourado, Fora = Azul)")
            except Exception as e:
                st.warning("Não foi possível gerar o radar.")
        with col_mapa:
            st.markdown("### 🗺️ Mapa de Calor do Campo")
            if tactical['heatmap']:
                st.image(f"data:image/png;base64,{tactical['heatmap']}", use_container_width=True,
                         caption="Zonas de Desequilíbrio (Azul = Vantagem Casa, Vermelho = Vantagem Fora)")
            else:
                # Tentar gerar com a função interna
                try:
                    heat = field_heatmap(tactical['deltas'])
                    st.image(f"data:image/png;base64,{heat}", use_container_width=True,
                             caption="Zonas de Desequilíbrio")
                except:
                    st.info("Mapa de calor não disponível.")

        # Rotas Críticas (com explicação detalhada)
        st.markdown("### 🎯 Rotas Críticas do Jogo")
        if 'critical_routes' in tactical and tactical['critical_routes']:
            for dim, delta, interpretation in tactical['critical_routes']:
                if delta > 0:
                    st.success(f"**{interpretation}**\n\n> *{nome_casa}* tem vantagem significativa em **{dim}** (+{delta:.1f}). "
                               "Explore essa área para criar oportunidades de gol.")
                else:
                    st.error(f"**{interpretation}**\n\n> *{nome_fora}* leva vantagem em **{dim}** ({delta:.1f}). "
                             "Atenção redobrada da defesa do time da casa.")
        else:
            st.info("Nenhuma rota crítica detectada com diferença superior ao limiar.")

        # Tabela de Deltas (com cores e interpretação)
        st.markdown("### 📊 Diferencial por Dimensão")
        deltas_df = pd.DataFrame(
            tactical['deltas'].items(),
            columns=['Dimensão', 'Δ (Casa - Fora)']
        )
        # Adicionar coluna de interpretação
        def interpretar(delta):
            if delta > 10:
                return "🟢 Vantagem Casa"
            elif delta > 3:
                return "🟡 Leve Vantagem Casa"
            elif delta < -10:
                return "🔴 Vantagem Fora"
            elif delta < -3:
                return "🟠 Leve Vantagem Fora"
            else:
                return "⚪ Equilíbrio"
        deltas_df['Interpretação'] = deltas_df['Δ (Casa - Fora)'].apply(interpretar)
        deltas_df = deltas_df.sort_values('Δ (Casa - Fora)', key=abs, ascending=False)
        st.dataframe(deltas_df, use_container_width=True, hide_index=True)

    # ... (restante do código original, a partir do cabeçalho do confronto, mantido exatamente igual)
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
    
    # (O restante do código original de análises, gráficos de barra, resumo executivo etc. permanece igual.
    # Mantenha tudo o que já existia a partir daqui, sem alterações.)
