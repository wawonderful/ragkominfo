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
            elif selected == "PDF Viewer":
                st.switch_page("pages/PDF Viewer.pdf")

        DATABASE_PATH = "database"
        DATA_PATH = "data"
        st.header("Create Database")
        with st.form("create_database_form", clear_on_submit=True):
            form_database_name = st.text_input(label="Database Name", value="", max_chars=25, key="zzz")
            form_chunk_size = st.slider('Chunk Size', min_value=1, max_value=4000, value=500, step=100)
            form_chunk_overlap = st.slider('Chunk Overlap', min_value=1, max_value=1000, value=500, step=50)
            submit_btn = st.form_submit_button('Create Database')

        if submit_btn:
            chroma_path = os.path.join(DATABASE_PATH, form_database_name)
            if os.path.exists(chroma_path):
                form_warning = "Error, database with the same name exists"
                st.error(form_warning)
            else:
                include.generate_data_store(form_database_name, form_chunk_size, form_chunk_overlap, chroma_path)
                form_warning = f"Database Successfully Created  \nDatabase Name: {form_database_name}  \nChunk Overlap: {form_chunk_overlap}  \nLocation: {chroma_path}"
                st.warning(form_warning)
    else:
        st.error("API Error!  \nRedirecting to Initialize OpenAI API Page")
        time.sleep(6)
        st.switch_page("init.py")