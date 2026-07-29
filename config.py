# config.py — Constantes globais do MyPredict 2.0

# Prateleiras por posição
PRATELEIRAS = {
    'Elite':   (1, 3),
    'Alta':    (4, 7),
    'Media':   (8, 13),
    'Baixa':   (14, 16),
    'Critica': (17, 99)
}

# Pontuação base
PONTOS_BASE = {'V': 3, 'E': 1, 'D': 0}

# Bônus assimétricos
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

# Pesos dos recortes do IMA
PESOS_RECORTES = {
    '10G': 0.10,
    '5G':  0.15,
    '3G':  0.20,
    '5CF': 0.25,
    '3CF': 0.30,
}

PISO_IMA = -2.0
TETO_IMA = 5.0

# OVRall
JOGOS_BASE_OVRALL = 38
PESOS_OVRALL = {
    'Ataque':       0.25,
    'Defesa':       0.25,
    'MeioCampo':    0.20,
    'Consistencia': 0.15,
    'Resiliencia':  0.15,
}

# MP Value (MPV)
PESOS_MPV = {
    'IMA':    1/3,
    'OVRall': 1/3,
    'IC':     1/3,
}

# Índice de Contexto (IC)
PESOS_IC = {
    'confronto_direto':              0.25,
    'mesmo_escalao':                 0.20,
    'contra_escalao_adversario':     0.20,
    'fator_casa':                    0.20,
    'odds':                          0.15,
}

JOGOS_CONFRONTO_DIRETO = 6

# Posições de referência para promovidos/rebaixados
POS_REF_PROMOVIDO = 16
POS_REF_REBAIXADO = 5

# Mercados
MAX_BONUS_CASA_MPV = 10.0
FATOR_BONUS_CASA = 0.1
SIGMOID_K = 0.12
SIGMA_EMPATE = 15.0
PROB_EMPATE_BASE = 0.28
MEDIA_GOLS_CASA_LIGA = 1.5
MEDIA_GOLS_FORA_LIGA = 1.2
PROPORCAO_GOLS_HT = 0.44
MARGEM_SEGURANCA_ESCANTEIOS = 2.0

# Motor de Mercados – Fatores de ajuste para IMA e IC
IMA_FACTOR = 0.005        # 0.5% de ajuste por ponto de IMA acima/abaixo de 50
IC_FACTOR = 0.003         # 0.3% de ajuste por ponto de IC
CONSISTENCY_FACTOR = 0.002  # Peso da consistência (desvio padrão) no ajuste

# Thresholds para selos
THRESHOLD_GOLD = 0.70     # MyPredict Gold (probabilidade >= 70%)
THRESHOLD_VALUE = 0.60    # Value
THRESHOLD_FAVORITO = 0.50 # Favorito

# ELO
ELO_INICIAL = 1500
ELO_K = 20
ELO_WEIGHT = 0.4          # Peso do ELO no MPV final (0 = só MPV, 1 = só ELO)

# Fator de superação (real vs projetada)
FATOR_SUPERACAO = 1.5     # pontos de MPV por nível de diferença
# ============================================================
# BENCHMARKS DA LIGA (exemplo com valores fictícios)
# ============================================================
LEAGUE_BENCHMARKS = {
    'gols_media': {'mean': 1.35, 'std': 0.38},
    'gols_sofridos_media': {'mean': 1.35, 'std': 0.42, 'lower_better': True},
    'xg_media': {'mean': 1.42, 'std': 0.35},
    'finalizacoes_alvo_media': {'mean': 4.8, 'std': 1.2},
    'conversao': {'mean': 0.28, 'std': 0.08},
    'posse_media': {'mean': 50.0, 'std': 8.5},
    'passes_certos_pct': {'mean': 78.0, 'std': 6.0},
    'desarmes_intercep_media': {'mean': 18.0, 'std': 4.0},
    # ... adicionar todos os indicadores usados
}

# ============================================================
# MAPEAMENTO DAS DIMENSÕES TÁTICAS
# ============================================================
DIMENSION_INDICATORS = {
    'ataque_posicional': ['gols_media', 'xg_media', 'finalizacoes_alvo_media', 'conversao'],
    'ataque_transicao': ['gols_contra_ataque', 'finalizacoes_velocidade'],
    'defesa_organizada': ['gols_sofridos_media', 'xga_media', 'finalizacoes_alvo_sofridas_media', 'desarmes_intercep_media'],
    'defesa_transicao': ['gols_sofridos_transicao'],
    'bola_parada_ofensiva': ['gols_escanteio', 'gols_falta'],
    'bola_parada_defensiva': ['gols_sofridos_escanteio', 'gols_sofridos_falta'],
    'controle_meio_campo': ['posse_media', 'passes_certos_pct', 'passes_progressivos'],
    'pressao_alta': ['recuperacoes_terco_ofensivo', 'ppda'],
    'resistencia_pressao': ['passes_certos_sob_pressao', 'perdas_posse_defensivo'],
}

# ============================================================
# PESOS DAS DIMENSÕES NO MPV
# ============================================================
DIMENSION_WEIGHTS = {
    'ataque_posicional': 0.15,
    'ataque_transicao': 0.10,
    'defesa_organizada': 0.15,
    'defesa_transicao': 0.10,
    'bola_parada_ofensiva': 0.08,
    'bola_parada_defensiva': 0.08,
    'controle_meio_campo': 0.14,
    'pressao_alta': 0.10,
    'resistencia_pressao': 0.10,
}

# ============================================================
# SENSIBILIDADE DOS MODULADORES
# ============================================================
IMA_MOD_SENSITIVITY = 0.3   # quanto o IMA influencia cada dimensão
IC_MOD_SENSITIVITY = 0.2    # quanto o IC influencia cada dimensão

# ============================================================
# MAPEAMENTO DAS ZONAS DO CAMPO
# ============================================================
FIELD_ZONES = {
    'ataque_posicional': {'x': 70, 'y': 20, 'width': 30, 'height': 28},
    'ataque_transicao': {'x': 40, 'y': 15, 'width': 30, 'height': 38},
    'defesa_organizada': {'x': 0, 'y': 20, 'width': 30, 'height': 28},
    'bola_parada_ofensiva': {'x': 85, 'y': 0, 'width': 15, 'height': 68},
    # ... completar para todas as dimensões
}
