# manual_app.py — MyPredict 2.0 (inicialização completa de estado)
import streamlit as st
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

def show():
    st.title("MyPredict 2.0 – Modo Manual")
    st.markdown("Preencha **todos** os campos abaixo. Só clique em **Calcular** quando os dados estiverem completos.")

    # Inicialização OBRIGATÓRIA de todas as chaves usadas
    defaults = {
        'dados_processados': False,
        'jogos_casa': [],
        'jogos_fora': [],
        'ovrall_casa': {},
        'ovrall_fora': {},
        'ic_casa': {},
        'ic_fora': {},
        'time_casa': "Flamengo",
        'time_fora': "Palmeiras",
        'pos_casa': 1,
        'pos_fora': 2,
        'prateleiras_extra': {},
        'media_gols_casa': MEDIA_GOLS_CASA_LIGA,
        'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
        'media_ht_casa': 0.75,
        'media_ht_fora': 0.65,
        'media_esc_casa': 5.0,
        'media_esc_fora': 4.5,
    }
    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

    entrada = st.radio("Modo de entrada", ["Preenchimento Manual", "Colar resposta da IA"])

    # ---------- MODO COLAR RESPOSTA DA IA ----------
    if entrada == "Colar resposta da IA":
        st.subheader("📥 Cole aqui a resposta completa da IA")
        texto = st.text_area("Resposta da IA", height=300)
        if st.button("Processar dados"):
            linhas = texto.strip().split('\n')
            secao = None
            jogos_temp_casa = []
            jogos_temp_fora = []
            ovrall_casa = {}
            ovrall_fora = {}
            ic_casa = {}
            ic_fora = {}
            pos_casa = 1
            pos_fora = 2
            time_casa = "Flamengo"
            time_fora = "Palmeiras"
            prateleiras_extra = {}
            media_gols_casa = MEDIA_GOLS_CASA_LIGA
            media_gols_fora = MEDIA_GOLS_FORA_LIGA
            media_ht_casa = 0.75
            media_ht_fora = 0.65
            media_esc_casa = 5.0
            media_esc_fora = 4.5

            for linha in linhas:
                linha = linha.strip()
                if not linha:
                    continue
                if linha.startswith("Time da casa:"):
                    time_casa = linha.split(":", 1)[1].strip()
                elif linha.startswith("Time da fora:"):
                    time_fora = linha.split(":", 1)[1].strip()
                elif linha.startswith("1. Posições"):
                    secao = "posicoes"
                    continue
                elif linha.startswith("2. Últimos 10 jogos do time da casa"):
                    secao = "jogos_casa"
                    continue
                elif linha.startswith("3. Últimos 10 jogos do time da fora"):
                    secao = "jogos_fora"
                    continue
                elif linha.startswith("4. Métricas OVRall do time da casa"):
                    secao = "ovrall_casa"
                    continue
                elif linha.startswith("5. Métricas OVRall do time da fora"):
                    secao = "ovrall_fora"
                    continue
                elif linha.startswith("6. Métricas IC do time da casa"):
                    secao = "ic_casa"
                    continue
                elif linha.startswith("7. Métricas IC do time da fora"):
                    secao = "ic_fora"
                    continue
                elif linha.startswith("8. Médias da Liga"):
                    secao = "medias_liga"
                    continue
                elif linha.startswith("9. Prateleiras"):
                    secao = "prateleiras"
                    continue

                if secao == "posicoes":
                    if linha.startswith("Casa:"):
                        try: pos_casa = int(linha.split(":")[1].strip())
                        except: pass
                    elif linha.startswith("Fora:"):
                        try: pos_fora = int(linha.split(":")[1].strip())
                        except: pass
                elif secao == "jogos_casa":
                    partes = [p.strip() for p in linha.split(',')]
                    if len(partes) >= 3:
                        res = partes[0]
                        adv = partes[1]
                        mand = partes[2].upper() == 'S'
                        jogos_temp_casa.append({"resultado": res, "adversario": adv, "mandante": mand})
                elif secao == "jogos_fora":
                    partes = [p.strip() for p in linha.split(',')]
                    if len(partes) >= 3:
                        res = partes[0]
                        adv = partes[1]
                        mand = partes[2].upper() == 'S'
                        jogos_temp_fora.append({"resultado": res, "adversario": adv, "mandante": mand})
                elif secao == "ovrall_casa":
                    partes = [x.strip() for x in linha.split(',')]
                    if len(partes) == 23:
                        for i, key in enumerate([
                            "gols_media", "gols_sofridos_media", "xg_media", "xga_media",
                            "finalizacoes_alvo_media", "finalizacoes_alvo_sofridas_media",
                            "chutes_media", "desarmes_intercep_media", "posse_media",
                            "passes_certos_pct", "passes_chave_media", "assistencias_media",
                            "conversao", "clean_sheets_pct", "desvio_pontos", "desvio_gols_pro",
                            "desvio_gols_sofridos", "pontos_pos_desvantagem_media",
                            "gols_ultimos_15min_media", "pontos_apos_derrota_media",
                            "diff_aprov_casa_fora", "aprov_viradas_favor", "aprov_viradas_contra"
                        ]):
                            ovrall_casa[key] = para_float(partes[i])
                elif secao == "ovrall_fora":
                    partes = [x.strip() for x in linha.split(',')]
                    if len(partes) == 23:
                        for i, key in enumerate([
                            "gols_media", "gols_sofridos_media", "xg_media", "xga_media",
                            "finalizacoes_alvo_media", "finalizacoes_alvo_sofridas_media",
                            "chutes_media", "desarmes_intercep_media", "posse_media",
                            "passes_certos_pct", "passes_chave_media", "assistencias_media",
                            "conversao", "clean_sheets_pct", "desvio_pontos", "desvio_gols_pro",
                            "desvio_gols_sofridos", "pontos_pos_desvantagem_media",
                            "gols_ultimos_15min_media", "pontos_apos_derrota_media",
                            "diff_aprov_casa_fora", "aprov_viradas_favor", "aprov_viradas_contra"
                        ]):
                            ovrall_fora[key] = para_float(partes[i])
                elif secao == "ic_casa":
                    partes = [x.strip() for x in linha.split(',')]
                    if len(partes) == 5:
                        for i, key in enumerate(["confronto_direto", "mesmo_escalao", "contra_escalao_adversario", "fator_casa", "odds"]):
                            ic_casa[key] = para_float(partes[i])
                elif secao == "ic_fora":
                    partes = [x.strip() for x in linha.split(',')]
                    if len(partes) == 5:
                        for i, key in enumerate(["confronto_direto", "mesmo_escalao", "contra_escalao_adversario", "fator_casa", "odds"]):
                            ic_fora[key] = para_float(partes[i])
                elif secao == "medias_liga":
                    if linha.startswith("Média gols casa:"):
                        media_gols_casa = para_float(linha.split(":", 1)[1])
                    elif linha.startswith("Média gols fora:"):
                        media_gols_fora = para_float(linha.split(":", 1)[1])
                    elif linha.startswith("Média gols 1º tempo casa:"):
                        media_ht_casa = para_float(linha.split(":", 1)[1])
                    elif linha.startswith("Média gols 1º tempo fora:"):
                        media_ht_fora = para_float(linha.split(":", 1)[1])
                    elif linha.startswith("Média escanteios casa:"):
                        media_esc_casa = para_float(linha.split(":", 1)[1])
                    elif linha.startswith("Média escanteios fora:"):
                        media_esc_fora = para_float(linha.split(":", 1)[1])
                elif secao == "prateleiras":
                    if ':' in linha:
                        adv, prat = linha.split(':', 1)
                        prateleiras_extra[adv.strip()] = prat.strip()

            st.session_state.jogos_casa = jogos_temp_casa
            st.session_state.jogos_fora = jogos_temp_fora
            st.session_state.ovrall_casa = ovrall_casa
            st.session_state.ovrall_fora = ovrall_fora
            st.session_state.ic_casa = ic_casa
            st.session_state.ic_fora = ic_fora
            st.session_state.time_casa = time_casa
            st.session_state.time_fora = time_fora
            st.session_state.pos_casa = pos_casa
            st.session_state.pos_fora = pos_fora
            st.session_state.prateleiras_extra = prateleiras_extra
            st.session_state.media_gols_casa = media_gols_casa
            st.session_state.media_gols_fora = media_gols_fora
            st.session_state.media_ht_casa = media_ht_casa
            st.session_state.media_ht_fora = media_ht_fora
            st.session_state.media_esc_casa = media_esc_casa
            st.session_state.media_esc_fora = media_esc_fora
            st.session_state.dados_processados = True
            st.success("Dados processados!")
            st.rerun()

        if st.session_state.dados_processados:
            time_casa = st.session_state.time_casa
            time_fora = st.session_state.time_fora
            pos_casa = st.session_state.pos_casa
            pos_fora = st.session_state.pos_fora
            jogos_casa = st.session_state.jogos_casa
            jogos_fora = st.session_state.jogos_fora
            ovrall_casa = st.session_state.ovrall_casa
            ovrall_fora = st.session_state.ovrall_fora
            ic_casa = st.session_state.ic_casa
            ic_fora = st.session_state.ic_fora
            media_gols_casa = st.session_state.media_gols_casa
            media_gols_fora = st.session_state.media_gols_fora
            media_ht_casa = st.session_state.media_ht_casa
            media_ht_fora = st.session_state.media_ht_fora
            media_esc_casa = st.session_state.media_esc_casa
            media_esc_fora = st.session_state.media_esc_fora
    else:
        # ---------- MODO MANUAL ----------
        c1, c2 = st.columns(2)
        time_casa = c1.text_input("Time da Casa", "Flamengo")
        time_fora = c2.text_input("Time da Fora", "Palmeiras")

        st.subheader("🏷 Projeção de Prateleiras")
        pos_casa = st.number_input("Posição do time da casa", 1, 20, 1)
        pos_fora = st.number_input("Posição do time da fora", 1, 20, 2)

        st.subheader("📊 IMA – Últimos 10 jogos")
        col_j1, col_j2 = st.columns(2)
        with col_j1:
            txt_casa = st.text_area("Time da casa", height=200, key="jogos_casa_manual")
        with col_j2:
            txt_fora = st.text_area("Time da fora", height=200, key="jogos_fora_manual")

        def parse_jogos(texto):
            jogos = []
            for linha in texto.strip().split('\n'):
                partes = [p.strip() for p in linha.split(',')]
                if len(partes) >= 3:
                    res = partes[0]
                    adv = partes[1]
                    mand = partes[2].upper() == 'S'
                    jogos.append({"resultado": res, "adversario": adv, "mandante": mand})
            return jogos

        jogos_casa = parse_jogos(txt_casa)
        jogos_fora = parse_jogos(txt_fora)

        st.subheader("📈 OVRall – Métricas da Temporada")
        def metrica(label, key_casa, key_fora):
            c1, c2 = st.columns(2)
            vc = para_float(c1.text_input(label, key=f"{key_casa}_val"))
            vf = para_float(c2.text_input(label, key=f"{key_fora}_val"))
            return vc, vf

        ovrall_casa = {}
        ovrall_fora = {}
        for label, key in [
            ("Gols marcados (média)", "gols_media"),
            ("Gols sofridos (média)", "gols_sofridos_media"),
            ("xG (média)", "xg_media"),
            ("xGA (média)", "xga_media"),
            ("Finalizações no alvo (média)", "finalizacoes_alvo_media"),
            ("Finalizações no alvo sofridas (média)", "finalizacoes_alvo_sofridas_media"),
            ("Chutes totais (média)", "chutes_media"),
            ("Desarmes + Interceptações (média)", "desarmes_intercep_media"),
            ("Posse de bola (%)", "posse_media"),
            ("Passes certos (%)", "passes_certos_pct"),
            ("Passes-chave (média)", "passes_chave_media"),
            ("Assistências (média)", "assistencias_media"),
            ("Conversão de finalizações (%)", "conversao"),
            ("Jogos sem sofrer gols (%)", "clean_sheets_pct"),
            ("Desvio padrão dos pontos", "desvio_pontos"),
            ("Desvio padrão gols marcados", "desvio_gols_pro"),
            ("Desvio padrão gols sofridos", "desvio_gols_sofridos"),
            ("Pontos após sair atrás (média)", "pontos_pos_desvantagem_media"),
            ("Gols nos últimos 15 min (média)", "gols_ultimos_15min_media"),
            ("Pontos após derrota (média)", "pontos_apos_derrota_media"),
            ("Diferença aprovação casa-fora (%)", "diff_aprov_casa_fora"),
            ("Aproveitamento viradas a favor (%)", "aprov_viradas_favor"),
            ("Aproveitamento viradas contra (%)", "aprov_viradas_contra"),
        ]:
            vc, vf = metrica(label, f"casa_{key}", f"fora_{key}")
            ovrall_casa[key] = vc
            ovrall_fora[key] = vf

        st.subheader("🧠 IC – Fatores Contextuais")
        ic_casa = {}
        ic_fora = {}
        for label, key in [
            ("Confronto direto (%)", "confronto_direto"),
            ("Mesmo escalão (%)", "mesmo_escalao"),
            ("Contra escalão adversário (%)", "contra_escalao_adversario"),
            ("Fator casa (%)", "fator_casa"),
            ("Odd", "odds"),
        ]:
            vc, vf = metrica(label, f"ic_casa_{key}", f"ic_fora_{key}")
            ic_casa[key] = vc
            ic_fora[key] = vf

        st.subheader("📊 Médias da Liga")
        c1, c2 = st.columns(2)
        with c1:
            media_gols_casa = st.number_input("Média gols casa", value=MEDIA_GOLS_CASA_LIGA)
            media_ht_casa = st.number_input("Média gols HT casa", value=0.75)
            media_esc_casa = st.number_input("Média escanteios casa", value=5.0)
        with c2:
            media_gols_fora = st.number_input("Média gols fora", value=MEDIA_GOLS_FORA_LIGA)
            media_ht_fora = st.number_input("Média gols HT fora", value=0.65)
            media_esc_fora = st.number_input("Média escanteios fora", value=4.5)

    # ---------- CÁLCULO ----------
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
        for adv, prat in st.session_state.prateleiras_extra.items():
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
