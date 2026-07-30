# ui/manual_page.py — Modo Manual com visual EA Sports (dourado)
import streamlit as st
import pandas as pd
import os
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
        /* Fundo geral e tipografia */
        .stApp {
            background-color: #0E1117;
            color: #EAEAEA;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        h1, h2, h3 {
            color: #FFD700 !important;
        }
        
        /* Cards dourados para times */
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
        
        /* Containers dourados para seletores */
        .golden-select {
            border: 1px solid #FFD700;
            border-radius: 12px;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 215, 0, 0.05);
        }
        
        /* Botões dourados */
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
        
        /* Tabs com destaque dourado */
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
        
        /* Expanders com borda dourada */
        .streamlit-expanderHeader {
            border: 1px solid #FFD700;
            border-radius: 10px;
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
# INTERFACE PRINCIPAL (com visual dourado)
# ============================================================
def render_manual():
    # Injetar CSS
    injetar_css_personalizado()
    
    # Cabeçalho inspirador
    frase = random.choice(FRASES_CABECALHO)
    st.markdown(f"""
    <div style="text-align:center; padding: 30px 0 20px 0;">
        <h1 style="font-size:3rem; margin:0; letter-spacing:3px;">⚽ MYPREDICT 2.0</h1>
        <p style="color:#FFD700; font-style:italic; font-size:1.2rem; margin-top:5px;">"{frase}"</p>
        <p style="color:#999; margin-top:10px;">🟣 Análise Tática • Contraste Inteligente • Previsão de Mercados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Abas principais
    tab_liga, tab_times, tab_analise = st.tabs(["🏆 Liga", "⚽ Times", "🔍 Analisar"])
    
    # ================================================================
    # ABA 1: LIGA (com médias editáveis)
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
                st.session_state.liga_ativa = liga_nome
                st.session_state.pkl_path = LIGAS_DISPONIVEIS[liga_nome]
                st.success(f"Liga '{liga_nome}' carregada! Modelo pronto.")
        
        if st.session_state.liga_ativa:
            st.info(f"🏟️ Liga atual: **{st.session_state.liga_ativa}**")
        
        # Médias da liga (editáveis)
        with st.expander("📊 Médias da Liga (personalize)", expanded=False):
            st.caption("Esses valores são usados como referência nos cálculos. Altere se necessário.")
            ml_col1, ml_col2 = st.columns(2)
            media_gols_casa_liga = ml_col1.number_input("Média Gols Casa (liga)", 0.0, 5.0, MEDIA_GOLS_CASA_LIGA, key="ml_casa")
            media_gols_fora_liga = ml_col2.number_input("Média Gols Fora (liga)", 0.0, 5.0, MEDIA_GOLS_FORA_LIGA, key="ml_fora")
            st.session_state.media_gols_casa_liga = media_gols_casa_liga
            st.session_state.media_gols_fora_liga = media_gols_fora_liga
    
    # ================================================================
    # ABA 2: CENTRAL DE TIMES (visual EA)
    # ================================================================
    with tab_times:
        st.subheader("Central de Times")
        st.caption("Cadastre os times da liga ativa. Eles ficarão salvos para análises futuras.")
        
        with st.expander("➕ Adicionar / Editar Time", expanded=False):
            nome_time = st.text_input("Nome do Time", key="ed_nome")
            col_pos, col_prat = st.columns(2)
            posicao = col_pos.number_input("Posição atual", 1, 20, key="ed_pos")
            prat_proj = col_prat.selectbox("Prateleira Projetada", ["Elite", "Alta", "Media", "Baixa", "Critica"],
                                           help="Expectativa pré-temporada (usada no fator de superação).")
            
            st.markdown("**📊 Estatísticas (médias por jogo)**")
            col1, col2, col3 = st.columns(3)
            gols_media = col1.number_input("⚽ Gols Marcados", 0.0, 5.0, 1.4, 0.1, key="ed_gols")
            gols_sofridos = col2.number_input("🛡️ Gols Sofridos", 0.0, 5.0, 1.4, 0.1, key="ed_gols_s")
            posse = col3.number_input("📊 Posse (%)", 0, 100, 50, key="ed_posse")
            finalizacoes = col1.number_input("🎯 Finalizações Alvo", 0.0, 15.0, 4.0, 0.5, key="ed_fin")
            xg = col2.number_input("📈 xG", 0.0, 4.0, 1.2, 0.1, key="ed_xg")
            escanteios = col3.number_input("🏁 Escanteios", 0.0, 15.0, 5.0, 0.5, key="ed_esc")
            
            st.markdown("**📋 Últimos Jogos**")
            st.caption("Prateleira do adversário: REAL (posição no momento do jogo).")
            num_jogos = st.slider("Quantos jogos?", 3, 10, 5, key="ed_num_jogos")
            jogos_list = []
            for i in range(num_jogos):
                cols = st.columns([2, 3, 3, 1, 1])
                res = cols[0].selectbox("Res.", ['V', 'E', 'D'], key=f"ed_res_{i}")
                adv = cols[1].text_input("Adversário", key=f"ed_adv_{i}")
                prat_adv = cols[2].selectbox("Prat. Real Adv.", ["Elite", "Alta", "Media", "Baixa", "Critica"], key=f"ed_prat_{i}")
                gols_pro = cols[3].number_input("GP", 0, 10, 0, key=f"ed_gp_{i}")
                gols_contra = cols[4].number_input("GC", 0, 10, 0, key=f"ed_gc_{i}")
                jogos_list.append({
                    'resultado': res,
                    'adversario': adv,
                    'prateleira_adv': prat_adv,
                    'gols_pro': gols_pro,
                    'gols_contra': gols_contra,
                    'mandante': True
                })
            
            if st.button("💾 Salvar Time", use_container_width=True):
                if nome_time:
                    st.session_state.times[nome_time] = {
                        'nome': nome_time,
                        'pos_casa': posicao,
                        'prat_casa': prat_proj,
                        'ovrall_casa': {
                            'gols_media': gols_media,
                            'gols_sofridos_media': gols_sofridos,
                            'posse_media': posse,
                            'finalizacoes_alvo_media': finalizacoes,
                            'xg_media': xg,
                            'escanteios_media': escanteios,
                            'conversao': 0.25,
                            'desvio_pontos': 0.5,
                            'pontos_pos_desvantagem_media': 1.0,
                        },
                        'jogos_casa': jogos_list,
                        'jogos_fora': jogos_list,
                    }
                    st.success(f"Time '{nome_time}' salvo!")
                else:
                    st.error("Informe o nome do time.")
        
        # Lista de times cadastrados (visual EA)
        st.markdown("---")
        st.markdown("### ⭐ Times Cadastrados")
        if st.session_state.times:
            cols = st.columns(min(3, len(st.session_state.times)))
            for i, (nome, data) in enumerate(st.session_state.times.items()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="team-card">
                        <div class="badge">🛡️</div>
                        <h3>{nome}</h3>
                        <div class="position">#{data['pos_casa']} • {data['prat_casa']}</div>
                        <div style="text-align:left; margin-top:10px;">
                            <small>⚽ Ataque</small>
                            <div class="attr-bar"><div class="attr-fill" style="width:{min(100, data['ovrall_casa'].get('gols_media',1.4)*30)}%;"></div></div>
                            <small>🛡️ Defesa</small>
                            <div class="attr-bar"><div class="attr-fill" style="width:{min(100, 100 - data['ovrall_casa'].get('gols_sofridos_media',1.4)*30)}%;"></div></div>
                            <small>📊 Meio-Campo</small>
                            <div class="attr-bar"><div class="attr-fill" style="width:{min(100, data['ovrall_casa'].get('posse_media',50))}%;"></div></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Nenhum time cadastrado. Use o formulário acima para criar times com visual EA.")
    
    # ================================================================
    # ABA 3: ANALISAR JOGO (escolha de times como videogame)
    # ================================================================
    with tab_analise:
        st.subheader("🎮 Selecionar Confronto")
        
        if not st.session_state.times:
            st.warning("Cadastre ao menos dois times na aba 'Times' antes de analisar.")
            return
        
        nomes_times = list(st.session_state.times.keys())
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="golden-select">', unsafe_allow_html=True)
            time_casa_nome = st.selectbox("🏠 Time Casa", nomes_times, key="sel_casa")
            st.markdown('</div>', unsafe_allow_html=True)
            # Exibir minicard do time casa
            dados_casa = st.session_state.times[time_casa_nome]
            st.markdown(f"""
            <div class="team-card" style="border-color:#FFD700;">
                <div class="badge">🛡️</div>
                <h3>{time_casa_nome}</h3>
                <div class="position">#{dados_casa['pos_casa']} • {dados_casa['prat_casa']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown('<div class="golden-select">', unsafe_allow_html=True)
            time_fora_nome = st.selectbox("🏟️ Time Fora", nomes_times, key="sel_fora")
            st.markdown('</div>', unsafe_allow_html=True)
            dados_fora = st.session_state.times[time_fora_nome]
            st.markdown(f"""
            <div class="team-card" style="border-color:#C0C0C0;">
                <div class="badge">🛡️</div>
                <h3>{time_fora_nome}</h3>
                <div class="position">#{dados_fora['pos_casa']} • {dados_fora['prat_casa']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        if time_casa_nome == time_fora_nome:
            st.error("Selecione times diferentes.")
            return
        
        # Ajustes de contexto
        with st.expander("🧠 Ajustes de Contexto (opcional)", expanded=False):
            st.markdown("Preencha para melhorar o Índice de Contexto.")
            ic_casa = {}
            ic_fora = {}
            ic_casa['confronto_direto'] = st.slider(f"Aproveitamento {time_casa_nome} nos últimos 6 jogos contra {time_fora_nome} (%)", 0, 100, 50) / 100
            ic_fora['confronto_direto'] = 1.0 - ic_casa['confronto_direto']
            ic_casa['fator_casa'] = st.slider(f"Aproveitamento como mandante (%)", 0, 100, 60) / 100
            ic_fora['fator_casa'] = st.slider(f"Aproveitamento como visitante (%)", 0, 100, 40) / 100
        
        # Botão de cálculo
        if st.button("⚡ CALCULAR ANÁLISE COMPLETA", use_container_width=True, type="primary"):
            # Usar médias da liga personalizadas (se existirem na sessão)
            media_gols_casa = st.session_state.get('media_gols_casa_liga', MEDIA_GOLS_CASA_LIGA)
            media_gols_fora = st.session_state.get('media_gols_fora_liga', MEDIA_GOLS_FORA_LIGA)
            
            dados = {
                'time_casa': time_casa_nome,
                'time_fora': time_fora_nome,
                'pos_casa': dados_casa['pos_casa'],
                'pos_fora': dados_fora['pos_casa'],
                'prat_casa': dados_casa['prat_casa'],
                'prat_fora': dados_fora['prat_casa'],
                'ovrall_casa': dados_casa['ovrall_casa'],
                'ovrall_fora': dados_fora['ovrall_casa'],
                'jogos_casa': dados_casa['jogos_casa'],
                'jogos_fora': dados_fora['jogos_fora'],
                'ic_casa': ic_casa,
                'ic_fora': ic_fora,
                'media_gols_casa': media_gols_casa,
                'media_gols_fora': media_gols_fora,
                'media_ht_casa': 0.75,
                'media_ht_fora': 0.65,
                'media_esc_casa': 5.0,
                'media_esc_fora': 4.5,
                'prateleiras_extra': {},
            }
            
            pkl_path = st.session_state.get('pkl_path', 'calibration_params.pkl')
            res, err = executar_manual(dados, pkl_path)
            if err:
                st.error(err)
            else:
                show_results_manual(res)
                st.info(random.choice(FRASES_RESULTADOS))
