import streamlit as st
from streamlit_option_menu import option_menu
import time
import os
import openai
import io
import shutil
from create_database import generate_data_store
from query import kueri
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from PyPDF2 import PdfReader, PdfWriter
from streamlit_pdf_viewer import pdf_viewer

openai.api_key = st.secrets["OPENAI_API_KEY"]

stream = []

st.title("RAG KOMINFO")
with st.sidebar:
    selected = option_menu(
        menu_title="Navigasi",
        options=["Query", "Create Database", "PDF Viewer"]
    )

if selected == "Query":
    def query_manager(prompt, database_path):
        hasil_kueri = kueri(prompt, database_path)
        if hasil_kueri == None:
            return None
        else:
            output_response, output_source = hasil_kueri
            list_source = list(set(output_source))
            return output_response, list_source
        
    
    def response_generator(input, database_path):
        _rsp = query_manager(input, database_path)
        if _rsp != None:
            _resp = _rsp[0]
            _src = _rsp[1:]
            source = _src[0]
            response = f"{_resp}  \nSumber:  \n"
            i = 1
            for s in source:
                src = f"{1}. {s}  \n"
                response = response + src
        else:
            response = "TIdak dapat menemukan hasil yang cocok."
        stream.append(response)

        for word in response.split(" "):
            yield word + " "
            time.sleep(0.05)
        
    
    BASE_DATABASE_PATH = "database/"
    db_arr = os.listdir(BASE_DATABASE_PATH)

    st.header("Query")
    db_option = st.selectbox(
        "Database",
        (db_arr),
    )
    DATABASE_PATH = os.path.join(BASE_DATABASE_PATH, db_option)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages from history on app rerun
    for  message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator(prompt, DATABASE_PATH))

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

elif selected == "Create Database":
    DATABASE_PATH = "database"
    DATA_PATH = "data"
    st.header("Create Database")
    with st.form("create_database_form"):
        form_database_name = st.text_input(label="Database Name", value="", max_chars=25, key="zzz")
        form_chunk_size = st.slider('Chunk Size', min_value=1, max_value=5000, value=500, step=100)
        form_chunk_overlap = st.slider('Chunk Overlap', min_value=1, max_value=1000, value=500, step=50)
        submit_btn = st.form_submit_button('Create Database')

    if submit_btn:
        chroma_path = os.path.join(DATABASE_PATH, form_database_name)
        if os.path.exists(chroma_path):
            form_warning = "Error, database with the same name exists"
            st.error(form_warning)
        else:
            generate_data_store(form_database_name, form_chunk_size, form_chunk_overlap, chroma_path)
            form_warning = f"Database Successfully Created  \nDatabase Name: {form_database_name}  \nChunk Overlap: {form_chunk_overlap}  \nLocation: {chroma_path}"
            st.warning(form_warning)

elif selected == "PDF Viewer":
    if 'pdf_binary' not in st.session_state:
        pdf_path = "data/Detection of SQL Injection Attacks.pdf"
        with open(pdf_path, 'rb') as fo:
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

        return current_page

    # Load PDF to get total number of pages
    with io.BytesIO(st.session_state.pdf_binary) as fo:
        pdf_reader = PdfReader(fo)
        total_pages = len(pdf_reader.pages)

    st.session_state.current_page = pdf_navigator(st.session_state.pdf_binary, st.session_state.current_page)