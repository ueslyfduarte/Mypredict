# app.py — MyPredict 2.0
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

def main():
    st.set_page_config(page_title="MyPredict 2.0", layout="wide", page_icon="⚽")
    st.sidebar.markdown("# MyPredict 2.0")
    modo = st.sidebar.radio("Modo", ["Manual"])

    if modo == "Manual":
        from ui.manual_page import render_manual
        render_manual()

if __name__ == "__main__":
    main()
