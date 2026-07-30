import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from config import THRESHOLD_GOLD, THRESHOLD_VALUE, THRESHOLD_FAVORITO

# ------------------------------------------------------------
# Funções de gráfico
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
            rect = plt.Rectangle((x,y), w, h, color=color, alpha=intensity*0.5)
            ax.add_patch(rect)
            ax.text(x+w/2, y+h/2, f"{label}\n{delta:+.1f}", ha='center', va='center', fontsize=7, color='white', fontweight='bold')
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
# FUNÇÃO PRINCIPAL DE RESULTADOS
# ------------------------------------------------------------
def show_results_manual(res):
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']

    # CSS customizado (limpo e moderno)
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #FFFFFF; }
        .gold { color: #FFD700 !important; }
        .silver { color: #C0C0C0 !important; }
        .green { color: #00FF7F !important; }
        .red { color: #FF4D4D !important; }
        .big-number { font-size: 2.5rem; font-weight: 900; }
        .medium-number { font-size: 1.8rem; font-weight: 700; }
        .card { background: linear-gradient(145deg, #1a1e2b, #121621); border-radius: 20px; padding: 20px; margin: 10px 0; border: 1px solid #333; }
        .card-gold { border: 2px solid #FFD700; }
        .selo-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9rem; }
        hr { border-color: #333; }
    </style>
    """, unsafe_allow_html=True)

    # ========== SEÇÃO 1: PILARES ==========
    st.markdown("## 🔬 Pilares do MyPredict")
    with st.expander("⚡ IMA – Índice de Momentum Atual", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🏠 {nome_casa}**")
            st.markdown(f"<span class='big-number gold'>{res['ima_casa']:.1f}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**🏟️ {nome_fora}**")
            st.markdown(f"<span class='big-number gold'>{res['ima_fora']:.1f}</span>", unsafe_allow_html=True)
        if res.get('detalhes_ima'):
            det1, det2 = st.columns(2)
            for time, key, col in [(nome_casa, 'casa', det1), (nome_fora, 'fora', det2)]:
                with col:
                    for recorte, jogos in res['detalhes_ima'][key].items():
                        if jogos:
                            media = np.mean([j['pontos'] for j in jogos])
                            st.write(f"**{recorte}**: {media:.2f}")
                            for j in jogos:
                                st.caption(f"{j['jogo']} → {j['pontos']:.2f} pts")
        else:
            st.info("Menos de 5 jogos; IMA assume 50.0.")

    with st.expander("📈 OVRall – Desempenho Estrutural", expanded=False):
        if res.get('detalhes_ovr'):
            dims = ['Ataque', 'Defesa', 'MeioCampo', 'Consistencia', 'Resiliencia']
            for dim in dims:
                nota_c = res['notas_casa'].get(dim, 0)
                nota_f = res['notas_fora'].get(dim, 0)
                # Duelo de barras
                st.markdown(f"**{dim}**")
                bar_html = f"""
                <div style="display:flex; align-items:center; margin:5px 0;">
                    <div style="width:45%; text-align:right; padding-right:10px;">
                        <span class="gold">{nota_c:.1f}</span><br><small>{nome_casa}</small>
                    </div>
                    <div style="width:10%; text-align:center;">VS</div>
                    <div style="width:45%; text-align:left; padding-left:10px;">
                        <span class="silver">{nota_f:.1f}</span><br><small>{nome_fora}</small>
                    </div>
                </div>
                <div style="display:flex; align-items:center; height:20px; background:#2d3242; border-radius:10px; overflow:hidden;">
                    <div style="width:50%; height:100%; display:flex; justify-content:flex-end;">
                        <div style="height:100%; background:linear-gradient(90deg, #FFD700, #FFA500); width:{nota_c}%; border-radius:10px 0 0 10px;"></div>
                    </div>
                    <div style="width:50%; height:100%; display:flex;">
                        <div style="height:100%; background:linear-gradient(90deg, #0096c7, #00B4D8); width:{nota_f}%; border-radius:0 10px 10px 0;"></div>
                    </div>
                </div>
                """
                st.markdown(bar_html, unsafe_allow_html=True)
            col_t1, col_t2 = st.columns(2)
            with col_t1: st.metric(f"{nome_casa} OVRall", f"{res['ovrall_casa']:.1f}")
            with col_t2: st.metric(f"{nome_fora} OVRall", f"{res['ovrall_fora']:.1f}")
        else:
            st.info("Detalhamento OVRall indisponível.")

    with st.expander("🧠 IC – Índice de Contexto", expanded=False):
        ic_casa, ic_fora = res['ic_casa'], res['ic_fora']
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**🏠 {nome_casa}**")
            st.markdown(f"<span class='big-number gold'>{ic_casa:.1f}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"**🏟️ {nome_fora}**")
            st.markdown(f"<span class='big-number gold'>{ic_fora:.1f}</span>", unsafe_allow_html=True)
        st.caption("Fatores: confronto direto, fator casa/visitante, odds.")

    # ========== SEÇÃO 2: MYPREDICT VALUE ==========
    st.markdown("---")
    st.markdown("<h2 style='text-align:center; color:#FFD700;'>👑 MyPredict Value</h2>", unsafe_allow_html=True)
    mpv_casa, mpv_fora = res['mpv_casa'], res['mpv_fora']
    border_casa = '2px solid #FFD700' if mpv_casa >= mpv_fora else '1px solid #555'
    border_fora = '2px solid #FFD700' if mpv_fora >= mpv_casa else '1px solid #555'
    col_mpv1, col_mpv2 = st.columns(2)
    with col_mpv1:
        st.markdown(f"""
        <div class="card" style="border:{border_casa}; text-align:center;">
            <div style="font-size:1.2rem;">{nome_casa}</div>
            <div class="big-number gold">{mpv_casa:.1f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_mpv2:
        st.markdown(f"""
        <div class="card" style="border:{border_fora}; text-align:center;">
            <div style="font-size:1.2rem;">{nome_fora}</div>
            <div class="big-number gold">{mpv_fora:.1f}</div>
        </div>
        """, unsafe_allow_html=True)

    # Superação
    sup_casa = res.get('superacao_casa', 0)
    sup_fora = res.get('superacao_fora', 0)
    st.markdown(f"""
    <div style="text-align:center; margin:10px 0;">
        <span>🔺 Superação: </span>
        <span class="{'green' if sup_casa >= 0 else 'red'}">{nome_casa} {sup_casa:+.1f} pts</span> |
        <span class="{'green' if sup_fora >= 0 else 'red'}">{nome_fora} {sup_fora:+.1f} pts</span>
    </div>
    <div style="text-align:center; font-size:0.8rem; color:#aaa;">Superação mede se o time está acima ou abaixo da expectativa (prateleira projetada).</div>
    """, unsafe_allow_html=True)

    # ========== SEÇÃO 3: CONTRASTE TÁTICO ==========
    if res.get('tactical'):
        st.markdown("---")
        st.markdown("## 🧪 Contraste Tático (MPV Dye)")
        tac = res['tactical']
        col_radar, col_mapa = st.columns([2, 1])
        with col_radar:
            radar_img = radar_chart(tac['dimensions_casa'], tac['dimensions_fora'])
            if radar_img:
                st.image(f"data:image/png;base64,{radar_img}", use_container_width=True)
        with col_mapa:
            heat_img = field_heatmap_annotated(tac['deltas'], tac.get('critical_routes'))
            if heat_img:
                st.image(f"data:image/png;base64,{heat_img}", use_container_width=True, caption="Azul: vantagem casa, Vermelho: vantagem fora")
        # Rotas críticas
        st.markdown("### 🎯 Rotas Críticas")
        for dim, delta, interp in tac.get('critical_routes', []):
            if delta > 0:
                st.success(f"{interp} (Vantagem {nome_casa})")
            else:
                st.error(f"{interp} (Vantagem {nome_fora})")
        # Deltas
        st.markdown("### 📊 Diferencial Tático (Δ)")
        deltas = tac['deltas']
        rows = []
        for dim, d in deltas.items():
            if d > 0: vant = f"{nome_casa} +{d:.1f}"
            elif d < 0: vant = f"{nome_fora} +{abs(d):.1f}"
            else: vant = "Equilíbrio"
            rows.append((dim, vant, d))
        df = pd.DataFrame(rows, columns=['Dimensão', 'Vantagem', 'Δ']).sort_values('Δ', key=abs, ascending=False)
        st.dataframe(df[['Dimensão', 'Vantagem']], use_container_width=True)

    # ========== SEÇÃO 4: PROBABILIDADES ==========
    st.markdown("---")
    st.markdown("## 🎯 Probabilidades de Mercado")
    st.caption("Média entre modelo original e avançado")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown(f"<div class='card card-gold' style='text-align:center;'><div style='font-size:1.2rem;'>🏠 Casa</div><div class='big-number gold'>{res['p1']:.1%}</div></div>", unsafe_allow_html=True)
    with col_p2:
        st.markdown(f"<div class='card card-gold' style='text-align:center;'><div style='font-size:1.2rem;'>🤝 Empate</div><div class='big-number gold'>{res['pX']:.1%}</div></div>", unsafe_allow_html=True)
    with col_p3:
        st.markdown(f"<div class='card card-gold' style='text-align:center;'><div style='font-size:1.2rem;'>🏟️ Fora</div><div class='big-number gold'>{res['p2']:.1%}</div></div>", unsafe_allow_html=True)

    st.markdown("### 🎲 Mercados Especiais")
    cols_m = st.columns(4)
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
        bg = "#FFD700" if "GOLD" in selo else "#4CAF50" if "Value" in selo else "#2196F3" if "Favorito" in selo else "#555"
        with cols_m[i]:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
                <div style="font-size:0.9rem;">{nome}</div>
                <div class="medium-number gold">{prob:.1%}</div>
                <div class="selo-badge" style="background:{bg}; color:#000;">{selo if selo else '⚪'}</div>
            </div>
            """, unsafe_allow_html=True)
