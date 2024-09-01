# from langchain.document_loaders import DirectoryLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
# from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import openai
from dotenv import load_dotenv
import os
import shutil
from langchain_ai21 import AI21SemanticTextSplitter
with open("init.py", "w") as f:
    f.write('''
import streamlit as st
import io
import time
from PyPDF2 import PdfReader, PdfWriter
from streamlit_pdf_viewer import pdf_viewer

# Initialize the session state
if 'pdf_binary' not in st.session_state:
    pdf_path = "data/books/computers-12-00195-v2.pdf"
    with open(pdf_path, 'rb') as fo:
        st.session_state.pdf_binary = fo.read()

if 'current_page' not in st.session_state:
    st.session_state.current_page = 0

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Function to get the binary data of a specific page
def get_page_binary(pdf_binary, page_number):
    pdf_reader = PdfReader(io.BytesIO(pdf_binary))  # Use BytesIO to create a file-like object
    pdf_writer = PdfWriter()
    pdf_writer.add_page(pdf_reader.pages[page_number])
    output = io.BytesIO()
    pdf_writer.write(output)
    return output.getvalue()

# Function to handle PDF navigation
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

# PDF Navigation
st.session_state.current_page = pdf_navigator(st.session_state.pdf_binary, st.session_state.current_page)

# Streamed response emulator
def query_manager(prompt):
    i = 1
    output_response = 'Zayed Balbahaith dari College of Technological Innovation melakukan penelitian dengan judul "Feature-based Approach" dan rilisnya pada bulan September 2021'
    output_source = ['data/books/Detection of SQL Injection Attacks.pdf', 'data/books/SQL Injection Vulnerability Detection Using Deep Learning A Feature-based Approach.pdf', 'data/books/Detection of SQL Injection Attacks.pdf', 'data/books/Detection of SQL Injection Attacks.pdf', 'data/books/Detection of SQL Injection Attacks.pdf']
    my_list = list(set(output_source))
    formatted_response = f"{output_response}  \n  \nSumber:  \n"
    for s in my_list:
        src = f"{i}. {s}  \n"
        formatted_response = formatted_response + src

    return formatted_response

def response_generator(input):
    response = query_manager(input)
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)

# Chat interface
st.title("PDF Searcher")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
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
        response = st.write_stream(response_generator(prompt))
        st.write("GG")
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
''')

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
#---- Set OpenAI API key
# Change environment variable name from "OPENAI_API_KEY" to the name given in
# your .env file.
CHROMA_PATH = "zvcvc"
DATA_PATH = "data/books"

import os
from getpass import getpass

os.environ["AI21_API_KEY"] = getpass()

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    # text_splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=300,
    #     chunk_overlap=100,
    #     length_function=len,
    #     add_start_index=True,
    # )
    # chunks = text_splitter.split_documents(documents)
    # print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # document = chunks[10]
    # print(document.page_content)
    # print(document.metadata)

    semantic_text_splitter = AI21SemanticTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        add_start_index=True
    )
    chunks = semantic_text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks


def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")

generate_data_store()

!wget -q -O - ipv4.icanhazip.com

! streamlit run init.py & npx localtunnel --port 8501

terakhir("Apa isi article")

from google.colab import drive
drive.mount('/content/drive')

"""# Finish

# Compare Embedding
"""

from langchain_openai import OpenAIEmbeddings
from langchain.evaluation import load_evaluator
from dotenv import load_dotenv
import openai
import os

def compare_embedding():
    # Get embedding for a word.
    embedding_function = OpenAIEmbeddings()
    vector = embedding_function.embed_query("apple")
    print(f"Vector for 'apple': {vector}")
    print(f"Vector length: {len(vector)}")

    # Compare vector of two words
    evaluator = load_evaluator("pairwise_embedding_distance")
    words = ("apple", "iphone")
    x = evaluator.evaluate_string_pairs(prediction=words[0], prediction_b=words[1])
    print(f"Comparing ({words[0]}, {words[1]}): {x}")

nga

!zip -r 'db.zip' '/content/chromaz'
