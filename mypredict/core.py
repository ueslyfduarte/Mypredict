"""
MyPredict 2.0 - Motor de Cálculo (com estatísticas expandidas e fallback)
"""
import statistics

PARAMS = {
    'prateleiras': {'Elite': 1, 'Alta': 2, 'Meio': 3, 'Baixa': 4, 'Critico': 5},
    'S': 400,
    'V_mando': 75,
    'K': {'normal': 15, 'atencao': 25, 'alerta': 35},
    'limiar_confianca_alta': 120,
    'limiar_confianca_media': 60,
    'limiar_estabilidade_alta': 10,
    'limiar_estabilidade_media': 15,
    'edge_dourado': 0.05,
    'edge_verde': 0.03,
    'pesos_ima': [0.10, 0.15, 0.20, 0.25, 0.30],
    'pesos_ovrall': [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
}

# ---------- IMA ----------
def pontos_do_jogo(prat_time, prat_adv, mando, resultado):
    if mando == 'casa':
        dif_ef = (prat_adv - prat_time) + 1
    else:
        dif_ef = (prat_adv - prat_time) - 1
    if dif_ef < 0:
        ajuste = (abs(dif_ef) / 5) * 1.5
    elif dif_ef > 0:
        ajuste = -(dif_ef / 5) * 2.0
    else:
        ajuste = 0.0
    if resultado == 'V':
        return 3.0 + ajuste if dif_ef < 0 else 3.0
    elif resultado == 'E':
        return 1.0 + ajuste
    else:
        return 0.0 + ajuste if dif_ef > 0 else 0.0

def calcular_nota_janela(jogos):
    if not jogos:
        return 50.0
    P_obtida = P_max = P_min = 0.0
    for j in jogos:
        P_obtida += pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], j['resultado'])
        P_max += pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'V')
        P_min += pontos_do_jogo(j['prat_time'], j['prat_adv'], j['mando'], 'D')
    if P_max == P_min:
        return 50.0
    return ((P_obtida - P_min) / (P_max - P_min)) * 100

def calcular_IMA(jogos, time, data_ref, mando_proximo=None):
    jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref]
    jogos_time.sort(key=lambda x: x['data'], reverse=True)
    def ultimos(n, apenas_mando=None):
        filtrados = []
        for j in jogos_time:
            if apenas_mando is None or j['mando'] == apenas_mando:
                filtrados.append(j)
            if len(filtrados) == n:
                break
        return filtrados
    if mando_proximo is None:
        jogo_atual = [j for j in jogos if j['time'] == time and j['data'] == data_ref]
        mando_proximo = jogo_atual[0]['mando'] if jogo_atual else 'casa'
    G10 = ultimos(10)
    G5 = ultimos(5)
    G3 = ultimos(3)
    L5 = ultimos(5, apenas_mando=mando_proximo)
    L3 = ultimos(3, apenas_mando=mando_proximo)
    notas = [calcular_nota_janela(w) for w in [G10, G5, G3, L5, L3]]
    ima = sum(p * n for p, n in zip(PARAMS['pesos_ima'], notas))
    try:
        desvio = statistics.stdev([notas[2], notas[3], notas[4]])
    except:
        desvio = 10.0
    return ima, desvio

# ---------- FUNÇÕES AUXILIARES ----------
def media_ponderada_38_10(serie):
    if not serie:
        return 0.0
    longa = sum(serie[-38:]) / len(serie[-38:]) if len(serie) >= 38 else sum(serie)/len(serie)
    curta = sum(serie[-10:]) / len(serie[-10:]) if len(serie) >= 10 else sum(serie)/len(serie)
    return 0.6 * longa + 0.4 * curta

# ---------- OVRall expandido ----------
def calcular_ATA(jogos, time, data_ref):
    jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref]
    if not jogos_time:
        return 50.0
    # Componentes obrigatórios: gols
    gols = [j.get('gols', 0) for j in jogos_time]
    media_gols = media_ponderada_38_10(gols)
    nota_gols = min(100, max(0, (media_gols / 3) * 100))

    # Opcionais: finalizações no alvo (SoT), chutes totais (ST)
    tem_sot = any('finalizacoes_alvo' in j for j in jogos_time)
    tem_st = any('finalizacoes_totais' in j for j in jogos_time)

    pesos = [1.0]  # peso do componente gols (sempre presente)
    notas = [nota_gols]

    if tem_sot:
        sot = [j.get('finalizacoes_alvo', 0) for j in jogos_time]
        conv = sum(gols[-10:]) / sum(sot[-10:]) if sum(sot[-10:]) > 0 else 0
        nota_conv = min(100, max(0, (conv / 0.5) * 100))
        notas.append(nota_conv)
        pesos.append(0.6)  # peso do SoT
    else:
        pesos[0] += 0.6  # redistribui para gols

    if tem_st:
        st = [j.get('finalizacoes_totais', 0) for j in jogos_time]
        # Índice de precipitação: chutes/gol
        razao = sum(st[-10:]) / sum(gols[-10:]) if sum(gols[-10:]) > 0 else 0
        # Quanto menor a razão, melhor (mais cirúrgico)
        nota_razao = min(100, max(0, 100 - (razao / 20) * 100))  # 0 a 100
        notas.append(nota_razao)
        pesos.append(0.4)  # peso do volume de chutes
    else:
        pesos[0] += 0.4  # redistribui

    # Média ponderada com pesos ajustados
    soma_pesos = sum(pesos)
    return sum(n * p / soma_pesos for n, p in zip(notas, pesos))

def calcular_DEF(jogos, time, data_ref):
    jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref]
    if not jogos_time:
        return 50.0
    # Componentes obrigatórios: gols sofridos e clean sheets
    sofridos = [j.get('gols_sofridos', 0) for j in jogos_time]
    media_sofridos = media_ponderada_38_10(sofridos)
    nota_sofridos = min(100, max(0, 100 - (media_sofridos / 3) * 100))
    clean = sum(1 for g in sofridos[-10:] if g == 0) / len(sofridos[-10:]) if sofridos else 0
    nota_clean = clean * 100

    pesos = [0.6, 0.4]  # gols sofridos, clean sheets
    notas = [nota_sofridos, nota_clean]

    # Opcional: faltas cometidas (disciplina) – se disponível
    tem_faltas = any('faltas_cometidas' in j for j in jogos_time)
    if tem_faltas:
        faltas = [j.get('faltas_cometidas', 0) for j in jogos_time]
        media_faltas = media_ponderada_38_10(faltas)
        nota_faltas = min(100, max(0, 100 - (media_faltas / 15) * 100))  # muitas faltas = pior
        notas.append(nota_faltas)
        pesos.append(0.3)
        # Ajustar pesos anteriores
        pesos[0] *= 0.7
        pesos[1] *= 0.7
        soma_pesos = sum(pesos)
        return sum(n * p / soma_pesos for n, p in zip(notas, pesos))
    else:
        # Sem faltas, mantém apenas os dois componentes
        soma_pesos = sum(pesos)
        return sum(n * p / soma_pesos for n, p in zip(notas, pesos))

def calcular_MEI(jogos, time, data_ref):
    jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref]
    if not jogos_time:
        return 50.0
    # Escanteios a favor (já temos)
    esc = [j.get('escanteios', 0) for j in jogos_time]
    media_esc = sum(esc[-10:]) / len(esc[-10:]) if esc else 3
    nota_esc = min(100, max(0, (media_esc / 8) * 100))

    # Faltas sofridas (já temos)
    faltas = [j.get('faltas_sofridas', 0) for j in jogos_time]
    media_faltas = sum(faltas[-10:]) / len(faltas[-10:]) if faltas else 10
    nota_faltas = min(100, max(0, (media_faltas / 15) * 100))

    # Opcional: índice de precipitação (chutes/gols) – se tivermos finalizações totais
    tem_st = any('finalizacoes_totais' in j for j in jogos_time)
    if tem_st:
        st = [j.get('finalizacoes_totais', 0) for j in jogos_time]
        gols = [j.get('gols', 0) for j in jogos_time]
        razao = sum(st[-10:]) / sum(gols[-10:]) if sum(gols[-10:]) > 0 else 0
        nota_razao = min(100, max(0, 100 - (razao / 20) * 100))
        # Combina com esc e faltas: pesos 0.4, 0.3, 0.3
        return 0.4 * nota_esc + 0.3 * nota_faltas + 0.3 * nota_razao
    else:
        # Sem finalizações, peso maior para esc e faltas
        return 0.5 * nota_esc + 0.5 * nota_faltas

def calcular_FOR(jogos, time, data_ref):
    jogos_time = [j for j in jogos if j['time'] == time and j['data'] <= data_ref]
    if not jogos_time:
        return 50.0
    # Escanteios a favor (proxy de imposição ofensiva)
    esc = [j.get('escanteios', 0) for j in jogos_time]
    media_esc = sum(esc[-10:]) / len(esc[-10:]) if esc else 3
    nota_esc = min(100, max(0, (media_esc / 8) * 100))

    # Opcionais: cartões amarelos/vermelhos (se disponíveis)
    tem_cartoes = any('cartoes_amarelos' in j or 'cartoes_vermelhos' in j for j in jogos_time)
    if tem_cartoes:
        amar = [j.get('cartoes_amarelos', 0) for j in jogos_time]
        verm = [j.get('cartoes_vermelhos', 0) for j in jogos_time]
        total_cartoes = [a + 2*v for a,v in zip(amar, verm)]  # vermelho = 2x
        media_cartoes = sum(total_cartoes[-10:]) / len(total_cartoes[-10:]) if total_cartoes else 0
        nota_cartoes = min(100, max(0, (media_cartoes / 3) * 100))  # muitos cartões = mais força
        return 0.6 * nota_esc + 0.4 * nota_cartoes
    else:
        return nota_esc

def calcular_CONS(jogos, time, data_ref):
    return 50.0

def calcular_RES(jogos, time, data_ref):
    return 50.0

def calcular_OVRall(componentes):
    return sum(p * c for p, c in zip(PARAMS['pesos_ovrall'], componentes))

# ---------- MPV ----------
def inicializar_MPV(ovrall):
    return 1000 + ovrall * 10

def atualizar_MPV(mpv_time, mpv_adv, mando, resultado_real, ima_time):
    if mando == 'casa':
        esperado = 1 / (1 + 10 ** ((mpv_adv - (mpv_time + PARAMS['V_mando'])) / PARAMS['S']))
    else:
        esperado = 1 / (1 + 10 ** ((mpv_adv - (mpv_time - PARAMS['V_mando'])) / PARAMS['S']))
    real = {'V': 1.0, 'E': 0.5, 'D': 0.0}[resultado_real]
    if 40 <= ima_time <= 60:
        K = PARAMS['K']['normal']
    elif 25 <= ima_time < 40 or 60 < ima_time <= 75:
        K = PARAMS['K']['atencao']
    else:
        K = PARAMS['K']['alerta']
    return mpv_time + K * (real - esperado)

def probabilidades_1x2(mpv_casa, mpv_fora):
    P_casa = 1 / (1 + 10 ** ((mpv_fora - (mpv_casa + PARAMS['V_mando'])) / PARAMS['S']))
    dif_norm = abs(mpv_casa + PARAMS['V_mando'] - mpv_fora) / PARAMS['S']
    P_empate = max(0.14, min(0.32, 0.30 - 0.05 * dif_norm))
    P_casa_final = P_casa - 0.5 * P_empate
    P_fora_final = 1 - P_casa_final - P_empate
    return P_casa_final, P_empate, P_fora_final

def calcular_edge(prob_mpv, odd):
    return (prob_mpv * odd) - 1

def determinar_selo(edge, dif_mpv, desvio_ima):
    if dif_mpv > PARAMS['limiar_confianca_alta'] and desvio_ima <= PARAMS['limiar_estabilidade_alta']:
        confianca = 'alta'
    elif dif_mpv > PARAMS['limiar_confianca_media'] and desvio_ima <= PARAMS['limiar_estabilidade_media']:
        confianca = 'media'
    else:
        confianca = 'baixa'
    if edge >= PARAMS['edge_dourado'] and confianca == 'alta':
        return '🥇 Dourado'
    elif edge >= PARAMS['edge_verde'] and confianca in ('alta', 'media'):
        return '🟢 Verde'
    elif edge > 0:
        return '⚪ Marginal'
    else:
        return '🔴 Sem Valor'
