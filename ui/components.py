# ui/components.py — Componentes reutilizáveis com Radar, MPV 10.0 e Auto-Insight
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')          # backend não interativo (obrigatório no Streamlit Cloud)
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from config import THRESHOLD_GOLD, THRESHOLD_VALUE, THRESHOLD_FAVORITO, MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

# ------------------------------------------------------------
# Funções auxiliares já existentes (mantidas)
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
# Radar Chart (corrigido)
# ------------------------------------------------------------
def radar_chart(casa_scores, fora_scores):
    """Retorna imagem base64 de um radar comparando dois times, ou None se não for possível."""
    # Obter dimensões comuns
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
# Mapa de calor do campo (funcional)
# ------------------------------------------------------------
def field_heatmap(deltas):
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 68)
    ax.set_facecolor('#1a472a')
    
    # Linhas do campo
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

# ------------------------------------------------------------
# Auto-Insight: análise tática gerada automaticamente
# ------------------------------------------------------------
def generate_auto_insight(res):
    """Gera um texto tático com sugestões de mercados baseado nas rotas críticas e MPV."""
    nome_casa = res['time_casa']
    nome_fora = res['time_fora']
    tactical = res.get('tactical')
    
    if not tactical or not tactical.get('critical_routes'):
        return "Análise tática indisponível por falta de dados suficientes."
    
    routes = tactical['critical_routes']
    # Vamos construir frases para as 3 principais rotas
    insights = []
    for dim, delta, interpretation in routes:
        if dim == 'ataque_posicional':
            if delta > 10:
                insights.append(f"- O ataque posicional do **{nome_casa}** é muito superior (+{delta:.1f}). Isso favorece **Over 2.5 Gols** e **Gol do {nome_casa}**.")
            elif delta < -10:
                insights.append(f"- O **{nome_fora}** domina o ataque posicional ({delta:.1f}). A defesa do {nome_casa} terá trabalho, aumentando a chance de **BTTS**.")
        elif dim == 'defesa_organizada':
            if delta > 10:
                insights.append(f"- A defesa sólida do **{nome_casa}** (+{delta:.1f}) tende a anular o ataque adversário. Isso reduz a probabilidade de **Over 2.5** e favorece **Ambas Não Marcam**.")
            elif delta < -10:
                insights.append(f"- A defesa do **{nome_fora}** é mais consistente ({delta:.1f}), dificultando os ataques do {nome_casa}. Jogo pode ter menos gols (**Under 2.5**).")
        elif dim == 'bola_parada_ofensiva':
            if delta > 10:
                insights.append(f"- **{nome_casa}** leva grande vantagem em bolas paradas (+{delta:.1f}). Considere o mercado de **Escanteios** e **Gol de Cabeça** (se disponível).")
            elif delta < -10:
                insights.append(f"- **{nome_fora}** é perigoso em bolas paradas ({delta:.1f}), podendo surpreender. Atenção para **Over Escanteios** e **Gol Fora** em lances de bola parada.")
        elif dim == 'pressao_alta':
            if delta > 10:
                insights.append(f"- A pressão alta do **{nome_casa}** (+{delta:.1f}) deve forçar erros do adversário. Chance de **Gol no 1º Tempo** e **Over 2.5**.")
            elif delta < -10:
                insights.append(f"- O **{nome_fora}** pressiona mais ({delta:.1f}), podendo criar chances cedo. Fique de olho em **Gol no 1º Tempo** para o visitante.")
        else:
            # Para outras dimensões, uma frase genérica
            if delta > 10:
                insights.append(f"- Vantagem significativa para **{nome_casa}** em {dim} (+{delta:.1f}). Explore mercados relacionados a essa característica.")
            elif delta < -10:
                insights.append(f"- Vantagem para **{nome_fora}** em {dim} ({delta:.1f}). Isso pode influenciar o resultado final e mercados como **1X2**.")
    
    if not insights:
        return "Nenhuma rota crítica com desequilíbrio suficiente para sugerir mercados específicos."
    
    # Adiciona uma conclusão baseada no MPV Score
    mpv_score = res.get('mpv_score', 5.0)
    if mpv_score >= 7.5:
        conclusao = f"🏆 Com MP Value {mpv_score:.1f}, o **{nome_casa}** é amplamente favorito. Considere apostas em vitória da casa e mercados de gols a favor."
    elif mpv_score <= 2.5:
        conclusao = f"🔻 O **{nome_fora}** é o grande favorito (MP Value {mpv_score:.1f} para o {nome_casa}). Vitória do visitante e under podem ser boas opções."
    else:
        conclusao = f"⚖️ Confronto equilibrado (MP Value {mpv_score:.1f}). Foco nos mercados de nicho (escanteios, gols no 1º tempo) baseados nas dimensões acima."
    
    return "### 🧠 Análise Tática Automática\n" + "\n".join(insights) + "\n\n" + conclusao

# ------------------------------------------------------------
# Função principal de exibição (com todas as novidades)
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
    # MP VALUE 10.0
    # ================================================================
    # Calcula nota de 0 a 10 baseada no MPV tático, deltas e superação
    try:
        mpv_tactical_casa = res.get('mpv_tactical_casa', 50)
        mpv_tactical_fora = res.get('mpv_tactical_fora', 50)
        # Média dos deltas normalizados (0 a 100)
        if 'tactical' in res and res['tactical'] is not None:
            deltas = list(res['tactical']['deltas'].values())
            delta_medio = np.mean([abs(d) for d in deltas]) if deltas else 0
        else:
            delta_medio = 0
        # Superação (já está entre -10 e 10)
        superacao_casa = res.get('superacao_casa', 0)
        # Fórmula MPV Score 10.0
        raw = (mpv_tactical_casa / 100) * 7 + (delta_medio / 30) * 2 + (superacao_casa / 10) * 1
        mpv_score = max(0, min(10, raw))
        mpv_score = round(mpv_score, 1)
    except:
        mpv_score = 5.0  # fallback
    
    res['mpv_score'] = mpv_score   # guarda para o insight
    
    # Exibir card do MP Value 10.0
    score_color = "#FFD700" if mpv_score >= 7 else ("#00B4D8" if mpv_score >= 4 else "#FF4D4D")
    st.markdown(f"""
    <div style="background:linear-gradient(145deg, #1a1e2b 0%, #121621 100%); border:2px solid {score_color}; 
                border-radius:20px; padding:20px; text-align:center; margin:20px 0;">
        <div style="font-size:1.2rem; color:#aaa;">MYPREDICT VALUE 10.0</div>
        <div style="font-size:4rem; font-weight:900; color:{score_color};">{mpv_score}</div>
        <div style="color:#aaa;">Força do {nome_casa} no confronto (escala 0–10)</div>
    </div>
    """, unsafe_allow_html=True)

    # ================================================================
    # SEÇÃO DO CONTRASTE TÁTICO (MPV Dye) – Radar, Mapa, Rotas
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
            st.markdown("### 🗺️ Mapa de Calor")
            try:
                heat = field_heatmap(tactical['deltas'])
                st.image(f"data:image/png;base64,{heat}", use_container_width=True,
                         caption="Azul = Vantagem Casa, Vermelho = Vantagem Fora")
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

        # Auto-Insight (gerado automaticamente)
        insight_text = generate_auto_insight(res)
        st.markdown(insight_text)

    # ================================================================
    # RESTO DO RELATÓRIO (mantido igual ao seu código original)
    # ================================================================
    # (Cabeçalho do confronto, MPV Hero, Composição, Probabilidades, etc.)
    # (Mantenha exatamente o que já existia, não vou repetir aqui para não alongar)
    # ...
