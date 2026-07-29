# app.py — Ponto de entrada do MyPredict 2.0
import streamlit as st

def main():
    st.set_page_config(page_title="MyPredict 2.0", layout="wide", page_icon="⚽")
    st.sidebar.markdown("# MyPredict 2.0")
    modo = st.sidebar.radio("Modo", ["Automático (API)", "Manual"])

    if modo == "Automático (API)":
        from ui.automatic_page import render_automatico
        render_automatico()
    else:
        from ui.manual_page import render_manual
        render_manual()

if __name__ == "__main__":
    main()
