import pickle
import numpy as np
from core.ratings import calcular_ima, calcular_ovrall, calcular_ic, calcular_mpv, obter_prateleira, _percentil
from core.elo import calcular_elo, normalizar_elo
from config import MEDIA_GOLS_CASA_LIGA, MEDIA_GOLS_FORA_LIGA, FATOR_SUPERACAO, ELO_WEIGHT, ELO_K

from core.tactical_dimensions import compute_all_dimensions, modulate_with_context, compute_mpv
from core.market_engine_v2 import (
    predict_over25, predict_btts, predict_1x2, predict_ht_goal, predict_corners
)
from core.markets import (
    prob_over_2_5, prob_ambas_marcam, prob_gol_ht, prob_over_escanteios,
    _gols_esperados
)

try:
    from core.contrast import contrast_vector, critical_routes, generate_heatmap
    CONTRAST_AVAILABLE = True
except ImportError:
    CONTRAST_AVAILABLE = False

def _build_stats_for_dimensions(ovrall_dict):
    return {
        'gols_media': ovrall_dict.get('gols_media', 1.4),
        'gols_sofridos_media': ovrall_dict.get('gols_sofridos_media', 1.4),
        'chutes_media': ovrall_dict.get('chutes_media', 12),
        'chutes_alvo_media': ovrall_dict.get('finalizacoes_alvo_media', 4.5),
        'chutes_alvo_sofridos_media': ovrall_dict.get('finalizacoes_alvo_sofridas_media', 4.5),
        'escanteios_media': ovrall_dict.get('escanteios_media', 5.0),
        'posse_media': ovrall_dict.get('posse_media', 50.0),
        'conversao': ovrall_dict.get('conversao', 0.25),
        'gols_escanteio': ovrall_dict.get('gols_escanteio', 0.36),
        'gols_sofridos_escanteio': ovrall_dict.get('gols_sofridos_escanteio', 0.21),
    }

def aproveitamento_contra_prateleira(jogos, prateleira_alvo):
    if not jogos:
        return 50.0
    jogos_alvo = [j for j in jogos if j.get('prateleira_adv') == prateleira_alvo]
    if len(jogos_alvo) >= 3:
        pontos = sum(3 if j['resultado'] == 'V' else 1 if j['resultado'] == 'E' else 0 for j in jogos_alvo)
        return (pontos / (len(jogos_alvo) * 3)) * 100
    else:
        total = jogos[:10]
        pontos = sum(3 if j['resultado'] == 'V' else 1 if j['resultado'] == 'E' else 0 for j in total)
        return (pontos / (len(total) * 3)) * 100 if total else 50.0

def classificar_estilo(stats, benchmarks):
    posse = stats.get('posse_media', 50)
    gols = stats.get('gols_media', 1.4)
    gols_sofridos = stats.get('gols_sofridos_media', 1.4)
    finalizacoes = stats.get('finalizacoes_alvo_media', 4.5)
    escanteios = stats.get('escanteios_media', 5.0)
    gols_esc = stats.get('gols_escanteio', 0.36)
    conversao = stats.get('conversao', 0.25)
    passes_certos = stats.get('passes_certos_pct', 78)
    passes_chave = stats.get('passes_chave_media', 2)
    assistencias = stats.get('assistencias_media', 1.2)

    posse_efetiva = (gols / posse) * 100 if posse > 0 else 0
    eficiencia = gols / finalizacoes if finalizacoes > 0 else 0
    vulnerabilidade = (gols_sofridos / (100 - posse)) * 100 if (100 - posse) > 0 else 0
    dependencia_bp = gols_esc / gols if gols > 0 else 0

    estilo = "Equilibrado"
    if posse > 55 and finalizacoes > 5 and passes_certos > 80:
        estilo = "Posse & Pressão"
    elif posse > 52 and passes_certos > 82 and passes_chave > 2.5 and assistencias > 1.5:
        estilo = "Controle de Meio‑Campo"
    elif posse < 45 and posse_efetiva > 0.07:
        estilo = "Contra‑Ataque"
    elif dependencia_bp > 0.25:
        estilo = "Aéreo / Bola Parada"
    elif posse < 40 and gols_sofridos < 1.0:
        estilo = "Defensivo / Reativo"

    return {
        'estilo': estilo,
        'posse_efetiva': round(posse_efetiva, 2),
        'eficiencia_finalizacao': round(eficiencia, 2),
        'vulnerabilidade_transicao': round(vulnerabilidade, 2),
        'dependencia_bola_parada': round(dependencia_bp, 2),
    }

def gerar_cenario(estilo_casa, estilo_fora, res_mercados):
    nome_casa = res_mercados['time_casa']
    nome_fora = res_mercados['time_fora']
    over = res_mercados['over25']
    btts = res_mercados['btts']
    gol_ht = res_mercados['gol_ht']
    esc = res_mercados['esc']
    p1 = res_mercados['p1']
    p2 = res_mercados['p2']

    texto = f"**🔮 Cenário Tático:** {nome_casa} ({estilo_casa}) vs {nome_fora} ({estilo_fora})\n\n"

    if estilo_casa == "Posse & Pressão" and estilo_fora == "Contra‑Ataque":
        texto += (f"⚽ O {nome_casa} deve controlar a posse e pressionar, enquanto o {nome_fora} aposta em transições. ")
        if btts >= 0.55: texto += "**Ambas Marcam** e **Over 2.5 Gols** são favorecidos."
        else: texto += "O **Over 2.5 Gols** pode ter valor."
    elif estilo_casa == "Controle de Meio‑Campo" and estilo_fora == "Posse & Pressão":
        texto += (f"🧠 O {nome_casa} tentará controlar o meio‑campo, enquanto o {nome_fora} pressiona alto. ")
        if esc >= 0.55: texto += "**Over 8.5 Escanteios** pode ser interessante. "
        if over < 0.50: texto += "O jogo pode ter menos gols que o esperado (**Under 2.5**)."
    elif estilo_casa == "Contra‑Ataque" and estilo_fora == "Posse & Pressão":
        texto += (f"🔄 Situação inversa: o {nome_fora} terá a posse, o {nome_casa} será perigoso nos contra‑ataques. ")
        if over >= 0.60: texto += "**Over 2.5 Gols** surge como opção. "
        if gol_ht >= 0.50: texto += "**Gol no 1º Tempo** também merece atenção. "
    elif estilo_casa == "Posse & Pressão" and estilo_fora == "Posse & Pressão":
        texto += (f"🔥 Ambos gostam de ter a bola. Meio‑campo disputado. ")
        if esc >= 0.55: texto += f"**Over 8.5 Escanteios** é interessante. "
        if over < 0.50: texto += "**Under 2.5 Gols** pode ter valor. "
    elif estilo_casa == "Contra‑Ataque" and estilo_fora == "Contra‑Ataque":
        texto += (f"⚡ Jogo de transições rápidas! ")
        if over >= 0.60 and btts >= 0.60: texto += "**Over 2.5 Gols** e **BTTS** fortemente favorecidos. "
    elif estilo_casa == "Aéreo / Bola Parada" or estilo_fora == "Aéreo / Bola Parada":
        texto += (f"🎯 Pelo menos um time depende de jogadas aéreas. ")
        if esc >= 0.55: texto += f"**Over 8.5 Escanteios** ganha destaque. "
    else:
        texto += (f"⚖️ Confronto equilibrado. Probabilidades: 🏠 {p1:.1%}, 🤝 {res_mercados['pX']:.1%}, 🏟️ {p2:.1%}. ")

    texto += "\n\n**📊 Indicadores Derivados:**\n"
    texto += f"- {nome_casa}: Posse Efetiva {res_mercados['estilo_casa']['posse_efetiva']:.2f} (gols/%posse), "
    texto += f"Eficiência Finalização {res_mercados['estilo_casa']['eficiencia_finalizacao']:.2f} (gols/finalizações alvo), "
    texto += f"Vulnerabilidade Transição {res_mercados['estilo_casa']['vulnerabilidade_transicao']:.2f} (gols sofridos/% sem posse), "
    texto += f"Dep. Bola Parada {res_mercados['estilo_casa']['dependencia_bola_parada']:.2%} (gols escanteio/total gols)\n"
    texto += f"- {nome_fora}: Posse Efetiva {res_mercados['estilo_fora']['posse_efetiva']:.2f}, "
    texto += f"Eficiência {res_mercados['estilo_fora']['eficiencia_finalizacao']:.2f}, "
    texto += f"Vulnerabilidade {res_mercados['estilo_fora']['vulnerabilidade_transicao']:.2f}, "
    texto += f"Dep. Bola Parada {res_mercados['estilo_fora']['dependencia_bola_parada']:.2%}"

    return texto

def compute_style_impact(estilo_casa, estilo_fora):
    impact_map = {
        ('Posse & Pressão', 'Posse & Pressão'): {'over25': 0.05, 'btts': 0.04, 'gol_ht': 0.03, 'esc': 0.08},
        ('Posse & Pressão', 'Contra‑Ataque'): {'over25': 0.08, 'btts': 0.07, 'gol_ht': 0.04, 'esc': 0.03},
        ('Posse & Pressão', 'Aéreo / Bola Parada'): {'over25': 0.04, 'btts': 0.03, 'gol_ht': 0.02, 'esc': 0.07},
        ('Posse & Pressão', 'Controle de Meio‑Campo'): {'over25': 0.03, 'btts': 0.02, 'gol_ht': 0.02, 'esc': 0.05},
        ('Posse & Pressão', 'Defensivo / Reativo'): {'over25': -0.05, 'btts': -0.04, 'gol_ht': -0.02, 'esc': -0.04},
        ('Contra‑Ataque', 'Posse & Pressão'): {'over25': 0.08, 'btts': 0.07, 'gol_ht': 0.04, 'esc': 0.03},
        ('Contra‑Ataque', 'Contra‑Ataque'): {'over25': 0.10, 'btts': 0.09, 'gol_ht': 0.05, 'esc': 0.02},
        ('Contra‑Ataque', 'Aéreo / Bola Parada'): {'over25': 0.06, 'btts': 0.05, 'gol_ht': 0.03, 'esc': 0.06},
        ('Contra‑Ataque', 'Controle de Meio‑Campo'): {'over25': 0.07, 'btts': 0.06, 'gol_ht': 0.03, 'esc': 0.04},
        ('Contra‑Ataque', 'Defensivo / Reativo'): {'over25': 0.02, 'btts': 0.01, 'gol_ht': 0.01, 'esc': -0.05},
        ('Aéreo / Bola Parada', 'Posse & Pressão'): {'over25': 0.04, 'btts': 0.03, 'gol_ht': 0.02, 'esc': 0.07},
        ('Aéreo / Bola Parada', 'Contra‑Ataque'): {'over25': 0.06, 'btts': 0.05, 'gol_ht': 0.03, 'esc': 0.06},
        ('Aéreo / Bola Parada', 'Aéreo / Bola Parada'): {'over25': 0.05, 'btts': 0.04, 'gol_ht': 0.02, 'esc': 0.12},
        ('Aéreo / Bola Parada', 'Controle de Meio‑Campo'): {'over25': 0.03, 'btts': 0.02, 'gol_ht': 0.02, 'esc': 0.08},
        ('Aéreo / Bola Parada', 'Defensivo / Reativo'): {'over25': -0.02, 'btts': -0.02, 'gol_ht': -0.01, 'esc': 0.04},
        ('Controle de Meio‑Campo', 'Posse & Pressão'): {'over25': 0.03, 'btts': 0.02, 'gol_ht': 0.02, 'esc': 0.05},
        ('Controle de Meio‑Campo', 'Contra‑Ataque'): {'over25': 0.07, 'btts': 0.06, 'gol_ht': 0.03, 'esc': 0.04},
        ('Controle de Meio‑Campo', 'Aéreo / Bola Parada'): {'over25': 0.03, 'btts': 0.02, 'gol_ht': 0.02, 'esc': 0.08},
        ('Controle de Meio‑Campo', 'Controle de Meio‑Campo'): {'over25': 0.02, 'btts': 0.02, 'gol_ht': 0.01, 'esc': 0.05},
        ('Controle de Meio‑Campo', 'Defensivo / Reativo'): {'over25': -0.04, 'btts': -0.03, 'gol_ht': -0.02, 'esc': 0.02},
        ('Defensivo / Reativo', 'Posse & Pressão'): {'over25': -0.05, 'btts': -0.04, 'gol_ht': -0.02, 'esc': -0.04},
        ('Defensivo / Reativo', 'Contra‑Ataque'): {'over25': 0.02, 'btts': 0.01, 'gol_ht': 0.01, 'esc': -0.05},
        ('Defensivo / Reativo', 'Aéreo / Bola Parada'): {'over25': -0.02, 'btts': -0.02, 'gol_ht': -0.01, 'esc': 0.04},
        ('Defensivo / Reativo', 'Controle de Meio‑Campo'): {'over25': -0.04, 'btts': -0.03, 'gol_ht': -0.02, 'esc': 0.02},
        ('Defensivo / Reativo', 'Defensivo / Reativo'): {'over25': -0.08, 'btts': -0.07, 'gol_ht': -0.04, 'esc': -0.06},
        ('Equilibrado', 'Equilibrado'): {'over25': 0.0, 'btts': 0.0, 'gol_ht': 0.0, 'esc': 0.0},
    }
    key = (estilo_casa, estilo_fora)
    impact = impact_map.get(key, {'over25': 0.0, 'btts': 0.0, 'gol_ht': 0.0, 'esc': 0.0})
    text = f"**Impacto dos Estilos:**\n"
    for mercado, ajuste in impact.items():
        if ajuste > 0: text += f"- {mercado}: +{ajuste*100:.0f}% (favorecido)\n"
        elif ajuste < 0: text += f"- {mercado}: {ajuste*100:.0f}% (desfavorecido)\n"
        else: text += f"- {mercado}: sem influência\n"
    return impact, text

def executar_manual(dados, pkl_path='calibration_params.pkl', modo_livre=False):
    # --- Benchmarks ---
    if dados.get('benchmarks_usr'):
        benchmarks = dados['benchmarks_usr']
    else:
        if not modo_livre:
            try:
                with open(pkl_path, 'rb') as f:
                    calib = pickle.load(f)
                benchmarks = calib['benchmarks']
            except:
                benchmarks = {}
        else:
            benchmarks = {}

    # --- Prateleiras (para superação e IC) ---
    prat_proj_casa = dados.get('prat_casa', 'Media')
    prat_proj_fora = dados.get('prat_fora', 'Media')
    prat_real_casa = obter_prateleira(dados['pos_casa'])
    prat_real_fora = obter_prateleira(dados['pos_fora'])
    prateleiras = {dados['time_casa']: prat_proj_casa, dados['time_fora']: prat_proj_fora}
    for j in dados.get('jogos_casa', []) + dados.get('jogos_fora', []):
        prat_adv = j.get('prateleira_adv', 'Media')
        nome_adv = j.get('adversario', '')
        if nome_adv and nome_adv not in prateleiras: prateleiras[nome_adv] = prat_adv
    for adv, prat in dados.get('prateleiras_extra', {}).items():
        if adv not in prateleiras: prateleiras[adv] = prat

    # --- IMA ---
    odds = dados.get('odds', {})
    odd_casa = odds.get('odd_casa', 2.0)
    odd_empate = odds.get('odd_empate', 3.5)
    odd_fora = odds.get('odd_fora', 3.8)
    n_jogos_ima = dados.get('n_jogos_ima', 5)

    jogos_casa_mandante = [j for j in dados.get('jogos_casa', []) if j.get('mandante', True)]
    ima_casa = calcular_ima(odd_casa, odd_empate, odd_fora, jogos_casa_mandante[:n_jogos_ima])
    jogos_fora_visitante = [j for j in dados.get('jogos_fora', []) if not j.get('mandante', False)]
    ima_fora = calcular_ima(odd_fora, odd_empate, odd_casa, jogos_fora_visitante[:n_jogos_ima])

    def detalhes_ima(odd_t, odd_e, odd_a, jogos, ima_val):
        inv_t = 1/odd_t; inv_e = 1/odd_e; inv_a = 1/odd_a
        soma = inv_t + inv_e + inv_a
        E_atual = inv_t / soma
        if jogos:
            pts = sum(3 if j['resultado']=='V' else 1 if j['resultado']=='E' else 0 for j in jogos)
            A_real = pts / (len(jogos)*3) if jogos else 0
        else:
            A_real = 0
        delta = A_real - E_atual
        return {'E_atual': E_atual, 'A_real': A_real, 'delta': delta, 'jogos_utilizados': len(jogos)}

    ima_det_casa = detalhes_ima(odd_casa, odd_empate, odd_fora, jogos_casa_mandante[:n_jogos_ima], ima_casa)
    ima_det_fora = detalhes_ima(odd_fora, odd_empate, odd_casa, jogos_fora_visitante[:n_jogos_ima], ima_fora)

    # --- OVRall (NOVA VERSÃO ABSOLUTA) ---
    ovr_casa = dados.get('ovrall_casa', {}).copy()
    ovr_fora = dados.get('ovrall_fora', {}).copy()
    fator_liga = dados.get('fator_liga', 1.0)

    # Garantir que benchmarks_liga tenha as chaves necessárias (fallback para defaults)
    if not benchmarks:
        benchmarks = {
            'gols_media': {'mean': 1.4, 'std': 0.5, 'lower_better': False},
            'xg_media': {'mean': 1.3, 'std': 0.3, 'lower_better': False},
            'finalizacoes_alvo_media': {'mean': 4.0, 'std': 1.5, 'lower_better': False},
            'gols_sofridos_media': {'mean': 1.4, 'std': 0.5, 'lower_better': True},
            'xga_media': {'mean': 1.2, 'std': 0.3, 'lower_better': True},
            'desarmes_intercep_media': {'mean': 15.0, 'std': 4.0, 'lower_better': False},
            'posse_media': {'mean': 50.0, 'std': 10.0, 'lower_better': False},
            'passes_certos_pct': {'mean': 78.0, 'std': 6.0, 'lower_better': False},
            'passes_chave_media': {'mean': 2.0, 'std': 0.8, 'lower_better': False},
            'desvio_pontos': {'mean': 0.5, 'std': 0.2, 'lower_better': True},
            'clean_sheets_pct': {'mean': 30.0, 'std': 15.0, 'lower_better': False},
            'pontos_pos_desvantagem_media': {'mean': 1.0, 'std': 0.5, 'lower_better': False},
            'gols_ultimos_15min_media': {'mean': 0.3, 'std': 0.2, 'lower_better': False},
        }

    ovrall_val_casa = calcular_ovrall(ovr_casa, benchmarks, fator_liga)
    ovrall_val_fora = calcular_ovrall(ovr_fora, benchmarks, fator_liga)

    # Detalhamento do OVRall (notas individuais)
    def detalhes_ovr_absoluto(dados_time, benchmarks_liga):
        dims = {
            'Ataque': [('gols_media', False), ('xg_media', False), ('finalizacoes_alvo_media', False)],
            'Defesa': [('gols_sofridos_media', True), ('xga_media', True), ('desarmes_intercep_media', False)],
            'MeioCampo': [('posse_media', False), ('passes_certos_pct', False), ('passes_chave_media', False)],
            'Consistencia': [('desvio_pontos', True), ('clean_sheets_pct', False)],
            'Resiliencia': [('pontos_pos_desvantagem_media', False), ('gols_ultimos_15min_media', False)],
        }
        detalhes = {}
        for dim, indicadores in dims.items():
            notas = []
            for ind, menor_melhor in indicadores:
                if ind in dados_time and ind in benchmarks_liga:
                    val = dados_time[ind]
                    b = benchmarks_liga[ind]
                    if b['std'] > 0:
                        z = (val - b['mean']) / b['std']
                    else:
                        z = 0.0
                    if menor_melhor:
                        z = -z
                    nota = 100.0 / (1.0 + np.exp(-1.5 * z))
                    notas.append((ind, val, nota))
            if notas:
                nota_dim = sum(n[2] for n in notas) / len(notas)
                detalhes[dim] = {'indicadores': notas, 'nota_media': nota_dim}
        return detalhes

    detalhes_ovr_casa = detalhes_ovr_absoluto(ovr_casa, benchmarks)
    detalhes_ovr_fora = detalhes_ovr_absoluto(ovr_fora, benchmarks)

    notas_casa = {dim: d['nota_media'] for dim, d in detalhes_ovr_casa.items()}
    notas_fora = {dim: d['nota_media'] for dim, d in detalhes_ovr_fora.items()}

    # --- IC ---
    ic_casa = dados.get('ic_casa', {})
    ic_fora = dados.get('ic_fora', {})
    ic_casa['contra_escalao_adversario'] = aproveitamento_contra_prateleira(dados.get('jogos_casa', []), prat_real_fora) / 100.0
    ic_fora['contra_escalao_adversario'] = aproveitamento_contra_prateleira(dados.get('jogos_fora', []), prat_real_casa) / 100.0
    ic_val_casa = calcular_ic(ic_casa)
    ic_val_fora = calcular_ic(ic_fora)

    # --- MPV base ---
    mpv_base_casa = calcular_mpv(ima_casa, ovrall_val_casa, ic_val_casa)
    mpv_base_fora = calcular_mpv(ima_fora, ovrall_val_fora, ic_val_fora)

    # --- Superação ---
    niveis = {'Elite':5, 'Alta':4, 'Media':3, 'Baixa':2, 'Critica':1}
    def fator_superacao(prat_real, prat_projetada):
        diff = niveis.get(prat_real, 3) - niveis.get(prat_projetada, 3)
        return diff * FATOR_SUPERACAO
    superacao_casa = fator_superacao(prat_real_casa, prat_proj_casa)
    superacao_fora = fator_superacao(prat_real_fora, prat_proj_fora)
    mpv_base_casa += max(-10.0, min(10.0, superacao_casa))
    mpv_base_fora += max(-10.0, min(10.0, superacao_fora))

    # --- ELO ---
    elo_casa = calcular_elo(dados['time_casa'], dados.get('jogos_casa', []), prateleiras, k=ELO_K)
    elo_fora = calcular_elo(dados['time_fora'], dados.get('jogos_fora', []), prateleiras, k=ELO_K)
    elos_liga = [elo_casa, elo_fora]
    elo_norm_casa = normalizar_elo(elo_casa, elos_liga)
    elo_norm_fora = normalizar_elo(elo_fora, elos_liga)

    mpv_casa = ELO_WEIGHT * elo_norm_casa + (1 - ELO_WEIGHT) * mpv_base_casa
    mpv_fora = ELO_WEIGHT * elo_norm_fora + (1 - ELO_WEIGHT) * mpv_base_fora

    # --- Probabilidades 1X2 ---
    diff_aprov = ovr_casa.get('diff_aprov_casa_fora', 0)
    bonus_casa = 0.0
    if abs(mpv_casa - mpv_fora) < 10 and diff_aprov > 5:
        bonus_casa = min(0.05, diff_aprov / 200.0)

    delta_mpv = mpv_casa - mpv_fora
    if delta_mpv == 0:
        p_casa = 0.5
    else:
        p_casa = 0.5 + (delta_mpv / 50.0) * 0.3
        p_casa = max(0.1, min(0.9, p_casa))

    p_casa += bonus_casa
    p_fora = 1.0 - p_casa
    p_empate = 0.28 * np.exp(- (abs(delta_mpv) / 15.0) ** 2)

    total = p_casa + p_empate + p_fora
    p1_orig = p_casa / total
    pX_orig = p_empate / total
    p2_orig = p_fora / total

    # --- Demais probabilidades originais ---
    gols_media_casa = ovr_casa.get('gols_media', 1.5)
    gols_media_fora = ovr_fora.get('gols_media', 1.2)
    gols_sofridos_casa = ovr_casa.get('gols_sofridos_media', 1.2)
    gols_sofridos_fora = ovr_fora.get('gols_sofridos_media', 1.5)
    over25_orig = prob_over_2_5(gols_media_casa, gols_media_fora, gols_sofridos_casa, gols_sofridos_fora)

    media_gols_casa_liga = dados.get('media_gols_casa', MEDIA_GOLS_CASA_LIGA)
    media_gols_fora_liga = dados.get('media_gols_fora', MEDIA_GOLS_FORA_LIGA)
    gols_esp_casa = _gols_esperados(gols_media_casa, gols_sofridos_fora, media_gols_fora_liga)
    gols_esp_fora = _gols_esperados(gols_media_fora, gols_sofridos_casa, media_gols_casa_liga)
    btts_orig = prob_ambas_marcam(gols_esp_casa, gols_esp_fora)

    gol_ht_orig = prob_gol_ht(
        ovr_casa.get('gols_ht_media', 0.5) or 0.5, ovr_fora.get('gols_ht_media', 0.5) or 0.5,
        ovr_casa.get('gols_ht_sofridos_media', 0.5) or 0.5, ovr_fora.get('gols_ht_sofridos_media', 0.5) or 0.5
    )
    esc_orig = prob_over_escanteios(
        ovr_casa.get('escanteios_media', 5.0) or 5.0, ovr_fora.get('escanteios_media', 5.0) or 5.0,
        ovr_casa.get('escanteios_sofridos_media', 5.0) or 5.0, ovr_fora.get('escanteios_sofridos_media', 5.0) or 5.0
    )

    # --- Dimensões táticas ---
    dimension_weights = {}
    if not modo_livre and not dados.get('benchmarks_usr'):
        try:
            with open(pkl_path, 'rb') as f:
                calib = pickle.load(f)
            benchmarks = calib.get('benchmarks', benchmarks)
            dimension_weights = calib.get('dimension_weights', {})
        except: pass

    stats_casa = _build_stats_for_dimensions(ovr_casa)
    stats_fora = _build_stats_for_dimensions(ovr_fora)

    INDICATORS_MAP = {
        'ataque_posicional': ['gols_media', 'chutes_alvo_media', 'conversao'],
        'ataque_transicao': [],
        'defesa_organizada': ['gols_sofridos_media', 'chutes_alvo_sofridos_media'],
        'defesa_transicao': [],
        'bola_parada_ofensiva': ['gols_escanteio'],
        'bola_parada_defensiva': ['gols_sofridos_escanteio'],
        'controle_meio_campo': ['posse_media'],
        'pressao_alta': [],
        'resistencia_pressao': [],
    }

    dims_casa_raw = compute_all_dimensions(stats_casa, INDICATORS_MAP, benchmarks)
    dims_fora_raw = compute_all_dimensions(stats_fora, INDICATORS_MAP, benchmarks)

    dims_casa_mod = modulate_with_context(dims_casa_raw, ima_casa, ic_val_casa)
    dims_fora_mod = modulate_with_context(dims_fora_raw, ima_fora, ic_val_fora)

    mpv_tactical_casa = compute_mpv(dims_casa_mod, dimension_weights) if dimension_weights else 50.0
    mpv_tactical_fora = compute_mpv(dims_fora_mod, dimension_weights) if dimension_weights else 50.0

    # --- Modelo calibrado ---
    adv_probs_1x2 = None; adv_over25 = None; adv_btts = None; adv_ht = None; adv_esc = None
    if not modo_livre:
        adv_probs_1x2 = predict_1x2(mpv_tactical_casa, mpv_tactical_fora, ovrall_val_casa, ovrall_val_fora, ic_val_casa, ic_val_fora, elo_norm_casa, elo_norm_fora, superacao_casa, superacao_fora)
        adv_over25 = predict_over25(dims_casa_mod, dims_fora_mod, ovrall_val_casa, ovrall_val_fora, ic_val_casa, ic_val_fora, elo_norm_casa, elo_norm_fora, superacao_casa, superacao_fora, gols_media_casa, gols_media_fora, gols_sofridos_casa, gols_sofridos_fora, media_gols_casa_liga, media_gols_fora_liga)
        adv_btts = predict_btts(dims_casa_mod, dims_fora_mod, ovrall_val_casa, ovrall_val_fora, ic_val_casa, ic_val_fora, elo_norm_casa, elo_norm_fora, superacao_casa, superacao_fora, gols_media_casa, gols_media_fora, gols_sofridos_casa, gols_sofridos_fora, media_gols_casa_liga, media_gols_fora_liga)
        adv_ht = predict_ht_goal(dims_casa_mod, dims_fora_mod, ovrall_val_casa, ovrall_val_fora, ic_val_casa, ic_val_fora, elo_norm_casa, elo_norm_fora, superacao_casa, superacao_fora, ovr_casa.get('gols_ht_media', 0.5) or 0.5, ovr_fora.get('gols_ht_media', 0.5) or 0.5, ovr_casa.get('gols_ht_sofridos_media', 0.5) or 0.5, ovr_fora.get('gols_ht_sofridos_media', 0.5) or 0.5)
        adv_esc = predict_corners(dims_casa_mod, dims_fora_mod, ovrall_val_casa, ovrall_val_fora, ic_val_casa, ic_val_fora, elo_norm_casa, elo_norm_fora, superacao_casa, superacao_fora, ovr_casa.get('escanteios_media', 5.0) or 5.0, ovr_fora.get('escanteios_media', 5.0) or 5.0, ovr_casa.get('escanteios_sofridos_media', 5.0) or 5.0, ovr_fora.get('escanteios_sofridos_media', 5.0) or 5.0)

    # --- Probabilidades médias ---
    def media_prob(orig, adv):
        if modo_livre or adv is None: return orig
        return (orig + adv) / 2.0

    p1 = media_prob(p1_orig, adv_probs_1x2['casa'] if adv_probs_1x2 else None)
    pX = media_prob(pX_orig, adv_probs_1x2['empate'] if adv_probs_1x2 else None)
    p2 = media_prob(p2_orig, adv_probs_1x2['fora'] if adv_probs_1x2 else None)
    over25 = media_prob(over25_orig, adv_over25)
    btts = media_prob(btts_orig, adv_btts)
    gol_ht = media_prob(gol_ht_orig, adv_ht)
    esc = media_prob(esc_orig, adv_esc)

    # --- Contraste tático ---
    deltas = {}; routes = []; heatmap_img = None
    if CONTRAST_AVAILABLE and dims_casa_mod and dims_fora_mod:
        deltas = contrast_vector(dims_casa_mod, dims_fora_mod)
        routes = critical_routes(deltas)
        heatmap_img = generate_heatmap(deltas)

    # --- Edge Score ---
    edges = {}
    if odd_casa and odd_empate and odd_fora:
        impl_c = 1 / odd_casa; impl_e = 1 / odd_empate; impl_f = 1 / odd_fora
        total_impl = impl_c + impl_e + impl_f
        edges['edge_casa'] = p1 - (impl_c / total_impl)
        edges['edge_empate'] = pX - (impl_e / total_impl)
        edges['edge_fora'] = p2 - (impl_f / total_impl)
    if odds.get('odd_over'): edges['edge_over'] = over25 - (1 / odds['odd_over'])
    if odds.get('odd_btts'): edges['edge_btts'] = btts - (1 / odds['odd_btts'])
    if odds.get('odd_ht'):   edges['edge_ht'] = gol_ht - (1 / odds['odd_ht'])
    if odds.get('odd_esc'):  edges['edge_esc'] = esc - (1 / odds['odd_esc'])

    # --- Estilos e cenário ---
    estilo_casa = classificar_estilo(ovr_casa, benchmarks)
    estilo_fora = classificar_estilo(ovr_fora, benchmarks)
    texto_cenario = gerar_cenario(estilo_casa['estilo'], estilo_fora['estilo'], {'time_casa': dados['time_casa'], 'time_fora': dados['time_fora'], 'over25': over25, 'btts': btts, 'gol_ht': gol_ht, 'esc': esc, 'p1': p1, 'pX': pX, 'p2': p2, 'estilo_casa': estilo_casa, 'estilo_fora': estilo_fora})
    style_impact, style_impact_text = compute_style_impact(estilo_casa['estilo'], estilo_fora['estilo'])
    adj_over25 = max(0, min(1, over25 + style_impact.get('over25', 0)))
    adj_btts = max(0, min(1, btts + style_impact.get('btts', 0)))
    adj_gol_ht = max(0, min(1, gol_ht + style_impact.get('gol_ht', 0)))
    adj_esc = max(0, min(1, esc + style_impact.get('esc', 0)))

    # --- Resultado final ---
    res = {
        'time_casa': dados['time_casa'], 'time_fora': dados['time_fora'],
        'p1': p1, 'pX': pX, 'p2': p2,
        'over25': over25, 'btts': btts, 'gol_ht': gol_ht, 'esc': esc,
        'adj_over25': adj_over25, 'adj_btts': adj_btts, 'adj_gol_ht': adj_gol_ht, 'adj_esc': adj_esc,
        'style_impact': style_impact, 'style_impact_text': style_impact_text,
        'p1_orig': p1_orig, 'pX_orig': pX_orig, 'p2_orig': p2_orig,
        'over25_orig': over25_orig, 'btts_orig': btts_orig,
        'gol_ht_orig': gol_ht_orig, 'esc_orig': esc_orig,
        'p1_adv': adv_probs_1x2['casa'] if adv_probs_1x2 else None,
        'pX_adv': adv_probs_1x2['empate'] if adv_probs_1x2 else None,
        'p2_adv': adv_probs_1x2['fora'] if adv_probs_1x2 else None,
        'over25_adv': adv_over25, 'btts_adv': adv_btts,
        'gol_ht_adv': adv_ht, 'esc_adv': adv_esc,
        'ima_casa': ima_casa, 'ima_fora': ima_fora,
        'mpv_casa': mpv_casa, 'mpv_fora': mpv_fora,
        'ovrall_casa': ovrall_val_casa, 'ovrall_fora': ovrall_val_fora,
        'ic_casa': ic_val_casa, 'ic_fora': ic_val_fora,
        'notas_casa': notas_casa, 'notas_fora': notas_fora,
        'detalhes_ima': {'casa': ima_det_casa, 'fora': ima_det_fora},
        'detalhes_ovr': {'casa': detalhes_ovr_casa, 'fora': detalhes_ovr_fora},
        'prateleiras': prateleiras,
        'superacao_casa': superacao_casa, 'superacao_fora': superacao_fora,
        'prat_real_casa': prat_real_casa, 'prat_real_fora': prat_real_fora,
        'prat_proj_casa': prat_proj_casa, 'prat_proj_fora': prat_proj_fora,
        'elo_norm_casa': elo_norm_casa, 'elo_norm_fora': elo_norm_fora,
        'mpv_tactical_casa': mpv_tactical_casa, 'mpv_tactical_fora': mpv_tactical_fora,
        'tactical': {
            'dimensions_casa': dims_casa_mod,
            'dimensions_fora': dims_fora_mod,
            'deltas': deltas,
            'critical_routes': routes,
            'heatmap': heatmap_img,
        } if (CONTRAST_AVAILABLE and dims_casa_mod and dims_fora_mod) else None,
        'edges': edges,
        'benchmarks': benchmarks,
        'stats_casa': ovr_casa,
        'stats_fora': ovr_fora,
        'estilo_casa': estilo_casa,
        'estilo_fora': estilo_fora,
        'cenario': texto_cenario,
    }
    return res, None
