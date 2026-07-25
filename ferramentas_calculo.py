# =========================================================================
# CAIXA DE FERRAMENTAS: MOTORES MATEMÁTICOS INTEGRAL DO MÉTODO
# =========================================================================

# -------------------------------------------------------------------------
# 🛠️ PASSO 1: MÁQUINA DE CALCULAR OVERALL (Escala 0 a 100)
# -------------------------------------------------------------------------

def calcular_fmp(prateleira_time, prateleira_rival):
    """
    🏛️ FILTRO CRUCIAL: Fator de Modulação de Prateleira Dinâmico (FMP)
    Define de forma assimétrica o peso dos erros e acertos históricos.
    """
    if prateleira_time == "Elite" and prateleira_rival in ["Meio", "Baixo"]:
        return 0.60, 1.40  # 1.40 para erros defensivos | 0.60 para acertos ofensivos
    elif prateleira_time in ["Meio", "Baixo"] and prateleira_rival == "Elite":
        return 1.30, 0.70  # 0.70 para erros defensivos | 1.30 para acertos ofensivos
    else:
        return 1.00, 1.00  # Multiplicador Neutro

def calcular_bloco_ataque(fvo, fco):
    """ A) Bloco de Ataque (Peso: 25% do OVR) """
    nota_final_ataque = (fvo * 0.60) + (fco * 0.40)
    return min(100.0, max(0.0, nota_final_ataque))

def calcular_bloco_defesa(frd, fcd_defensivo):
    """ B) Bloco de Defesa (Peso: 25% do OVR) """
    nota_final_defesa = (frd * 0.60) + (fcd_defensivo * 0.40)
    return min(100.0, max(0.0, nota_final_defesa))

def calcular_bloco_consistencia(fdm, ier):
    """ C) Bloco de Consistência (Peso: 35% do OVR) """
    return (fdm * 0.60) + (ier * 0.40)

def calcular_bloco_resistencia_pressao(fcd_res, egz_res, fri_res, fzc_res):
    """ D) Bloco de Resistência à Pressão (Peso: 15% do OVR) """
    return (fcd_res * 0.30) + (egz_res * 0.30) + (fri_res * 0.20) + (fzc_res * 0.20)

def calcular_overall_unificado(consistencia, ataque, defesa, resistencia_pressao):
    """ Composição Final do Passo 1 """
    return (consistencia * 0.35) + (ataque * 0.25) + (defesa * 0.25) + (resistencia_pressao * 0.15)

def classificar_intervalo_fifa(nota):
    if nota >= 86: return "Elite (86-99)"
    if nota >= 78: return "Alto (78-85)"
    if nota >= 70: return "Médio (70-77)"
    if nota >= 60: return "Baixo (60-69)"
    return "Crítico (<60)"

# -------------------------------------------------------------------------
# 📈 PASSO 2: ÍNDICE DE MOMENTO - IM / ImA (Escala 0 a 100)
# -------------------------------------------------------------------------

def calcular_im_final(cc3, cc5, geral_3, geral_5, geral_10, tabela_dinamica):
    """ Composição Ponderada do Passo 2 """
    sub_bloco_campo = (cc3 * 0.65) + (cc5 * 0.35)
    sub_bloco_general = (geral_3 * 0.50) + (geral_5 * 0.35) + (geral_10 * 0.15)
    return (sub_bloco_campo * 0.45) + (sub_bloco_general * 0.35) + (tabela_dinamica * 0.20)

# -------------------------------------------------------------------------
# ⚖️ PASSO 3: RETROVISOR DE AJUSTE DE EMPATES (HISTÓRICO)
# -------------------------------------------------------------------------

def calcular_pontos_retrovisor(mando, resultado, prateleira_rival):
    """ O empate assume valores ponderados de vitória """
    if resultado == "VITÓRIA": return 3.0
    if resultado == "DERROTA": return 0.0
    
    if mando == "VISITANTE":
        if prateleira_rival == "Elite (Top 4)": return 3.0 * 0.666
        else: return 3.0 * 1.000
    else: # MANDANTE
        if prateleira_rival in ["Elite (Top 4)", "Igual"]: return 3.0 * 0.666
        elif prateleira_rival == "Meio de Tabela": return 3.0 * 0.333
        elif prateleira_rival == "Z-4": return 3.0 * 0.000
    return 1.0
