# utils.py — MyPredict 2.0 (parser robusto)
def para_float(valor_str):
    if valor_str is None or valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        return None

def extrair_jogos(texto):
    jogos = []
    # Normaliza o texto: junta tudo em uma única linha e depois divide por vírgulas
    texto_limpo = texto.replace('\n', ',').replace(' ', '')
    partes = [p.strip() for p in texto_limpo.split(',') if p.strip()]

    # Agora percorre as partes em grupos de 3
    i = 0
    while i + 2 < len(partes):
        res = partes[i]
        adv = partes[i+1]
        mand = partes[i+2]
        # Verifica se parece um jogo válido
        if res in ('V','v','E','e','D','d') and mand.upper() in ('S','N'):
            jogos.append({
                "resultado": res.upper(),
                "adversario": adv,
                "mandante": mand.upper() == 'S'
            })
            i += 3
        else:
            i += 1  # avança um e tenta de novo

    return jogos
