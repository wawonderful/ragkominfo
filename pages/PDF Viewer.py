import streamlit as st
import time
import include
import os
from streamlit_option_menu import option_menu
from PyPDF2 import PdfReader, PdfWriter
import io
from streamlit_pdf_viewer import pdf_viewer

if "openai_api" not in st.session_state:
    st.error("API Key Not Found!  \n  \nRedirecting to Initialize OpenAI API Page...")
    time.sleep(3)
    st.switch_page("init.py")
else:
    if include.check_openai_api_key(st.session_state.openai_api):
        os.environ['OPENAI_API_KEY'] = st.session_state.openai_api
        with st.sidebar:
            selected = option_menu(
                menu_title="Navigasi",
                options=["Query", "Create Database", "PDF Viewer"],
                default_index = 2
            )
            if selected == "Query":
                st.switch_page("pages/Query.py")
            elif selected == "Create Database":
                st.switch_page("pages/Create Database.py")
            elif selected == "PDF Viewer":
                pass
        
        DATA_PATH = "data/"
        pdf_files = [f for f in os.listdir(DATA_PATH) if os.path.isfile(os.path.join(DATA_PATH, f))]
        pdf_files = [f for f in pdf_files if f.endswith('.pdf') or f.endswith('.PDF')]

        st.title("RAG KOMINFO")
        st.header("PDF Viewer")
        if not pdf_files:
            st.error(f'There is no PDF that can be viewed.')
        else:
            pdf_option = st.selectbox(
                "Select PDF",
                (pdf_files),
            )
            PDF_PATH = os.path.join(DATA_PATH, pdf_option)

            with open(PDF_PATH, 'rb') as fo:
                st.session_state.pdf_binary = fo.read()

            if 'current_page' not in st.session_state:
                st.session_state.current_page = 0

            def get_page_binary(pdf_binary, page_number):
                pdf_reader = PdfReader(io.BytesIO(pdf_binary))  # Use BytesIO to create a file-like object
                pdf_writer = PdfWriter()
                pdf_writer.add_page(pdf_reader.pages[page_number])
                output = io.BytesIO()
                pdf_writer.write(output)
                return output.getvalue()
            
            def pdf_navigator(pdf_binary, current_page):
                page_binary = get_page_binary(pdf_binary, current_page)
                pdf_viewer(page_binary)
            
                # Navigation buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Previous Page") and current_page > 0:
                        current_page -= 1
                with col2:
                    if st.button("Next Page") and current_page < total_pages - 1:
                        current_page += 1
            
                # "Go to Page" button and input
                go_to_page = st.number_input("Go to Page", min_value=1, max_value=total_pages, value=current_page+1, step=1)
                if st.button("Go"):
                    current_page = go_to_page - 1  # Adjust because pages are 0-indexed internally
            
                return current_page

            # Load PDF to get total number of pages
            with io.BytesIO(st.session_state.pdf_binary) as fo:
                pdf_reader = PdfReader(fo)
                total_pages = len(pdf_reader.pages)

            if st.session_state.current_page >= total_pages - 1:
                st.session_state.current_page = total_pages - 1
            st.session_state.current_page = pdf_navigator(st.session_state.pdf_binary, st.session_state.current_page)
    else:
        st.error("API Error!  \nRedirecting to Initialize OpenAI API Page")
        time.sleep(3)
        st.switch_page("init.py")
