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

PISO_IMA = -2.0   # pior caso: derrota de Elite para Crítica
TETO_IMA = 5.0    # melhor caso: vitória de Crítica sobre Elite

# ------------------------------------------------------------
# OVRALL
# ------------------------------------------------------------

JOGOS_BASE_OVRALL = 38          # quantidade padrão de jogos para análise
PESOS_OVRALL = {
    'Ataque':       0.25,
    'Defesa':       0.25,
    'MeioCampo':    0.20,
    'Consistencia': 0.15,
    'Resiliencia':  0.15,
}

# ------------------------------------------------------------
# MPV
# ------------------------------------------------------------

ALPHA_MPV = 0.4   # peso do IMA na fusão (IMA vs OVRall)

# ------------------------------------------------------------
# HERANÇA ESTATÍSTICA (times promovidos / rebaixados)
# ------------------------------------------------------------

POS_REF_PROMOVIDO = 16   # 1º fora da zona de rebaixamento (ex.: 17º a 20º)
POS_REF_REBAIXADO = 5    # 1º fora da zona de acesso (ex.: G4)
NUM_REBAIXADOS = 4
NUM_PROMOVIDOS = 4
