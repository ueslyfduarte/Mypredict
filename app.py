# =========================================================================
# NOVA ABA DADOS ONLINE COM SELEÇÃO DE LIGA E TIME (FALLBACK)
# =========================================================================
elif aba == "🌐 Dados Online (Seleção)":
    st.header("🌐 Dados Online – Selecione Liga e Times")
    st.caption("Escolha a liga e os times. Dados obtidos via API ou lista estática.")

    # Lista estática de times por liga (fallback)
    TIMES_POR_LIGA = {
        "Brasileirão Série A": [
            "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Santos",
            "Internacional", "Grêmio", "Atlético Mineiro", "Cruzeiro", "Fluminense",
            "Botafogo", "Athletico Paranaense", "Fortaleza", "Bahia", "Ceará",
            "América Mineiro", "Goiás", "Coritiba", "Red Bull Bragantino", "Cuiabá"
        ],
        "Premier League": [
            "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton",
            "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham",
            "Liverpool", "Luton Town", "Manchester City", "Manchester United",
            "Newcastle United", "Nottingham Forest", "Sheffield United", "Tottenham", "West Ham", "Wolverhampton"
        ],
        "La Liga": ["Real Madrid", "Barcelona", "Atlético Madrid", "Sevilla", "Valencia", "Real Sociedad", "Betis", "Athletic Bilbao", "Villarreal", "Getafe"],
        "Série A Italiana": ["Juventus", "Inter", "Milan", "Napoli", "Roma", "Lazio", "Atalanta", "Fiorentina", "Torino", "Bologna"],
        "Bundesliga": ["Bayern Munich", "Borussia Dortmund", "RB Leipzig", "Bayer Leverkusen", "Eintracht Frankfurt", "Borussia M'gladbach", "Wolfsburg", "Freiburg", "Hoffenheim", "Augsburg"],
        "Ligue 1": ["PSG", "Olympique Marseille", "Lyon", "Monaco", "Lille", "Nice", "Rennes", "Strasbourg", "Montpellier", "Nantes"],
        "Eredivisie": ["Ajax", "PSV", "Feyenoord", "AZ Alkmaar", "Twente", "Vitesse", "Utrecht"],
        "Primeira Liga": ["Benfica", "Porto", "Sporting CP", "Braga", "Vitória Guimarães", "Boavista", "Rio Ave"]
    }

    ligas = list(TIMES_POR_LIGA.keys())

    col1, col2 = st.columns(2)
    with col1:
        liga_a = st.selectbox("Liga do Time A", ligas, key="liga_a")
        times_a = TIMES_POR_LIGA[liga_a]
        time_a_nome = st.selectbox("Time A (Mandante)", times_a, key="time_a")
        # Permitir nome personalizado se não encontrado
        if time_a_nome == "Outro...":
            time_a_nome = st.text_input("Digite o nome do Time A", key="time_a_custom")
    with col2:
        liga_b = st.selectbox("Liga do Time B", ligas, key="liga_b")
        times_b = TIMES_POR_LIGA[liga_b]
        time_b_nome = st.selectbox("Time B (Visitante)", times_b, key="time_b")
        if time_b_nome == "Outro...":
            time_b_nome = st.text_input("Digite o nome do Time B", key="time_b_custom")

    if st.button("🔎 Buscar Dados (API ou estático)"):
        # Tenta API Football-Data.org primeiro
        with st.spinner("Tentando API..."):
            med_a = None
            med_b = None
            try:
                # Buscar ID do time na API (opcional, pode falhar)
                league_map = {"Brasileirão Série A": "BSA", "Premier League": "PL", "La Liga": "PD",
                              "Série A Italiana": "SA", "Bundesliga": "BL1", "Ligue 1": "FL1",
                              "Eredivisie": "DED", "Primeira Liga": "PPL"}
                code_a = league_map.get(liga_a, "BSA")
                code_b = league_map.get(liga_b, "BSA")
                # Função para obter ID via API (pode retornar None)
                def get_team_id(name, league_code):
                    url = f"https://api.football-data.org/v4/competitions/{league_code}/teams"
                    headers = {}
                    if FOOTBALL_DATA_API_KEY:
                        headers["X-Auth-Token"] = FOOTBALL_DATA_API_KEY
                    resp = requests.get(url, headers=headers, timeout=5)
                    if resp.status_code == 200:
                        teams = resp.json().get("teams", [])
                        for t in teams:
                            if name.lower() in t["name"].lower():
                                return t["id"]
                    return None
                id_a = get_team_id(time_a_nome, code_a)
                id_b = get_team_id(time_b_nome, code_b)
                if id_a and id_b:
                    matches_a = buscar_partidas_time(id_a, 10)
                    matches_b = buscar_partidas_time(id_b, 10)
                    if matches_a and matches_b:
                        med_a = calcular_medias_partidas(matches_a, id_a)
                        med_b = calcular_medias_partidas(matches_b, id_b)
            except:
                pass

        # Fallback: usar dados estáticos simples (apenas gols baseados em médias históricas)
        if med_a is None or med_b is None:
            st.warning("API indisponível. Usando estimativas estáticas.")
            # Valores médios aproximados por liga (gols por jogo)
            med_a = {"gols": 1.4, "chutes": None, "chutes_gol": None, "xg": None}
            med_b = {"gols": 1.4, "chutes": None, "chutes_gol": None, "xg": None}
            # Você pode ajustar manualmente depois

        st.session_state.dados_time_a = med_a
        st.session_state.dados_time_b = med_b
        st.session_state.nomes_times = (time_a_nome, time_b_nome)
        st.success("Dados preparados! Ajuste manualmente se necessário.")

    # Restante da exibição (idêntico ao código anterior)
    if "dados_time_a" in st.session_state and "dados_time_b" in st.session_state:
        med_a = st.session_state.dados_time_a
        med_b = st.session_state.dados_time_b
        nome_a, nome_b = st.session_state.nomes_times
        st.markdown("---")
        st.subheader("📊 Dados (médias por jogo)")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**{nome_a}**")
            st.write(med_a)
        with col2:
            st.write(f"**{nome_b}**")
            st.write(med_b)

        with st.expander("🛡️ Completar dados defensivos"):
            med_a['gols_sofridos'] = st.number_input(f"Gols Sofridos {nome_a}", 0.0, 10.0, 1.0, key="ga")
            med_a['chutes_sofridos'] = st.number_input(f"Chutes Sofridos {nome_a}", 0.0, 50.0, 10.0, key="ca")
            med_b['gols_sofridos'] = st.number_input(f"Gols Sofridos {nome_b}", 0.0, 10.0, 1.0, key="gb")
            med_b['chutes_sofridos'] = st.number_input(f"Chutes Sofridos {nome_b}", 0.0, 50.0, 10.0, key="cb")

        st.markdown("### 🧠 Fatores Psicológicos")
        col1, col2 = st.columns(2)
        with col1:
            rod_a = st.number_input("Rodada A", 1, 38, 20, key="ra")
            pos_a = st.slider("Posição A", 0, 100, 60, key="pa")
            org_a = st.slider("Orgulho A", 0, 30, 0, key="oa")
        with col2:
            rod_b = st.number_input("Rodada B", 1, 38, 20, key="rb")
            pos_b = st.slider("Posição B", 0, 100, 40, key="pb")
            org_b = st.slider("Orgulho B", 0, 30, 0, key="ob")

        if st.button("⚡ GERAR MYPREDICT (Online)", use_container_width=True):
            # ... (código de cálculo igual ao da resposta anterior)
            st.success("Previsão gerada (simplificada).")
