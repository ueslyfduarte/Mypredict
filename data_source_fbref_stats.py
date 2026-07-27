# data_source_fbref_stats.py — MyPredict 2.0 (usando fbrefdata)
import pandas as pd
from fbrefdata import FBref

def _instanciar_fbref(liga, temporada):
    """Cria uma instância do scraper para a liga e temporada."""
    # A biblioteca espera nomes no formato 'ENG-Premier League', etc.
    # Vamos usar nosso mapeamento local para converter.
    codigos = {
        'Brasileirão': 'BRA-Serie A',
        'Premier League': 'ENG-Premier League',
        'La Liga': 'ESP-La Liga',
        'Bundesliga': 'GER-Bundesliga',
        'Serie A': 'ITA-Serie A',
        'Ligue 1': 'FRA-Ligue 1',
        'Eredivisie': 'NED-Eredivisie',
        'Primeira Liga': 'POR-Primeira Liga',
        'MLS': 'USA-Major League Soccer',
        'Championship': 'ENG-Championship',
        'Série B': 'BRA-Serie B',
    }
    # Formato da temporada: '2024' ou '2024-2025' (a biblioteca aceita ambos)
    nome_fbref = codigos.get(liga, liga)
    return FBref(nome_fbref, str(temporada))

def obter_codigo_fbref(nome_liga):
    """Não precisamos mais de código numérico."""
    return nome_liga  # Apenas repassamos o nome

def obter_classificacao(liga, temporada):
    """Retorna {posição: time} usando a tabela de classificação do FBref."""
    fbref = _instanciar_fbref(liga, temporada)
    # read_schedule() retorna TODAS as partidas; vamos extrair a classificação da página principal
    # A biblioteca não tem um método direto para classificação, mas podemos obter via read_team_season_stats
    # e ordenar por pontos.
    try:
        df = fbref.read_team_season_stats(stat_type='standard')
        # df tem índice 'team' e colunas como 'W', 'D', 'L', 'Pts'
        if 'Pts' in df.columns:
            df = df.sort_values('Pts', ascending=False)
        elif 'W' in df.columns and 'D' in df.columns:
            df['Pts'] = df['W'] * 3 + df['D']
            df = df.sort_values('Pts', ascending=False)
        classif = {i+1: time for i, time in enumerate(df.index)}
        return classif
    except Exception:
        # Fallback: tenta extrair da página de schedule
        schedule = fbref.read_schedule()
        # Pega os times únicos e ordena por pontos (não ideal, mas serve)
        times = sorted(set(schedule['home_team'].unique()) | set(schedule['away_team'].unique()))
        return {i+1: t for i, t in enumerate(times)}

def obter_partidas_time(liga, temporada, time):
    """Retorna lista de partidas do time com HT."""
    fbref = _instanciar_fbref(liga, temporada)
    schedule = fbref.read_schedule()
    
    # Filtra partidas do time
    jogos_time = schedule[(schedule['home_team'] == time) | (schedule['away_team'] == time)]
    
    jogos = []
    for _, row in jogos_time.iterrows():
        if pd.isna(row.get('home_goals')):
            continue  # jogo não disputado
        
        mandante = row['home_team']
        visitante = row['away_team']
        gols_casa = int(row['home_goals'])
        gols_fora = int(row['away_goals'])
        
        # HT placar
        ht_str = row.get('halftime_score', '')
        ht_placar = None
        if isinstance(ht_str, str) and '-' in ht_str:
            try:
                ht_casa, ht_fora = map(int, ht_str.split('-'))
                if time == mandante:
                    ht_placar = [ht_casa, ht_fora]
                else:
                    ht_placar = [ht_fora, ht_casa]
            except:
                pass
        
        data = row.get('date', None)
        mandante_flag = (time == mandante)
        adversario = visitante if mandante_flag else mandante
        gols_pro = gols_casa if mandante_flag else gols_fora
        gols_contra = gols_fora if mandante_flag else gols_casa
        resultado = 'V' if gols_pro > gols_contra else ('E' if gols_pro == gols_contra else 'D')
        
        jogos.append({
            'data': data,
            'resultado': resultado,
            'adversario': adversario,
            'mandante': mandante_flag,
            'gols_pro': gols_pro,
            'gols_contra': gols_contra,
            'ht_placar': ht_placar,
            'xg': None, 'xga': None,
            'finalizacoes_tot': None, 'finalizacoes_alvo': None,
            'posse': None, 'passes_certos': None, 'passes_totais': None,
            'passes_chave': None, 'assistencias': None,
            'desarmes': None, 'interceptacoes': None,
            'escanteios': None, 'escanteios_sofridos': None,
            'gols_ultimos_15': None,
        })
    return sorted(jogos, key=lambda x: x['data'] if x['data'] else '')

def obter_stats_time(liga, temporada, time):
    """Retorna estatísticas agregadas do time (médias)."""
    fbref = _instanciar_fbref(liga, temporada)
    try:
        df = fbref.read_team_season_stats(stat_type='standard')
        if time not in df.index:
            return {}
        row = df.loc[time]
        dados = {
            'gols_media': row.get('Gls') / row.get('MP', 1) if 'Gls' in row and 'MP' in row else None,
            'gols_sofridos_media': row.get('GA') / row.get('MP', 1) if 'GA' in row and 'MP' in row else None,
            'xg_media': row.get('xG') / row.get('MP', 1) if 'xG' in row and 'MP' in row else None,
            'xga_media': row.get('xGA') / row.get('MP', 1) if 'xGA' in row and 'MP' in row else None,
            'posse_media': row.get('Poss'),
            'passes_certos_pct': row.get('Cmp%'),
        }
        return {k: v for k, v in dados.items() if v is not None}
    except Exception:
        return {}
