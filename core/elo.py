# core/elo.py
def calcular_elo(time, jogos, prateleiras, elo_atual=None, k=20):
    if elo_atual is None:
        elo = 1500
    else:
        elo = elo_atual

    for jogo in jogos:
        prat_adv = jogo.get('prateleira_adv', 'Media')
        elo_adv = {
            'Elite': 1700,
            'Alta': 1600,
            'Media': 1500,
            'Baixa': 1400,
            'Critica': 1300
        }.get(prat_adv, 1500)

        esperado = 1 / (1 + 10 ** ((elo_adv - elo) / 400))

        if jogo['resultado'] == 'V':
            real = 1
        elif jogo['resultado'] == 'E':
            real = 0.5
        else:
            real = 0

        diff_gols = abs(jogo.get('gols_pro', 0) - jogo.get('gols_contra', 0))
        fator_gols = 1 + min(diff_gols, 3) * 0.1

        elo += k * fator_gols * (real - esperado)

    return elo

def normalizar_elo(elo, liga_elos):
    if not liga_elos or len(liga_elos) < 2:
        return 50.0
    minimo = min(liga_elos)
    maximo = max(liga_elos)
    if maximo == minimo:
        return 50.0
    return (elo - minimo) / (maximo - minimo) * 100
