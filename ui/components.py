import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from config import THRESHOLD_GOLD, THRESHOLD_VALUE, THRESHOLD_FAVORITO, MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

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
# MAPA DE CALOR (mantido)
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
    ax.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode()
    plt.close()
    return img_base64

# ------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE EXIBIÇÃO
# ------------------------------------------------------------
def show_results_manual(res):
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']

    # ========== SEÇÃO 1: PILARES FUNDAMENTAIS ==========
    st.markdown("## 🔬 Pilares Fundamentais do MyPredict")
    with st.expander("📊 Todos os valores dos pilares", expanded=False):
        st.write(f"**⚡ IMA:** {nome_casa} = {res['ima_casa']:.2f} | {nome_fora} = {res['ima_fora']:.2f}")
        st.write(f"**📈 OVRall:** {nome_casa} = {res['ovrall_casa']:.2f} | {nome_fora} = {res['ovrall_fora']:.2f}")
        st.write(f"**🧠 IC:** {nome_casa} = {res['ic_casa']:.2f} | {nome_fora} = {res['ic_fora']:.2f}")
        st.write(f"**🔺 Superação:** {nome_casa} = {res.get('superacao_casa',0):+.1f} | {nome_fora} = {res.get('superacao_fora',0):+.1f}")
        st.write(f"**🏅 ELO norm:** {nome_casa} = {res.get('elo_norm_casa',50):.1f} | {nome_fora} = {res.get('elo_norm_fora',50):.1f}")

    # Detalhamento IMA
    with st.expander(f"⚡ Detalhamento do IMA (cada jogo vale pontos)"):
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
            st.info("Menos de 5 jogos fornecidos; IMA assume 50.0")

    # Detalhamento OVRall
    with st.expander(f"📈 Detalhamento do OVRall (percentis)"):
        if res.get('detalhes_ovr'):
            for dim, dados in res['detalhes_ovr'].items():
                st.write(f"**{dim}**")
                st.write(f"{nome_casa}: {res['notas_casa'].get(dim, 0):.1f} | {nome_fora}: {res['notas_fora'].get(dim, 0):.1f}")
                for ind, val, perc in dados['casa']:
                    st.caption(f"  {ind}: {nome_casa} {val:.2f} (percentil {perc:.0f})")
                for ind, val, perc in dados['fora']:
                    st.caption(f"  {ind}: {nome_fora} {val:.2f} (percentil {perc:.0f})")
        else:
            st.info("Detalhamento OVRall não disponível.")

    # ========== SEÇÃO 2: MPVs ==========
    st.markdown("---")
    st.markdown("## 👑 Valores MyPredict")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🛡️ MPV Tradicional")
        st.markdown(f"""
        <div style="background:#1a1e2b; border-radius:20px; padding:20px; text-align:center;">
            <span style="font-size:2rem; color:#ffd700;">{nome_casa} {res['mpv_casa']:.1f}</span><br>
            <span style="font-size:2rem; color:#c0c0c0;">{res['mpv_fora']:.1f} {nome_fora}</span>
        </div>
        """, unsafe_allow_html=True)
        st.caption("(IMA+OVRall+IC)/3 + Superação + ELO×0.4")
    with col2:
        st.markdown("### 💎 MP Value 10.0")
        try:
            mpv_tatico_casa = res.get('mpv_tactical_casa', 50)
            mpv_tatico_fora = res.get('mpv_tactical_fora', 50)
            ovr_casa = res['ovrall_casa']; ovr_fora = res['ovrall_fora']
            ic_casa = res['ic_casa']; ic_fora = res['ic_fora']
            elo_casa = res.get('elo_norm_casa', 50); elo_fora = res.get('elo_norm_fora', 50)
            super_casa = res.get('superacao_casa', 0); super_fora = res.get('superacao_fora', 0)
            w = {'mpv_tatico':0.3, 'ovr':0.25, 'ic':0.15, 'elo':0.2, 'super':0.1}
            def nota(mpv_t, ovr, ic, elo, sup):
                return (w['mpv_tatico']*mpv_t + w['ovr']*ovr + w['ic']*ic + w['elo']*elo + w['super']*(sup+10)*5) / 100 * 10
            nc = min(10, max(0, nota(mpv_tatico_casa, ovr_casa, ic_casa, elo_casa, super_casa)))
            nf = min(10, max(0, nota(mpv_tatico_fora, ovr_fora, ic_fora, elo_fora, super_fora)))
            st.markdown(f"""
            <div style="display:flex; justify-content:space-around;">
                <div style="text-align:center;"><span style="font-size:3rem; color:#ffd700;">{nc:.1f}</span><br>{nome_casa}</div>
                <div style="text-align:center;"><span style="font-size:3rem; color:#00B4D8;">{nf:.1f}</span><br>{nome_fora}</div>
            </div>
            """, unsafe_allow_html=True)
            st.caption("Pesos: mpv_tatico 0.3, ovr 0.25, ic 0.15, elo 0.2, super 0.1")
        except:
            st.warning("Nota 10.0 indisponível.")

    # ========== SEÇÃO 3: PROBABILIDADES ==========
    st.markdown("---")
    st.markdown("## 🎯 Probabilidades de Mercado")
    st.markdown("### 📜 Fórmulas Originais")
    col_o1, col_o2, col_o3, col_o4, col_o5 = st.columns(5)
    col_o1.metric("1X2 Casa", f"{res['p1_orig']:.1%}")
    col_o2.metric("Empate", f"{res['pX_orig']:.1%}")
    col_o3.metric("1X2 Fora", f"{res['p2_orig']:.1%}")
    col_o4.metric("Over 2.5", f"{res['over25_orig']:.1%}")
    col_o5.metric("BTTS", f"{res['btts_orig']:.1%}")
    col_o1.metric("Gol HT", f"{res['gol_ht_orig']:.1%}")
    col_o2.metric("Escanteios", f"{res['esc_orig']:.1%}")

    st.markdown("### 🧪 Modelo Avançado (Premier League)")
    if res.get('p1_adv') is not None:
        col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)
        col_a1.metric("1X2 Casa", f"{res['p1_adv']:.1%}")
        col_a2.metric("Empate", f"{res['pX_adv']:.1%}")
        col_a3.metric("1X2 Fora", f"{res['p2_adv']:.1%}")
        col_a4.metric("Over 2.5", f"{res['over25_adv']:.1%}")
        col_a5.metric("BTTS", f"{res['btts_adv']:.1%}")
        col_a1.metric("Gol HT", f"{res['gol_ht_adv']:.1%}")
        col_a2.metric("Escanteios", f"{res['esc_adv']:.1%}")
    else:
        st.info("Modelo calibrado não disponível. Verifique o arquivo .pkl.")

    # ========== SEÇÃO 4: CONTRASTE TÁTICO ==========
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
            if tac['heatmap']:
                st.image(f"data:image/png;base64,{tac['heatmap']}", use_container_width=True)
        st.markdown("### 🎯 Rotas Críticas")
        for dim, delta, interp in tac.get('critical_routes', []):
            if delta > 0: st.success(interp)
            else: st.error(interp)
        st.markdown("### 📊 Deltas")
        st.dataframe(pd.DataFrame(tac['deltas'].items(), columns=['Dimensão', 'Δ']).sort_values('Δ', key=abs, ascending=False))

    # ========== SEÇÃO 5: ANÁLISE DETALHADA (COMPARATIVOS) ==========
    st.markdown("---")
    st.markdown("## 📊 Análise Completa Detalhada")
    # (Adicione aqui as seções de comparativo real, gráfico de atributos, etc., se desejar.)
