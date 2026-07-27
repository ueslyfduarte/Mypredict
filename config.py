# config.py — MyPredict 2.0
# Configurações gerais do projeto.

# ------------------------------------------------------------
# PRATELEIRAS E BÔNUS DO IMA
# ------------------------------------------------------------

PRATELEIRAS = {
    'Elite':   (1, 3),
    'Alta':    (4, 7),
    'Media':   (8, 13),
    'Baixa':   (14, 16),
    'Critica': (17, 99)
}

PONTOS_BASE = {'V': 3, 'E': 1, 'D': 0}

BONUS_SIMETRICOS = {
    ('Elite', 'Elite'):       (+0.25, -0.25),
    ('Alta', 'Alta'):         (+0.15, -0.15),
    ('Media', 'Media'):       (0.0, 0.0),
    ('Baixa', 'Baixa'):       (+0.15, -0.15),
    ('Critica', 'Critica'):   (+0.25, -0.25),
}

BONUS_VITORIA_ASSIM = {
    ('Critica', 'Elite'): +2.0,
    ('Baixa', 'Elite'):   +0.5,
}

BONUS_DERROTA_ASSIM = {
    ('Elite', 'Critica'): -2.0,
    ('Elite', 'Baixa'):   -0.5,
}

BONUS_EMPATE = {
    ('Elite', 'Critica'):   -1.0,
    ('Critica', 'Elite'):   +2.0,
    ('Critica', 'Critica'): +0.5,
}

# ------------------------------------------------------------
# PESOS DOS RECORTES DO IMA
# ------------------------------------------------------------

PESOS_RECORTES = {
    '10G': 0.10,
    '5G':  0.15,
    '3G':  0.20,
    '5CF': 0.25,
    '3CF': 0.30,
}

# ------------------------------------------------------------
# NORMALIZAÇÃO IMA (0–100)
# ------------------------------------------------------------

PISO_IMA = -2.0
TETO_IMA = 5.0

# ------------------------------------------------------------
# OVRALL
# ------------------------------------------------------------

JOGOS_BASE_OVRALL = 38
PESOS_OVRALL = {
    'Ataque':       0.25,
    'Defesa':       0.25,
    'MeioCampo':    0.20,
    'Consistencia': 0.15,
    'Resiliencia':  0.15,
}

# ------------------------------------------------------------
# MPV — Pesos dos três pilares
# ------------------------------------------------------------

PESOS_MPV = {
    'IMA':    1/3,
    'OVRall': 1/3,
    'IC':     1/3,
}

# ------------------------------------------------------------
# IC (Índice de Contexto) — Fatores e pesos iniciais
# ------------------------------------------------------------

# Pesos dos fatores dentro do IC (somam 1)
PESOS_IC = {
    'confronto_direto':              0.25,
    'mesmo_escalao':                 0.20,
    'contra_escalao_adversario':     0.20,
    'fator_casa':                    0.20,
    'odds':                          0.15,
}

# Número de jogos para cálculo do confronto direto
JOGOS_CONFRONTO_DIRETO = 6

# ------------------------------------------------------------
# HERANÇA ESTATÍSTICA (times promovidos / rebaixados)
# ------------------------------------------------------------

POS_REF_PROMOVIDO = 16
POS_REF_REBAIXADO = 5
NUM_REBAIXADOS = 4
NUM_PROMOVIDOS = 4
