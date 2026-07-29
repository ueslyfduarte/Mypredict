# utils.py
def para_float(valor_str):
    if valor_str is None or valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        return None

def extrair_jogos(texto):
    jogos = []
    texto_limpo = texto.replace('\n', ',').replace(' ', ',')
    partes = [p.strip() for p in texto_limpo.split(',') if p.strip()]
    i = 0
    while i + 2 < len(partes):
        res = partes[i]
        adv = partes[i+1]
        mand = partes[i+2]
        if res in ('V','v','E','e','D','d') and mand.upper() in ('S','N'):
            jogos.append({
                "resultado": res.upper(),
                "adversario": adv,
                "mandante": mand.upper() == 'S'
            })
            i += 3
        else:
            i += 1
    return jogos
