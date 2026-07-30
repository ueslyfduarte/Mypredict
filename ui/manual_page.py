# ui/manual_page.py — Visual EA Sports, Liga rica e Análise Direta
import streamlit as st
import pandas as pd
import os
import pickle
import random
from ui.styles import injetar_css
from ui.components import show_results_manual
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from core.calculations import executar_manual
from core.ratings import obter_prateleira

# ============================================================
# FRASES INSPIRADORAS
# ============================================================
FRASES_CABECALHO = [
    "Futebol é a arte do imprevisível. Mas o imprevisível também tem padrões.",
    "Tática é saber o que fazer quando não se tem a bola. Estratégia é saber o que fazer com ela. – Johan Cruyff",
    "O futebol não é uma ciência exata, mas a análise pode revelar os caminhos que os olhos não veem.",
]

FRASES_RESULTADOS = [
    "Os números nunca ganham jogos, mas mostram onde as batalhas serão vencidas.",
    "Em cada passe, em cada desarme, existe uma rota. Nós só a colorimos.",
    "Prever não é adivinhar. É reconhecer padrões que o tempo ainda não revelou.",
    "A análise não substitui a paixão, mas a direciona.",
    "Quem conhece o caminho, chega mais rápido.",
]

# ============================================================
# CSS PERSONALIZADO (EA SPORTS DOURADO)
# ============================================================
def injetar_css_personalizado():
    st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #EAEAEA;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        h1, h2, h3 {
            color: #FFD700 !important;
        }
        .team-card {
            background: linear-gradient(145deg, #1a1e2b 0%, #121621 100%);
            border: 2px solid #FFD700;
            border-radius: 20px;
            padding: 25px 20px;
            text-align: center;
            margin: 15px 0;
            box-shadow: 0 8px 20px rgba(255, 215, 0, 0.2);
        }
        .team-card h3 {
            font-size: 2.2rem;
            font-weight: 900;
            color: #FFD700;
            margin: 10px 0 5px 0;
        }
        .team-card .badge {
            font-size: 4rem;
            margin-bottom: 5px;
        }
        .team-card .position {
            font-size: 1rem;
            color: #aaa;
            margin-bottom: 15px;
        }
        .attr-bar {
            background: #2d3242;
            border-radius: 10px;
            height: 8px;
            width: 100%;
            margin: 5px 0 10px 0;
        }
        .attr-fill {
            background: linear-gradient(90deg, #FFD700, #FFA500);
            height: 8px;
            border-radius: 10px;
        }
        .golden-select {
            border: 1px solid #FFD700;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 215, 0, 0.05);
        }
        .stButton > button {
            background: linear-gradient(90deg, #FFD700, #FFA500) !important;
            color: #000 !important;
            font-weight: bold;
            border: none;
            border-radius: 12px;
            transition: 0.3s;
        }
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 15px #FFD700;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1a1e2b;
            color: #FFD700;
            border-radius: 12px 12px 0 0;
            padding: 10px 25px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFD700 !important;
            color: #0E1117 !important;
            font-weight: bold;
        }
        .streamlit-expanderHeader {
            border: 1px solid #FFD700;
            border-radius: 10px;
        }
        .league-metric {
            background: rgba(255,215,0,0.1);
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            margin: 5px;
        }
        .league-metric h4 {
            color: #FFD700;
            margin: 0;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# MAPA DE LIGAS → ARQUIVO .PKL
# ============================================================
LIGAS_DISPONIVEIS = {
    "Premier League": "calibration_params.pkl",
    "La Liga": "calibration_laliga.pkl",
    "Brasileirão": "calibration_brasileirao.pkl",
}

# ============================================================
# INTERFACE PRINCIPAL
# ============================================================
def render_manual():
    injetar_css_personalizado()
    
    # Cabeçalho
    frase = random.choice(FRASES_CABECALHO)
    st.markdown(f"""
    <div style="text-align:center; padding: 30px 0 20px 0;">
        <h1 style="font-size:3rem; margin:0; letter-spacing:3px;">⚽ MYPREDICT 2.0</h1>
        <p style="color:#FFD700; font-style:italic; font-size:1.2rem; margin-top:5px;">"{frase}"</p>
        <p style="color:#999; margin-top:10px;">🟣 Análise Tática • Contraste Inteligente • Previsão de Mercados</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_liga, tab_analise = st.tabs(["🏆 Liga", "🔍 Analisar"])
    
    # ================================================================
    # ABA LIGA: Painel de informações da liga + ajustes manuais
    # ================================================================
    with tab_liga:
        st.subheader("Selecione o campeonato")
        col1, col2 = st.columns([3, 1])
        with col1:
            liga_nome = st.selectbox("Liga Ativa", list(LIGAS_DISPONIVEIS.keys()),
                                     help="Escolha a liga para carregar o modelo calibrado.")
        with col2:
            st.write("")
            st.write("")
            if st.button("🎮 Carregar Liga", use_container_width=True):
                pkl_file = LIGAS_DISPONIVEIS[liga_nome]
                if os.path.exists(pkl_file):
                    with open(pkl_file, 'rb') as f:
                        calib = pickle.load(f)
                    st.session_state.liga_ativa = liga_nome
                    st.session_state.pkl_path = pkl_file
                    st.session_state.benchmarks = calib['benchmarks']
                    st.success(f"Liga '{liga_nome}' carregada! Benchmarks da liga disponíveis.")
                else:
                    st.warning(f"Arquivo '{pkl_file}' não encontrado. Usando modelo padrão.")
                    st.session_state.liga_ativa = liga_nome
                    st.session_state.pkl_path = 'calibration_params.pkl'
        
        if 'benchmarks' in st.session_state:
            benchmarks = st.session_state.benchmarks
            
            # Cards com as principais métricas
            st.markdown("### 📊 Métricas de Referência da Liga")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.markdown('<div class="league-metric"><h4>⚽ Gols Marcados</h4><p style="font-size:1.5rem;">{:.2f}</p></div>'.format(benchmarks['gols_media']['mean']), unsafe_allow_html=True)
            with col_m2:
                st.markdown('<div class="league-metric"><h4>🛡️ Gols Sofridos</h4><p style="font-size:1.5rem;">{:.2f}</p></div>'.format(benchmarks['gols_sofridos_media']['mean']), unsafe_allow_html=True)
            with col_m3:
                st.markdown('<div class="league-metric"><h4>📊 Posse (%)</h4><p style="font-size:1.5rem;">{:.0f}</p></div>'.format(benchmarks['posse_media']['mean']), unsafe_allow_html=True)
            with col_m4:
                st.markdown('<div class="league-metric"><h4>🎯 Finalizações Alvo</h4><p style="font-size:1.5rem;">{:.1f}</p></div>'.format(benchmarks['chutes_alvo_media']['mean']), unsafe_allow_html=True)
            
            col_m5, col_m6, col_m7, col_m8 = st.columns(4)
            with col_m5:
                st.markdown('<div class="league-metric"><h4>📈 xG</h4><p style="font-size:1.5rem;">{:.2f}</p></div>'.format(benchmarks.get('xg_media', {'mean':1.2})['mean']), unsafe_allow_html=True)
            with col_m6:
                st.markdown('<div class="league-metric"><h4>🏁 Escanteios</h4><p style="font-size:1.5rem;">{:.1f}</p></div>'.format(benchmarks['escanteios_media']['mean']), unsafe_allow_html=True)
            with col_m7:
                st.markdown('<div class="league-metric"><h4>⚡ Conversão</h4><p style="font-size:1.5rem;">{:.1%}</p></div>'.format(benchmarks['conversao']['mean']), unsafe_allow_html=True)
            with col_m8:
                # Mostrar característica da liga baseada na média de gols
                media_gols = benchmarks['gols_media']['mean']
                if media_gols > 1.5:
                    estilo = "🔥 Ofensiva"
                elif media_gols < 1.2:
                    estilo = "🔒 Defensiva"
                else:
                    estilo = "⚖️ Equilibrada"
                st.markdown(f'<div class="league-metric"><h4>Estilo</h4><p style="font-size:1.5rem;">{estilo}</p></div>', unsafe_allow_html=True)
            
            # Opção de ajustes manuais (apenas médias de gols, se quiser personalizar)
            with st.expander("⚙️ Ajustes Manuais (opcional)"):
                st.caption("Aqui você pode substituir as médias de gols da liga para este cálculo específico. Deixe em branco para usar os padrões do modelo.")
                col_adj1, col_adj2 = st.columns(2)
                with col_adj1:
                    custom_casa = st.number_input("Média Gols Casa (liga)", 0.0, 5.0, value=benchmarks['gols_media']['mean'], key="cust_casa")
                with col_adj2:
                    custom_fora = st.number_input("Média Gols Fora (liga)", 0.0, 5.0, value=benchmarks['gols_sofridos_media']['mean'], key="cust_fora")
                st.session_state.custom_gols_casa = custom_casa
                st.session_state.custom_gols_fora = custom_fora
        else:
            st.info("Selecione uma liga e clique em 'Carregar Liga' para visualizar os benchmarks.")
    
    # ================================================================
    # ABA ANALISAR: formulário direto (mantido igual ao último código)
    # ================================================================
    with tab_analise:
        st.subheader("🎮 Analisar Confronto Direto")
        st.caption("Preencha os dados dos dois times para gerar a análise completa.")
        
        col_casa, col_fora = st.columns(2)
        
        with col_casa:
            st.markdown('<div class="golden-select">', unsafe_allow_html=True)
            st.markdown("### 🏠 Time Casa")
            nome_casa = st.text_input("Nome do Time", value="Arsenal", key="nc_casa")
            pos_casa = st.number_input("Posição na tabela", 1, 20, 1, key="pos_casa")
            prat_casa = st.selectbox("Prateleira Projetada", ["Elite", "Alta", "Media", "Baixa", "Critica"], key="prat_casa")
            
            st.markdown("**Estatísticas (médias por jogo)**")
            gols_media_casa = st.number_input("⚽ Gols Marcados", 0.0, 5.0, 1.8, 0.1, key="gols_casa")
            gols_sofridos_casa = st.number_input("🛡️ Gols Sofridos", 0.0, 5.0, 0.9, 0.1, key="gols_s_casa")
            posse_casa = st.number_input("📊 Posse (%)", 0, 100, 55, key="posse_casa")
            finalizacoes_casa = st.number_input("🎯 Finalizações Alvo", 0.0, 15.0, 5.2, 0.5, key="fin_casa")
            xg_casa = st.number_input("📈 xG", 0.0, 4.0, 1.6, 0.1, key="xg_casa")
            escanteios_casa = st.number_input("🏁 Escanteios", 0.0, 15.0, 5.5, 0.5, key="esc_casa")
            
            st.markdown("**Últimos 5 Jogos**")
            jogos_casa = []
            for i in range(10):
                c = st.columns([2, 3, 3, 1, 1])
                res = c[0].selectbox("Res.", ['V', 'E', 'D'], key=f"c_res_{i}")
                adv = c[1].text_input("Adversário", key=f"c_adv_{i}")
                prat_adv = c[2].selectbox("Prat. Real Adv.", ["Elite", "Alta", "Media", "Baixa", "Critica"], key=f"c_prat_{i}")
                gp = c[3].number_input("GP", 0, 10, 0, key=f"c_gp_{i}")
                gc = c[4].number_input("GC", 0, 10, 0, key=f"c_gc_{i}")
                jogos_casa.append({
                    'resultado': res, 'adversario': adv, 'prateleira_adv': prat_adv,
                    'gols_pro': gp, 'gols_contra': gc, 'mandante': True
                })
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_fora:
            st.markdown('<div class="golden-select">', unsafe_allow_html=True)
            st.markdown("### 🏟️ Time Fora")
            nome_fora = st.text_input("Nome do Time", value="Chelsea", key="nc_fora")
            pos_fora = st.number_input("Posição na tabela", 1, 20, 5, key="pos_fora")
            prat_fora = st.selectbox("Prateleira Projetada", ["Elite", "Alta", "Media", "Baixa", "Critica"], key="prat_fora")
            
            st.markdown("**Estatísticas (médias por jogo)**")
            gols_media_fora = st.number_input("⚽ Gols Marcados", 0.0, 5.0, 1.4, 0.1, key="gols_fora")
            gols_sofridos_fora = st.number_input("🛡️ Gols Sofridos", 0.0, 5.0, 1.1, 0.1, key="gols_s_fora")
            posse_fora = st.number_input("📊 Posse (%)", 0, 100, 48, key="posse_fora")
            finalizacoes_fora = st.number_input("🎯 Finalizações Alvo", 0.0, 15.0, 4.5, 0.5, key="fin_fora")
            xg_fora = st.number_input("📈 xG", 0.0, 4.0, 1.3, 0.1, key="xg_fora")
            escanteios_fora = st.number_input("🏁 Escanteios", 0.0, 15.0, 4.8, 0.5, key="esc_fora")
            
            st.markdown("**Últimos 5 Jogos**")
            jogos_fora = []
            for i in range(10):
                c = st.columns([2, 3, 3, 1, 1])
                res = c[0].selectbox("Res.", ['V', 'E', 'D'], key=f"f_res_{i}")
                adv = c[1].text_input("Adversário", key=f"f_adv_{i}")
                prat_adv = c[2].selectbox("Prat. Real Adv.", ["Elite", "Alta", "Media", "Baixa", "Critica"], key=f"f_prat_{i}")
                gp = c[3].number_input("GP", 0, 10, 0, key=f"f_gp_{i}")
                gc = c[4].number_input("GC", 0, 10, 0, key=f"f_gc_{i}")
                jogos_fora.append({
                    'resultado': res, 'adversario': adv, 'prateleira_adv': prat_adv,
                    'gols_pro': gp, 'gols_contra': gc, 'mandante': False
                })
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Contexto (IC)
        with st.expander("🧠 Ajustes de Contexto (opcional)"):
            col_ic1, col_ic2 = st.columns(2)
            with col_ic1:
                st.markdown(f"**{nome_casa}**")
                ic_casa = {}
                ic_casa['confronto_direto'] = st.slider(f"Aproveitamento contra {nome_fora} (%)", 0, 100, 50) / 100
                ic_casa['fator_casa'] = st.slider("Aproveitamento como mandante (%)", 0, 100, 60) / 100
            with col_ic2:
                st.markdown(f"**{nome_fora}**")
                ic_fora = {}
                ic_fora['confronto_direto'] = 1.0 - ic_casa['confronto_direto']
                ic_fora['fator_casa'] = st.slider("Aproveitamento como visitante (%)", 0, 100, 40) / 100
        
        if st.button("⚡ CALCULAR ANÁLISE COMPLETA", use_container_width=True, type="primary"):
            # Usar médias personalizadas se definidas, senão as do benchmark
            if 'custom_gols_casa' in st.session_state:
                media_gols_casa = st.session_state.custom_gols_casa
                media_gols_fora = st.session_state.custom_gols_fora
            else:
                media_gols_casa = MEDIA_GOLS_CASA_LIGA
                media_gols_fora = MEDIA_GOLS_FORA_LIGA
            
            dados = {
                'time_casa': nome_casa, 'time_fora': nome_fora,
                'pos_casa': pos_casa, 'pos_fora': pos_fora,
                'prat_casa': prat_casa, 'prat_fora': prat_fora,
                'ovrall_casa': {
                    'gols_media': gols_media_casa, 'gols_sofridos_media': gols_sofridos_casa,
                    'posse_media': posse_casa, 'finalizacoes_alvo_media': finalizacoes_casa,
                    'xg_media': xg_casa, 'escanteios_media': escanteios_casa,
                    'conversao': 0.25, 'desvio_pontos': 0.5, 'pontos_pos_desvantagem_media': 1.0
                },
                'ovrall_fora': {
                    'gols_media': gols_media_fora, 'gols_sofridos_media': gols_sofridos_fora,
                    'posse_media': posse_fora, 'finalizacoes_alvo_media': finalizacoes_fora,
                    'xg_media': xg_fora, 'escanteios_media': escanteios_fora,
                    'conversao': 0.25, 'desvio_pontos': 0.5, 'pontos_pos_desvantagem_media': 1.0
                },
                'jogos_casa': jogos_casa, 'jogos_fora': jogos_fora,
                'ic_casa': ic_casa, 'ic_fora': ic_fora,
                'media_gols_casa': media_gols_casa, 'media_gols_fora': media_gols_fora,
                'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
                'media_esc_casa': 5.0, 'media_esc_fora': 4.5,
                'prateleiras_extra': {}
            }
            
            pkl_path = st.session_state.get('pkl_path', 'calibration_params.pkl')
            res, err = executar_manual(dados, pkl_path)
            if err:
                st.error(err)
            else:
                show_results_manual(res)
                st.info(random.choice(FRASES_RESULTADOS))
