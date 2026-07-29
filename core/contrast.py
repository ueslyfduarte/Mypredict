# core/contrast.py
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from config import FIELD_ZONES

def contrast_vector(scores_a, scores_b):
    """
    Calcula o diferencial tático entre dois times.
    
    Returns:
        dict: {dimension: delta}
    """
    deltas = {}
    for dim in scores_a.keys():
        deltas[dim] = scores_a[dim] - scores_b[dim]
    return deltas

def critical_routes(deltas, top_n=3):
    """
    Identifica as rotas críticas do jogo.
    
    Returns:
        list of tuples: [(dimension, delta, interpretation), ...]
    """
    sorted_deltas = sorted(deltas.items(), key=lambda x: abs(x[1]), reverse=True)
    routes = []
    
    for dim, delta in sorted_deltas[:top_n]:
        if delta > 0:
            interpretation = f"Rota de Ataque (Time A): Explorar {dim} — vantagem de +{delta:.1f}"
        else:
            interpretation = f"Ponto de Perigo (Time A): Sofrer com {dim} — desvantagem de {delta:.1f}"
        routes.append((dim, delta, interpretation))
    
    return routes

def generate_heatmap(deltas, field_zones=None):
    """
    Gera uma imagem do campo de futebol com as zonas coloridas
    conforme a intensidade e direção do diferencial.
    
    Returns:
        str: imagem em base64 para embed no HTML
    """
    if field_zones is None:
        field_zones = FIELD_ZONES
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Desenha o campo básico
    ax.plot([0, 0, 100, 100, 0], [0, 68, 68, 0, 0], 'white', linewidth=2)
    ax.plot([50, 50], [0, 68], 'white', linewidth=1.5)
    ax.add_patch(plt.Circle((50, 34), 9.15, fill=False, color='white'))
    # ... adicionar mais linhas do campo conforme necessário
    
    # Pinta as zonas conforme os deltas
    for dim, delta in deltas.items():
        if dim in field_zones:
            zone = field_zones[dim]
            intensity = min(abs(delta) / 30, 1.0)  # normaliza
            color = 'blue' if delta > 0 else 'red'
            rect = plt.Rectangle(
                (zone['x'], zone['y']),
                zone['width'], zone['height'],
                color=color, alpha=intensity * 0.6
            )
            ax.add_patch(rect)
    
    ax.set_xlim(-5, 105)
    ax.set_ylim(-5, 73)
    ax.set_facecolor('#1a472a')  # verde do campo
    ax.axis('off')
    
    # Converte para base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', transparent=True)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64
