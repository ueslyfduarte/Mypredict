import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from config import THRESHOLD_GOLD, THRESHOLD_VALUE, THRESHOLD_FAVORITO

# ------------------------------------------------------------
# GRÁFICOS
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

# ------------------------------------------------------------
# ANÁLISE DESCRITIVA AUTOMÁTICA
# ------------------------------------------------------------
def gerar_analise_descritiva(res):
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']
    ima_casa = res['ima_casa']
    ima_fora = res['ima_fora']
    ovr_casa = res['ovrall_casa']
    ovr_fora = res['ovrall_fora']
    ic_casa = res['ic_casa']
    ic_fora = res['ic_fora']
    mpv_casa = res['mpv_casa']
    mpv_fora = res['mpv_fora']
    sup_casa = res.get('superacao_casa', 0)
    sup_fora = res.get('superacao_fora', 0)

    texto = f"### 📝 Análise Descritiva Completa\n"
    texto += f"**{nome_casa}** e **{nome_fora}** se enfrentam em um confronto que, segundo o MyPredict, "
    if mpv_casa > mpv_fora + 1:
        texto += f"aponta ligeiro favoritismo para o time da casa, com MyPredict Value de {mpv_casa:.1f} contra {mpv_fora:.1f}.\n"
    elif mpv_fora > mpv_casa + 1:
        texto += f"aponta ligeiro favoritismo para o visitante, com MyPredict Value de {mpv_fora:.1f} contra {mpv_casa:.1f}.\n"
    else:
        texto += f"indica um duelo muito equilibrado, com MyPredict Value de {mpv_casa:.1f} para o mandante e {mpv_fora:.1f} para o visitante.\n"

    # IMA
    texto += f"\n**⚡ Momento (IMA):** "
    if ima_casa > ima_fora + 3:
        texto += f"O {nome_casa} vive melhor fase (IMA {ima_casa:.1f} vs {ima_fora:.1f}). "
    elif ima_fora > ima_casa + 3:
        texto += f"O {nome_fora} chega em melhor momento (IMA {ima_fora:.1f} vs {ima_casa:.1f}). "
    else:
        texto += f"Ambos os times têm momentos semelhantes (IMA {ima_casa:.1f} e {ima_fora:.1f}). "

    # OVRall
    texto += f"\n**📈 Força Estrutural (OVRall):** "
    if ovr_casa > ovr_fora + 3:
        texto += f"O {nome_casa} apresenta um desempenho estrutural superior (OVRall {ovr_casa:.1f} vs {ovr_fora:.1f}). "
        if res.get('notas_casa'):
            atk_c = res['notas_casa'].get('Ataque', 50)
            atk_f = res['notas_fora'].get('Ataque', 50)
            if atk_c > atk_f + 5:
                texto += f"Seu ataque é o ponto forte (nota {atk_c:.0f} contra {atk_f:.0f}). "
    elif ovr_fora > ovr_casa + 3:
        texto += f"O {nome_fora} leva vantagem estrutural (OVRall {ovr_fora:.1f} vs {ovr_casa:.1f}). "
    else:
        texto += f"Estruturalmente, os times são parecidos (OVRall {ovr_casa:.1f} e {ovr_fora:.1f}). "

    # IC
    texto += f"\n**🧠 Contexto (IC):** O índice de contexto, que considera fatores como histórico recente e local, "
    if ic_casa > ic_fora + 5:
        texto += f"favorece o {nome_casa} (IC {ic_casa:.1f} vs {ic_fora:.1f}). "
    elif ic_fora > ic_casa + 5:
        texto += f"favorece o {nome_fora} (IC {ic_fora:.1f} vs {ic_casa:.1f}). "
    else:
        texto += f"está equilibrado (IC {ic_casa:.1f} e {ic_fora:.1f}). "

    # Superação
    texto += f"\n**🔺 Superação:** "
    if sup_casa > 0:
        texto += f"O {nome_casa} está superando as expectativas (+{sup_casa:.1f} pts). "
    elif sup_casa < 0:
        texto += f"O {nome_casa} está abaixo do esperado ({sup_casa:.1f} pts). "
    if sup_fora > 0:
        texto += f"O {nome_fora} também supera as expectativas (+{sup_fora:.1f} pts). "
    elif sup_fora < 0:
        texto += f"O {nome_fora} está abaixo do projetado ({sup_fora:.1f} pts). "

    # Contraste tático
    if res.get('tactical') and res['tactical']['critical_routes']:
        texto += f"\n**🧪 Contraste Tático:** "
        rotas = res['tactical']['critical_routes']
        for dim, delta, _ in rotas[:2]:
            if delta > 0:
                texto += f"O {nome_casa} leva vantagem em {dim} (+{delta:.1f}). "
            else:
                texto += f"O {nome_fora} leva vantagem em {dim} ({delta:.1f}). "

    # Probabilidades
    texto += f"\n**🎯 Probabilidades:** O modelo estima {res['p1']:.1%} de vitória do {nome_casa}, {res['pX']:.1%} de empate e {res['p2']:.1%} de vitória do {nome_fora}. "
    texto += f"No mercado de gols, Over 2.5 tem {res['over25']:.1%} de chance; BTTS, {res['btts']:.1%}. "
    texto += f"Gol no 1º tempo apresenta {res['gol_ht']:.1%}, e Over 8.5 escanteios, {res['esc']:.1%}."

    return texto

# ------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE RESULTADOS
# ------------------------------------------------------------
def show_results_manual(res):
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']

    # CSS refinado
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #FFFFFF; }
        .gold { color: #FFD700 !important; }
        .silver { color: #C0C0C0 !important; }
        .green { color: #00FF7F !important; }
        .red { color: #FF4D4D !important; }
        .big-number { font-size: 2.2rem; font-weight: 900; }
        .card { background: linear-gradient(145deg, #1a1e2b, #121621); border-radius: 20px; padding: 20px; margin: 10px 0; border: 1px solid #333; }
        .card-gold { border: 2px solid #FFD700; }
        .selo-badge { display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9rem; }
        hr { border-color: #333; }
    </style>
    """, unsafe_allow_html=True)

    # Abas de resultado
    tabs = st.tabs(["📋 Resumo & Análise", "🔬 Pilares", "🧪 Contraste Tático", "🎯 Mercados"])

    # ====================== ABA 1: RESUMO & ANÁLISE DESCRITIVA ======================
    with tabs[0]:
        st.markdown(f"<h1 style='text-align:center;'>{nome_casa} vs {nome_fora}</h1>", unsafe_allow_html=True)
        mpv_casa = res['mpv_casa']
        mpv_fora = res['mpv_fora']
        border_casa = '2px solid #FFD700' if mpv_casa >= mpv_fora else '1px solid #555'
        border_fora = '2px solid #FFD700' if mpv_fora >= mpv_casa else '1px solid #555'
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="card" style="border:{border_casa}; text-align:center;">
                <div style="font-size:1.2rem;">{nome_casa}</div>
                <div class="big-number gold">{mpv_casa:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="card" style="border:{border_fora}; text-align:center;">
                <div style="font-size:1.2rem;">{nome_fora}</div>
                <div class="big-number gold">{mpv_fora:.1f}</div>
            </div>
            """, unsafe_allow_html=True)

        sup_casa = res.get('superacao_casa', 0)
        sup_fora = res.get('superacao_fora', 0)
        st.markdown(f"""
        <div style="text-align:center; margin:10px 0;">
            <span>🔺 Superação: </span>
            <span class="{'green' if sup_casa >= 0 else 'red'}">{nome_casa} {sup_casa:+.1f} pts</span> |
            <span class="{'green' if sup_fora >= 0 else 'red'}">{nome_fora} {sup_fora:+.1f} pts</span>
        </div>
        """, unsafe_allow_html=True)

        # Análise descritiva automática
        st.markdown(gerar_analise_descritiva(res))

    # ====================== ABA 2: PILARES ======================
    with tabs[1]:
        st.markdown("## 🔬 Pilares do MyPredict")
        # Cartões visíveis (IMA, OVRall, IC)
        col_ima, col_ovr, col_ic = st.columns(3)
        with col_ima:
            st.markdown(f"**⚡ IMA**")
            st.markdown(f"<div class='card' style='text-align:center;'><span class='big-number gold'>{res['ima_casa']:.1f}</span><br><small>{nome_casa}</small></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card' style='text-align:center;'><span class='big-number gold'>{res['ima_fora']:.1f}</span><br><small>{nome_fora}</small></div>", unsafe_allow_html=True)
        with col_ovr:
            st.markdown(f"**📈 OVRall**")
            st.markdown(f"<div class='card' style='text-align:center;'><span class='big-number gold'>{res['ovrall_casa']:.1f}</span><br><small>{nome_casa}</small></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card' style='text-align:center;'><span class='big-number gold'>{res['ovrall_fora']:.1f}</span><br><small>{nome_fora}</small></div>", unsafe_allow_html=True)
        with col_ic:
            st.markdown(f"**🧠 IC**")
            st.markdown(f"<div class='card' style='text-align:center;'><span class='big-number gold'>{res['ic_casa']:.1f}</span><br><small>{nome_casa}</small></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='card' style='text-align:center;'><span class='big-number gold'>{res['ic_fora']:.1f}</span><br><small>{nome_fora}</small></div>", unsafe_allow_html=True)

        # Detalhamento IMA
        with st.expander("⚡ Detalhamento do IMA"):
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

        # Detalhamento OVRall (duelo de barras)
        with st.expander("📈 Detalhamento do OVRall (subníveis)"):
            if res.get('detalhes_ovr'):
                dims = ['Ataque', 'Defesa', 'MeioCampo', 'Consistencia', 'Resiliencia']
                for dim in dims:
                    nota_c = res['notas_casa'].get(dim, 0)
                    nota_f = res['notas_fora'].get(dim, 0)
                    st.markdown(f"**{dim}**")
                    col_bar1, col_bar2, col_bar3 = st.columns([1, 3, 1])
                    with col_bar1:
                        st.markdown(f"<span class='gold'>{nota_c:.1f}</span>")
                    with col_bar2:
                        st.markdown(f"""
                        <div style="display:flex; align-items:center; height:20px; background:#2d3242; border-radius:10px; overflow:hidden;">
                            <div style="width:50%; height:100%; display:flex; justify-content:flex-end;">
                                <div style="height:100%; background:linear-gradient(90deg, #FFD700, #FFA500); width:{nota_c}%; border-radius:10px 0 0 10px;"></div>
                            </div>
                            <div style="width:50%; height:100%; display:flex;">
                                <div style="height:100%; background:linear-gradient(90deg, #0096c7, #00B4D8); width:{nota_f}%; border-radius:0 10px 10px 0;"></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_bar3:
                        st.markdown(f"<span class='silver'>{nota_f:.1f}</span>")
            else:
                st.info("Detalhamento OVRall indisponível.")

        # IC
        with st.expander("🧠 Detalhamento do IC"):
            st.write("Fatores: confronto direto, fator casa/visitante, odds.")
            st.write(f"{nome_casa}: {res['ic_casa']:.1f} | {nome_fora}: {res['ic_fora']:.1f}")

    # ====================== ABA 3: CONTRASTE TÁTICO ======================
    with tabs[2]:
        st.markdown("## 🧪 Contraste Tático (MPV Dye)")
        if res.get('tactical'):
            tac = res['tactical']
            st.markdown("### 📡 Radar Tático")
            radar_img = radar_chart(tac['dimensions_casa'], tac['dimensions_fora'])
            if radar_img:
                st.image(f"data:image/png;base64,{radar_img}", use_container_width=True)
            else:
                st.info("Dimensões insuficientes para gerar radar.")

            # Deltas com barras
            st.markdown("### 📊 Diferencial por Dimensão")
            deltas = tac['deltas']
            for dim, d in deltas.items():
                if d > 0:
                    bar_color = '#FFD700'
                    label = f"{nome_casa} +{d:.1f}"
                elif d < 0:
                    bar_color = '#00B4D8'
                    label = f"{nome_fora} +{abs(d):.1f}"
                else:
                    bar_color = '#888'
                    label = "Equilíbrio"
                st.markdown(f"""
                <div style="display:flex; align-items:center; margin:5px 0;">
                    <div style="width:150px; text-align:right; padding-right:10px; color:#aaa;">{dim}</div>
                    <div style="flex:1; background:#2d3242; border-radius:10px; height:12px;">
                        <div style="width:{min(abs(d), 50)}%; background:{bar_color}; border-radius:10px; height:12px;"></div>
                    </div>
                    <div style="width:120px; text-align:left; padding-left:10px; color:{bar_color};">{label}</div>
                </div>
                """, unsafe_allow_html=True)

            # Rotas críticas
            st.markdown("### 🎯 Rotas Críticas")
            for dim, delta, interp in tac.get('critical_routes', []):
                if delta > 0:
                    color = '#FFD700'
                    icon = '⚔️'
                    vant = f"Vantagem {nome_casa}"
                else:
                    color = '#FF4D4D'
                    icon = '🛡️'
                    vant = f"Vantagem {nome_fora}"
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid {color}; padding:10px; margin:10px 0;">
                    <span style="font-size:1.2rem;">{icon} {interp}</span><br>
                    <small style="color:#aaa;">{vant}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Dados táticos indisponíveis.")

    # ====================== ABA 4: MERCADOS ======================
    with tabs[3]:
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
            ("Over 8.5 Escanteios", res['esc']),
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
                    <div class="big-number gold">{prob:.1%}</div>
                    <div class="selo-badge" style="background:{bg}; color:#000;">{selo if selo else '⚪'}</div>
                </div>
                """, unsafe_allow_html=True)
