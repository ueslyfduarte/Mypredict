import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import altair as alt
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

def field_heatmap_annotated(dimensions_casa, dimensions_fora, deltas):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 68)
    ax.set_facecolor('#1a472a')

    zones = {
        'ataque_posicional': (70, 20, 30, 28, "Ataque\nPosicional", 'ataque_posicional'),
        'ataque_transicao': (40, 15, 30, 38, "Transição", 'ataque_transicao'),
        'defesa_organizada': (0, 20, 30, 28, "Defesa\nOrganizada", 'defesa_organizada'),
        'bola_parada_ofensiva': (85, 0, 15, 68, "Bola\nParada", 'bola_parada_ofensiva'),
        'controle_meio_campo': (30, 15, 40, 38, "Meio-Campo", 'controle_meio_campo'),
    }

    for dim_name, (x, y, w, h, label, dim_key) in zones.items():
        delta = deltas.get(dim_key, 0)
        intensity = min(abs(delta) / 30, 1.0) if delta else 0.2
        color = 'blue' if delta > 0 else 'red' if delta < 0 else 'gray'
        rect = plt.Rectangle((x, y), w, h, color=color, alpha=intensity * 0.4)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, f"{label}\n{delta:+.1f}", ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    for line in [
        [(0,0),(0,68)], [(0,68),(100,68)], [(100,68),(100,0)], [(100,0),(0,0)],
        [(50,0),(50,68)], [(0,16.5),(16.5,16.5)], [(16.5,16.5),(16.5,51.5)], [(0,51.5),(16.5,51.5)],
        [(83.5,16.5),(100,16.5)], [(83.5,16.5),(83.5,51.5)], [(83.5,51.5),(100,51.5)]
    ]:
        ax.plot([p[0] for p in line], [p[1] for p in line], color='white', lw=1.5, zorder=10)
    ax.add_patch(plt.Circle((50, 34), 9.15, fill=False, color='white', lw=1.5, zorder=10))

    ax.axis('off')
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
    ima_casa, ima_fora = res['ima_casa'], res['ima_fora']
    ovr_casa, ovr_fora = res['ovrall_casa'], res['ovrall_fora']
    ic_casa, ic_fora = res['ic_casa'], res['ic_fora']
    mpv_casa, mpv_fora = res['mpv_casa'], res['mpv_fora']
    sup_casa, sup_fora = res.get('superacao_casa', 0), res.get('superacao_fora', 0)

    texto = f"### 📝 Análise Descritiva Completa\n"
    texto += f"**{nome_casa}** e **{nome_fora}** se enfrentam em um confronto que, segundo o MyPredict, "
    if mpv_casa > mpv_fora + 1:
        texto += f"aponta ligeiro favoritismo para o time da casa, com MyPredict Value de {mpv_casa:.1f} contra {mpv_fora:.1f}.\n"
    elif mpv_fora > mpv_casa + 1:
        texto += f"aponta ligeiro favoritismo para o visitante, com MyPredict Value de {mpv_fora:.1f} contra {mpv_casa:.1f}.\n"
    else:
        texto += f"indica um duelo muito equilibrado, com MyPredict Value de {mpv_casa:.1f} para o mandante e {mpv_fora:.1f} para o visitante.\n"

    texto += f"\n**⚡ Momento (IMA):** "
    if ima_casa > ima_fora + 3:
        texto += f"O {nome_casa} vive melhor fase (IMA {ima_casa:.1f} vs {ima_fora:.1f}). "
    elif ima_fora > ima_casa + 3:
        texto += f"O {nome_fora} chega em melhor momento (IMA {ima_fora:.1f} vs {ima_casa:.1f}). "
    else:
        texto += f"Ambos os times têm momentos semelhantes (IMA {ima_casa:.1f} e {ima_fora:.1f}). "

    texto += f"\n**📈 Força Estrutural (OVRall):** "
    if ovr_casa > ovr_fora + 3:
        texto += f"O {nome_casa} apresenta um desempenho estrutural superior (OVRall {ovr_casa:.1f} vs {ovr_fora:.1f}). "
    elif ovr_fora > ovr_casa + 3:
        texto += f"O {nome_fora} leva vantagem estrutural (OVRall {ovr_fora:.1f} vs {ovr_casa:.1f}). "
    else:
        texto += f"Estruturalmente, os times são parecidos (OVRall {ovr_casa:.1f} e {ovr_fora:.1f}). "

    texto += f"\n**🧠 Contexto (IC):** "
    if ic_casa > ic_fora + 5:
        texto += f"O contexto favorece o {nome_casa} (IC {ic_casa:.1f} vs {ic_fora:.1f}). "
    elif ic_fora > ic_casa + 5:
        texto += f"O contexto favorece o {nome_fora} (IC {ic_fora:.1f} vs {ic_casa:.1f}). "
    else:
        texto += f"O contexto está equilibrado (IC {ic_casa:.1f} e {ic_fora:.1f}). "

    texto += f"\n**🔺 Superação:** "
    if sup_casa > 0: texto += f"O {nome_casa} está superando as expectativas (+{sup_casa:.1f} pts). "
    elif sup_casa < 0: texto += f"O {nome_casa} está abaixo do esperado ({sup_casa:.1f} pts). "
    if sup_fora > 0: texto += f"O {nome_fora} também supera as expectativas (+{sup_fora:.1f} pts). "
    elif sup_fora < 0: texto += f"O {nome_fora} está abaixo do projetado ({sup_fora:.1f} pts). "

    if res.get('tactical') and res['tactical']['critical_routes']:
        texto += f"\n**🧪 Contraste Tático:** "
        for dim, delta, _ in res['tactical']['critical_routes'][:2]:
            if delta > 0: texto += f"O {nome_casa} leva vantagem em {dim} (+{delta:.1f}). "
            else: texto += f"O {nome_fora} leva vantagem em {dim} ({delta:.1f}). "

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

    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #FFFFFF; }
        .gold { color: #FFD700 !important; }
        .big-number { font-size: 2.2rem; font-weight: 900; }
        .card { background: linear-gradient(145deg, #1a1e2b, #121621); border-radius: 20px; padding: 20px; margin: 10px 0; border: 1px solid #333; text-align:center; }
        .card-winner { background: linear-gradient(145deg, #FFD700, #FFA500); border-radius: 20px; padding: 20px; margin: 10px 0; border: 2px solid #000; text-align:center; }
        .card-winner .big-number, .card-winner div, .card-winner small { color: #000 !important; }
        .card-loser { background: linear-gradient(145deg, #1a1e2b, #121621); border-radius: 20px; padding: 20px; margin: 10px 0; border: 2px solid #FFD700; text-align:center; }
        .card-loser .big-number, .card-loser div { color: #FFD700 !important; }
        .card-loser small { color: #aaa !important; }
        .selo-badge { display: inline-block; padding: 8px 20px; border-radius: 25px; font-weight: bold; font-size: 1.1rem; margin-top:8px; }
        hr { border-color: #333; }
    </style>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🔬 Pilares", "🧪 Contraste Tático", "🔮 Cenários & Estilos", "📋 Resumo & Análise", "🎯 Mercados"])

    # ====================== ABA 1: PILARES ======================
    with tabs[0]:
        st.markdown("## 🔬 Pilares do MyPredict")

        st.markdown("### ⚡ IMA – Índice de Momentum Atual")
        col_ima1, col_ima2 = st.columns(2)
        winner_ima = nome_casa if res['ima_casa'] >= res['ima_fora'] else nome_fora
        with col_ima1:
            card_class = "card-winner" if nome_casa == winner_ima else "card-loser"
            st.markdown(f"<div class='{card_class}'><span class='big-number'>{res['ima_casa']:.1f}</span><br><small>{nome_casa}</small></div>", unsafe_allow_html=True)
        with col_ima2:
            card_class = "card-winner" if nome_fora == winner_ima else "card-loser"
            st.markdown(f"<div class='{card_class}'><span class='big-number'>{res['ima_fora']:.1f}</span><br><small>{nome_fora}</small></div>", unsafe_allow_html=True)

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

        st.markdown("### 📈 OVRall – Desempenho Estrutural")
        col_ovr1, col_ovr2 = st.columns(2)
        winner_ovr = nome_casa if res['ovrall_casa'] >= res['ovrall_fora'] else nome_fora
        with col_ovr1:
            card_class = "card-winner" if nome_casa == winner_ovr else "card-loser"
            st.markdown(f"<div class='{card_class}'><span class='big-number'>{res['ovrall_casa']:.1f}</span><br><small>{nome_casa}</small></div>", unsafe_allow_html=True)
        with col_ovr2:
            card_class = "card-winner" if nome_fora == winner_ovr else "card-loser"
            st.markdown(f"<div class='{card_class}'><span class='big-number'>{res['ovrall_fora']:.1f}</span><br><small>{nome_fora}</small></div>", unsafe_allow_html=True)

        st.markdown("#### 📈 Detalhamento do OVRall (subníveis)")
        if res.get('detalhes_ovr'):
            for dim in ['Ataque', 'Defesa', 'MeioCampo', 'Consistencia', 'Resiliencia']:
                nota_c = res['notas_casa'].get(dim, 0)
                nota_f = res['notas_fora'].get(dim, 0)
                st.markdown(f"**{dim}**")
                col_bar1, col_bar2, col_bar3 = st.columns([1, 3, 1])
                with col_bar1: st.markdown(f"<span class='gold'>{nota_c:.1f}</span>", unsafe_allow_html=True)
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
                with col_bar3: st.markdown(f"<span class='silver'>{nota_f:.1f}</span>", unsafe_allow_html=True)
        else:
            st.info("Detalhamento OVRall indisponível.")

        st.markdown("### 🧠 IC – Índice de Contexto")
        col_ic1, col_ic2 = st.columns(2)
        winner_ic = nome_casa if res['ic_casa'] >= res['ic_fora'] else nome_fora
        with col_ic1:
            card_class = "card-winner" if nome_casa == winner_ic else "card-loser"
            st.markdown(f"<div class='{card_class}'><span class='big-number'>{res['ic_casa']:.1f}</span><br><small>{nome_casa}</small></div>", unsafe_allow_html=True)
            st.progress(res['ic_casa'] / 100)
        with col_ic2:
            card_class = "card-winner" if nome_fora == winner_ic else "card-loser"
            st.markdown(f"<div class='{card_class}'><span class='big-number'>{res['ic_fora']:.1f}</span><br><small>{nome_fora}</small></div>", unsafe_allow_html=True)
            st.progress(res['ic_fora'] / 100)
        with st.expander("🧠 Detalhamento do IC"):
            st.write("Fatores: confronto direto (manual), desempenho contra a prateleira do adversário (automático), fator casa/visitante (manual).")
            st.write(f"{nome_casa}: {res['ic_casa']:.1f} | {nome_fora}: {res['ic_fora']:.1f}")

        sup_casa = res.get('superacao_casa', 0)
        sup_fora = res.get('superacao_fora', 0)
        st.markdown(f"""
        <div style="text-align:center; margin:10px 0;">
            <span>🔺 Superação: </span>
            <span style="color:{'#00FF7F' if sup_casa >= 0 else '#FF4D4D'};">{nome_casa} {sup_casa:+.1f} pts</span> |
            <span style="color:{'#00FF7F' if sup_fora >= 0 else '#FF4D4D'};">{nome_fora} {sup_fora:+.1f} pts</span>
        </div>
        """, unsafe_allow_html=True)

    # ====================== ABA 2: CONTRASTE TÁTICO ======================
    with tabs[1]:
        st.markdown("## 🧪 Contraste Tático (MPV Dye)")
        if res.get('tactical'):
            tac = res['tactical']
            col_radar, col_mapa = st.columns([2, 1])
            with col_radar:
                st.markdown("### 📡 Radar Tático")
                radar_img = radar_chart(tac['dimensions_casa'], tac['dimensions_fora'])
                if radar_img:
                    st.image(f"data:image/png;base64,{radar_img}", use_container_width=True)
            with col_mapa:
                st.markdown("### 🗺️ Mapa de Calor")
                heat_img = field_heatmap_annotated(tac['dimensions_casa'], tac['dimensions_fora'], tac['deltas'])
                if heat_img:
                    st.image(f"data:image/png;base64,{heat_img}", use_container_width=True, caption="Azul: vantagem casa, Vermelho: vantagem fora")

            st.markdown("### ⚖️ Força Estrutural (OVRall) por Setor")
            if res.get('notas_casa') and res.get('notas_fora'):
                dims_ovr = ['Ataque', 'Defesa', 'MeioCampo', 'Consistencia', 'Resiliencia']
                notas_c = [res['notas_casa'].get(d, 0) for d in dims_ovr]
                notas_f = [res['notas_fora'].get(d, 0) for d in dims_ovr]
                df_ovr = pd.DataFrame({
                    'Setor': dims_ovr,
                    nome_casa: notas_c,
                    nome_fora: notas_f
                })
                df_long = df_ovr.melt('Setor', var_name='Time', value_name='Nota')
                chart = alt.Chart(df_long).mark_bar().encode(
                    x=alt.X('Setor:N', title=None),
                    y=alt.Y('Nota:Q', title='Nota (0-100)'),
                    color=alt.Color('Time:N', scale=alt.Scale(range=['#FFD700', '#00B4D8']), legend=alt.Legend(title=None)),
                    xOffset='Time:N'
                ).properties(width='container', height=300)
                st.altair_chart(chart, use_container_width=True)

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

            st.markdown("### 🎯 Rotas Críticas")
            for dim, delta, interp in tac.get('critical_routes', []):
                if delta > 0:
                    color = '#FFD700'; icon = '⚔️'; vant = f"Vantagem {nome_casa}"
                else:
                    color = '#FF4D4D'; icon = '🛡️'; vant = f"Vantagem {nome_fora}"
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid {color}; padding:10px; margin:10px 0; text-align:left;">
                    <span style="font-size:1.2rem;">{icon} {interp}</span><br>
                    <small style="color:#aaa;">{vant}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Dados táticos indisponíveis. Verifique o modelo calibrado.")

    # ====================== ABA 3: CENÁRIOS & ESTILOS (ATUALIZADA) ======================
    with tabs[2]:
        st.markdown("## 🔮 Cenários & Estilos de Jogo")
        if res.get('estilo_casa') and res.get('estilo_fora'):
            estilo_casa = res['estilo_casa']
            estilo_fora = res['estilo_fora']
            col_estilo1, col_estilo2 = st.columns(2)
            with col_estilo1:
                st.markdown(f"### 🏠 {nome_casa}")
                st.markdown(f"**Estilo:** {estilo_casa['estilo']}")
                st.markdown(f"- Posse Efetiva: {estilo_casa['posse_efetiva']:.2f} gols/%posse")
                st.markdown(f"- Eficiência de Finalização: {estilo_casa['eficiencia_finalizacao']:.2f}")
                st.markdown(f"- Vulnerabilidade em Transição: {estilo_casa['vulnerabilidade_transicao']:.2f}")
                st.markdown(f"- Dependência de Bola Parada: {estilo_casa['dependencia_bola_parada']:.2%}")
                # Confidence Score
                conf = res.get('confianca_casa', 50)
                st.markdown(f"**🔒 Confiança do Modelo:** {conf:.0f}/100")
                st.progress(conf / 100)
                # Curva de Momentum
                if res.get('curva_casa'):
                    st.markdown("**📈 Evolução do IMA (últimos recortes)**")
                    curva = res['curva_casa']
                    df_curva = pd.DataFrame({'Recorte': ['10J', '5J', '3J'], 'Pontuação': curva})
                    st.line_chart(df_curva.set_index('Recorte'), use_container_width=True)
            with col_estilo2:
                st.markdown(f"### 🏟️ {nome_fora}")
                st.markdown(f"**Estilo:** {estilo_fora['estilo']}")
                st.markdown(f"- Posse Efetiva: {estilo_fora['posse_efetiva']:.2f} gols/%posse")
                st.markdown(f"- Eficiência de Finalização: {estilo_fora['eficiencia_finalizacao']:.2f}")
                st.markdown(f"- Vulnerabilidade em Transição: {estilo_fora['vulnerabilidade_transicao']:.2f}")
                st.markdown(f"- Dependência de Bola Parada: {estilo_fora['dependencia_bola_parada']:.2%}")
                conf = res.get('confianca_fora', 50)
                st.markdown(f"**🔒 Confiança do Modelo:** {conf:.0f}/100")
                st.progress(conf / 100)
                if res.get('curva_fora'):
                    st.markdown("**📈 Evolução do IMA (últimos recortes)**")
                    curva = res['curva_fora']
                    df_curva = pd.DataFrame({'Recorte': ['10J', '5J', '3J'], 'Pontuação': curva})
                    st.line_chart(df_curva.set_index('Recorte'), use_container_width=True)

            st.markdown("---")
            st.markdown(res.get('cenario', 'Análise de cenário indisponível.'))
        else:
            st.info("Dados insuficientes para classificar os estilos de jogo.")

    # ====================== ABA 4: RESUMO & ANÁLISE ======================
    with tabs[3]:
        st.markdown(f"<h1 style='text-align:center;'>{nome_casa} vs {nome_fora}</h1>", unsafe_allow_html=True)
        mpv_casa, mpv_fora = res['mpv_casa'], res['mpv_fora']
        winner_mpv = nome_casa if mpv_casa >= mpv_fora else nome_fora
        col_mpv1, col_mpv2 = st.columns(2)
        with col_mpv1:
            card_class = "card-winner" if nome_casa == winner_mpv else "card-loser"
            st.markdown(f"<div class='{card_class}'><span class='big-number'>{mpv_casa:.1f}</span><br><small>{nome_casa}</small></div>", unsafe_allow_html=True)
        with col_mpv2:
            card_class = "card-winner" if nome_fora == winner_mpv else "card-loser"
            st.markdown(f"<div class='{card_class}'><span class='big-number'>{mpv_fora:.1f}</span><br><small>{nome_fora}</small></div>", unsafe_allow_html=True)

        st.markdown(gerar_analise_descritiva(res))

        if res.get('benchmarks'):
            st.markdown("### 📊 Comparativo com a Liga")
            bm = res['benchmarks']
            stats_casa = res.get('stats_casa', {})
            stats_fora = res.get('stats_fora', {})
            col_comp1, col_comp2 = st.columns(2)
            with col_comp1:
                st.write(f"**{nome_casa}**")
                st.write(f"Gols Marcados: {stats_casa.get('gols_media', 0):.1f} (Liga: {bm.get('gols_media', {}).get('mean', 0):.1f})")
                st.write(f"Gols Sofridos: {stats_casa.get('gols_sofridos_media', 0):.1f} (Liga: {bm.get('gols_sofridos_media', {}).get('mean', 0):.1f})")
                st.write(f"Posse: {stats_casa.get('posse_media', 0):.1f}% (Liga: {bm.get('posse_media', {}).get('mean', 50):.0f}%)")
            with col_comp2:
                st.write(f"**{nome_fora}**")
                st.write(f"Gols Marcados: {stats_fora.get('gols_media', 0):.1f} (Liga: {bm.get('gols_media', {}).get('mean', 0):.1f})")
                st.write(f"Gols Sofridos: {stats_fora.get('gols_sofridos_media', 0):.1f} (Liga: {bm.get('gols_sofridos_media', {}).get('mean', 0):.1f})")
                st.write(f"Posse: {stats_fora.get('posse_media', 0):.1f}% (Liga: {bm.get('posse_media', {}).get('mean', 50):.0f}%)")

    # ====================== ABA 5: MERCADOS ======================
    with tabs[4]:
        st.markdown("## 🎯 Probabilidades de Mercado")
        st.caption("Média entre modelo original e avançado")

        probs_1x2 = {'Casa': res['p1'], 'Empate': res['pX'], 'Fora': res['p2']}
        max_key = max(probs_1x2, key=probs_1x2.get)
        cols_1x2 = st.columns(3)
        edges = res.get('edges', {})
        for i, (key, prob) in enumerate(probs_1x2.items()):
            card_class = "card-winner" if key == max_key else "card-loser"
            emoji = {"Casa":"🏠", "Empate":"🤝", "Fora":"🏟️"}[key]
            edge_val = edges.get(f"edge_{key.lower()}", None)
            edge_html = ""
            if edge_val is not None:
                if edge_val > 0.05:
                    edge_html = f"<div class='selo-badge' style='background:#FFD700; color:#000;'>🟢 MyPredict Edge ({edge_val:+.1%})</div>"
                elif edge_val > 0:
                    edge_html = f"<div class='selo-badge' style='background:#00FF7F; color:#000;'>🟢 Value ({edge_val:+.1%})</div>"
                else:
                    edge_html = f"<div class='selo-badge' style='background:#aaa; color:#000;'>{edge_val:+.1%}</div>"
            with cols_1x2[i]:
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="font-size:1.2rem;">{emoji} {key}</div>
                    <div class="big-number">{prob:.1%}</div>
                    {edge_html}
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 🎲 Mercados Especiais")
        mercados = [
            ("Over 2.5 Gols", res['over25'], edges.get('edge_over')),
            ("Ambas Marcam", res['btts'], edges.get('edge_btts')),
            ("Gol 1º Tempo", res['gol_ht'], edges.get('edge_ht')),
            ("Over 8.5 Escanteios", res['esc'], edges.get('edge_esc')),
        ]
        cols_m = st.columns(4)
        max_prob = max([m[1] for m in mercados])
        for i, (nome, prob, edge_val) in enumerate(mercados):
            selo = ""
            if prob >= 0.70: selo = "🥇 GOLD"
            elif prob >= 0.60: selo = "✅ Value"
            elif prob >= 0.50: selo = "🔵 Favorito"
            bg = "#FFD700" if "GOLD" in selo else "#4CAF50" if "Value" in selo else "#2196F3" if "Favorito" in selo else "#555"
            edge_html = ""
            if edge_val is not None:
                if edge_val > 0.05:
                    edge_html = f"<div class='selo-badge' style='background:#FFD700; color:#000;'>🟢 MyPredict Edge ({edge_val:+.1%})</div>"
                elif edge_val > 0:
                    edge_html = f"<div class='selo-badge' style='background:#00FF7F; color:#000;'>🟢 Value ({edge_val:+.1%})</div>"
            card_class = "card-winner" if prob == max_prob else "card-loser"
            with cols_m[i]:
                st.markdown(f"""
                <div class="{card_class}">
                    <div style="font-size:0.9rem;">{nome}</div>
                    <div class="big-number">{prob:.1%}</div>
                    <div class="selo-badge" style="background:{bg}; color:#000;">{selo if selo else '⚪'}</div>
                    {edge_html}
                </div>
                """, unsafe_allow_html=True)
