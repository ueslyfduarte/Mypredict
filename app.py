import sys, os
import streamlit as st

# Força o diretório do app no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Diagnóstico
st.set_page_config(page_title="Diagnóstico MyPredict", layout="wide")
st.title("Verificação de Estrutura")

raiz = os.path.dirname(os.path.abspath(__file__))
st.write("Diretório do app:", raiz)
st.write("sys.path:", sys.path[:3])

# Verifica existência das pastas
for pasta in ["core", "data", "ui"]:
    if os.path.isdir(pasta):
        st.success(f"Pasta '{pasta}' existe")
        arquivos = os.listdir(pasta)
        st.write(f"  Conteúdo de '{pasta}': {arquivos}")
        if "__init__.py" not in arquivos:
            st.error(f"  ❌ Faltando __init__.py em '{pasta}'!")
        if pasta == "core" and "calculations.py" not in arquivos:
            st.error(f"  ❌ Faltando calculations.py em '{pasta}'!")
    else:
        st.error(f"Pasta '{pasta}' NÃO encontrada!")
