"""
MyPredict 2.0 - Motor de Cálculo
Contém todas as funções do método: IMA, OVRall, MPV e auxiliares.
"""

# ============================================================
# PARÂMETROS GLOBAIS
# ============================================================
PARAMS = {
    'prateleiras': {'Elite': 1, 'Alta': 2, 'Meio': 3, 'Baixa': 4, 'Critico': 5},
    'S': 400,                         # Escala do Elo
    'V_mando': 75,                    # Bônus de rating por jogar em casa
    'K': {'normal': 15, 'atencao': 25, 'alerta': 35},
    'limiar_confianca_alta': 120,     # Diferença mínima de MPV para confiança alta
    'limiar_confianca_media': 60,
    'limiar_estabilidade_alta': 10,   # Desvio máximo do IMA para confiança alta
    'limiar_estabilidade_media': 15,
    'edge_dourado': 0.05,             # Edge mínimo para selo dourado
    'edge_verde': 0.03,               # Edge mínimo para selo verde
    'pesos_ima': [0.10, 0.15, 0.20, 0.25, 0.30],  # G10, G5, G3, L5, L3
    'pesos_ovrall': [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]  # ATA, DEF, MEI, FOR, CONS, RES
}

# ============================================================
# FUNÇÕES BÁSICAS DO IMA
# ============================================================
def pontos_do_jogo(prat_time, prat_adv, mando, resultado):
    """Calcula os pontos ganhos por UM time em UM jogo."""
    if mando == 'casa':
        dif_ef = (prat_adv - prat_time) + 1
    else:
        dif_ef = (prat_adv - prat_time) - 1

    if dif_ef < 0:
        ajuste = (abs(dif_ef) / 5) * 1.5
    elif dif_ef > 0:
        ajuste = -(dif_ef / 5) * 2.0
    else:
        ajuste = 0.0

    if resultado == 'V':
        return 3.0 + ajuste if dif_ef < 0 else 3.0
    elif resultado == 'E':
        return 1.0 + ajuste
    else:  # 'D'
        return 0.0 + ajuste if dif_ef > 0 else 0.0


def calcular_nota_janela(jogos):
    """Transforma uma lista de jogos em nota 0-100."""
    if not jogos:
        return 50.0

    P_obtida = P_max = P_min = 0.0
    for j in jogos:
        P_obtida += pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], j['resultado'])
        P_max += pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'V')
        P_min += pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'D')

    if P_max == P_min:
        return 50.0
    return ((P_obtida - P_min) / (P_max - P_min)) * 100


def calcular_IMA(jogos, time, data_ref, mando_proximo=None):
    """
    Calcula o IMA de um time até uma data de referência.
    jogos: lista de dicts com 'time', 'adv', 'data', 'mando', 'resultado',
           'prat_time', 'prat_adv'
    mando_proximo: 'casa' ou 'fora' (para definir janelas L5 e L3)
    """
    # Filtra jogos do time até a data
    jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref]
    jogos_time.sort(key=lambda x: x['data'], reverse=True)

    def ultimos(n, apenas_mando=None):
        filtrados = []
        for j in jogos_time:
            if apenas_mando is None or j['mando'] == apenas_mando:
                filtrados.append(j)
            if len(filtrados) == n:
                break
        return filtrados

    # Se não definido, tenta deduzir do próximo jogo (seria o jogo na data_ref)
    if mando_proximo is None:
        jogo_atual = [j for j in jogos if j['time'] == time and j['data'] == data_ref]
        if jogo_atual:
            mando_proximo = jogo_atual[0]['mando']
        else:
            mando_proximo = 'casa'

    G10 = ultimos(10)
    G5 = ultimos(5)
    G3 = ultimos(3)
    L5 = ultimos(5, apenas_mando=mando_proximo)
    L3 = ultimos(3, apenas_mando=mando_proximo)

    notas = [
        calcular_nota_janela(G10),
        calcular_nota_janela(G5),
        calcular_nota_janela(G3),
        calcular_nota_janela(L5),
        calcular_nota_janela(L3)
    ]

    pesos = PARAMS['pesos_ima']
    ima = sum(p * n for p, n in zip(pesos, notas))

    import statistics
    try:
        desvio = statistics.stdev([notas[2], notas[3], notas[4]])
    except:
        desvio = 10.0

    return ima, desvio


# ============================================================
# OVRALL (SIMPLIFICADO)
# ============================================================
def calcular_ATA(jogos, time, data_ref):
    """Versão simplificada: usa apenas média de gols."""
    jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref]
    if not jogos_time:
        return 50.0
    gols = [j.get('gols', 0) for j in jogos_time[-10:]]
    media = sum(gols) / len(gols)
    return min(100, max(0, (media / 3.0) * 100))


def calcular_DEF(jogos, time, data_ref):
    """Versão simplificada: usa média de gols sofridos."""
    jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref]
    if not jogos_time:
        return 50.0
    gols_sofridos = [j.get('gols_sofridos', 0) for j in jogos_time[-10:]]
    media = sum(gols_sofridos) / len(gols_sofridos)
    return min(100, max(0, 100 - (media / 3.0) * 100))


def calcular_MEI(jogos, time, data_ref):
    """Placeholder."""
    return 50.0

def calcular_FOR(jogos, time, data_ref):
    """Placeholder."""
    return 50.0

def calcular_CONS(jogos, time, data_ref):
    """Placeholder."""
    return 50.0

def calcular_RES(jogos, time, data_ref):
    """Placeholder."""
    return 50.0


def calcular_OVRall(componentes):
    """componentes: lista [ATA, DEF, MEI, FOR, CONS, RES]"""
    return sum(p * c for p, c in zip(PARAMS['pesos_ovrall'], componentes))


# ============================================================
# MYPREDICT VALUE (MPV)
# ============================================================
def inicializar_MPV(ovrall):
    """Converte OVRall (0-100) para escala de rating (1000-2000)."""
    return 1000 + ovrall * 10


def atualizar_MPV(mpv_time, mpv_adv, mando, resultado_real, ima_time):
    """Atualiza rating pós-jogo."""
    if mando == 'casa':
        esperado = 1 / (1 + 10 ** ((mpv_adv - (mpv_time + PARAMS['V_mando'])) / PARAMS['S']))
    else:
        esperado = 1 / (1 + 10 ** ((mpv_adv - (mpv_time - PARAMS['V_mando'])) / PARAMS['S']))

    resultado_map = {'V': 1.0, 'E': 0.5, 'D': 0.0}
    real = resultado_map[resultado_real]

    if 40 <= ima_time <= 60:
        K = PARAMS['K']['normal']
    elif 25 <= ima_time < 40 or 60 < ima_time <= 75:
        K = PARAMS['K']['atencao']
    else:
        K = PARAMS['K']['alerta']

    return mpv_time + K * (real - esperado)


def probabilidades_1x2(mpv_casa, mpv_fora):
    """Retorna (prob_casa, prob_empate, prob_fora)."""
    P_casa = 1 / (1 + 10 ** ((mpv_fora - (mpv_casa + PARAMS['V_mando'])) / PARAMS['S']))
    dif_norm = abs(mpv_casa + PARAMS['V_mando'] - mpv_fora) / PARAMS['S']
    P_empate = max(0.14, min(0.32, 0.30 - 0.05 * dif_norm))
    P_casa_final = P_casa - 0.5 * P_empate
    P_fora_final = 1 - P_casa_final - P_empate
    return P_casa_final, P_empate, P_fora_final


def calcular_edge(prob_mpv, odd):
    """Retorna edge (vantagem percentual)."""
    return (prob_mpv * odd) - 1


def determinar_selo(edge, dif_mpv, desvio_ima):
    """
    Retorna o selo: '🥇 Dourado', '🟢 Verde', '⚪ Marginal', '🔴 Sem Valor'
    """
    if dif_mpv > PARAMS['limiar_confianca_alta'] and desvio_ima <= PARAMS['limiar_estabilidade_alta']:
        confianca = 'alta'
    elif dif_mpv > PARAMS['limiar_confianca_media'] and desvio_ima <= PARAMS['limiar_estabilidade_media']:
        confianca = 'media'
    else:
        confianca = 'baixa'

    if edge >= PARAMS['edge_dourado'] and confianca == 'alta':
        return '🥇 Dourado'
    elif edge >= PARAMS['edge_verde'] and confianca in ('alta', 'media'):
        return '🟢 Verde'
    elif edge > 0:
        return '⚪ Marginal'
    else:
        return '🔴 Sem Valor'
