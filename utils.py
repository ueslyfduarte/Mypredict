# utils.py — MyPredict 2.0 (funções utilitárias)
def para_float(valor_str):
    if valor_str is None or valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        return None

def extrair_jogos(texto):
    jogos = []
    for linha in texto.split('\n'):
        linha = linha.strip()
        if not linha: continue
        partes = [p.strip() for p in linha.split(',')]
        if len(partes) == 3 and partes[0] in ('V','E','D') and partes[2].upper() in ('S','N'):
            jogos.append({"resultado": partes[0], "adversario": partes[1], "mandante": partes[2].upper() == 'S'})
    if len(jogos) >= 10: return jogos
    for linha in texto.split('\n'):
        linha = linha.strip()
        if not linha: continue
        partes = [p.strip() for p in linha.split(',')]
        if len(partes) >= 30:
            for i in range(0, len(partes)-2, 3):
                res = partes[i]; adv = partes[i+1]; mand = partes[i+2]
                if res in ('V','E','D') and mand.upper() in ('S','N'):
                    jogos.append({"resultado": res, "adversario": adv, "mandante": mand.upper() == 'S'})
            break
    return jogos
