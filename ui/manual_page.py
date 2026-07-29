# ui/manual_page.py — Tela do modo manual (entrada de dados e resultados)
import streamlit as st
from ui.styles import injetar_css
from ui.components import show_results_manual
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from utils import extrair_jogos, para_float
from core.calculations import executar_manual

# Constantes para exibição
PESOS_RECORTES_EX = {'10G': 0.10, '5G': 0.15, '3G': 0.20, '5CF': 0.25, '3CF': 0.30}
PESOS_OVRALL_EX = {'Ataque': 0.25, 'Defesa': 0.25, 'MeioCampo': 0.20, 'Consistencia': 0.15, 'Resiliencia': 0.15}
PESOS_IC_EX = {'confronto_direto': 0.25, 'mesmo_escalao': 0.20, 'contra_escalao_adversario': 0.20, 'fator_casa': 0.20, 'odds': 0.15}

def render_manual():
    injetar_css()
    st.markdown('<div class="main-title">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">ANÁLISE PREDITIVA PREMIUM</div>', unsafe_allow_html=True)

    # Inicializar sessão
    for chave, padrao in {
        'time_casa':'','time_fora':'','pos_casa':1,'pos_fora':2,
        'jogos_casa':[],'jogos_fora':[],'ovrall_casa':{},'ovrall_fora':{},
        'ic_casa':{},'ic_fora':{},'media_gols_casa':MEDIA_GOLS_CASA_LIGA,
        'media_gols_fora':MEDIA_GOLS_FORA_LIGA,'media_ht_casa':0.75,'media_ht_fora':0.65,
        'media_esc_casa':5.0,'media_esc_fora':4.5,'prateleiras_extra':{}
    }.items():
        if chave not in st.session_state:
            st.session_state[chave] = padrao

    # --- Times ---
    st.markdown('<div class="section-title">⚔️ TIMES</div>', unsafe_allow_html=True)
    col_casa, col_fora = st.columns(2)
    with col_casa:
        st.markdown('<div class="team-block home"><div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        st.text_input("Nome do time", key="time_casa_input", value=st.session_state.time_casa, placeholder="Time da casa")
        st.number_input("Posição", 1, 20, key="pos_casa_input", value=st.session_state.pos_casa)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora:
        st.markdown('<div class="team-block away"><div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        st.text_input("Nome do time", key="time_fora_input", value=st.session_state.time_fora, placeholder="Time de fora")
        st.number_input("Posição", 1, 20, key="pos_fora_input", value=st.session_state.pos_fora)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- IMA (entrada por texto ou manual) ---
    st.markdown('<div class="section-title">📊 IMA · ÚLTIMOS 10 JOGOS</div>', unsafe_allow_html=True)
    st.markdown("**Opção rápida:** cole os jogos no formato `V Flamengo S` (resultado, adversário, mandante S/N)")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🏠 Casa")
        texto_casa = st.text_area("Colar jogos da casa", height=120, key="texto_casa", placeholder="V Palmeiras S\nE São Paulo N\n...")
        if st.button("Processar Casa"):
            st.session_state.jogos_casa = extrair_jogos(texto_casa)
            st.success(f"{len(st.session_state.jogos_casa)} jogos processados.")
    with col2:
        st.markdown("#### 🏟️ Fora")
        texto_fora = st.text_area("Colar jogos do fora", height=120, key="texto_fora", placeholder="D Flamengo N\nV Corinthians S\n...")
        if st.button("Processar Fora"):
            st.session_state.jogos_fora = extrair_jogos(texto_fora)
            st.success(f"{len(st.session_state.jogos_fora)} jogos processados.")

    # Caso queira editar manualmente, mostra uma tabela (simplificada)
    if st.checkbox("Editar jogos manualmente (avançado)"):
        st.caption("Preencha os últimos 10 jogos abaixo (deixe em branco se não quiser usar).")
        colA, colB = st.columns(2)
        with colA:
            for i in range(10):
                j = st.session_state.jogos_casa[i] if i < len(st.session_state.jogos_casa) else {}
                c1, c2, c3 = st.columns([0.5, 2, 0.7])
                res = c1.selectbox("", ["", "V", "E", "D"], key=f"man_casa_res_{i}", index=(["", "V", "E", "D"].index(j.get('resultado', '')) if j.get('resultado') in ["V","E","D"] else 0), label_visibility="collapsed")
                adv = c2.text_input("", value=j.get('adversario',''), key=f"man_casa_adv_{i}", label_visibility="collapsed")
                mand = c3.checkbox("Mandante", value=j.get('mandante', False), key=f"man_casa_mand_{i}")
                if res and adv:
                    if i >= len(st.session_state.jogos_casa):
                        st.session_state.jogos_casa.append({"resultado": res, "adversario": adv, "mandante": mand})
                    else:
                        st.session_state.jogos_casa[i] = {"resultado": res, "adversario": adv, "mandante": mand}
        with colB:
            for i in range(10):
                j = st.session_state.jogos_fora[i] if i < len(st.session_state.jogos_fora) else {}
                c1, c2, c3 = st.columns([0.5, 2, 0.7])
                res = c1.selectbox("", ["", "V", "E", "D"], key=f"man_fora_res_{i}", index=(["", "V", "E", "D"].index(j.get('resultado', '')) if j.get('resultado') in ["V","E","D"] else 0), label_visibility="collapsed")
                adv = c2.text_input("", value=j.get('adversario',''), key=f"man_fora_adv_{i}", label_visibility="collapsed")
                mand = c3.checkbox("Mandante", value=j.get('mandante', False), key=f"man_fora_mand_{i}")
                if res and adv:
                    if i >= len(st.session_state.jogos_fora):
                        st.session_state.jogos_fora.append({"resultado": res, "adversario": adv, "mandante": mand})
                    else:
                        st.session_state.jogos_fora[i] = {"resultado": res, "adversario": adv, "mandante": mand}

    # --- OVRall ---
    st.markdown('<div class="section-title">📈 OVRALL · MÉTRICAS DA TEMPORADA</div>', unsafe_allow_html=True)
    st.caption("Preencha as métricas. Deixe em branco se não disponível.")
    dimensoes = {
        "⚔️ ATAQUE": [("Gols marcados (média)","gols_media"),("xG (média)","xg_media"),
                      ("Finalizações no alvo (média)","finalizacoes_alvo_media"),("Conversão (%)","conversao")],
        "🛡️ DEFESA": [("Gols sofridos (média)","gols_sofridos_media"),("xGA (média)","xga_media"),
                       ("Finalizações no alvo sofridas (média)","finalizacoes_alvo_sofridas_media"),
                       ("Desarmes + Interceptações (média)","desarmes_intercep_media")],
        "🧩 MEIO-CAMPO": [("Posse de bola (%)","posse_media"),("Passes certos (%)","passes_certos_pct"),
                         ("Passes-chave (média)","passes_chave_media"),("Assistências (média)","assistencias_media"),
                         ("Chutes totais (média)","chutes_media")],
        "📏 CONSISTÊNCIA": [("Desvio padrão pontos","desvio_pontos"),("Desvio padrão gols pró","desvio_gols_pro"),
                           ("Desvio padrão gols sofridos","desvio_gols_sofridos"),
                           ("Jogos sem sofrer gols (%)","clean_sheets_pct")],
        "🔄 RESILIÊNCIA": [("Pontos após sair atrás","pontos_pos_desvantagem_media"),
                          ("Gols nos últimos 15 min","gols_ultimos_15min_media"),
                          ("Pontos após derrota","pontos_apos_derrota_media"),
                          ("Dif. aprovação casa-fora (%)","diff_aprov_casa_fora"),
                          ("Viradas a favor (%)","aprov_viradas_favor"),
                          ("Viradas contra (%)","aprov_viradas_contra")],
        "⚡ MERCADOS (1ºT / ESCANTEIOS)": [("Gols 1º tempo (média)","gols_ht_media"),
                                          ("Gols sofridos 1º tempo (média)","gols_ht_sofridos_media"),
                                          ("Escanteios (média)","escanteios_media"),
                                          ("Escanteios sofridos (média)","escanteios_sofridos_media")]
    }
    col_casa_ovr, col_fora_ovr = st.columns(2)
    with col_casa_ovr:
        st.markdown('<div class="team-block home"><div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        for nome_dim, indicadores in dimensoes.items():
            st.markdown(f'<div class="dimension-title">{nome_dim}</div>', unsafe_allow_html=True)
            for label, key in indicadores:
                val = st.text_input(label, key=f"casa_ovr_{key}", placeholder=label, label_visibility="visible")
                st.session_state.ovrall_casa[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora_ovr:
        st.markdown('<div class="team-block away"><div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        for nome_dim, indicadores in dimensoes.items():
            st.markdown(f'<div class="dimension-title">{nome_dim}</div>', unsafe_allow_html=True)
            for label, key in indicadores:
                val = st.text_input(label, key=f"fora_ovr_{key}", placeholder=label, label_visibility="visible")
                st.session_state.ovrall_fora[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)

    # --- IC ---
    st.markdown('<div class="section-title">🧠 IC · ÍNDICE DE CONTEXTO</div>', unsafe_allow_html=True)
    metricas_ic = [
        ("Confronto direto (%)","confronto_direto"),
        ("Mesmo escalão (%)","mesmo_escalao"),
        ("Contra escalão adversário (%)","contra_escalao_adversario"),
        ("Fator casa (%)","fator_casa"),
        ("Odds (decimal)","odds"),
    ]
    col_casa_ic, col_fora_ic = st.columns(2)
    with col_casa_ic:
        st.markdown('<div class="team-block home"><div class="team-title home-title">🏠 CASA</div>', unsafe_allow_html=True)
        for label, key in metricas_ic:
            val = st.text_input(label, key=f"ic_casa_{key}", placeholder=label, label_visibility="visible")
            st.session_state.ic_casa[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)
    with col_fora_ic:
        st.markdown('<div class="team-block away"><div class="team-title away-title">🏟️ FORA</div>', unsafe_allow_html=True)
        for label, key in metricas_ic:
            val = st.text_input(label, key=f"ic_fora_{key}", placeholder=label, label_visibility="visible")
            st.session_state.ic_fora[key] = para_float(val) if val else None
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Médias da Liga ---
    st.markdown('<div class="section-title">📊 MÉDIAS DA LIGA</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        mgc = st.number_input("Média gols casa", value=MEDIA_GOLS_CASA_LIGA, key="mgc")
        mhtc = st.number_input("Média gols HT casa", value=0.75, key="mhtc")
        mecc = st.number_input("Média escanteios casa", value=5.0, key="mecc")
    with c2:
        mgf = st.number_input("Média gols fora", value=MEDIA_GOLS_FORA_LIGA, key="mgf")
        mhtf = st.number_input("Média gols HT fora", value=0.65, key="mhtf")
        mecf = st.number_input("Média escanteios fora", value=4.5, key="mecf")

    # --- Gerar ---
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    if st.button("🔥 GERAR MYPREDICT VALUE", use_container_width=True):
        st.session_state.time_casa = st.session_state.time_casa_input
        st.session_state.time_fora = st.session_state.time_fora_input
        st.session_state.pos_casa = st.session_state.pos_casa_input
        st.session_state.pos_fora = st.session_state.pos_fora_input
        st.session_state.media_gols_casa = mgc; st.session_state.media_gols_fora = mgf
        st.session_state.media_ht_casa = mhtc; st.session_state.media_ht_fora = mhtf
        st.session_state.media_esc_casa = mecc; st.session_state.media_esc_fora = mecf

        dados = {k:v for k,v in st.session_state.items() if k in [
            'time_casa','time_fora','pos_casa','pos_fora','jogos_casa','jogos_fora',
            'ovrall_casa','ovrall_fora','ic_casa','ic_fora','media_gols_casa','media_gols_fora',
            'media_ht_casa','media_ht_fora','media_esc_casa','media_esc_fora','prateleiras_extra']}
        res, err = executar_manual(dados)
        if err:
            st.error(err)
        else:
            st.session_state.resultados = res
            st.rerun()

    # Exibir resultados
    if 'resultados' in st.session_state:
        show_results_manual(st.session_state.resultados)
