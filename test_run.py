# test_run.py
from data_loader import (
    gerar_prateleiras, obter_dados_ovrall_time, classificação_anterior,
    obter_ultimos_jogos_com_heranca, extrair_recortes_ima
)
from ratings import calcular_ima
from markets import prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht, calcular_bonus_casa
from data_source_fbref import obter_classificacao

liga = 'Brasileirão'
temporada = 2024
time_casa = 'Flamengo'
time_fora = 'Palmeiras'

# 1. Classificação real
class_ant = obter_classificacao(liga, temporada)

# 2. Dados de jogos
dados_casa = obter_dados_ovrall_time(time_casa, liga, temporada, class_ant)
dados_fora = obter_dados_ovrall_time(time_fora, liga, temporada, class_ant)

# 3. IMA (com prateleiras manuais se não tiver promovidos)
prateleiras = gerar_prateleiras(liga, temporada)  # precisará de promovidos/rebaixados configurados

# ... (código similar ao app.py)
