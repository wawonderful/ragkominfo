import streamlit as st
from streamlit_option_menu import option_menu

with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["init"],
    )

if selected == "init":
    st.title(f"Youve got mailed")
