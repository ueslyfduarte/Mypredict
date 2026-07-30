import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from config import THRESHOLD_GOLD, THRESHOLD_VALUE, THRESHOLD_FAVORITO

# ------------------------------------------------------------
# Funções para gráficos (mantidas)
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
    ax.plot([0,0,100,100,0], [0,68,68,0,0], color='white', lw=2)
    ax.plot([50,50], [0,68], color='white', lw=1.5)
    ax.plot([0,16.5],[13.84,13.84], color='white'); ax.plot([16.5,16.5],[13.84,54.16], color='white')
    ax.plot([0,16.5],[54.16,54.16], color='white')
    ax.plot([83.5,100],[13.84,13.84], color='white'); ax.plot([83.5,83.5],[13.84,54.16], color='white')
    ax.plot([83.5,100],[54.16,54.16], color='white')
    ax.add_patch(plt.Circle((50,34), 9.15, fill=False, color='white'))
    zones = {
        'ataque_posicional': (70,20,30,28, "Ataque Pos."),
        'ataque_transicao': (40,15,30,38, "Transição"),
        'defesa_organizada': (0,20,30,28, "Defesa Org."),
        'bola_parada_ofensiva': (85,0,15,68, "Bola Parada"),
        'controle_meio_campo': (30,15,40,38, "Meio-Campo"),
        'pressao_alta': (60,0,40,68, "Pressão Alta"),
        'resistencia_pressao': (0,0,30,68, "Resist. Press."),
    }
    for dim, delta in deltas.items():
        if dim in zones:
            x,y,w,h,label = zones[dim]
            intensity = min(abs(delta)/30, 1.0)
            color = 'blue' if delta>0 else 'red'
            rect = plt.Rectangle((x,y), w, h, color=color, alpha=intensity*0.6)
            ax.add_patch(rect)
            ax.text(x+w/2, y+h/2, f"{label}\n{delta:+.1f}", ha='center', va='center', fontsize=7, color='white', fontweight='bold')
    ax.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

# ------------------------------------------------------------
# Função principal de exibição
# ------------------------------------------------------------
def show_results_manual(res):
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']

    # Estilo global: texto branco
    st.markdown("""
    <style>
        body, .stApp, p, h1, h2, h3, h4, h5, h6, span, div {
            color: #FFFFFF !important;
        }
        .stMetric label, .stMetric div {
            color: #FFFFFF !important;
        }
        .gold { color: #FFD700 !important; }
        .green { color: #00FF7F !important; }
        .red { color: #FF4D4D !important; }
    </style>
    """, unsafe_allow_html=True)

    # ========== SEÇÃO 1: CABEÇALHO E MPV ==========
    st.markdown(f"<h1 style='text-align:center;'>{nome_casa} vs {nome_fora}</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#FFD700 !important;'>MyPredict Value</h2>", unsafe_allow_html=True)

    col_mpv1, col_mpv2 = st.columns(2)
    with col_mpv1:
        st.markdown(f"<div style='text-align:center;'><span style='font-size:3rem; color:#FFD700;'>{res['mpv_casa']:.1f}</span><br><span style='color:#FFFFFF;'>{nome_casa}</span></div>", unsafe_allow_html=True)
    with col_mpv2:
        st.markdown(f"<div style='text-align:center;'><span style='font-size:3rem; color:#FFD700;'>{res['mpv_fora']:.1f}</span><br><span style='color:#FFFFFF;'>{nome_fora}</span></div>", unsafe_allow_html=True)

    # Superação com cores
    sup_casa = res.get('superacao_casa',0)
    sup_fora = res.get('superacao_fora',0)
    cor_casa = '#00FF7F' if sup_casa >= 0 else '#FF4D4D'
    cor_fora = '#00FF7F' if sup_fora >= 0 else '#FF4D4D'
    st.markdown(f"<div style='text-align:center;'>🔺 Superação: {nome_casa} <span style='color:{cor_casa};'>{sup_casa:+.1f} pts</span> | {nome_fora} <span style='color:{cor_fora};'>{sup_fora:+.1f} pts</span></div>", unsafe_allow_html=True)
    st.caption("Superação: diferença entre a prateleira real (posição) e a projetada. Positiva (verde) indica time acima do esperado; negativa (vermelho), abaixo.")

    # ========== SEÇÃO 2: PILARES (IMA, OVRall, IC) ==========
    st.markdown("---")
    st.markdown("## 🔬 Pilares do MyPredict")
    tab_ima, tab_ovr, tab_ic = st.tabs(["⚡ IMA", "📈 OVRall", "🧠 IC"])

    with tab_ima:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{nome_casa} IMA", f"{res['ima_casa']:.1f}")
        with col2:
            st.metric(f"{nome_fora} IMA", f"{res['ima_fora']:.1f}")
        with st.expander("Detalhamento do IMA"):
            if res.get('detalhes_ima'):
                for time, key in [(nome_casa, 'casa'), (nome_fora, 'fora')]:
                    st.write(f"**{time}**")
                    for recorte, jogos in res['detalhes_ima'][key].items():
                        if jogos:
                            media = np.mean([j['pontos'] for j in jogos])
                            st.write(f"{recorte}: média {media:.2f}")
                            for j in jogos:
                                st.caption(f"  {j['jogo']} → {j['pontos']:.2f} pts (Prat. time: {j['prateleira_time']}, Adv: {j['prateleira_adv']})")
            else:
                st.info("Menos de 5 jogos; IMA assume 50.0")

    with tab_ovr:
        # Gráficos de barras por subnível
        if res.get('detalhes_ovr'):
            dims_order = ['Ataque', 'Defesa', 'MeioCampo', 'Consistencia', 'Resiliencia']
            notas_casa = [res['notas_casa'].get(d, 0) for d in dims_order]
            notas_fora = [res['notas_fora'].get(d, 0) for d in dims_order]
            df_ovr = pd.DataFrame({'Dimensão': dims_order, nome_casa: notas_casa, nome_fora: notas_fora}).set_index('Dimensão')
            st.bar_chart(df_ovr, use_container_width=True)
            st.caption("Notas por dimensão do OVRall (0-100)")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{nome_casa} OVRall", f"{res['ovrall_casa']:.1f}")
        with col2:
            st.metric(f"{nome_fora} OVRall", f"{res['ovrall_fora']:.1f}")
        with st.expander("Detalhamento do OVRall"):
            if res.get('detalhes_ovr'):
                for dim, dados in res['detalhes_ovr'].items():
                    st.write(f"**{dim}**")
                    for ind, val, perc in dados['casa']:
                        st.caption(f"  {ind}: {nome_casa} {val:.2f} (percentil {perc:.0f})")
                    for ind, val, perc in dados['fora']:
                        st.caption(f"  {ind}: {nome_fora} {val:.2f} (percentil {perc:.0f})")

    with tab_ic:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{nome_casa} IC", f"{res['ic_casa']:.1f}")
        with col2:
            st.metric(f"{nome_fora} IC", f"{res['ic_fora']:.1f}")
        st.caption("IC: média ponderada de fatores contextuais (confronto direto, fator casa, odds).")

    # ========== SEÇÃO 3: PROBABILIDADES MÉDIAS ==========
    st.markdown("---")
    st.markdown("## 🎯 Probabilidades de Mercado (Média Original + Avançado)")
    prob_cols = st.columns(5)
    prob_cols[0].metric("Casa", f"{res['p1']:.1%}")
    prob_cols[1].metric("Empate", f"{res['pX']:.1%}")
    prob_cols[2].metric("Fora", f"{res['p2']:.1%}")
    prob_cols[3].metric("Over 2.5", f"{res['over25']:.1%}")
    prob_cols[4].metric("BTTS", f"{res['btts']:.1%}")
    prob_cols2 = st.columns(2)
    prob_cols2[0].metric("Gol 1ºT", f"{res['gol_ht']:.1%}")
    prob_cols2[1].metric("Escanteios", f"{res['esc']:.1%}")

    st.markdown("**Selos de confiança (baseados nas probabilidades médias):**")
    selos_cols = st.columns(5)
    mercados = [
        ("1X2 Casa", res['p1']), ("Empate", res['pX']), ("1X2 Fora", res['p2']),
        ("Over 2.5", res['over25']), ("BTTS", res['btts'])
    ]
    for i, (nome, prob) in enumerate(mercados):
        selo = ""
        if prob >= 0.70: selo = "🥇 GOLD"
        elif prob >= 0.60: selo = "✅ Value"
        elif prob >= 0.50: selo = "🔵 Favorito"
        with selos_cols[i]:
            st.markdown(f"**{nome}** {selo}")

    # ========== SEÇÃO 4: CONTRASTE TÁTICO (se disponível) ==========
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
        st.markdown("### 🎯 Rotas Críticas")
        for dim, delta, interp in tac.get('critical_routes', []):
            if delta > 0:
                st.success(interp)
            else:
                st.error(interp)
        st.markdown("### 📊 Deltas por Dimensão")
        st.dataframe(pd.DataFrame(tac['deltas'].items(), columns=['Dimensão', 'Δ']).sort_values('Δ', key=abs, ascending=False))
