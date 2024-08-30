from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai 
from dotenv import load_dotenv
import os
import shutil
import streamlit as st
from create_database import generate_data_store

openai.api_key = st.secrets["OPENAI_API_KEY"]
DATABASE_PATH = "database"
DATA_PATH = "data"

st.title("PDF Searcher")

with st.form("create_database_form"):
   st.write("Create Database")
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
        form_warning = f"Database Succesfully Created  \nDatabase Name: {form_database_name}  \nChunk Size: {form_chunk_size}  \nChunk Overlap: {form_chunk_overlap}  \nLocation: {chroma_path}"
        st.warning(form_warning)

# This is outside the form
