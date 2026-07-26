# =========================================================================
# CAIXA DE FERRAMENTAS: MOTORES MATEMÁTICOS INTEGRALIZADOS DO MÉTODO
# =========================================================================

# -------------------------------------------------------------------------
# CONSTANTES (evita números mágicos)
# -------------------------------------------------------------------------
PESO_FVO = 0.60
PESO_FCO = 0.40
PESO_FRD = 0.60
PESO_FCD_DEF = 0.40
PESO_FDM = 0.60
PESO_IER = 0.40

PESO_CONSISTENCIA = 0.35
PESO_ATAQUE = 0.25
PESO_DEFESA = 0.25
PESO_RESISTENCIA = 0.15

# -------------------------------------------------------------------------
# 🛠️ VALIDAÇÃO
# -------------------------------------------------------------------------
def validar_nota(valor, nome):
    """Garante que o valor está entre 0 e 100"""
    if valor is None:
        raise ValueError(f"❌ {nome} está vazio.")
    if not (0 <= valor <= 100):
        raise ValueError(f"❌ {nome} = {valor} fora do intervalo 0-100.")
    return float(valor)

# -------------------------------------------------------------------------
# PASSO 1: MÁQUINA DE CALCULAR OVERALL (Escala 0 a 100)
# -------------------------------------------------------------------------
def calcular_fmp(prateleira_time, prateleira_rival):
    if prateleira_time == "Elite" and prateleira_rival in ["Meio", "Baixo"]:
        return 0.60, 1.40
    elif prateleira_time in ["Meio", "Baixo"] and prateleira_rival == "Elite":
        return 1.30, 0.70
    else:
        return 1.00, 1.00

def calcular_bloco_ataque(fvo, fco):
    fvo = validar_nota(fvo, "FVO")
    fco = validar_nota(fco, "FCO")
    return min(100.0, max(0.0, (fvo * PESO_FVO) + (fco * PESO_FCO)))

def calcular_bloco_defesa(frd, fcd_defensivo):
    frd = validar_nota(frd, "FRD")
    fcd_defensivo = validar_nota(fcd_defensivo, "FCD Defensivo")
    return min(100.0, max(0.0, (frd * PESO_FRD) + (fcd_defensivo * PESO_FCD_DEF)))

def calcular_bloco_consistencia(fdm, ier):
    fdm = validar_nota(fdm, "FDM")
    ier = validar_nota(ier, "IER")
    return (fdm * PESO_FDM) + (ier * PESO_IER)

def calcular_bloco_resistencia_pressao(fcd_res, egz_res, fri_res, fzc_res):
    return (fcd_res * 0.30) + (egz_res * 0.30) + (fri_res * 0.20) + (fzc_res * 0.20)

def calcular_overall_unificado(consistencia, ataque, defesa, resistencia_pressao):
    return (consistencia * PESO_CONSISTENCIA) + (ataque * PESO_ATAQUE) + (defesa * PESO_DEFESA) + (resistencia_pressao * PESO_RESISTENCIA)

def classificar_intervalo_fifa(nota):
    if nota >= 86: return "Elite (86-99)"
    if nota >= 78: return "Alto (78-85)"
    if nota >= 70: return "Médio (70-77)"
    if nota >= 60: return "Baixo (60-69)"
    return "Crítico (<60)"

# -------------------------------------------------------------------------
# PASSO 2 E 3: ÍNDICE DE MOMENTO - IM E AJUSTE DE EMPATES
# -------------------------------------------------------------------------
def calcular_pontos_retrovisor(mando, resultado, escalao_rival):
    if resultado == "VITÓRIA": return 3.0
    if resultado == "DERROTA": return 0.0
    
    if mando == "VISITANTE":
        if escalao_rival == "Escalão A (Elite)":
            return 3.0 * 0.666
        else:
            return 3.0 * 1.000
    else:
        if escalao_rival == "Escalão A (Elite)":
            return 3.0 * 0.666
        elif escalao_rival == "Escalão B (Meio)":
            return 3.0 * 0.333
        elif escalao_rival == "Escalão C (Risco)":
            return 3.0 * 0.000
    return 1.0

def calcular_im_final(cc3, cc5, geral_3, geral_5, geral_10, tabela_dinamica):
    # ✅ CORRIGIDO: removido o "get_3 ="
    sub_campo = (cc3 * 0.65) + (cc5 * 0.35)
    sub_geral = (geral_3 * 0.50) + (geral_5 * 0.35) + (geral_10 * 0.15)
    return (sub_campo * 0.45) + (sub_geral * 0.35) + (tabela_dinamica * 0.20)

# -------------------------------------------------------------------------
# PILAR 3: ÍNDICE DE RESPOSTA COMPETITIVA CONTROLADO (IRC: 0 a 100)
# -------------------------------------------------------------------------
def calcular_fac(rodada):
    if 1 <= rodada <= 10: return 0.30
    if 11 <= rodada <= 25: return 0.60
    if 26 <= rodada <= 33: return 0.85
    return 1.00

def calcular_irc_final(rodada, nota_posicao, prospeccao_elite, orgulho_ferido, revanche):
    fac = calcular_fac(rodada)
    fpt = -10 if (1 <= rodada <= 10 and prospeccao_elite) else 0
    urgencia_real = nota_posicao + fpt
    nota_irc = 50 + (urgencia_real + orgulho_ferido + revanche) * fac
    return max(0.0, min(100.0, nota_irc))

# -------------------------------------------------------------------------
# PASSO 4: JUNÇÃO UNIFICADA E DISPARIDADE CRÍTICA
# -------------------------------------------------------------------------
def calcular_juncao_unificada(overall, im, irc):
    return (overall + im + irc) / 3
