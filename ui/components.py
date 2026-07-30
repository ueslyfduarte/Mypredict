import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from config import THRESHOLD_GOLD, THRESHOLD_VALUE, THRESHOLD_FAVORITO

# ------------------------------------------------------------
# Funções de gráfico (mantidas, mas ajustadas)
# ------------------------------------------------------------
def radar_chart(casa_scores, fora_scores):
    labels = [dim for dim in casa_scores.keys() if dim in fora_scores.keys()]
    if not labels:
        return None
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    values_casa = [casa_scores.get(dim, 50) for dim in labels] + [casa_scores.get(labels[0], 50)]
    values_fora = [fora_scores.get(dim, 50) for dim in labels] + [fora_scores.get(labels[0], 50)]
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
    return base64.b64encode(buf.read()).decode()

def field_heatmap_annotated(deltas, critical_routes=None):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 68)
    ax.set_facecolor('#1a472a')
    # Desenho do campo
    ax.plot([0,0,100,100,0], [0,68,68,0,0], color='white', lw=2)
    ax.plot([50,50], [0,68], color='white', lw=1.5)
    ax.plot([0,16.5],[13.84,13.84], color='white'); ax.plot([16.5,16.5],[13.84,54.16], color='white')
    ax.plot([0,16.5],[54.16,54.16], color='white')
    ax.plot([83.5,100],[13.84,13.84], color='white'); ax.plot([83.5,83.5],[13.84,54.16], color='white')
    ax.plot([83.5,100],[54.16,54.16], color='white')
    ax.add_patch(plt.Circle((50,34), 9.15, fill=False, color='white'))
    # Zonas com anotações
    zones = {
        'ataque_posicional': (70,20,30,28, "Ataque\nPosicional"),
        'ataque_transicao': (40,15,30,38, "Transição"),
        'defesa_organizada': (0,20,30,28, "Defesa\nOrganizada"),
        'bola_parada_ofensiva': (85,0,15,68, "Bola\nParada"),
        'controle_meio_campo': (30,15,40,38, "Meio-Campo"),
        'pressao_alta': (60,0,40,68, "Pressão\nAlta"),
        'resistencia_pressao': (0,0,30,68, "Resist.\nPressão"),
    }
    for dim, delta in deltas.items():
        if dim in zones:
            x,y,w,h,label = zones[dim]
            intensity = min(abs(delta)/30, 1.0)
            color = 'blue' if delta>0 else 'red'
            rect = plt.Rectangle((x,y), w, h, color=color, alpha=intensity*0.6)
            ax.add_patch(rect)
            ax.text(x+w/2, y+h/2, f"{label}\n{delta:+.1f}", ha='center', va='center', fontsize=7, color='white', fontweight='bold')
    # Destaque das rotas críticas com setas
    if critical_routes:
        for i, (dim, delta, _) in enumerate(critical_routes[:3]):
            if dim in zones:
                x,y,w,h,_ = zones[dim]
                ax.annotate('', xy=(x+w/2, y+h/2), xytext=(50,34),
                            arrowprops=dict(arrowstyle='->', color='yellow', lw=2))
                ax.text(x+w/2+2, y+h/2+2, f"Rota {i+1}", fontsize=6, color='yellow')
    ax.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# ------------------------------------------------------------
# FUNÇÃO PRINCIPAL
# ------------------------------------------------------------
def show_results_manual(res):
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']

    # Estilo global: texto branco
    st.markdown("""
    <style>
        .stApp, p, h1, h2, h3, h4, h5, h6, span, div {
            color: #FFFFFF !important;
        }
        .gold { color: #FFD700 !important; }
        .green { color: #00FF7F !important; }
        .red { color: #FF4D4D !important; }
        .big-number { font-size: 2.5rem; font-weight: 900; }
        .medium-number { font-size: 1.8rem; font-weight: 700; }
        .highlight-card { border: 2px solid #FFD700; border-radius: 20px; padding: 20px; background: linear-gradient(145deg, #1a1e2b, #121621); }
        .selo-badge { font-size: 1.2rem; font-weight: bold; padding: 5px 15px; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

    # ========== SEÇÃO 1: PILARES (IMA, OVRall, IC) ==========
    st.markdown("## 🔬 Pilares do MyPredict")

    # IMA
    with st.expander("⚡ IMA – Índice de Momentum Atual", expanded=False):
        col_ima1, col_ima2 = st.columns(2)
        with col_ima1:
            st.markdown(f"### 🏠 {nome_casa}")
            st.markdown(f"<div class='big-number gold'>{res['ima_casa']:.1f}</div>", unsafe_allow_html=True)
        with col_ima2:
            st.markdown(f"### 🏟️ {nome_fora}")
            st.markdown(f"<div class='big-number gold'>{res['ima_fora']:.1f}</div>", unsafe_allow_html=True)
        if res.get('detalhes_ima'):
            st.markdown("**Detalhamento por recorte:**")
            det_col1, det_col2 = st.columns(2)
            for time, key, col in [(nome_casa, 'casa', det_col1), (nome_fora, 'fora', det_col2)]:
                with col:
                    for recorte, jogos in res['detalhes_ima'][key].items():
                        if jogos:
                            media = np.mean([j['pontos'] for j in jogos])
                            st.write(f"📊 {recorte}: média **{media:.2f}**")
                            for j in jogos:
                                st.caption(f"   {j['jogo']} → {j['pontos']:.2f} pts (Adv: {j['prateleira_adv']})")
        else:
            st.info("Menos de 5 jogos; IMA assume 50.0")

    # OVRall
    with st.expander("📈 OVRall – Desempenho Estrutural", expanded=False):
        dims_order = ['Ataque', 'Defesa', 'MeioCampo', 'Consistencia', 'Resiliencia']
        if res.get('detalhes_ovr'):
            for dim in dims_order:
                nota_c = res['notas_casa'].get(dim, 0)
                nota_f = res['notas_fora'].get(dim, 0)
                st.markdown(f"**{dim}**")
                col_ovr1, col_ovr2, col_ovr3 = st.columns([1, 3, 1])
                with col_ovr1:
                    st.markdown(f"<span class='medium-number' style='color:#FFD700;'>{nota_c:.1f}</span><br><small>{nome_casa}</small>", unsafe_allow_html=True)
                with col_ovr2:
                    # Barra de força centralizada
                    st.markdown(f"""
                    <div style="display:flex; align-items:center; justify-content:center; height:30px;">
                        <div style="background:linear-gradient(90deg, #FFD700, #FFA500); height:20px; width:{nota_c}%; border-radius:10px; text-align:right; padding-right:5px; color:black; font-weight:bold;">{nota_c:.0f}</div>
                        <div style="width:10px;"></div>
                        <div style="background:linear-gradient(90deg, #00B4D8, #0096c7); height:20px; width:{nota_f}%; border-radius:10px; text-align:left; padding-left:5px; color:black; font-weight:bold;">{nota_f:.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_ovr3:
                    st.markdown(f"<span class='medium-number' style='color:#00B4D8;'>{nota_f:.1f}</span><br><small>{nome_fora}</small>", unsafe_allow_html=True)
        col_ovr_total1, col_ovr_total2 = st.columns(2)
        with col_ovr_total1:
            st.metric(f"{nome_casa} OVRall", f"{res['ovrall_casa']:.1f}")
        with col_ovr_total2:
            st.metric(f"{nome_fora} OVRall", f"{res['ovrall_fora']:.1f}")

    # IC
    with st.expander("🧠 IC – Índice de Contexto", expanded=False):
        ic_casa = res['ic_casa']
        ic_fora = res['ic_fora']
        cor_ic_casa = '#FFD700' if ic_casa >= ic_fora else '#FFFFFF'
        cor_ic_fora = '#FFD700' if ic_fora >= ic_casa else '#FFFFFF'
        col_ic1, col_ic2 = st.columns(2)
        with col_ic1:
            st.markdown(f"### 🏠 {nome_casa}")
            st.markdown(f"<div class='big-number' style='color:{cor_ic_casa};'>{ic_casa:.1f}</div>", unsafe_allow_html=True)
        with col_ic2:
            st.markdown(f"### 🏟️ {nome_fora}")
            st.markdown(f"<div class='big-number' style='color:{cor_ic_fora};'>{ic_fora:.1f}</div>", unsafe_allow_html=True)
        st.caption("IC: média ponderada de fatores contextuais (confronto direto, fator casa, odds).")

    # ========== SEÇÃO 2: MYPREDICT VALUE (DESTAQUE) ==========
    st.markdown("---")
    st.markdown("<h2 style='text-align:center; color:#FFD700 !important;'>👑 MyPredict Value</h2>", unsafe_allow_html=True)
    mpv_casa = res['mpv_casa']
    mpv_fora = res['mpv_fora']
    maior_casa = mpv_casa >= mpv_fora
    border_casa = '3px solid #FFD700' if maior_casa else '1px solid #555'
    border_fora = '3px solid #FFD700' if not maior_casa else '1px solid #555'
    col_mpv1, col_mpv2 = st.columns(2)
    with col_mpv1:
        st.markdown(f"""
        <div class="highlight-card" style="border:{border_casa};">
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">{nome_casa}</div>
                <div class="big-number gold">{mpv_casa:.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_mpv2:
        st.markdown(f"""
        <div class="highlight-card" style="border:{border_fora};">
            <div style="text-align:center;">
                <div style="font-size:1.5rem;">{nome_fora}</div>
                <div class="big-number gold">{mpv_fora:.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Superação
    sup_casa = res.get('superacao_casa',0)
    sup_fora = res.get('superacao_fora',0)
    cor_casa = '#00FF7F' if sup_casa >= 0 else '#FF4D4D'
    cor_fora = '#00FF7F' if sup_fora >= 0 else '#FF4D4D'
    st.markdown(f"""
    <div style="text-align:center; margin:10px 0;">
        <span>🔺 Superação: </span>
        <span style="color:{cor_casa};">{nome_casa} {sup_casa:+.1f} pts</span> &nbsp;|&nbsp;
        <span style="color:{cor_fora};">{nome_fora} {sup_fora:+.1f} pts</span>
    </div>
    <div style="text-align:center; font-size:0.8rem; color:#aaa;">Superação mede se o time está acima ou abaixo da expectativa (prateleira projetada).</div>
    """, unsafe_allow_html=True)

    # ========== SEÇÃO 3: CONTRASTE TÁTICO (se disponível) ==========
    if res.get('tactical'):
        st.markdown("---")
        st.markdown("## 🧪 Contraste Tático (MPV Dye)")
        tac = res['tactical']
        col_radar, col_mapa = st.columns([2,1])
        with col_radar:
            radar_img = radar_chart(tac['dimensions_casa'], tac['dimensions_fora'])
            if radar_img:
                st.image(f"data:image/png;base64,{radar_img}", use_container_width=True)
        with col_mapa:
            if tac['heatmap']:
                st.image(f"data:image/png;base64,{tac['heatmap']}", use_container_width=True)
            else:
                st.info("Mapa de calor indisponível.")
        # Rotas Críticas
        st.markdown("### 🎯 Rotas Críticas")
        if tac.get('critical_routes'):
            for dim, delta, interp in tac['critical_routes']:
                if delta > 0:
                    st.success(f"{interp} (Vantagem {nome_casa})")
                else:
                    st.error(f"{interp} (Vantagem {nome_fora})")
        else:
            st.info("Nenhuma rota crítica com diferença significativa.")
        # Deltas (vantagem absoluta)
        st.markdown("### 📊 Diferencial Tático (Δ)")
        deltas = tac['deltas']
        delta_rows = []
        for dim, d in deltas.items():
            if d > 0:
                vantagem = f"{nome_casa} +{d:.1f}"
            elif d < 0:
                vantagem = f"{nome_fora} +{abs(d):.1f}"
            else:
                vantagem = "Equilíbrio"
            delta_rows.append((dim, vantagem, d))
        df_deltas = pd.DataFrame(delta_rows, columns=['Dimensão', 'Vantagem', 'Δ']).sort_values('Δ', key=abs, ascending=False)
        st.dataframe(df_deltas[['Dimensão', 'Vantagem']], use_container_width=True)

    # ========== SEÇÃO 4: PROBABILIDADES DE MERCADO (FINAL) ==========
    st.markdown("---")
    st.markdown("## 🎯 Probabilidades de Mercado")
    st.markdown("*(Média entre fórmulas originais e modelo avançado)*")
    # Grandes métricas
    col_p1, col_p2, col_p3 = st.columns(3)
    col_p1.markdown(f"<div class='highlight-card'><div style='font-size:1.5rem;'>🏠 Casa</div><div class='big-number gold'>{res['p1']:.1%}</div></div>", unsafe_allow_html=True)
    col_p2.markdown(f"<div class='highlight-card'><div style='font-size:1.5rem;'>🤝 Empate</div><div class='big-number gold'>{res['pX']:.1%}</div></div>", unsafe_allow_html=True)
    col_p3.markdown(f"<div class='highlight-card'><div style='font-size:1.5rem;'>🏟️ Fora</div><div class='big-number gold'>{res['p2']:.1%}</div></div>", unsafe_allow_html=True)

    st.markdown("### 🎲 Mercados Especiais")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    mercados = [
        ("Over 2.5 Gols", res['over25']),
        ("Ambas Marcam", res['btts']),
        ("Gol 1º Tempo", res['gol_ht']),
        ("Over Escanteios", res['esc']),
    ]
    for i, (nome, prob) in enumerate(mercados):
        selo = ""
        if prob >= 0.70: selo = "🥇 GOLD"
        elif prob >= 0.60: selo = "✅ Value"
        elif prob >= 0.50: selo = "🔵 Favorito"
        with [col_m1, col_m2, col_m3, col_m4][i]:
            st.markdown(f"""
            <div class="highlight-card" style="text-align:center;">
                <div style="font-size:1.2rem;">{nome}</div>
                <div class="medium-number gold">{prob:.1%}</div>
                <div class="selo-badge" style="background:{'#FFD700' if selo=='🥇 GOLD' else '#4CAF50' if selo=='✅ Value' else '#2196F3' if selo=='🔵 Favorito' else '#888'}; color:black;">{selo}</div>
            </div>
            """, unsafe_allow_html=True)
