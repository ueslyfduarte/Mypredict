# ui_manual.py — MyPredict 2.0 (interface manual separada)
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

# CSS para setas e selos
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
    # Inicializa todas as variáveis que serão usadas
    if 'time_casa' not in st.session_state: st.session_state.time_casa = "Flamengo"
    if 'time_fora' not in st.session_state: st.session_state.time_fora = "Palmeiras"
    if 'pos_casa' not in st.session_state: st.session_state.pos_casa = 1
    if 'pos_fora' not in st.session_state: st.session_state.pos_fora = 2
    if 'jogos_casa' not in st.session_state: st.session_state.jogos_casa = []
    if 'jogos_fora' not in st.session_state: st.session_state.jogos_fora = []
    if 'ovrall_casa' not in st.session_state: st.session_state.ovrall_casa = {}
    if 'ovrall_fora' not in st.session_state: st.session_state.ovrall_fora = {}
    if 'ic_casa' not in st.session_state: st.session_state.ic_casa = {}
    if 'ic_fora' not in st.session_state: st.session_state.ic_fora = {}
    if 'media_gols_casa' not in st.session_state: st.session_state.media_gols_casa = MEDIA_GOLS_CASA_LIGA
    if 'media_gols_fora' not in st.session_state: st.session_state.media_gols_fora = MEDIA_GOLS_FORA_LIGA
    if 'media_ht_casa' not in st.session_state: st.session_state.media_ht_casa = 0.75
    if 'media_ht_fora' not in st.session_state: st.session_state.media_ht_fora = 0.65
    if 'media_esc_casa' not in st.session_state: st.session_state.media_esc_casa = 5.0
    if 'media_esc_fora' not in st.session_state: st.session_state.media_esc_fora = 4.5
    if 'prateleiras_extra' not in st.session_state: st.session_state.prateleiras_extra = {}

    st.title("MyPredict 2.0 – Modo Manual")
    entrada = st.radio("Método de entrada", ["Preenchimento Manual", "Colar resposta da IA"])

    if entrada == "Colar resposta da IA":
        st.subheader("📥 Cole aqui a resposta completa da IA")
        texto = st.text_area("Resposta da IA", height=300, key="ia_text")
        if st.button("Processar dados"):
            if texto.strip():
                # Divide em blocos por linha em branco
                blocos = texto.strip().split('\n\n')
                for bloco in blocos:
                    linhas = bloco.strip().split('\n')
                    if not linhas: continue
                    primeira = linhas[0].strip()
                    if primeira.startswith('Time da casa:'):
                        st.session_state.time_casa = primeira.split(':',1)[1].strip()
                    elif primeira.startswith('Time da fora:'):
                        st.session_state.time_fora = primeira.split(':',1)[1].strip()
                    elif primeira.startswith('1. Posições:'):
                        for l in linhas[1:]:
                            if l.startswith('Casa:'):
                                try: st.session_state.pos_casa = int(l.split(':')[1].strip())
                                except: pass
                            elif l.startswith('Fora:'):
                                try: st.session_state.pos_fora = int(l.split(':')[1].strip())
                                except: pass
                    elif primeira.startswith('2. Últimos 10 jogos do time da casa:'):
                        jogos = []
                        for l in linhas[1:]:
                            partes = [p.strip() for p in l.split(',')]
                            if len(partes) == 3:
                                jogos.append({"resultado": partes[0], "adversario": partes[1], "mandante": partes[2].upper() == 'S'})
                        st.session_state.jogos_casa = jogos
                    elif primeira.startswith('3. Últimos 10 jogos do time da fora:'):
                        jogos = []
                        for l in linhas[1:]:
                            partes = [p.strip() for p in l.split(',')]
                            if len(partes) == 3:
                                jogos.append({"resultado": partes[0], "adversario": partes[1], "mandante": partes[2].upper() == 'S'})
                        st.session_state.jogos_fora = jogos
                    elif primeira.startswith('4. Métricas OVRall do time da casa'):
                        chaves = ["gols_media","gols_sofridos_media","xg_media","xga_media",
                                  "finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media",
                                  "chutes_media","desarmes_intercep_media","posse_media",
                                  "passes_certos_pct","passes_chave_media","assistencias_media",
                                  "conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro",
                                  "desvio_gols_sofridos","pontos_pos_desvantagem_media",
                                  "gols_ultimos_15min_media","pontos_apos_derrota_media",
                                  "diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
                        vals = [para_float(x) for x in linhas[-1].split(',')]
                        st.session_state.ovrall_casa = {chaves[i]: vals[i] for i in range(len(chaves)) if i < len(vals)}
                    elif primeira.startswith('5. Métricas OVRall do time da fora'):
                        chaves = ["gols_media","gols_sofridos_media","xg_media","xga_media",
                                  "finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media",
                                  "chutes_media","desarmes_intercep_media","posse_media",
                                  "passes_certos_pct","passes_chave_media","assistencias_media",
                                  "conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro",
                                  "desvio_gols_sofridos","pontos_pos_desvantagem_media",
                                  "gols_ultimos_15min_media","pontos_apos_derrota_media",
                                  "diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
                        vals = [para_float(x) for x in linhas[-1].split(',')]
                        st.session_state.ovrall_fora = {chaves[i]: vals[i] for i in range(len(chaves)) if i < len(vals)}
                    elif primeira.startswith('6. Métricas IC do time da casa'):
                        chaves = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
                        vals = [para_float(x) for x in linhas[-1].split(',')]
                        st.session_state.ic_casa = {chaves[i]: vals[i] for i in range(len(chaves)) if i < len(vals)}
                    elif primeira.startswith('7. Métricas IC do time da fora'):
                        chaves = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
                        vals = [para_float(x) for x in linhas[-1].split(',')]
                        st.session_state.ic_fora = {chaves[i]: vals[i] for i in range(len(chaves)) if i < len(vals)}
                    elif primeira.startswith('8. Médias da Liga:'):
                        for l in linhas[1:]:
                            if 'casa:' in l: st.session_state.media_gols_casa = para_float(l.split(':')[1])
                            elif 'fora:' in l: st.session_state.media_gols_fora = para_float(l.split(':')[1])
                            elif '1º tempo casa:' in l: st.session_state.media_ht_casa = para_float(l.split(':')[1])
                            elif '1º tempo fora:' in l: st.session_state.media_ht_fora = para_float(l.split(':')[1])
                            elif 'escanteios casa:' in l: st.session_state.media_esc_casa = para_float(l.split(':')[1])
                            elif 'escanteios fora:' in l: st.session_state.media_esc_fora = para_float(l.split(':')[1])
                    elif primeira.startswith('9. Prateleiras'):
                        prat = {}
                        for l in linhas[1:]:
                            if ':' in l:
                                adv, prat_val = l.split(':',1)
                                prat[adv.strip()] = prat_val.strip()
                        st.session_state.prateleiras_extra = prat
                st.success("Dados processados!")
                st.rerun()
            else:
                st.error("Por favor, cole a resposta da IA.")

        # Exibe os dados carregados
        st.success("Dados carregados. Clique em Calcular para ver os resultados.")
    else:
        # MODO MANUAL
        c1, c2 = st.columns(2)
        with c1: st.session_state.time_casa = st.text_input("Time da Casa", value=st.session_state.time_casa)
        with c2: st.session_state.time_fora = st.text_input("Time da Fora", value=st.session_state.time_fora)

        st.subheader("🏷 Projeção de Prateleiras")
        st.session_state.pos_casa = st.number_input("Posição do time da casa", 1, 20, st.session_state.pos_casa)
        st.session_state.pos_fora = st.number_input("Posição do time da fora", 1, 20, st.session_state.pos_fora)

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
                if len(partes) == 3 and partes[0] in ('V','E','D') and partes[2].upper() in ('S','N'):
                    jogos.append({"resultado": partes[0], "adversario": partes[1], "mandante": partes[2].upper() == 'S'})
            return jogos

        st.session_state.jogos_casa = parse_jogos(txt_casa)
        st.session_state.jogos_fora = parse_jogos(txt_fora)

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
        st.session_state.ovrall_casa = ovrall_casa
        st.session_state.ovrall_fora = ovrall_fora

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
        st.session_state.ic_casa = ic_casa
        st.session_state.ic_fora = ic_fora

        st.subheader("📊 Médias da Liga")
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.media_gols_casa = st.number_input("Média gols casa", value=st.session_state.media_gols_casa)
            st.session_state.media_ht_casa = st.number_input("Média gols HT casa", value=st.session_state.media_ht_casa)
            st.session_state.media_esc_casa = st.number_input("Média escanteios casa", value=st.session_state.media_esc_casa)
        with c2:
            st.session_state.media_gols_fora = st.number_input("Média gols fora", value=st.session_state.media_gols_fora)
            st.session_state.media_ht_fora = st.number_input("Média gols HT fora", value=st.session_state.media_ht_fora)
            st.session_state.media_esc_fora = st.number_input("Média escanteios fora", value=st.session_state.media_esc_fora)

    # ---------- CÁLCULO (comum a ambos os modos) ----------
    if st.button("Calcular MyPredict Manual"):
        if len(st.session_state.jogos_casa) < 10 or len(st.session_state.jogos_fora) < 10:
            st.error(f"Foram encontrados {len(st.session_state.jogos_casa)} jogos para o time da casa e {len(st.session_state.jogos_fora)} para o time da fora. São necessários 10 de cada.")
            st.stop()
        if not st.session_state.ovrall_casa or not st.session_state.ovrall_fora:
            st.error("Métricas OVRall não encontradas.")
            st.stop()

        # Prateleiras
        prat_casa = obter_prateleira(st.session_state.pos_casa)
        prat_fora = obter_prateleira(st.session_state.pos_fora)
        prateleiras = {st.session_state.time_casa: prat_casa, st.session_state.time_fora: prat_fora}
        for j in st.session_state.jogos_casa + st.session_state.jogos_fora:
            if j['adversario'] not in prateleiras:
                prateleiras[j['adversario']] = "Media"
        for adv, prat in st.session_state.prateleiras_extra.items():
            if adv in prateleiras:
                prateleiras[adv] = prat

        # IMA
        rec_casa = {
            '10G': st.session_state.jogos_casa[:10], '5G': st.session_state.jogos_casa[:5], '3G': st.session_state.jogos_casa[:3],
            '5CF': [j for j in st.session_state.jogos_casa if j['mandante']][:5],
            '3CF': [j for j in st.session_state.jogos_casa if j['mandante']][:3],
        }
        rec_fora = {
            '10G': st.session_state.jogos_fora[:10], '5G': st.session_state.jogos_fora[:5], '3G': st.session_state.jogos_fora[:3],
            '5CF': [j for j in st.session_state.jogos_fora if j['mandante']][:5],
            '3CF': [j for j in st.session_state.jogos_fora if j['mandante']][:3],
        }

        ima_casa = calcular_ima(st.session_state.time_casa,
                                rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                                rec_casa['5CF'], rec_casa['3CF'], prateleiras)
        ima_fora = calcular_ima(st.session_state.time_fora,
                                rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                                rec_fora['5CF'], rec_fora['3CF'], prateleiras)

        # OVRall
        dados_liga = {k: [st.session_state.ovrall_casa.get(k, 0) or 0, st.session_state.ovrall_fora.get(k, 0) or 0] for k in set(st.session_state.ovrall_casa) | set(st.session_state.ovrall_fora)}
        ovrall_val_casa = calcular_ovrall(st.session_state.ovrall_casa, dados_liga)
        ovrall_val_fora = calcular_ovrall(st.session_state.ovrall_fora, dados_liga)

        # IC
        ic_val_casa = calcular_ic(st.session_state.ic_casa)
        ic_val_fora = calcular_ic(st.session_state.ic_fora)

        # MPV
        mpv_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
        mpv_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

        bonus_casa = calcular_bonus_casa(st.session_state.ovrall_casa.get('diff_aprov_casa_fora') or 0)
        p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

        over25 = prob_over_2_5(
            st.session_state.ovrall_casa.get('gols_media'), st.session_state.ovrall_fora.get('gols_media'),
            st.session_state.ovrall_casa.get('gols_sofridos_media'), st.session_state.ovrall_fora.get('gols_sofridos_media'),
            media_casa=st.session_state.media_gols_casa, media_fora=st.session_state.media_gols_fora
        )

        gols_esp_casa = _gols_esperados(st.session_state.ovrall_casa.get('gols_media'),
                                        st.session_state.ovrall_fora.get('gols_sofridos_media'),
                                        st.session_state.media_gols_casa)
        gols_esp_fora = _gols_esperados(st.session_state.ovrall_fora.get('gols_media'),
                                        st.session_state.ovrall_casa.get('gols_sofridos_media'),
                                        st.session_state.media_gols_fora)
        btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)

        gol_ht = prob_gol_ht(
            st.session_state.ovrall_casa.get('gols_ht_media', 0.5) or 0.5,
            st.session_state.ovrall_fora.get('gols_ht_media', 0.5) or 0.5,
            st.session_state.ovrall_casa.get('gols_ht_sofridos_media', 0.5) or 0.5,
            st.session_state.ovrall_fora.get('gols_ht_sofridos_media', 0.5) or 0.5,
            media_ht_casa=st.session_state.media_ht_casa, media_ht_fora=st.session_state.media_ht_fora
        )

        esc = prob_over_escanteios(
            st.session_state.ovrall_casa.get('escanteios_media', 5.0) or 5.0,
            st.session_state.ovrall_fora.get('escanteios_media', 5.0) or 5.0,
            st.session_state.ovrall_casa.get('escanteios_sofridos_media', 5.0) or 5.0,
            st.session_state.ovrall_fora.get('escanteios_sofridos_media', 5.0) or 5.0,
            media_casa=st.session_state.media_esc_casa, media_fora=st.session_state.media_esc_fora
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
            st.write(f"**{st.session_state.time_casa}** – IMA: {ima_casa:.1f}, OVRall: {ovrall_val_casa:.1f}, IC: {ic_val_casa:.1f}, MPV: {mpv_casa:.1f}")
            st.write(f"**{st.session_state.time_fora}** – IMA: {ima_fora:.1f}, OVRall: {ovrall_val_fora:.1f}, IC: {ic_val_fora:.1f}, MPV: {mpv_fora:.1f}")
