# interfaces.py — MyPredict 2.0 (com rastreamento completo)
import streamlit as st
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from manual import processar_texto_ia, processar_lista_simples, executar_manual
from utils import para_float, extrair_jogos
from data_source_api_football import get_api_usage
from automatico import inicializar_estado, carregar_ligas, buscar_temporadas, buscar_times, executar_automatico

def injetar_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background: radial-gradient(circle at 20% 50%, #1e1e2f, #0e1117); }
        .title-glow {
            font-size: 3rem; font-weight: 900; text-align: center;
            background: linear-gradient(to right, #ffd700, #ffaa00, #ffd700);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .subtitle-glow { text-align: center; color: #aaa; font-size: 1.1rem; margin-bottom: 2rem; }
        .card-comparativo {
            display: flex; justify-content: space-between; align-items: center;
            margin: 8px 0; padding: 12px; background: rgba(255,255,255,0.03);
            border-radius: 12px; border: 1px solid rgba(255,215,0,0.1);
        }
        .gold-text { color: #ffd700 !important; }
        .silver-text { color: #c0c0c0 !important; }
        .selo-dourado {
            background: linear-gradient(145deg, #ffd700, #b8860b);
            color: #000; font-weight: 900; text-align: center; border-radius: 50%;
            width: 100px; height: 100px; display: flex; align-items: center; justify-content: center;
            margin: 20px auto; font-size: 0.9rem; box-shadow: 0 0 40px #ffd700; animation: pulse 2s infinite;
        }
        @keyframes pulse { 0% { box-shadow: 0 0 20px #ffd700; } 50% { box-shadow: 0 0 40px #ffd700, 0 0 80px #ffaa00; } 100% { box-shadow: 0 0 20px #ffd700; } }
        .stButton > button {
            background: linear-gradient(135deg, #ffd700, #ff8c00); color: #000; border: none;
            font-weight: 700; font-size: 1.2rem; border-radius: 16px; padding: 16px;
            transition: 0.3s; letter-spacing: 1px; box-shadow: 0 4px 20px rgba(255,215,0,0.4);
        }
        .stButton > button:hover { transform: scale(1.02); box-shadow: 0 8px 30px rgba(255,215,0,0.6); }
        .usage-badge { background: rgba(30,30,30,0.8); border: 1px solid #ffd700; border-radius: 20px; padding: 4px 16px; display: inline-flex; align-items: center; gap: 8px; font-size: 0.85rem; color: #ffd700; margin-bottom: 20px; }
        .rastro-box { background: rgba(255,255,255,0.02); border-radius: 12px; padding: 12px; margin: 8px 0; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# ---------- TELA AUTOMÁTICA (inalterada) ----------
def tela_automatico(lista_ligas, temporadas, times_carregados, uso_api, limite_api, msg_erro, resultados):
    # ... (código existente, omitido por brevidade)
    pass

# ---------- TELA MANUAL (com rastreio) ----------
def tela_manual():
    st.set_page_config(page_title="MyPredict 2.0 – Manual", layout="centered")
    injetar_css()

    for chave, padrao in {
        'time_casa': 'Flamengo', 'time_fora': 'Palmeiras', 'pos_casa': 1, 'pos_fora': 2,
        'jogos_casa': [], 'jogos_fora': [], 'ovrall_casa': {}, 'ovrall_fora': {},
        'ic_casa': {}, 'ic_fora': {}, 'media_gols_casa': MEDIA_GOLS_CASA_LIGA,
        'media_gols_fora': MEDIA_GOLS_FORA_LIGA, 'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
        'media_esc_casa': 5.0, 'media_esc_fora': 4.5, 'prateleiras_extra': {}
    }.items():
        if chave not in st.session_state: st.session_state[chave] = padrao

    st.markdown('<div class="title-glow">⚽ MyPredict 2.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle-glow">Modo Manual · Análise Preditiva Premium</div>', unsafe_allow_html=True)

    entrada = st.radio("Método de entrada",
                       ["Preenchimento Manual", "Colar resposta da IA", "Colar apenas números (ordem fixa)"],
                       horizontal=True, key="modo_manual")

    # ... (código de entrada de dados igual ao último, com os botões Processar)
    # Para não alongar, assumirei que essa parte está igual e que st.session_state está preenchido.

    if st.session_state.get('jogos_casa') and st.session_state.get('jogos_fora'):
        st.markdown("---")
        if st.button("🔥 GERAR MYPREDICT VALUE", use_container_width=True):
            dados_calc = {k: v for k, v in st.session_state.items() if k in [
                'time_casa','time_fora','pos_casa','pos_fora','jogos_casa','jogos_fora',
                'ovrall_casa','ovrall_fora','ic_casa','ic_fora','media_gols_casa','media_gols_fora',
                'media_ht_casa','media_ht_fora','media_esc_casa','media_esc_fora','prateleiras_extra']}
            res, err = executar_manual(dados_calc)
            if err:
                st.error(err)
            else:
                st.session_state.resultados = res
                st.rerun()

    if 'resultados' in st.session_state:
        res = st.session_state.resultados
        # ... (exibição dos cards comparativos e mercados, igual à versão anterior)

        # 🔎 RASTREIO COMPLETO
        with st.expander("🔎 RASTREIO COMPLETO DOS CÁLCULOS (Passo a passo)"):
            st.markdown("## 1. IMA (Índice de Momento Atual)")
            for lado, time, ima, det in [('casa', res['time_casa'], res['ima_casa'], res['detalhes_ima']['casa']),
                                         ('fora', res['time_fora'], res['ima_fora'], res['detalhes_ima']['fora'])]:
                st.markdown(f"**{time}** – Valor final: {ima:.1f}")
                for recorte, jogos in det.items():
                    if not jogos: continue
                    st.write(f"Recorte {recorte}:")
                    for j in jogos:
                        st.write(f"  {j['jogo']} → {j['pontos']:.2f} pts (Time: {j['prateleira_time']}, Adv: {j['prateleira_adv']})")
                    media = sum(j['pontos'] for j in jogos) / len(jogos)
                    st.write(f"  Média do recorte: {media:.2f}")

            st.markdown("## 2. OVRall (Força Geral)")
            for nome, det in res.get('detalhes_ovr', {}).items():
                st.markdown(f"**{nome}**")
                st.write("Indicadores Casa:")
                for ind, valor, perc in det['casa']:
                    st.write(f"- {ind}: {valor} → nota {perc:.1f}")
                st.write(f"Nota Casa: {res['notas_casa'][nome]:.1f}")
                st.write("Indicadores Fora:")
                for ind, valor, perc in det['fora']:
                    st.write(f"- {ind}: {valor} → nota {perc:.1f}")
                st.write(f"Nota Fora: {res['notas_fora'][nome]:.1f}")

            st.markdown("## 3. IC (Índice de Contexto)")
            st.write(f"Casa: {res['ic_casa']:.1f}  Fora: {res['ic_fora']:.1f}")

            st.markdown("## 4. MPV (MyPredict Value)")
            st.write(f"Casa: {res['mpv_casa']:.1f}  Fora: {res['mpv_fora']:.1f}")

            st.markdown("## 5. Mercados")
            st.write(f"1X2: {res['p1']:.1%} / {res['pX']:.1%} / {res['p2']:.1%}")
            st.write(f"Over 2.5: {res['over25']:.1%}" if res['over25'] else "N/D")
            st.write(f"Ambas Marcam: {res['btts']:.1%}" if res['btts'] else "N/D")
            st.write(f"Gol HT: {res['gol_ht']:.1%}" if res['gol_ht'] else "N/D")
            st.write(f"Escanteios: {res['esc']:.1%}" if res['esc'] else "N/D")
