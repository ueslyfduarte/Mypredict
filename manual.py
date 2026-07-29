# manual.py — MyPredict 2.0 (parser funcional para texto corrido)
from ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira
from markets import (
    prob_1x2, prob_over_2_5, prob_ambas_marcam, prob_gol_ht,
    prob_over_escanteios, calcular_bonus_casa, _gols_esperados
)
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA
from utils import extrair_jogos, para_float

def processar_texto_ia(texto):
    texto = texto.replace('\n', ' ').strip()
    dados = {
        'time_casa': "", 'time_fora': "",
        'pos_casa': 1, 'pos_fora': 2,
        'jogos_casa': [], 'jogos_fora': [],
        'ovrall_casa': {}, 'ovrall_fora': {},
        'ic_casa': {}, 'ic_fora': {},
        'media_gols_casa': MEDIA_GOLS_CASA_LIGA, 'media_gols_fora': MEDIA_GOLS_FORA_LIGA,
        'media_ht_casa': 0.75, 'media_ht_fora': 0.65,
        'media_esc_casa': 5.0, 'media_esc_fora': 4.5,
        'prateleiras_extra': {}
    }

    # Divide por palavras-chave (ordem exata do texto)
    partes = texto.split("Time da casa:")
    if len(partes) > 1:
        restante = partes[1]
        # time_casa
        if "Time da fora:" in restante:
            dados['time_casa'] = restante.split("Time da fora:")[0].strip()
            restante = restante.split("Time da fora:", 1)[1]
        else:
            dados['time_casa'] = restante.strip()
            restante = ""

    if "Posições:" in restante:
        dados['time_fora'] = restante.split("Posições:")[0].strip()
        restante = restante.split("Posições:", 1)[1]
    else:
        dados['time_fora'] = restante.strip()
        restante = ""

    # Posições
    if "Casa:" in restante and "Fora:" in restante:
        p_casa = restante.split("Casa:")[1].split("Fora:")[0].strip()
        p_fora = restante.split("Fora:")[1].split("Últimos 10 jogos")[0].strip()
        try: dados['pos_casa'] = int(p_casa)
        except: pass
        try: dados['pos_fora'] = int(p_fora)
        except: pass

    # Jogos
    if "Últimos 10 jogos do time da casa:" in texto and "Últimos 10 jogos do time da fora:" in texto:
        jogos_casa_bruto = texto.split("Últimos 10 jogos do time da casa:")[1].split("Últimos 10 jogos do time da fora:")[0]
        jogos_fora_bruto = texto.split("Últimos 10 jogos do time da fora:")[1].split("Métricas OVRall")[0]
        dados['jogos_casa'] = extrair_jogos(jogos_casa_bruto)
        dados['jogos_fora'] = extrair_jogos(jogos_fora_bruto)

    # OVRall
    chaves_ovr = ["gols_media","gols_sofridos_media","xg_media","xga_media","finalizacoes_alvo_media","finalizacoes_alvo_sofridas_media","chutes_media","desarmes_intercep_media","posse_media","passes_certos_pct","passes_chave_media","assistencias_media","conversao","clean_sheets_pct","desvio_pontos","desvio_gols_pro","desvio_gols_sofridos","pontos_pos_desvantagem_media","gols_ultimos_15min_media","pontos_apos_derrota_media","diff_aprov_casa_fora","aprov_viradas_favor","aprov_viradas_contra"]
    for lado, marcador in [('ovrall_casa', 'Métricas OVRall do time da casa'), ('ovrall_fora', 'Métricas OVRall do time da fora')]:
        if marcador in texto:
            trecho = texto.split(marcador)[1]
            # Pega a primeira sequência de números e vírgulas
            nums = ""
            for c in trecho:
                if c in '0123456789.,-':
                    nums += c
                else:
                    if nums: break
            vals = [para_float(x) for x in nums.split(',') if x.strip()]
            for i, k in enumerate(chaves_ovr):
                if i < len(vals): dados[lado][k] = vals[i]

    # IC
    chaves_ic = ["confronto_direto","mesmo_escalao","contra_escalao_adversario","fator_casa","odds"]
    for lado, marcador in [('ic_casa', 'Métricas IC do time da casa'), ('ic_fora', 'Métricas IC do time da fora')]:
        if marcador in texto:
            trecho = texto.split(marcador)[1]
            nums = ""
            for c in trecho:
                if c in '0123456789.,-':
                    nums += c
                else:
                    if nums: break
            vals = [para_float(x) for x in nums.split(',') if x.strip()]
            for i, k in enumerate(chaves_ic):
                if i < len(vals): dados[lado][k] = vals[i]

    # Médias da Liga
    for nome, chave in [('Média gols casa:', 'media_gols_casa'), ('Média gols fora:', 'media_gols_fora'),
                        ('Média gols 1º tempo casa:', 'media_ht_casa'), ('Média gols 1º tempo fora:', 'media_ht_fora'),
                        ('Média escanteios casa:', 'media_esc_casa'), ('Média escanteios fora:', 'media_esc_fora')]:
        if nome in texto:
            val = texto.split(nome)[1].strip().split()[0]
            dados[chave] = para_float(val)

    # Prateleiras
    if "Prateleiras" in texto:
        trecho = texto.split("Prateleiras")[1]
        for item in trecho.split(','):
            if ':' in item:
                adv, prat = item.split(':', 1)
                dados['prateleiras_extra'][adv.strip()] = prat.strip()

    return dados

def executar_manual(dados):
    if len(dados['jogos_casa']) < 5 or len(dados['jogos_fora']) < 5:
        return None, f"Poucos jogos: Casa={len(dados['jogos_casa'])}, Fora={len(dados['jogos_fora'])}"
    if not dados['ovrall_casa'] or not dados['ovrall_fora']:
        return None, "Métricas OVRall não encontradas."

    prat_casa = obter_prateleira(dados['pos_casa'])
    prat_fora = obter_prateleira(dados['pos_fora'])
    prateleiras = {dados['time_casa']: prat_casa, dados['time_fora']: prat_fora}
    for j in dados['jogos_casa'] + dados['jogos_fora']:
        if j['adversario'] not in prateleiras:
            prateleiras[j['adversario']] = "Media"
    for adv, prat in dados.get('prateleiras_extra', {}).items():
        if adv in prateleiras:
            prateleiras[adv] = prat

    rec_casa = {
        '10G': dados['jogos_casa'][:10], '5G': dados['jogos_casa'][:5], '3G': dados['jogos_casa'][:3],
        '5CF': [j for j in dados['jogos_casa'] if j['mandante']][:5],
        '3CF': [j for j in dados['jogos_casa'] if j['mandante']][:3],
    }
    rec_fora = {
        '10G': dados['jogos_fora'][:10], '5G': dados['jogos_fora'][:5], '3G': dados['jogos_fora'][:3],
        '5CF': [j for j in dados['jogos_fora'] if j['mandante']][:5],
        '3CF': [j for j in dados['jogos_fora'] if j['mandante']][:3],
    }

    ima_casa = calcular_ima(dados['time_casa'], rec_casa['10G'], rec_casa['5G'], rec_casa['3G'],
                            rec_casa['5CF'], rec_casa['3CF'], prateleiras)
    ima_fora = calcular_ima(dados['time_fora'], rec_fora['10G'], rec_fora['5G'], rec_fora['3G'],
                            rec_fora['5CF'], rec_fora['3CF'], prateleiras)

    dados_liga = {k: [dados['ovrall_casa'].get(k, 0) or 0, dados['ovrall_fora'].get(k, 0) or 0] for k in set(dados['ovrall_casa']) | set(dados['ovrall_fora'])}
    ovrall_val_casa = calcular_ovrall(dados['ovrall_casa'], dados_liga)
    ovrall_val_fora = calcular_ovrall(dados['ovrall_fora'], dados_liga)

    dims = {
        'Ataque': [('gols_media', False), ('xg_media', False), ('finalizacoes_alvo_media', False), ('conversao', False)],
        'Defesa': [('gols_sofridos_media', True), ('xga_media', True), ('finalizacoes_alvo_sofridas_media', True), ('desarmes_intercep_media', False)],
        'MeioCampo': [('posse_media', False), ('passes_certos_pct', False), ('passes_chave_media', False), ('assistencias_media', False), ('chutes_media', False)],
        'Consistencia': [('desvio_pontos', True), ('desvio_gols_pro', True), ('desvio_gols_sofridos', True), ('clean_sheets_pct', False)],
        'Resiliencia': [('pontos_pos_desvantagem_media', False), ('gols_ultimos_15min_media', False), ('pontos_apos_derrota_media', False), ('diff_aprov_casa_fora', True), ('aprov_viradas_favor', False), ('aprov_viradas_contra', True)],
    }
    notas_casa = {}
    notas_fora = {}
    for nome, indicadores in dims.items():
        vals_c = []
        vals_f = []
        for ind, menor in indicadores:
            vc = dados['ovrall_casa'].get(ind)
            vf = dados['ovrall_fora'].get(ind)
            if vc is not None and vf is not None:
                lista = [vc, vf]
                from ratings import _percentil
                vals_c.append(_percentil(vc, lista, menor))
                vals_f.append(_percentil(vf, lista, menor))
        if vals_c:
            notas_casa[nome] = sum(vals_c) / len(vals_c)
            notas_fora[nome] = sum(vals_f) / len(vals_f)

    ic_val_casa = calcular_ic(dados['ic_casa'])
    ic_val_fora = calcular_ic(dados['ic_fora'])

    mpv_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
    mpv_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

    bonus_casa = calcular_bonus_casa(dados['ovrall_casa'].get('diff_aprov_casa_fora') or 0)
    p1, pX, p2 = prob_1x2(mpv_casa, mpv_fora, bonus_casa)

    over25 = prob_over_2_5(
        dados['ovrall_casa'].get('gols_media'), dados['ovrall_fora'].get('gols_media'),
        dados['ovrall_casa'].get('gols_sofridos_media'), dados['ovrall_fora'].get('gols_sofridos_media'),
        media_casa=dados.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA), media_fora=dados.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)
    )
    gols_esp_casa = _gols_esperados(dados['ovrall_casa'].get('gols_media'), dados['ovrall_fora'].get('gols_sofridos_media'), dados.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA))
    gols_esp_fora = _gols_esperados(dados['ovrall_fora'].get('gols_media'), dados['ovrall_casa'].get('gols_sofridos_media'), dados.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA))
    btts = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)
    gol_ht = prob_gol_ht(
        dados['ovrall_casa'].get('gols_ht_media', 0.5) or 0.5,
        dados['ovrall_fora'].get('gols_ht_media', 0.5) or 0.5,
        dados['ovrall_casa'].get('gols_ht_sofridos_media', 0.5) or 0.5,
        dados['ovrall_fora'].get('gols_ht_sofridos_media', 0.5) or 0.5,
        media_ht_casa=dados.get('media_ht_casa', 0.75), media_ht_fora=dados.get('media_ht_fora', 0.65)
    )
    esc = prob_over_escanteios(
        dados['ovrall_casa'].get('escanteios_media', 5.0) or 5.0,
        dados['ovrall_fora'].get('escanteios_media', 5.0) or 5.0,
        dados['ovrall_casa'].get('escanteios_sofridos_media', 5.0) or 5.0,
        dados['ovrall_fora'].get('escanteios_sofridos_media', 5.0) or 5.0,
        media_casa=dados.get('media_esc_casa', 5.0), media_fora=dados.get('media_esc_fora', 4.5)
    )

    return {
        'time_casa': dados['time_casa'], 'time_fora': dados['time_fora'],
        'p1': p1, 'pX': pX, 'p2': p2,
        'over25': over25, 'btts': btts, 'gol_ht': gol_ht, 'esc': esc,
        'ima_casa': ima_casa, 'ima_fora': ima_fora,
        'mpv_casa': mpv_casa, 'mpv_fora': mpv_fora,
        'ovrall_casa': ovrall_val_casa, 'ovrall_fora': ovrall_val_fora,
        'ic_casa': ic_val_casa, 'ic_fora': ic_val_fora,
        'notas_casa': notas_casa, 'notas_fora': notas_fora
    }, None
