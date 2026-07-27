import json

CONFIG_LIGAS_PATH = 'config_ligas.json'

def _carregar_config_ligas():
    with open(CONFIG_LIGAS_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def _obter_promovidos_ordenados(liga: str, temporada: int) -> List[str]:
    config = _carregar_config_ligas()
    return config.get(liga, {}).get(str(temporada), {}).get('promovidos', [])

def _obter_rebaixados(liga: str, temporada: int) -> List[str]:
    config = _carregar_config_ligas()
    return config.get(liga, {}).get(str(temporada), {}).get('rebaixados', [])
