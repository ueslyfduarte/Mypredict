import streamlit as st

def main():
    st.set_page_config(page_title="MyPredict 2.0", layout="wide")
    
    # Inicializa estados globais (se não existirem)
    if 'liga_ativa' not in st.session_state:
        st.session_state.liga_ativa = None
    if 'times' not in st.session_state:
        st.session_state.times = {}
    
    st.sidebar.title("MyPredict 2.0")
    modo = st.sidebar.radio("Modo", ["Manual"])
    
    if modo == "Manual":
        from ui.manual_page import render_manual
        render_manual()

if __name__ == "__main__":
    main()
