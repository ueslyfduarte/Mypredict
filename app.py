# app.py — MyPredict 2.0
import streamlit as st
from interfaces import show_automatico, show_manual

with st.sidebar:
    st.markdown("# MyPredict 2.0")
    modo = st.radio("Modo", ["Automático (API)", "Manual"])

if modo == "Manual":
    show_manual()
else:
    show_automatico()
