# data_loader.py — MyPredict 2.0 (trecho alterado)
# ... (importações e outras funções permanecem)

def _obter_promovidos_ordenados(liga_slug, temporada):
    """Retorna lista de promovidos da temporada atual (ordem alfabética)."""
    class_atual = classificação_anterior(liga_slug, temporada)
    class_ant = classificação_anterior(liga_slug, temporada - 1) if temporada > 2010 else {}
    if not class_ant:
        return []
    promovidos = [t for t in class_atual.values() if t not in class_ant.values()]
    return sorted(promovidos)  # ordem alfabética

def _obter_rebaixados(liga_slug, temporada):
    """Retorna lista de rebaixados da temporada anterior."""
    class_atual = classificação_anterior(liga_slug, temporada)
    class_ant = classificação_anterior(liga_slug, temporada - 1) if temporada > 2010 else {}
    if not class_ant:
        return []
    rebaixados = [t for t in class_ant.values() if t not in class_atual.values()]
    return rebaixados

def classificação_anterior(liga_slug, temporada):
    """Retorna classificação {pos: time} usando worldfootball."""
    from data_source_worldfootball import obter_classificacao as wf_class
    return wf_class(liga_slug, temporada)

def gerar_prateleiras(liga_slug, temporada):
    class_ant = classificação_anterior(liga_slug, temporada)
    if not class_ant:
        return {}
    promovidos = _obter_promovidos_ordenados(liga_slug, temporada)
    rebaixados = _obter_rebaixados(liga_slug, temporada - 1) if temporada > 2010 else []
    pos_rebaixados = sorted([pos for pos, time in class_ant.items() if time in rebaixados])
    nova_class = class_ant.copy()
    for i, time_prom in enumerate(promovidos):
        if i < len(pos_rebaixados):
            nova_class[pos_rebaixados[i]] = time_prom
    from ratings import obter_prateleira
    return {time: obter_prateleira(pos) for pos, time in nova_class.items()}

# As demais funções (carregar_jogos_temporada, obter_ultimos_jogos_com_heranca, etc.) 
# passam a receber liga_slug diretamente e usam as funções do worldfootball.
# Substitua todas as chamadas de 'liga' por 'liga_slug' onde aplicável.
