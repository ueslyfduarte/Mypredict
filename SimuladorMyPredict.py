"""
Simulador MyPredict 2.0 - Teste com CSV
"""
import csv
from datetime import datetime
from mypredict.core import (
    calcular_IMA,
    calcular_ATA,
    calcular_DEF,
    calcular_OVRall,
    inicializar_MPV,
    atualizar_MPV,
    probabilidades_1x2,
    calcular_edge,
    determinar_selo
)

# Leitura do CSV
jogos = []
with open('data/exemplo_jogos.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row['prat_time'] = int(row['prat_time'])
        row['prat_adv'] = int(row['prat_adv'])
        row['data'] = datetime.strptime(row['data'], '%Y-%m-%d')
        row['gols'] = int(row.get('gols', 0))
        jogos.append(row)

times = list(set(j['time'] for j in jogos))
print("Times encontrados:", times)

mpv_atual = {}
for time in times:
    ata = calcular_ATA(jogos, time, datetime.today())
    def_ = calcular_DEF(jogos, time, datetime.today())
    ovrall = calcular_OVRall([ata, def_, 50, 50, 50, 50])
    mpv_atual[time] = inicializar_MPV(ovrall)
    print(f"{time}: OVRall inicial = {ovrall:.1f}, MPV = {mpv_atual[time]:.0f}")

jogos.sort(key=lambda x: x['data'])
for jogo in jogos:
    time = jogo['time']
    adv = jogo['adv']
    data = jogo['data']
    mando = jogo['mando']
    resultado = jogo['resultado']

    ima, desvio = calcular_IMA(jogos, time, data, mando_proximo=mando)
    mpv_adv = mpv_atual.get(adv, 1500)

    mpv_antes = mpv_atual[time]
    mpv_depois = atualizar_MPV(mpv_antes, mpv_adv, mando, resultado, ima)
    mpv_atual[time] = mpv_depois

    if mando == 'casa':
        prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_antes, mpv_adv)
    else:
        prob_casa, prob_empate, prob_fora = probabilidades_1x2(mpv_adv, mpv_antes)

    edge = calcular_edge(prob_casa if mando == 'casa' else prob_fora, 2.0)
    dif_mpv = abs(mpv_antes - mpv_adv + (75 if mando == 'casa' else -75))
    selo = determinar_selo(edge, dif_mpv, desvio)

    print(f"{data.date()} | {time} x {adv} ({mando}) => "
          f"IMA={ima:.1f}, MPV: {mpv_antes:.0f} -> {mpv_depois:.0f}, "
          f"P_casa={prob_casa:.1%}, Edge={edge:.2%}, Selo={selo}")
