# ratings.py — MyPredict 2.0
# Contém as funções de cálculo do IMA, OVRall (futuro) e MPV.

# ------------------------------------------------------------
# 1. CONFIGURAÇÕES DAS PRATELEIRAS E BÔNUS
# ------------------------------------------------------------

PRATELEIRAS = {
    'Elite':   (1, 3),
    'Alta':    (4, 7),
    'Media':   (8, 13),
    'Baixa':   (14, 16),
    'Critica': (17, 99)   # limite superior alto para capturar todos
}

PONTOS_BASE = {'V': 3, 'E': 1, 'D': 0}

# Bônus simétricos (vitória, derrota) para confrontos na mesma prateleira
BONUS_SIMETRICOS = {
    ('Elite', 'Elite'):       (+0.25, -0.25),
    ('Alta', 'Alta'):         (+0.15, -0.15),
    ('Media', 'Media'):       (0.0, 0.0),
    ('Baixa', 'Baixa'):       (+0.15, -0.15),
    ('Critica', 'Critica'):   (+0.25, -0.25),
}

# Bônus assimétricos para vitórias e derrotas específicas
BONUS_VITORIA_ASSIM = {
    ('Critica', 'Elite'): +2.0,
    ('Baixa', 'Elite'):   +0.5,
}

BONUS_DERROTA_ASSIM = {
    ('Elite', 'Critica'): -2.0,
    ('Elite', 'Baixa'):   -0.5,
}

# Bônus específicos para empates
BONUS_EMPATE = {
    ('Elite', 'Critica'):   -1.0,
    ('Critica', 'Elite'):   +2.0,
    ('Critica', 'Critica'): +0.5,
}

# Pesos para os recortes de jogos (devem somar 1)
PESOS_RECORTES = {
    '10G': 0.10,
    '5G':  0.15,
    '3G':  0.20,
    '5CF': 0.25,
    '3CF': 0.30,
}

# Parâmetros de normalização 0-100 para o IMA
PISO_IMA = -2.0   # pior pontuação possível (derrota de Elite para Crítica)
TETO_IMA = 5.0    # melhor pontuação possível (vitória de Crítica sobre Elite)

# Coeficiente de fusão do MPV (IMA vs OVRall) — será definido futuramente
ALPHA_MPV = 0.4   # peso do IMA (placeholder)


# ------------------------------------------------------------
# 2. FUNÇÕES AUXILIARES
# ------------------------------------------------------------

def obter_prateleira(posicao: int) -> str:
    """Retorna o nome da prateleira de acordo com a posição na tabela projetada."""
    for nome, (inf, sup) in PRATELEIRAS.items():
        if inf <= posicao <= sup:
            return nome
    return 'Critica'  # fallback, caso a posição ultrapasse 99 (improvável)


def calcular_pontuacao_jogo(resultado: str, prateleira_time: str, prateleira_adv: str) -> float:
    """
    Calcula a pontuação ajustada de um jogo para o time analisado,
    aplicando bônus e penalidades conforme as prateleiras.
    
    Parâmetros:
        resultado: 'V' (vitória), 'E' (empate) ou 'D' (derrota)
        prateleira_time: prateleira do time em análise
        prateleira_adv: prateleira do adversário
    
    Retorna:
        Pontuação ajustada (float)
    """
    pontos = PONTOS_BASE[resultado]

    # Vitória
    if resultado == 'V':
        # Primeiro verifica assimétricos
        if (prateleira_time, prateleira_adv) in BONUS_VITORIA_ASSIM:
            pontos += BONUS_VITORIA_ASSIM[(prateleira_time, prateleira_adv)]
        elif (prateleira_time, prateleira_adv) in BONUS_SIMETRICOS:
            pontos += BONUS_SIMETRICOS[(prateleira_time, prateleira_adv)][0]

    # Derrota
    elif resultado == 'D':
        if (prateleira_time, prateleira_adv) in BONUS_DERROTA_ASSIM:
            pontos += BONUS_DERROTA_ASSIM[(prateleira_time, prateleira_adv)]
        elif (prateleira_time, prateleira_adv) in BONUS_SIMETRICOS:
            pontos += BONUS_SIMETRICOS[(prateleira_time, prateleira_adv)][1]

    # Empate
    elif resultado == 'E':
        if (prateleira_time, prateleira_adv) in BONUS_EMPATE:
            pontos += BONUS_EMPATE[(prateleira_time, prateleira_adv)]
        # para demais combinações, mantém 1 ponto base sem bônus

    return pontos


# ------------------------------------------------------------
# 3. CÁLCULO DO IMA
# ------------------------------------------------------------

def calcular_ima(
    time: str,
    jogos_10G: list,
    jogos_5G: list,
    jogos_3G: list,
    jogos_5CF: list,
    jogos_3CF: list,
    projecao_classificacao: dict
) -> float:
    """
    Calcula o Índice de Momento Atual (IMA) de um time, normalizado entre 0 e 100.

    Parâmetros:
        time: nome do time sendo analisado
        jogos_10G, jogos_5G, jogos_3G: listas de jogos gerais (casa e fora)
        jogos_5CF, jogos_3CF: listas de jogos mandante (se time for casa) / visitante (se fora)
        projecao_classificacao: dicionário {time: posicao}
    
    Cada jogo é um dicionário com:
        'resultado': 'V', 'E' ou 'D'
        'adversario': nome do adversário
    """
    def media_recorte(jogos):
        if not jogos:
            return 0.0  # valor neutro; pode ser discutido
        pts = []
        for j in jogos:
            pos_time = projecao_classificacao[time]
            pos_adv = projecao_classificacao[j['adversario']]
            prat_time = obter_prateleira(pos_time)
            prat_adv = obter_prateleira(pos_adv)
            pts.append(calcular_pontuacao_jogo(j['resultado'], prat_time, prat_adv))
        return sum(pts) / len(pts)

    # Médias de cada recorte
    medias = {
        '10G': media_recorte(jogos_10G),
        '5G':  media_recorte(jogos_5G),
        '3G':  media_recorte(jogos_3G),
        '5CF': media_recorte(jogos_5CF),
        '3CF': media_recorte(jogos_3CF),
    }

    # Média ponderada
    ima_bruto = sum(medias[k] * PESOS_RECORTES[k] for k in PESOS_RECORTES)

    # Normalização para 0–100
    ima = (ima_bruto - PISO_IMA) / (TETO_IMA - PISO_IMA) * 100
    ima = max(0.0, min(100.0, ima))  # segurança numérica

    return ima


# ------------------------------------------------------------
# 4. CÁLCULO DO OVRall (PLACEHOLDER)
# ------------------------------------------------------------

def calcular_ovrall(estatisticas: dict) -> float:
    """
    Calcula a nota OVRall (0–100) baseada em seis dimensões:
    Ataque, Defesa, Meio, Consistência, Resiliência, Força.
    A ser implementado conforme definição futura.
    """
    # Placeholder: retornar valor neutro
    return 50.0


# ------------------------------------------------------------
# 5. CÁLCULO DO MPV (MyPredict Value)
# ------------------------------------------------------------

def calcular_mpv(ima: float, ovrall: float, alpha: float = ALPHA_MPV) -> float:
    """
    Combina IMA e OVRall no rating dinâmico MPV (0–100).
    Fórmula: MPV = alpha * IMA + (1 - alpha) * OVRall
    """
    return alpha * ima + (1 - alpha) * ovrall
