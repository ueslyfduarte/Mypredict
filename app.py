# app.py — MyPredict 2.0 (ponto de entrada)
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

def main():
    st.set_page_config(page_title="MyPredict 2.0", layout="wide", page_icon="⚽")
    st.sidebar.markdown("# MyPredict 2.0")
    modo = st.sidebar.radio("Modo", ["Manual", "Manual com IA"])

    if modo == "Manual":
        from ui.manual_page import render_manual
        render_manual()
    else:
        from ui.manual_ia_page import render_manual_ia
        render_manual_ia()

if __name__ == "__main__":
    main()
