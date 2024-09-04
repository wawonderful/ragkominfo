import streamlit as st
import time
import include
import os
from streamlit_option_menu import option_menu

if "openai_api" not in st.session_state:
    st.error("API Key Not Found!  \n  \nRedirecting to Initialize OpenAI API Page...")
    time.sleep(6)
    st.switch_page("init.py")
else:
    if include.check_openai_api_key(st.session_state.openai_api):
        st.success("API Benar!")
        os.environ['OPENAI_API_KEY'] = st.session_state.openai_api
        with st.sidebar:
            selected = option_menu(
                menu_title="Navigasi",
                options=["Query", "Create Database", "PDF Viewer"],
                default_index = 1,
            )
            if selected == "Query":
                st.switch_page("pages/Query.py")
            elif selected == "Create Database":
                pass

        DATABASE_PATH = "database"
        DATA_PATH = "data"
        st.header("Create Database")
    else:
        st.error("API Error!  \nRedirecting to Initialize OpenAI API Page")
        time.sleep(6)
        st.switch_page("init.py")