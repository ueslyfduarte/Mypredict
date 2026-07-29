# ui/manual_ia_page.py — Modo Manual com extração por IA (DeepSeek)
import streamlit as st
import json
from openai import OpenAI
from ui.styles import injetar_css
from ui.components import show_results_manual
from core.calculations import executar_manual

SYSTEM_PROMPT = """Você é um assistente de análise de futebol. O usuário fornecerá um texto com informações sobre dois times que vão se enfrentar, incluindo nomes, posições na tabela, últimos resultados e estatísticas da temporada.

Extraia esses dados e retorne EXCLUSIVAMENTE um objeto JSON válido, sem explicações, sem markdown, apenas o JSON puro. Use o formato exato abaixo. Se um dado não for encontrado, coloque null (exceto para listas, que devem ser []).

{
  "time_casa": "",
  "time_fora": "",
  "pos_casa": null,
  "pos_fora": null,
  "prat_casa": "Media",
  "prat_fora": "Media",
  "jogos_casa": [
    {"resultado": "V", "adversario": "Nome", "mandante": true, "prateleira_adv": "Media"}
  ],
  "jogos_fora": [
    {"resultado": "V", "adversario": "Nome", "mandante": true, "prateleira_adv": "Media"}
  ],
  "ovrall_casa": {
    "gols_media": null,
    "gols_sofridos_media": null,
    "xg_media": null,
    "finalizacoes_alvo_media": null,
    "conversao": null,
    "xga_media": null,
    "finalizacoes_alvo_sofridas_media": null,
    "desarmes_intercep_media": null,
    "posse_media": null,
    "passes_certos_pct": null,
    "passes_chave_media": null,
    "assistencias_media": null,
    "chutes_media": null,
    "desvio_pontos": null,
    "desvio_gols_pro": null,
    "desvio_gols_sofridos": null,
    "clean_sheets_pct": null,
    "pontos_pos_desvantagem_media": null,
    "gols_ultimos_15min_media": null,
    "pontos_apos_derrota_media": null,
    "diff_aprov_casa_fora": null,
    "aprov_viradas_favor": null,
    "aprov_viradas_contra": null,
    "gols_ht_media": null,
    "gols_ht_sofridos_media": null,
    "escanteios_media": null,
    "escanteios_sofridos_media": null
  },
  "ovrall_fora": {},
  "ic_casa": {
    "confronto_direto": null,
    "mesmo_escalao": null,
    "contra_escalao_adversario": null,
    "fator_casa": null,
    "odds": null
  },
  "ic_fora": {},
  "media_gols_casa": null,
  "media_gols_fora": null,
  "media_ht_casa": null,
  "media_ht_fora": null,
  "media_esc_casa": null,
  "media_esc_fora": null,
  "prateleiras_extra": {}
}
"""

def chamar_deepseek_para_extrair_dados(texto_usuario):
    if not st.secrets.get("DEEPSEEK_API_KEY"):
        st.error("Chave do DeepSeek não configurada. Adicione DEEPSEEK_API_KEY nos secrets do Streamlit.")
        return None
    
    client = OpenAI(
        api_key=st.secrets["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com"
    )
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extraia os dados do seguinte texto: {texto_usuario}"}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        resposta = response.choices[0].message.content.strip()
        # Limpeza de possíveis blocos markdown
        if resposta.startswith("```"):
            resposta = resposta.split("```")[1]
            if resposta.startswith("json"):
                resposta = resposta[4:]
        dados = json.loads(resposta)
        return dados
    except json.JSONDecodeError:
        st.error("A IA retornou um JSON inválido. Tente novamente com um texto mais claro.")
        return None
    except Exception as e:
        st.error(f"Erro ao comunicar com o DeepSeek: {e}")
        return None

def render_manual_ia():
    injetar_css()
    st.markdown('<div class="main-title">🤖 MyPredict 2.0 · Assistente IA (DeepSeek)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Cole um texto com dados da partida e a IA preencherá automaticamente.</div>', unsafe_allow_html=True)
    st.caption("Funciona com textos do Flashscore, GE, Sofascore, etc. Quanto mais estatísticas você colar, melhor!")

    texto = st.text_area("📋 Texto da partida", height=300, placeholder="Cole aqui o texto...")

    if st.button("🧠 Processar com IA e Gerar MyPredict", use_container_width=True):
        if not texto.strip():
            st.warning("Por favor, cole algum texto.")
            return
        with st.spinner("A IA está analisando o texto... Isso pode levar alguns segundos."):
            dados_extraidos = chamar_deepseek_para_extrair_dados(texto)
        if dados_extraidos is None:
            return

        # Preencher a session_state com os dados extraídos
        for chave in ['time_casa', 'time_fora', 'pos_casa', 'pos_fora',
                      'prat_casa', 'prat_fora', 'jogos_casa', 'jogos_fora',
                      'ovrall_casa', 'ovrall_fora', 'ic_casa', 'ic_fora',
                      'media_gols_casa', 'media_gols_fora',
                      'media_ht_casa', 'media_ht_fora',
                      'media_esc_casa', 'media_esc_fora',
                      'prateleiras_extra']:
            if chave in dados_extraidos:
                st.session_state[chave] = dados_extraidos[chave]

        # Garantir que times não fiquem vazios
        if not st.session_state.get('time_casa'):
            st.session_state.time_casa = "Time da Casa"
        if not st.session_state.get('time_fora'):
            st.session_state.time_fora = "Time Visitante"
        if not st.session_state.get('pos_casa'):
            st.session_state.pos_casa = 1
        if not st.session_state.get('pos_fora'):
            st.session_state.pos_fora = 2

        # Executar o cálculo
        dados = {k: v for k, v in st.session_state.items() if k in [
            'time_casa', 'time_fora', 'pos_casa', 'pos_fora', 'prat_casa', 'prat_fora',
            'jogos_casa', 'jogos_fora', 'ovrall_casa', 'ovrall_fora', 'ic_casa', 'ic_fora',
            'media_gols_casa', 'media_gols_fora', 'media_ht_casa', 'media_ht_fora',
            'media_esc_casa', 'media_esc_fora', 'prateleiras_extra'
        ]}
        res, err = executar_manual(dados)
        if err:
            st.error(err)
        else:
            st.session_state.resultados = res
            st.rerun()

    # Exibir resultados se existirem
    if 'resultados' in st.session_state and st.session_state.resultados is not None:
        show_results_manual(st.session_state.resultados)
