# core/elo.py
def calcular_elo(time, jogos, prateleiras, elo_atual=None, k=20):
    """
    Atualiza o ELO de um time com base em uma lista de jogos.
    jogos: lista de dicts com 'resultado', 'adversario', 'gols_pro', 'gols_contra'.
    Retorna o ELO final após processar todos os jogos.
    """
    if elo_atual is None:
        elo = 1500
    else:
        elo = elo_atual

    for jogo in jogos:
        # Estimar ELO do adversário (simplificado: baseado na prateleira)
        prat_adv = prateleiras.get(jogo['adversario'], 'Media')
        # Mapeamento simples de prateleira para ELO médio (pode ser refinado)
        elo_adv = {
            'Elite': 1700,
            'Alta': 1600,
            'Media': 1500,
            'Baixa': 1400,
            'Critica': 1300
        }.get(prat_adv, 1500)

        # Resultado esperado
        esperado = 1 / (1 + 10 ** ((elo_adv - elo) / 400))

        # Resultado real
        if jogo['resultado'] == 'V':
            real = 1
        elif jogo['resultado'] == 'E':
            real = 0.5
        else:
            real = 0

        # Ajuste por diferença de gols
        diff_gols = abs(jogo.get('gols_pro', 0) - jogo.get('gols_contra', 0))
        fator_gols = 1 + min(diff_gols, 3) * 0.1  # máximo 30% extra

        elo += k * fator_gols * (real - esperado)

    return elo


def normalizar_elo(elo, liga_elos):
    """
    Normaliza o ELO para escala 0-100 baseado na distribuição da liga.
    liga_elos: lista com os ELOs de todos os times da liga (ou pelo menos os dois).
    """
    if not liga_elos or len(liga_elos) < 2:
        return 50.0
    minimo = min(liga_elos)
    maximo = max(liga_elos)
    if maximo == minimo:
        return 50.0
    return (elo - minimo) / (maximo - minimo) * 100
