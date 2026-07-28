# manual_app.py — MyPredict 2.0 (parser robusto para IA)
import streamlit as st
import re
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA

def para_float(valor_str):
    if valor_str is None or valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        return None

st.markdown("""
<style>
    .selo-dourado {
        background: linear-gradient(145deg, #ffd700, #b8860b);
        color: #0e1117; font-weight: 900; text-align: center;
        border-radius: 50%; width: 80px; height: 80px;
        display: flex; align-items: center; justify-content: center;
        margin: 10px auto; font-size: 12px; box-shadow: 0 0 20px #ffd700;
    }
    .selo-verde {
        background: #00ff7f; color: #0e1117; font-weight: 700;
        text-align: center; border-radius: 20px; padding: 4px 12px; margin: 5px;
    }
    .selo-amarelo {
        background: #ffaa00; color: #0e1117; font-weight: 700;
        text-align: center; border-radius: 20px; padding: 4px 12px; margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

def indicador(prob):
    if prob is None: return "⬜", ""
    if prob >= 0.70: return "⬆️", "selo-dourado"
    elif prob >= 0.55: return "⬆️", "selo-verde"
    elif prob >= 0.45: return "➖", "selo-amarelo"
    else: return "⬇️", ""

def parse_ia_text(texto):
    """Processa o texto da IA e retorna um dicionário com todos os dados."""
    # Normaliza: insere quebras antes de palavras-chave
    texto = re.sub(r'(Time da casa:|Time da fora:|Liga:|Temporada:|Posições:|Últimos 10 jogos|Métricas OVRall|Métricas IC|Médias da Liga:|Prateleiras)', r'\n\1', texto)
    linhas = texto.strip().split('\n')
    
    dados = {
        'time_casa': 'Flamengo', 'time_fora': 'Palmeiras', 'liga': '', 'temporada': 2026,
        'pos_casa': 1, 'pos_fora': 2,
        'jogos_casa': [], 'jogos_fora': [],
        'ovrall_casa': {}, 'ovrall_fora': {},
        'ic_casa': {}, 'ic_fora': {},
        'media_gols_casa': MEDIA_GOLS_CASA_LIGA, 'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
        'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
        'media_esc_casa': 5.0, 'media_esc_fora': 4.5,
        'prateleiras_extra': {}
    }
    
    secao = None
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        # Detecta seções
        if linha.startswith('Time da casa:'):
            dados['time_casa'] = linha.split(':', 1)[1].strip()
        elif linha.startswith('Time da fora:'):
            dados['time_fora'] = linha.split(':', 1)[1].strip()
        elif linha.startswith('Liga:'):
            dados['liga'] = linha.split(':', 1)[1].strip()
        elif linha.startswith('Temporada:'):
            try: dados['temporada'] = int(linha.split(':', 1)[1].strip())
            except: pass
        elif linha.startswith('Posições:'):
            secao = 'posicoes'
            continue
        elif 'Últimos 10 jogos do time da casa' in linha:
            secao = 'jogos_casa'
            continue
        elif 'Últimos 10 jogos do time da fora' in linha:
            secao = 'jogos_fora'
            continue
        elif 'Métricas OVRall do time da casa' in linha:
            secao = 'ovrall_casa'
            continue
        elif 'Métricas OVRall do time da fora' in linha:
            secao = 'ovrall_fora'
            continue
        elif 'Métricas IC do time da casa' in linha:
            secao = 'ic_casa'
            continue
        elif 'Métricas IC do time da fora' in linha:
            secao = 'ic_fora'
            continue
        elif 'Médias da Liga:' in linha or 'Médias da Liga' in linha:
            secao = 'medias_liga'
            continue
        elif 'Prateleiras' in linha:
            secao = 'prateleiras'
            continue
        
        # Processa de acordo com a seção atual
        if secao == 'posicoes':
            if linha.startswith('Casa:'):
                try: dados['pos_casa'] = int(linha.split(':')[1].strip())
                except: pass
            elif linha.startswith('Fora:'):
                try: dados['pos_fora'] = int(linha.split(':')[1].strip())
                except: pass
        elif secao == 'jogos_casa':
            partes = [p.strip() for p in linha.split(',')]
            if len(partes) >= 3:
                dados['jogos_casa'].append({
                    "resultado": partes[0],
                    "adversario": partes[1],
                    "mandante": partes[2].upper() == 'S'
                })
        elif secao == 'jogos_fora':
            partes = [p.strip() for p in linha.split(',')]
            if len(partes) >= 3:
                dados['jogos_fora'].append({
                    "resultado": partes[0],
                    "adversario": partes[1],
                    "mandante": partes[2].upper() == 'S'
                })
        elif secao == 'ovrall_casa':
            partes = [x.strip() for x in linha.split(',')]
            if len(partes) == 23:
                chaves = ["gols_media","gols_sofridos_media","xg_media","xga_media",
                          "finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media",
                          "chutes_media","desarmes_intercep_media","posse_media",
                          "passes_certos_pct","passes_chave_media","assistencias_media",
                          "conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro",
                          "desvio_gols_sofridos","pontos_pos_desvantagem_media",
                          "gols_ultimos_15min_media","pontos_apos_derrota_media",
                          "diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
                for i, chave in enumerate(chaves):
                    dados['ovrall_casa'][chave] = para_float(partes[i])
        elif secao == 'ovrall_fora':
            partes = [x.strip() for x in linha.split(',')]
            if len(partes) == 23:
                chaves = ["gols_media","gols_sofridos_media","xg_media","xga_media",
                          "finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media",
                          "chutes_media","desarmes_intercep_media","posse_media",
                          "passes_certos_pct","passes_chave_media","assistencias_media",
                          "conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro",
                          "desvio_gols_sofridos","pontos_pos_desvantagem_media",
                          "gols_ultimos_15min_media","pontos_apos_derrota_media",
                          "diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
                for i, chave in enumerate(chaves):
                    dados['ovrall_fora'][chave] = para_float(partes[i])
        elif secao == 'ic_casa':
            partes = [x.strip() for x in linha.split(',')]
            if len(partes) == 5:
                chaves = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
                for i, chave in enumerate(chaves):
                    dados['ic_casa'][chave] = para_float(partes[i])
        elif secao == 'ic_fora':
            partes = [x.strip() for x in linha.split(',')]
            if len(partes) == 5:
                chaves = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
                for i, chave in enumerate(chaves):
                    dados['ic_fora'][chave] = para_float(partes[i])
        elif secao == 'medias_liga':
            if 'Média gols casa:' in linha:
                dados['media_gols_casa'] = para_float(linha.split(':')[1])
            elif 'Média gols fora:' in linha:
                dados['media_gols_fora'] = para_float(linha.split(':')[1])
            elif 'Média gols 1º tempo casa:' in linha:
                dados['media_ht_casa'] = para_float(linha.split(':')[1])
            elif 'Média gols 1º tempo fora:' in linha:
                dados['media_ht_fora'] = para_float(linha.split(':')[1])
            elif 'Média escanteios casa:' in linha:
                dados['media_esc_casa'] = para_float(linha.split(':')[1])
            elif 'Média escanteios fora:' in linha:
                dados['media_esc_fora'] = para_float(linha.split(':')[1])
        elif secao == 'prateleiras':
            if ':' in linha:
                adv, prat = linha.split(':', 1)
                dados['prateleiras_extra'][adv.strip()] = prat.strip()
    
    return dados

def show():
    st.title("MyPredict 2.0 – Modo Manual")
    entrada = st.radio("Método de entrada", ["Preenchimento Manual", "Colar resposta da IA"])

    if entrada == "Colar resposta da IA":
        st.subheader("📥 Cole aqui a resposta completa da IA")
        texto = st.text_area("Resposta da IA", height=300, key="ia_text")
        if st.button("Processar dados"):
            if texto.strip():
                dados = parse_ia_text(texto)
                # Armazena no session_state
                for chave, valor in dados.items():
                    st.session_state[chave] = valor
                st.session_state.dados_processados = True
                st.success("Dados processados com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, cole a resposta da IA.")
        
        if st.session_state.get('dados_processados'):
            # Recupera do session_state
            time_casa = st.session_state.get('time_casa', 'Flamengo')
            time_fora = st.session_state.get('time_fora', 'Palmeiras')
            pos_casa = st.session_state.get('pos_casa', 1)
            pos_fora = st.session_state.get('pos_fora', 2)
            jogos_casa = st.session_state.get('jogos_casa', [])
            jogos_fora = st.session_state.get('jogos_fora', [])
            ovrall_casa = st.session_state.get('ovrall_casa', {})
            ovrall_fora = st.session_state.get('ovrall_fora', {})
            ic_casa = st.session_state.get('ic_casa', {})
            ic_fora = st.session_state.get('ic_fora', {})
            media_gols_casa = st.session_state.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA)
            media_gols_fora = st.session_state.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)
            media_ht_casa = st.session_state.get('media_ht_casa', 0.75)
            media_ht_fora = st.session_state.get('media_ht_fora', 0.65)
            media_esc_casa = st.session_state.get('media_esc_casa', 5.0)
            media_esc_fora = st.session_state.get('media_esc_fora', 4.5)
            prateleiras_extra = st.session_state.get('prateleiras_extra', {})
    else:
        # MODO MANUAL (inalterado, mesmo código de antes)
        c1, c2 = st.columns(2)
        time_casa = c1.text_input("Time da Casa", "Flamengo")
        time_fora = c2.text_input("Time da Fora", "Palmeiras")
        # ... (restante do código manual idêntico ao fornecido anteriormente, com todos os campos)
        # Para manter a resposta concisa, não repetirei todo o modo manual aqui, mas ele continua presente.
        # Basta copiar o bloco 'else' da versão anterior que você já possui.
        # Como a conversa é longa, se precisar do modo manual completo, peça que eu forneço.

    # ---------- CÁLCULO (comum) ----------
    if st.button("Calcular MyPredict Manual"):
        if len(jogos_casa) < 10 or len(jogos_fora) < 10:
            st.error("São necessários exatamente 10 jogos para cada time.")
            st.stop()
        if ovrall_casa.get('gols_media') is None or ovrall_fora.get('gols_media') is None:
            st.error("É obrigatório informar a média de gols marcados de ambos os times.")
            st.stop()

        prat_casa = obter_prateleira(pos_casa)
        prat_fora = obter_prateleira(pos_fora)
        prateleiras = {time_casa: prat_casa, time_fora: prat_fora}
        for j in jogos_casa + jogos_fora:
            if j['adversario'] not in prateleiras:
                prateleiras[j['adversario']] = "Media"
        for adv, prat in prateleiras_extra.items():
            if adv in prateleiras:
                prateleiras[adv] = prat

        rec_casa = {
            '10G': jogos_casa[:10], '5G': jogos_casa[:5], '3G': jogos_casa[:3],
            '5CF': [j for j in jogos_casa if j['mandante']][:5],
            '3CF': [j for j in jogos_casa if j['mandante']][:3],
        }
        rec_fora = {
            '10G': jogos_fora[:10], '5G': jogos_fora[:5], '3G': jogos_fora[:3],
            '5CF': [j for j in jogos_fora if j['mandante']][:5],
            '3CF': [j for j in jogos_fora if j['mandante']][:3],
        }

        ima_casa = calcular_ima(time_casa, rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                                rec_casa['5CF'], rec_casa['3CF'], prateleiras)
        ima_fora = calcular_ima(time_fora, rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                                rec_fora['5CF'], rec_fora['3CF'], prateleiras)

        dados_liga = {k: [ovrall_casa.get(k, 0) or 0, ovrall_fora.get(k, 0) or 0] for k in set(ovrall_casa) | set(ovrall_fora)}
        ovrall_val_casa = calcular_ovrall(ovrall_casa, dados_liga)
        ovrall_val_fora = calcular_ovrall(ovrall_fora, dados_liga)

        ic_val_casa = calcular_ic(ic_casa)
        ic_val_fora = calcular_ic(ic_fora)

        mpv_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
        mpv_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

        bonus_casa = calcular_bonus_casa(ovrall_casa.get('diff_aprov_casa_fora') or 0)
        p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

        over25 = prob_over_2_5(
            ovrall_casa.get('gols_media'), ovrall_fora.get('gols_media'),
            ovrall_casa.get('gols_sofridos_media'), ovrall_fora.get('gols_sofridos_media'),
            media_casa=media_gols_casa, media_fora=media_gols_fora
        )

        gols_esp_casa = _gols_esperados(ovrall_casa.get('gols_media'),
                                        ovrall_fora.get('gols_sofridos_media'),
                                        media_gols_casa)
        gols_esp_fora = _gols_esperados(ovrall_fora.get('gols_media'),
                                        ovrall_casa.get('gols_sofridos_media'),
                                        media_gols_fora)
        btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)

        gol_ht = prob_gol_ht(
            ovrall_casa.get('gols_ht_media', 0.5) or 0.5,
            ovrall_fora.get('gols_ht_media', 0.5) or 0.5,
            ovrall_casa.get('gols_ht_sofridos_media', 0.5) or 0.5,
            ovrall_fora.get('gols_ht_sofridos_media', 0.5) or 0.5,
            media_ht_casa=media_ht_casa, media_ht_fora=media_ht_fora
        )

        esc = prob_over_escanteios(
            ovrall_casa.get('escanteios_media', 5.0) or 5.0,
            ovrall_fora.get('escanteios_media', 5.0) or 5.0,
            ovrall_casa.get('escanteios_sofridos_media', 5.0) or 5.0,
            ovrall_fora.get('escanteios_sofridos_media', 5.0) or 5.0,
            media_casa=media_esc_casa, media_fora=media_esc_fora
        )

        # Resultados
        st.subheader("📊 Resultados")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vitória Casa", f"{p1:.1%}")
            seta, selo = indicador(p1)
            st.markdown(seta)
            if selo == "selo-dourado":
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
            elif selo == "selo-verde":
                st.markdown('<div class="selo-verde">FAVORITO</div>', unsafe_allow_html=True)
            elif selo == "selo-amarelo":
                st.markdown('<div class="selo-amarelo">EQUILIBRADO</div>', unsafe_allow_html=True)
        with col2:
            st.metric("Empate", f"{pX:.1%}")
            seta, selo = indicador(pX)
            st.markdown(seta)
        with col3:
            st.metric("Vitória Fora", f"{p2:.1%}")
            seta, selo = indicador(p2)
            st.markdown(seta)
            if selo == "selo-dourado":
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
            elif selo == "selo-verde":
                st.markdown('<div class="selo-verde">FAVORITO</div>', unsafe_allow_html=True)

        st.markdown("---")
        col4, col5 = st.columns(2)
        with col4:
            st.metric("Over 2.5 gols", f"{over25:.1%}" if over25 else "N/D")
            seta, selo = indicador(over25)
            st.markdown(seta)
            if over25 and over25 >= 0.70:
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)
        with col5:
            st.metric("Ambas Marcam", f"{btts:.1%}" if btts else "N/D")
            seta, selo = indicador(btts)
            st.markdown(seta)
            if btts and btts >= 0.70:
                st.markdown('<div class="selo-dourado">MYPREDICT<br>VALUE</div>', unsafe_allow_html=True)

        st.metric("Gol no 1º tempo", f"{gol_ht:.1%}" if gol_ht else "N/D")
        seta, _ = indicador(gol_ht)
        st.markdown(seta)

        st.metric("Over Escanteios", f"{esc:.1%}" if esc else "N/D")
        seta, _ = indicador(esc)
        st.markdown(seta)

        with st.expander("📊 Métricas detalhadas"):
            st.write(f"**{time_casa}** – IMA: {ima_casa:.1f}, OVRall: {ovrall_val_casa:.1f}, IC: {ic_val_casa:.1f}, MPV: {mpv_casa:.1f}")
            st.write(f"**{time_fora}** – IMA: {ima_fora:.1f}, OVRall: {ovrall_val_fora:.1f}, IC: {ic_val_fora:.1f}, MPV: {mpv_fora:.1f}")
