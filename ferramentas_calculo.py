# =========================================================================
# CAIXA DE FERRAMENTAS: MOTORES MATEMÁTICOS INTEGRALIZADOS DO MÉTODO
# =========================================================================

# -------------------------------------------------------------------------
# 🏛️ PASSO 1: MÁQUINA DE CALCULAR OVERALL (Escala 0 a 100)
# -------------------------------------------------------------------------

def calcular_fmp(prateleira_time, prateleira_rival):
    """
    🏛️ FILTRO CRUCIAL: Fator de Modulação de Prateleira Dinâmico (FMP)
    A relação de prateleiras define de forma assimétrica o peso dos erros e acertos.
    """
    if prateleira_time == "Elite" and prateleira_rival in ["Meio", "Baixo"]:
        return 0.60, 1.40  # 1.40 para erros defensivos | 0.60 para acertos ofensivos
    elif prateleira_time in ["Meio", "Baixo"] and prateleira_rival == "Elite":
        return 1.30, 0.70  # 0.70 para erros defensivos | 1.30 para acertos ofensivos
    else:
        return 1.00, 1.00  # Multiplicador Neutro (Prateleiras Iguais)

def calcular_bloco_ataque(fvo, fco):
    """ Nota Final de Ataque = (FVO × 0,60) + (FCO × 0,40) [Teto: 100] """
    return min(100.0, max(0.0, (fvo * 0.60) + (fco * 0.40)))

def calcular_bloco_defesa(frd, fcd_defensivo):
    """ Nota Final de Defesa = (FRD × 0,60) + (FCD Defensivo × 0,40) [Teto: 100] """
    return min(100.0, max(0.0, (frd * 0.60) + (fcd_defensivo * 0.40)))

def calcular_bloco_consistencia(fdm, ier):
    """ Nota Final de Consistência = (FDM × 0,60) + (IER × 0,40) """
    return (fdm * 0.60) + (ier * 0.40)

def calcular_bloco_resistencia_pressao(fcd_res, egz_res, fri_res, fzc_res):
    """ Bloco de Resistência à Pressão (Peso 15%): FCD(30%) | EGZ(30%) | FRI(20%) | FZC(20%) """
    return (fcd_res * 0.30) + (egz_res * 0.30) + (fri_res * 0.20) + (fzc_res * 0.20)

def calcular_overall_unificado(consistencia, ataque, defesa, resistencia_pressao):
    """ Composição: Consistência (35%) | Ataque (25%) | Defesa (25%) | Resistência (15%) """
    return (consistencia * 0.35) + (ataque * 0.25) + (defesa * 0.25) + (resistencia_pressao * 0.15)

def classificar_intervalo_fifa(nota):
    """ Classificação Formal Overall FIFA """
    if nota >= 86: return "Elite (86-99)"
    if nota >= 78: return "Alto (78-85)"
    if nota >= 70: return "Médio (70-77)"
    if nota >= 60: return "Baixo (60-69)"
    return "Crítico (<60)"

# -------------------------------------------------------------------------
# 📈 PASSO 2 E 3: ÍNDICE DE MOMENTO - IM / ImA E AJUSTE DE EMPATES
# -------------------------------------------------------------------------

def calcular_pontos_retrovisor(mando, resultado, escalao_rival):
    """
    ⚖️ PASSO 3: RETROVISOR DE AJUSTE DE EMPATES (HISTÓRICO)
    O empate assume valores ponderados de vitória (base de 3 pontos) conforme as prateleiras:
    """
    if resultado == "VITÓRIA": return 3.0
    if resultado == "DERROTA": return 0.0
    
    # Processamento do EMPATE ponderado conforme a ⚓ ÂNCORA DE REALIDADE do Rival:
    if mando == "VISITANTE":
        if escalao_rival == "Escalão A (Elite)":
            return 3.0 * 0.666  # Empate vale 66,6%
        else:
            return 3.0 * 1.000  # Contra igual/inferior vale 100%
    else: # MANDANTE
        if escalao_rival in ["Escalão A (Elite)", "Igual"]:
            return 3.0 * 0.666  # Vale 66,6%
        elif escalao_rival == "Escalão B (Meio)":
            return 3.0 * 0.333  # Vale 33,3%
        elif escalao_rival == "Escalão C (Risco)":
            return 3.0 * 0.000  # Fiasco (Vale 0%)
            
    return 1.0

def calcular_im_final(cc3, cc5, geral_3, geral_5, geral_10, tabela_dinamica):
    """
    PASSO 2: ÍNDICE DE MOMENTO (Escala 0 a 100)
    Condição de Campo (45%): CC3(65%) | CC5(35%)
    Geral (35%): G3(50%) | G5(35%) | G10(15%)
    Tabela Dinâmica (20%): Cruzamento de Posição Real vs Posição Recente
    """
    sub_campo = (cc3 * 0.65) + (cc5 * 0.35)
    sub_geral = (geral_3 * 0.50) + (geral_5 * 0.35) + (geral_10 * 0.15)
    return (sub_campo * 0.45) + (sub_geral * 0.35) + (tabela_dinamica * 0.20)

# -------------------------------------------------------------------------
# 🧠 PILAR 3: ÍNDICE DE RESPOSTA COMPETITIVA CONTROLADO (IRC: 0 a 100)
# -------------------------------------------------------------------------

def calcular_fac(rodada):
    """ 1. FAC (Fator de Altura da Competição): Modulador temporal obrigatório """
    if 1 <= rodada <= 10: return 0.30
    if 11 <= rodada <= 25: return 0.60
    if 26 <= rodada <= 33: return 0.85
    return 1.00  # Rodadas 34 a 38 (Impacto integral)

def calcular_irc_final(rodada, nota_posicao, prospecção_elite, orgulho_ferido, revanche):
    """
    🧠 Fórmula: Nota IRC = 50 + (Urgência Real + Orgulho Ferido + Revanche) × FAC
    Aplica Piso 0 e Teto 100 estritamente para evitar abusos de notas.
    """
    fac = calcular_fac(rodada)
    
    # 2. Urgência Real = Nota Posição Atual + FPT (Fator de Prospecção Teórica)
    fpt = -10 if (1 <= rodada <= 10 and prospecção_elite) else 0
    urgencia_real = nota_posicao + fpt
    
    # Execução da Equação Psicológica Controlada
    nota_irc = 50 + (urgencia_real + orgulho_ferido + revanche) * fac
    return max(0.0, min(100.0, nota_irc))

# -------------------------------------------------------------------------
# 🎯 PASSO 4: JUNÇÃO UNIFICADA E DISPARIDADE CRÍTICA
# -------------------------------------------------------------------------

def calcular_juncao_unificada(overall, im, irc):
    """ Nota Junção = (Overall + IM + IRC) / 3 """
    return (overall + im + irc) / 3
