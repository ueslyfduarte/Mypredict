# =========================================================================
# ABA BACKTESTING OFFLINE – CORRIGIDA COM LIMPEZA DE STRINGS
# =========================================================================
elif aba == "📊 Backtesting Offline":
    st.header("📊 Backtesting Walk‑Forward – Leitura Robusta de CSV (com limpeza)")
    st.caption("Cole todo o conteúdo do CSV. O sistema detecta o separador e limpa os nomes dos times automaticamente.")

    texto_dados = st.text_area("Cole os dados da temporada", height=250,
                               placeholder="Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,...")

    if st.button("▶️ Iniciar Simulação Completa"):
        if not texto_dados.strip():
            st.error("Insira os dados dos jogos.")
        else:
            try:
                # Auto-detecção de separador (vírgula, tab, etc.)
                df = pd.read_csv(io.StringIO(texto_dados), sep=None, engine='python')
                df.columns = [c.strip().lower().replace('"', '') for c in df.columns]

                obrigatorias = ['hometeam', 'awayteam', 'fthg', 'ftag']
                if any(c not in df.columns for c in obrigatorias):
                    st.error(f"Colunas obrigatórias não encontradas. Disponíveis: {list(df.columns)}")
                else:
                    # Limpeza dos nomes dos times (remove aspas e espaços)
                    df['hometeam'] = df['hometeam'].astype(str).str.strip().str.replace('"', '')
                    df['awayteam'] = df['awayteam'].astype(str).str.strip().str.replace('"', '')
                    st.success(f"CSV lido! {len(df)} jogos encontrados.")
                    st.write("**Exemplos de nomes limpos:**", df['hometeam'].head(3).tolist())

                    # Estruturas da simulação
                    times_stats = {}
                    resultados = []
                    progresso = st.progress(0)
                    total_jogos = len(df)

                    # Contadores de desempenho
                    st.session_state.acertos_por_mercado = {merc: 0 for merc in ['1X2', 'Gol HT', 'Over 1.5 FT', 'Over 2.5 FT', 'Ambas Marcam', 'Over 1.5 HT', 'Escanteios (média)']}
                    st.session_state.total_por_mercado = {merc: 0 for merc in st.session_state.acertos_por_mercado}
                    st.session_state.lucro_por_mercado = {merc: 0.0 for merc in st.session_state.acertos_por_mercado}

                    for idx, row in df.iterrows():
                        mandante = row['hometeam']
                        visitante = row['awayteam']
                        gols_m = int(row['fthg'])
                        gols_v = int(row['ftag'])

                        # Colunas opcionais
                        gols_ht_m = int(row['hthg']) if 'hthg' in df.columns and not pd.isna(row['hthg']) else None
                        gols_ht_v = int(row['htag']) if 'htag' in df.columns and not pd.isna(row['htag']) else None
                        chutes_m = float(row['hs']) if 'hs' in df.columns and not pd.isna(row['hs']) else None
                        chutes_v = float(row['as']) if 'as' in df.columns and not pd.isna(row['as']) else None
                        chutes_gol_m = float(row['hst']) if 'hst' in df.columns and not pd.isna(row['hst']) else None
                        chutes_gol_v = float(row['ast']) if 'ast' in df.columns and not pd.isna(row['ast']) else None
                        escanteios_m = float(row['hc']) if 'hc' in df.columns and not pd.isna(row['hc']) else None
                        escanteios_v = float(row['ac']) if 'ac' in df.columns and not pd.isna(row['ac']) else None

                        # Funções get_stats / update_stats (idênticas)
                        def get_stats(time_name):
                            if time_name not in times_stats:
                                return {
                                    'gols': 1.4, 'gols_sofridos': 1.2,
                                    'gols_ht': 0.6, 'gols_sofridos_ht': 0.5,
                                    'chutes': 12.0, 'chutes_sofridos': 12.0,
                                    'chutes_gol': 4.5, 'chutes_gol_sofridos': 4.5,
                                    'escanteios': 5.0, 'escanteios_sofridos': 5.0,
                                    'jogos': 0,
                                    'hist_gols': [], 'hist_gols_sofridos': [],
                                    'hist_gols_ht': [], 'hist_gols_sofridos_ht': [],
                                    'hist_chutes': [], 'hist_chutes_sofridos': [],
                                    'hist_chutes_gol': [], 'hist_chutes_gol_sofridos': [],
                                    'hist_escanteios': [], 'hist_escanteios_sofridos': [],
                                    'hist_ambas': [], 'hist_over25': [], 'hist_over15': [],
                                    'hist_over15_ht': [], 'hist_gol_ht': []
                                }
                            return times_stats[time_name]

                        stats_a = get_stats(mandante)
                        stats_b = get_stats(visitante)

                        # Cálculo do Overall simplificado (apenas gols)
                        est_a = {'gols': stats_a['gols'], 'gols_sofridos': stats_b['gols']}
                        est_b = {'gols': stats_b['gols'], 'gols_sofridos': stats_a['gols']}
                        medias_liga = {'gols': 1.4, 'gols_sofridos': 1.2}
                        def calc_overall(est):
                            fvo = normalizar_por_media(est['gols'], medias_liga['gols'])
                            frd = normalizar_por_media(est['gols_sofridos'], medias_liga['gols_sofridos'], inverter=True)
                            return (fvo * 0.5) + (frd * 0.5)
                        ovr_a = calc_overall(est_a)
                        ovr_b = calc_overall(est_b)
                        im_a, _, _, _, _ = calcular_im(50, 50, 50, 50, 50, 0, 50)
                        im_b, _, _, _, _ = calcular_im(50, 50, 50, 50, 50, 0, 50)
                        irc_a, _, _, _, _, _, _, _, _ = calcular_irc(20, 50, "Média", 0, 0, 0, 0, 0, 0)
                        irc_b, _, _, _, _, _, _, _, _ = calcular_irc(20, 50, "Média", 0, 0, 0, 0, 0, 0)
                        imp_a = calcular_imp(ovr_a, im_a, irc_a)
                        imp_b = calcular_imp(ovr_b, im_b, irc_b)
                        prob_1x2 = calcular_probabilidades(imp_a, imp_b)

                        # Mercados (frequência)
                        def prob_mercado(lista_a, lista_b):
                            if not lista_a or not lista_b: return None
                            return (sum(lista_a)/len(lista_a) + sum(lista_b)/len(lista_b)) / 2.0

                        mercados = {}
                        if stats_a['hist_gol_ht'] and stats_b['hist_gol_ht']:
                            mercados['Gol HT'] = prob_mercado(stats_a['hist_gol_ht'], stats_b['hist_gol_ht'])
                        if stats_a['hist_over15'] and stats_b['hist_over15']:
                            mercados['Over 1.5 FT'] = prob_mercado(stats_a['hist_over15'], stats_b['hist_over15'])
                        if stats_a['hist_over25'] and stats_b['hist_over25']:
                            mercados['Over 2.5 FT'] = prob_mercado(stats_a['hist_over25'], stats_b['hist_over25'])
                        if stats_a['hist_ambas'] and stats_b['hist_ambas']:
                            mercados['Ambas Marcam'] = prob_mercado(stats_a['hist_ambas'], stats_b['hist_ambas'])
                        if stats_a['hist_over15_ht'] and stats_b['hist_over15_ht']:
                            mercados['Over 1.5 HT'] = prob_mercado(stats_a['hist_over15_ht'], stats_b['hist_over15_ht'])
                        if stats_a['hist_escanteios'] and stats_b['hist_escanteios']:
                            media_esc_a = np.mean(stats_a['hist_escanteios']) if stats_a['hist_escanteios'] else 0
                            media_esc_b = np.mean(stats_b['hist_escanteios']) if stats_b['hist_escanteios'] else 0
                            mercados['Escanteios (média)'] = (media_esc_a + media_esc_b) / 2.0

                        # Resultados reais
                        real_1x2 = "Vitória Mandante" if gols_m > gols_v else ("Vitória Visitante" if gols_m < gols_v else "Empate")
                        real_gol_ht = (gols_ht_m + gols_ht_v) > 0 if (gols_ht_m is not None and gols_ht_v is not None) else None
                        real_over15_ft = (gols_m + gols_v) > 1
                        real_over25_ft = (gols_m + gols_v) > 2
                        real_ambas = (gols_m > 0 and gols_v > 0)
                        real_over15_ht = (gols_ht_m + gols_ht_v) > 1 if (gols_ht_m is not None and gols_ht_v is not None) else None
                        real_escanteios = (escanteios_m + escanteios_v) if (escanteios_m is not None and escanteios_v is not None) else None

                        previsao_1x2 = "Vitória Mandante" if prob_1x2[0] > prob_1x2[1] and prob_1x2[0] > prob_1x2[2] else ("Vitória Visitante" if prob_1x2[1] > prob_1x2[0] and prob_1x2[1] > prob_1x2[2] else "Empate")
                        acerto_1x2 = "Sim" if previsao_1x2 == real_1x2 else "Não"

                        resultados.append({
                            'Jogo': f"{mandante} vs {visitante}",
                            'Placar': f"{gols_m}x{gols_v}",
                            'Prob 1X2': f"{prob_1x2[0]:.1f}%/{prob_1x2[2]:.1f}%/{prob_1x2[1]:.1f}%",
                            'Previsão 1X2': previsao_1x2,
                            'Real 1X2': real_1x2,
                            'Acerto 1X2': acerto_1x2
                        })

                        # Atualiza contadores
                        st.session_state.total_por_mercado['1X2'] += 1
                        if acerto_1x2 == "Sim":
                            st.session_state.acertos_por_mercado['1X2'] += 1
                            st.session_state.lucro_por_mercado['1X2'] += (1.0 / (prob_1x2[0]/100) - 1) if previsao_1x2 == "Vitória Mandante" else ((1.0 / (prob_1x2[1]/100) - 1) if previsao_1x2 == "Vitória Visitante" else (1.0 / (prob_1x2[2]/100) - 1))
                        else:
                            st.session_state.lucro_por_mercado['1X2'] -= 1

                        for nome, prob in mercados.items():
                            if prob is None: continue
                            st.session_state.total_por_mercado[nome] += 1
                            if nome == 'Escanteios (média)':
                                if real_escanteios and abs(prob - real_escanteios) <= 1.5:
                                    st.session_state.acertos_por_mercado[nome] += 1
                                    st.session_state.lucro_por_mercado[nome] += 0.8
                                else:
                                    st.session_state.lucro_por_mercado[nome] -= 1
                            else:
                                if (nome == 'Gol HT' and real_gol_ht == (prob > 0.5)) or \
                                   (nome == 'Over 1.5 FT' and real_over15_ft == (prob > 0.5)) or \
                                   (nome == 'Over 2.5 FT' and real_over25_ft == (prob > 0.5)) or \
                                   (nome == 'Ambas Marcam' and real_ambas == (prob > 0.5)) or \
                                   (nome == 'Over 1.5 HT' and real_over15_ht == (prob > 0.5)):
                                    st.session_state.acertos_por_mercado[nome] += 1
                                    st.session_state.lucro_por_mercado[nome] += (1.0 / max(prob, 0.01)) - 1
                                else:
                                    st.session_state.lucro_por_mercado[nome] -= 1

                        # Atualiza históricos
                        def update_stats(time, gf, gc, gf_ht=None, gc_ht=None, chutes=None, chutes_sof=None,
                                         chutes_gol=None, chutes_gol_sof=None, escanteios=None, escanteios_sof=None):
                            if time not in times_stats: get_stats(time)
                            s = times_stats[time]
                            s['jogos'] += 1
                            s['hist_gols'].append(gf); s['hist_gols_sofridos'].append(gc)
                            if len(s['hist_gols']) > 10: s['hist_gols'].pop(0)
                            if len(s['hist_gols_sofridos']) > 10: s['hist_gols_sofridos'].pop(0)
                            s['gols'] = np.mean(s['hist_gols'])
                            s['gols_sofridos'] = np.mean(s['hist_gols_sofridos'])
                            if gf_ht is not None and gc_ht is not None:
                                s['hist_gols_ht'].append(gf_ht); s['hist_gols_sofridos_ht'].append(gc_ht)
                                if len(s['hist_gols_ht']) > 10: s['hist_gols_ht'].pop(0)
                                if len(s['hist_gols_sofridos_ht']) > 10: s['hist_gols_sofridos_ht'].pop(0)
                                s['gols_ht'] = np.mean(s['hist_gols_ht'])
                                s['gols_sofridos_ht'] = np.mean(s['hist_gols_sofridos_ht'])
                            if chutes is not None:
                                s['hist_chutes'].append(chutes)
                                if len(s['hist_chutes']) > 10: s['hist_chutes'].pop(0)
                                s['chutes'] = np.mean(s['hist_chutes'])
                            if chutes_sof is not None:
                                s['hist_chutes_sofridos'].append(chutes_sof)
                                if len(s['hist_chutes_sofridos']) > 10: s['hist_chutes_sofridos'].pop(0)
                                s['chutes_sofridos'] = np.mean(s['hist_chutes_sofridos'])
                            if chutes_gol is not None:
                                s['hist_chutes_gol'].append(chutes_gol)
                                if len(s['hist_chutes_gol']) > 10: s['hist_chutes_gol'].pop(0)
                                s['chutes_gol'] = np.mean(s['hist_chutes_gol'])
                            if chutes_gol_sof is not None:
                                s['hist_chutes_gol_sofridos'].append(chutes_gol_sof)
                                if len(s['hist_chutes_gol_sofridos']) > 10: s['hist_chutes_gol_sofridos'].pop(0)
                                s['chutes_gol_sofridos'] = np.mean(s['hist_chutes_gol_sofridos'])
                            if escanteios is not None:
                                s['hist_escanteios'].append(escanteios)
                                if len(s['hist_escanteios']) > 10: s['hist_escanteios'].pop(0)
                                s['escanteios'] = np.mean(s['hist_escanteios'])
                            if escanteios_sof is not None:
                                s['hist_escanteios_sofridos'].append(escanteios_sof)
                                if len(s['hist_escanteios_sofridos']) > 10: s['hist_escanteios_sofridos'].pop(0)
                                s['escanteios_sofridos'] = np.mean(s['hist_escanteios_sofridos'])
                            s['hist_ambas'].append(1 if (gf > 0 and gc > 0) else 0)
                            s['hist_over25'].append(1 if (gf + gc) > 2 else 0)
                            s['hist_over15'].append(1 if (gf + gc) > 1 else 0)
                            if gf_ht is not None and gc_ht is not None:
                                s['hist_gol_ht'].append(1 if (gf_ht + gc_ht) > 0 else 0)
                                s['hist_over15_ht'].append(1 if (gf_ht + gc_ht) > 1 else 0)
                            for lista in ['hist_ambas', 'hist_over25', 'hist_over15', 'hist_gol_ht', 'hist_over15_ht']:
                                if len(s[lista]) > 10: s[lista].pop(0)

                        update_stats(mandante, gols_m, gols_v, gols_ht_m, gols_ht_v, chutes_m, chutes_v, chutes_gol_m, chutes_gol_v, escanteios_m, escanteios_v)
                        update_stats(visitante, gols_v, gols_m, gols_ht_v, gols_ht_m, chutes_v, chutes_m, chutes_gol_v, chutes_gol_m, escanteios_v, escanteios_m)

                        progresso.progress((idx + 1) / total_jogos)

                    # Exibição
                    df_res = pd.DataFrame(resultados)
                    st.subheader("📋 Resultados dos Jogos")
                    st.dataframe(df_res, use_container_width=True, hide_index=True)

                    st.subheader("📈 Desempenho por Mercado")
                    resumo = []
                    for mercado in st.session_state.acertos_por_mercado:
                        total = st.session_state.total_por_mercado[mercado]
                        if total > 0:
                            acertos = st.session_state.acertos_por_mercado[mercado]
                            lucro = st.session_state.lucro_por_mercado[mercado]
                            roi = (lucro / total) * 100
                            resumo.append({
                                'Mercado': mercado,
                                'Apostas': total,
                                'Acertos': acertos,
                                'Taxa de Acerto': f"{acertos/total*100:.1f}%",
                                'Lucro/Prejuízo': f"{lucro:.2f} u",
                                'ROI': f"{roi:.1f}%"
                            })
                    if resumo:
                        df_resumo = pd.DataFrame(resumo)
                        st.dataframe(df_resumo, use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhum mercado pôde ser avaliado com os dados fornecidos.")
                    st.success("Simulação concluída!")

            except Exception as e:
                st.error(f"Erro ao processar os dados: {e}")
