# ui/components.py — Componentes reutilizáveis da interface
import streamlit as st
from config import THRESHOLD_GOLD, THRESHOLD_VALUE, THRESHOLD_FAVORITO

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

def show_results_manual(res):
    st.markdown(f"""
    <div style="text-align:center; margin:20px 0;">
        <span style="font-size:2rem; font-weight:900; color:#ffd700;">{res['time_casa']}</span>
        <span style="font-size:1.5rem; color:#888; margin:0 12px;">vs</span>
        <span style="font-size:2rem; font-weight:900; color:#c0c0c0;">{res['time_fora']}</span>
    </div>
    """, unsafe_allow_html=True)

    # Indicadores de superação
    st.caption(f"🔺 {res['time_casa']}: {res.get('prat_proj_casa','?')} → {res.get('prat_real_casa','?')} ({res.get('superacao_casa', 0):+.1f} pts) | 🔺 {res['time_fora']}: {res.get('prat_proj_fora','?')} → {res.get('prat_real_fora','?')} ({res.get('superacao_fora', 0):+.1f} pts)")

    # MPV Hero
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
        <span>{res['time_casa']} {res['mpv_casa']:.1f}</span>
        <span>{res['time_fora']} {res['mpv_fora']:.1f}</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Composição
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

    # Detalhamento por etapa
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
