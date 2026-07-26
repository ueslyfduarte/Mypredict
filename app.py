"""
MyPredict 2.0 - Aplicativo Completo (Conversor com Diagnóstico de Colunas)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from mypredict.core import *
from math import exp, factorial
import os

# Configuração visual
st.set_page_config(page_title="MyPredict 2.0", page_icon="⚽", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #111; color: #fff; }
    h1, h2, h3 { color: #DAA520; }
    .stButton>button { background:#DAA520; color:#000; font-weight:bold; border-radius:8px; }
    .positivo { color:#00C853; font-weight:bold; }
    .negativo { color:#FF1744; font-weight:bold; }
    .mpv-destaque { font-size:3rem; color:#DAA520; text-align:center; }
</style>
""", unsafe_allow_html=True)

def prob_over(media_gols, limite):
    prob_under = sum((media_gols**k) * exp(-media_gols) / factorial(k) for k in range(int(limite)+1))
    return 1 - prob_under

def prob_btts(ata_casa, def_fora, ata_fora, def_casa):
    media_casa = (ata_casa/50) * (1 - def_fora/100)
    media_fora = (ata_fora/50) * (1 - def_casa/100)
    prob_c = 1 - exp(-media_casa)
    prob_f = 1 - exp(-media_fora)
    return prob_c * prob_f

@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("data/meus_jogos.csv", parse_dates=["data"])
        return df.to_dict(orient="records")
    except FileNotFoundError:
        return []

jogos = carregar_dados()

st.sidebar.markdown("<h2 style='color:#DAA520;'>⚽ MyPredict 2.0</h2>", unsafe_allow_html=True)
opcao = st.sidebar.radio("Modo", ["Análise de Jogo", "Backtest", "Converter Dados Brutos"])

if opcao == "Converter Dados Brutos":
    st.markdown("<h1 style='text-align:center;'>🔄 Conversor de CSV</h1>", unsafe_allow_html=True)
    st.markdown("Converte arquivos da pasta `data/raw/` para o formato MyPredict.")

    raw_path = "data/raw"
    try:
        arquivos_raw = [f for f in os.listdir(raw_path) if f.endswith('.csv')]
    except FileNotFoundError:
        st.error("Pasta 'data/raw' não encontrada.")
        arquivos_raw = []

    if not arquivos_raw:
        st.warning("Nenhum arquivo CSV em data/raw/.")
    else:
        st.write("Arquivos encontrados:", arquivos_raw)
        if st.button("⚙️ Converter para meus_jogos.csv"):
            dfs = []
            colunas_por_arquivo = {}
            for arquivo in arquivos_raw:
                caminho = os.path.join(raw_path, arquivo)
                try:
                    df_temp = pd.read_csv(caminho, encoding='utf-8-sig')  # Trata BOM
                    # Remove espaços extras dos nomes das colunas
                    df_temp.columns = df_temp.columns.str.strip()
                    dfs.append(df_temp)
                    colunas_por_arquivo[arquivo] = df_temp.columns.tolist()
                except Exception as e:
                    st.error(f"Erro ao ler {arquivo}: {e}")

            # Mostrar as colunas de cada arquivo
            st.subheader("📋 Colunas encontradas nos arquivos originais:")
            for arq, cols in colunas_por_arquivo.items():
                st.write(f"**{arq}**: {', '.join(cols)}")

            if not dfs:
                st.stop()

            df = pd.concat(dfs, ignore_index=True)

            # Identificar coluna de data
            col_data = None
            for c in df.columns:
                if 'date' in c.lower():
                    col_data = c
                    break
            if not col_data:
                st.error("Nenhuma coluna de data encontrada (precisa conter 'date').")
                st.stop()

            try:
                df[col_data] = df[col_data].astype(str).str.split(' ').str[0]
                df[col_data] = pd.to_datetime(df[col_data], format='%d/%m/%Y', exact=False).dt.strftime('%Y-%m-%d')
            except Exception as e:
                st.error(f"Erro nas datas: {e}")
                st.stop()

            # Mapeamento flexível
            col_map = {
                'HomeTeam': ['HomeTeam', 'home_team', 'Home', 'HT', 'home_team_name'],
                'AwayTeam': ['AwayTeam', 'away_team', 'Away', 'AT', 'away_team_name'],
                'FTR': ['FTR', 'Result', 'R', 'full_time_result'],
                'FTHG': ['FTHG', 'HG', 'HomeGoals', 'FTHG'],
                'FTAG': ['FTAG', 'AG', 'AwayGoals', 'FTAG'],
                'HST': ['HST', 'HomeShotsOnTarget'],
                'AST': ['AST', 'AwayShotsOnTarget'],
                'HS': ['HS', 'HomeShots'],
                'AS': ['AS', 'AwayShots'],
                'HC': ['HC', 'HomeCorners'],
                'AC': ['AC', 'AwayCorners'],
                'HF': ['HF', 'HomeFouls'],
                'AF': ['AF', 'AwayFouls'],
                'HY': ['HY', 'HomeYellow'],
                'AY': ['AY', 'AwayYellow'],
                'HR': ['HR', 'HomeRed'],
                'AR': ['AR', 'AwayRed'],
                'B365H': ['B365H', 'Bet365H'],
                'B365D': ['B365D', 'Bet365D'],
                'B365A': ['B365A', 'Bet365A']
            }

            def get_col(df, mapa, padrao=None):
                for nome in mapa:
                    if nome in df.columns:
                        return df[nome]
                return pd.Series([padrao] * len(df))

            # Verificar colunas essenciais
            essenciais = ['HomeTeam', 'AwayTeam', 'FTR', 'FTHG', 'FTAG']
            for e in essenciais:
                if not any(c in df.columns for c in col_map[e]):
                    st.error(f"Coluna essencial não encontrada: {e}. Mapeamentos tentados: {col_map[e]}. Colunas disponíveis: {list(df.columns)}")
                    st.stop()

            home_team = get_col(df, col_map['HomeTeam'], '')
            away_team = get_col(df, col_map['AwayTeam'], '')
            ftr = get_col(df, col_map['FTR'], '')
            fthg = get_col(df, col_map['FTHG'], 0).astype(int)
            ftag = get_col(df, col_map['FTAG'], 0).astype(int)

            hst = get_col(df, col_map['HST'], 0).astype(float)
            ast = get_col(df, col_map['AST'], 0).astype(float)
            hs = get_col(df, col_map['HS'], 0).astype(float)
            as_ = get_col(df, col_map['AS'], 0).astype(float)
            hc = get_col(df, col_map['HC'], 0).astype(float)
            ac = get_col(df, col_map['AC'], 0).astype(float)
            hf = get_col(df, col_map['HF'], 0).astype(float)
            af = get_col(df, col_map['AF'], 0).astype(float)
            hy = get_col(df, col_map['HY'], 0).astype(int)
            ay = get_col(df, col_map['AY'], 0).astype(int)
            hr = get_col(df, col_map['HR'], 0).astype(int)
            ar = get_col(df, col_map['AR'], 0).astype(int)
            b365h = get_col(df, col_map['B365H'], 2.0).astype(float)
            b365d = get_col(df, col_map['B365D'], 3.0).astype(float)
            b365a = get_col(df, col_map['B365A'], 3.0).astype(float)

            def res_casa(ftr_val):
                if ftr_val == 'H': return 'V'
                elif ftr_val == 'A': return 'D'
                else: return 'E'

            def res_fora(ftr_val):
                if ftr_val == 'A': return 'V'
                elif ftr_val == 'H': return 'D'
                else: return 'E'

            linhas = []
            for i in range(len(df)):
                data = df[col_data].iloc[i]
                home = home_team.iloc[i]
                away = away_team.iloc[i]

                mandante = {
                    'data': data,
                    'time': home,
                    'adv': away,
                    'mando': 'casa',
                    'resultado': res_casa(ftr.iloc[i]),
                    'gols': int(fthg.iloc[i]),
                    'gols_sofridos': int(ftag.iloc[i]),
                    'prat_time': 3, 'prat_adv': 3,
                    'finalizacoes_alvo': float(hst.iloc[i]) if not pd.isna(hst.iloc[i]) else 0,
                    'finalizacoes_totais': float(hs.iloc[i]) if not pd.isna(hs.iloc[i]) else 0,
                    'escanteios': float(hc.iloc[i]) if not pd.isna(hc.iloc[i]) else 0,
                    'faltas_sofridas': float(af.iloc[i]) if not pd.isna(af.iloc[i]) else 0,
                    'faltas_cometidas': float(hf.iloc[i]) if not pd.isna(hf.iloc[i]) else 0,
                    'cartoes_amarelos': int(hy.iloc[i]) if not pd.isna(hy.iloc[i]) else 0,
                    'cartoes_vermelhos': int(hr.iloc[i]) if not pd.isna(hr.iloc[i]) else 0,
                    'B365H': float(b365h.iloc[i]) if not pd.isna(b365h.iloc[i]) else 2.0,
                    'B365D': float(b365d.iloc[i]) if not pd.isna(b365d.iloc[i]) else 3.0,
                    'B365A': float(b365a.iloc[i]) if not pd.isna(b365a.iloc[i]) else 3.0
                }
                visitante = {
                    'data': data,
                    'time': away,
                    'adv': home,
                    'mando': 'fora',
                    'resultado': res_fora(ftr.iloc[i]),
                    'gols': int(ftag.iloc[i]),
                    'gols_sofridos': int(fthg.iloc[i]),
                    'prat_time': 3, 'prat_adv': 3,
                    'finalizacoes_alvo': float(ast.iloc[i]) if not pd.isna(ast.iloc[i]) else 0,
                    'finalizacoes_totais': float(as_.iloc[i]) if not pd.isna(as_.iloc[i]) else 0,
                    'escanteios': float(ac.iloc[i]) if not pd.isna(ac.iloc[i]) else 0,
                    'faltas_sofridas': float(hf.iloc[i]) if not pd.isna(hf.iloc[i]) else 0,
                    'faltas_cometidas': float(af.iloc[i]) if not pd.isna(af.iloc[i]) else 0,
                    'cartoes_amarelos': int(ay.iloc[i]) if not pd.isna(ay.iloc[i]) else 0,
                    'cartoes_vermelhos': int(ar.iloc[i]) if not pd.isna(ar.iloc[i]) else 0,
                    'B365H': float(b365h.iloc[i]) if not pd.isna(b365h.iloc[i]) else 2.0,
                    'B365D': float(b365d.iloc[i]) if not pd.isna(b365d.iloc[i]) else 3.0,
                    'B365A': float(b365a.iloc[i]) if not pd.isna(b365a.iloc[i]) else 3.0
                }
                linhas.append(mandante)
                linhas.append(visitante)

            df_final = pd.DataFrame(linhas)
            st.success(f"Conversão concluída! {len(df_final)} linhas geradas.")
            st.dataframe(df_final.head(10))
            csv_exportado = df_final.to_csv(index=False)
            st.download_button(
                label="📥 Baixar meus_jogos.csv",
                data=csv_exportado,
                file_name="meus_jogos.csv",
                mime="text/csv"
            )
            st.info("Após baixar, substitua o conteúdo de `data/meus_jogos.csv` no GitHub pelo novo conteúdo.")

# ... (restante do código de Análise de Jogo e Backtest, igual ao último completo que eu havia enviado, mantendo a mesma estrutura)
