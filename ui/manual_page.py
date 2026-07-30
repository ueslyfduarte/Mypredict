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
# MAPA DE LIGAS → ARQUIVO .PKL
# ============================================================
LIGAS_DISPONIVEIS = {
    "Premier League": "calibration_premier.pkl",
    "La Liga": "calibration_laliga.pkl",
    "Brasileirão": "calibration_brasileirao.pkl",
}

# ============================================================
# INTERFACE PRINCIPAL
# ============================================================
def render_manual():
    # Por enquanto, vamos desabilitar o CSS customizado para garantir que a tela não fique preta.
    # injetar_css()
    
    # Cabeçalho inspirador
    frase = random.choice(FRASES_CABECALHO)
    st.markdown(f"""
    <div style="text-align:center; padding: 20px 0 10px 0;">
        <h1 style="color:#FFD700; margin-bottom:0;">MyPredict 2.0</h1>
        <p style="color:#aaa; font-style:italic; font-size:1.1rem;">"{frase}"</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Abas principais
    tab_liga, tab_times, tab_analise = st.tabs(["🏆 Liga", "⚽ Times", "🔍 Analisar"])
    
    # ================================================================
    # ABA 1: LIGA
    # ================================================================
    with tab_liga:
        st.subheader("Selecione o campeonato")
        liga_nome = st.selectbox("Liga Ativa", list(LIGAS_DISPONIVEIS.keys()),
                                 help="Escolha a liga para carregar o modelo calibrado correto.")
        pkl_file = LIGAS_DISPONIVEIS[liga_nome]
        
        if st.button("Carregar Liga", use_container_width=True):
            if os.path.exists(pkl_file):
                st.session_state.liga_ativa = liga_nome
                st.session_state.pkl_path = pkl_file
                st.success(f"Liga '{liga_nome}' carregada com sucesso! Modelo pronto para uso.")
            else:
                st.warning(f"Arquivo '{pkl_file}' não encontrado. Usando modelo padrão.")
                st.session_state.liga_ativa = liga_nome
                st.session_state.pkl_path = 'calibration_params.pkl'  # fallback
        
        if st.session_state.liga_ativa:
            st.info(f"🏟️ Liga atual: **{st.session_state.liga_ativa}**")
    
    # ================================================================
    # ABA 2: CENTRAL DE TIMES
    # ================================================================
    with tab_times:
        st.subheader("Central de Times")
        st.caption("Cadastre os times da liga ativa. Eles ficarão salvos para análises futuras.")
        
        with st.expander("➕ Adicionar / Editar Time", expanded=False):
            nome_time = st.text_input("Nome do Time", key="ed_nome")
            posicao = st.number_input("Posição atual na tabela", 1, 20, key="ed_pos")
            prat_proj = st.selectbox("Prateleira Projetada", ["Elite", "Alta", "Media", "Baixa", "Critica"],
                                     help="Expectativa antes da temporada (usada apenas para o fator de superação).")
            
            st.markdown("**📊 Estatísticas do Time (médias por jogo)**")
            col1, col2, col3 = st.columns(3)
            gols_media = col1.number_input("⚽ Gols Marcados", 0.0, 5.0, 1.4, 0.1, key="ed_gols")
            gols_sofridos = col2.number_input("🛡️ Gols Sofridos", 0.0, 5.0, 1.4, 0.1, key="ed_gols_s")
            posse = col3.number_input("📊 Posse (%)", 0, 100, 50, key="ed_posse")
            finalizacoes = col1.number_input("🎯 Finalizações Alvo", 0.0, 15.0, 4.0, 0.5, key="ed_fin")
            xg = col2.number_input("📈 xG", 0.0, 4.0, 1.2, 0.1, key="ed_xg")
            escanteios = col3.number_input("🏁 Escanteios", 0.0, 15.0, 5.0, 0.5, key="ed_esc")
            
            st.markdown("**📋 Últimos 10 Jogos**")
            st.caption("Prateleira do adversário: REAL (posição na tabela no momento do jogo).")
            num_jogos = st.slider("Quantos jogos adicionar?", 3, 10, 5, key="ed_num_jogos")
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
            
            if st.button("Salvar Time", use_container_width=True):
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
        
        st.markdown("---")
        st.markdown("### Times Cadastrados")
        if st.session_state.times:
            for nome, data in st.session_state.times.items():
                st.write(f"**{nome}** | Posição: {data['pos_casa']} | Projetada: {data['prat_casa']}")
        else:
            st.info("Nenhum time cadastrado ainda.")
    
    # ================================================================
    # ABA 3: ANALISAR JOGO
    # ================================================================
    with tab_analise:
        st.subheader("Analisar Confronto")
        
        if not st.session_state.times:
            st.warning("Cadastre ao menos dois times na aba 'Times' antes de analisar.")
            return
        
        nomes_times = list(st.session_state.times.keys())
        col_a, col_b = st.columns(2)
        time_casa_nome = col_a.selectbox("Time Casa", nomes_times, key="sel_casa")
        time_fora_nome = col_b.selectbox("Time Fora", nomes_times, key="sel_fora")
        
        if time_casa_nome == time_fora_nome:
            st.error("Selecione times diferentes.")
            return
        
        dados_casa = st.session_state.times[time_casa_nome]
        dados_fora = st.session_state.times[time_fora_nome]
        
        with st.expander("🧠 Ajustes de Contexto (opcional)"):
            st.markdown("Preencha para melhorar a precisão do Índice de Contexto.")
            ic_casa = {}
            ic_fora = {}
            ic_casa['confronto_direto'] = st.slider(f"Aproveitamento {time_casa_nome} nos últimos 6 jogos contra {time_fora_nome} (%)", 0, 100, 50) / 100
            ic_fora['confronto_direto'] = 1.0 - ic_casa['confronto_direto']
            ic_casa['fator_casa'] = st.slider(f"Aproveitamento como mandante (%)", 0, 100, 60) / 100
            ic_fora['fator_casa'] = st.slider(f"Aproveitamento como visitante (%)", 0, 100, 40) / 100
        
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
            'media_gols_casa': MEDIA_GOLS_CASA_LIGA,
            'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
            'media_ht_casa': 0.75,
            'media_ht_fora': 0.65,
            'media_esc_casa': 5.0,
            'media_esc_fora': 4.5,
            'prateleiras_extra': {},
        }
        
        if st.button("⚡ Calcular Análise Completa", use_container_width=True, type="primary"):
            pkl_path = st.session_state.get('pkl_path', 'calibration_params.pkl')
            res, err = executar_manual(dados, pkl_path)
            if err:
                st.error(err)
            else:
                show_results_manual(res)
                st.info(random.choice(FRASES_RESULTADOS))
