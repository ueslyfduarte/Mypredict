# ratings.py — MyPredict 2.0
# Cálculo do IMA, OVRall e MPV.

from config import (
    PRATELEIRAS, PONTOS_BASE,
    BONUS_SIMETRICOS, BONUS_VITORIA_ASSIM, BONUS_DERROTA_ASSIM, BONUS_EMPATE,
    PESOS_RECORTES, PISO_IMA, TETO_IMA,
    PESOS_OVRALL, ALPHA_MPV
)


# ------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------------------------------------

def obter_prateleira(posicao: int) -> str:
    """Retorna o nome da prateleira de acordo com a posição na tabela projetada."""
    for nome, (inf, sup) in PRATELEIRAS.items():
        if inf <= posicao <= sup:
            return nome
    return 'Critica'  # fallback


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

    if resultado == 'V':
        # Assimétrico primeiro
        if (prateleira_time, prateleira_adv) in BONUS_VITORIA_ASSIM:
            pontos += BONUS_VITORIA_ASSIM[(prateleira_time, prateleira_adv)]
        elif (prateleira_time, prateleira_adv) in BONUS_SIMETRICOS:
            pontos += BONUS_SIMETRICOS[(prateleira_time, prateleira_adv)][0]

    elif resultado == 'D':
        if (prateleira_time, prateleira_adv) in BONUS_DERROTA_ASSIM:
            pontos += BONUS_DERROTA_ASSIM[(prateleira_time, prateleira_adv)]
        elif (prateleira_time, prateleira_adv) in BONUS_SIMETRICOS:
            pontos += BONUS_SIMETRICOS[(prateleira_time, prateleira_adv)][1]

    elif resultado == 'E':
        if (prateleira_time, prateleira_adv) in BONUS_EMPATE:
            pontos += BONUS_EMPATE[(prateleira_time, prateleira_adv)]
        # outros empates mantêm 1 ponto

    return pontos


# ------------------------------------------------------------
# CÁLCULO DO IMA
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
        jogos_5CF, jogos_3CF: listas de jogos como mandante/visitante
        projecao_classificacao: dict {time: posicao}

    Cada jogo é um dicionário com:
        'resultado': 'V', 'E' ou 'D'
        'adversario': nome do adversário
    """
    def media_recorte(jogos):
        if not jogos:
            return 0.0
        pts = []
        for j in jogos:
            pos_time = projecao_classificacao[time]
            pos_adv = projecao_classificacao[j['adversario']]
            prat_time = obter_prateleira(pos_time)
            prat_adv = obter_prateleira(pos_adv)
            pts.append(calcular_pontuacao_jogo(j['resultado'], prat_time, prat_adv))
        return sum(pts) / len(pts)

    medias = {
        '10G': media_recorte(jogos_10G),
        '5G':  media_recorte(jogos_5G),
        '3G':  media_recorte(jogos_3G),
        '5CF': media_recorte(jogos_5CF),
        '3CF': media_recorte(jogos_3CF),
    }

    ima_bruto = sum(medias[k] * PESOS_RECORTES[k] for k in PESOS_RECORTES)

    ima = (ima_bruto - PISO_IMA) / (TETO_IMA - PISO_IMA) * 100
    ima = max(0.0, min(100.0, ima))
    return ima


# ------------------------------------------------------------
# CÁLCULO DO OVRall (PLACEHOLDER)
# ------------------------------------------------------------

def calcular_ovrall(estatisticas: dict) -> float:
    """
    Calcula a nota OVRall (45 a 100) baseada em cinco dimensões:
    Ataque, Defesa, MeioCampo, Consistencia, Resiliencia.

    Parâmetros:
        estatisticas: dict com chaves:
            'Ataque', 'Defesa', 'MeioCampo', 'Consistencia', 'Resiliencia'
            cada uma com valor 0–100 (float).
            Valores ausentes são redistribuídos proporcionalmente.

    Retorna:
        OVRall no intervalo [45, 100].
    """
    # Verifica quais dimensões estão presentes
    disponiveis = {dim: valor for dim, valor in estatisticas.items()
                   if valor is not None and dim in PESOS_OVRALL}
    if not disponiveis:
        return 45.0  # mínimo possível

    # Pesos originais
    pesos_originais = PESOS_OVRALL.copy()

    # Redistribui pesos das dimensões ausentes
    peso_total_disp = sum(pesos_originais[dim] for dim in disponiveis)
    if peso_total_disp == 0:
        return 45.0

    ovrall_bruto = 0.0
    for dim, valor in disponiveis.items():
        peso_ajustado = pesos_originais[dim] / peso_total_disp  # normaliza para soma 1
        ovrall_bruto += peso_ajustado * valor

    # Mapeia [0, 100] para [45, 100]
    ovrall = 45.0 + (ovrall_bruto * 0.55)
    ovrall = max(45.0, min(100.0, ovrall))
    return ovrall


# ------------------------------------------------------------
# CÁLCULO DO MPV
# ------------------------------------------------------------

def calcular_mpv(ima: float, ovrall: float, alpha: float = ALPHA_MPV) -> float:
    """
    Combina IMA e OVRall no rating dinâmico MPV (0–100).
    Fórmula: MPV = alpha * IMA + (1 - alpha) * OVRall
    """
    return alpha * ima + (1 - alpha) * ovrall
