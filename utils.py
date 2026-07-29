# utils.py — Funções utilitárias

def para_float(valor_str):
    """Converte string para float, aceitando vírgula como separador decimal."""
    if valor_str is None or valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        return None

def extrair_jogos(texto):
    """
    Extrai lista de jogos a partir de um texto formatado.
    Formato: "V Flamengo S" (resultado, adversário, mandante S/N)
    """
    jogos = []
    # Substitui quebras de linha e múltiplos espaços
    texto_limpo = texto.replace('\n', ' ').replace(',', ' ')
    partes = [p.strip() for p in texto_limpo.split() if p.strip()]
    i = 0
    while i + 2 < len(partes):
        res = partes[i]
        adv = partes[i+1]
        mand = partes[i+2]
        if res.upper() in ('V', 'E', 'D') and mand.upper() in ('S', 'N'):
            jogos.append({
                "resultado": res.upper(),
                "adversario": adv,
                "mandante": mand.upper() == 'S'
            })
            i += 3
        else:
            i += 1
    return jogos
