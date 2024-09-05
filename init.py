import os
import shutil
import streamlit as st
import io
import time
import openai
import gc
import include
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from PyPDF2 import PdfReader, PdfWriter
from streamlit_pdf_viewer import pdf_viewer
from langchain.evaluation import load_evaluator
from dotenv import load_dotenv
from langchain_ai21 import AI21SemanticTextSplitter
from streamlit_option_menu import option_menu  
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

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

    # "Go to Page" button and input
    go_to_page = st.number_input("Go to Page", min_value=1, max_value=total_pages, value=current_page+1, step=1)
    if st.button("Go"):
        current_page = go_to_page - 1  # Adjust because pages are 0-indexed internally

    return current_page

def query_manager(prompt):
    hasil_kueri = include.kueri(prompt)
    if hasil_kueri == None:
        return None
    else:
        output_response, output_source = hasil_kueri
        list_source = list(set(output_source))
        return output_response, list_source

# Load PDF to get total number of pages
with io.BytesIO(st.session_state.pdf_binary) as fo:
    pdf_reader = PdfReader(fo)
    total_pages = len(pdf_reader.pages)

def response_generator(input):
    response = query_manager(input)
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)

# Navbar setup
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Source PDF", "test"],  # Add other options if needed
    )

if selected == "Home":
    st.title("RAG PDF Viewer")

elif selected == "Source PDF":
    # PDF Navigation
    st.session_state.current_page = pdf_navigator(st.session_state.pdf_binary, st.session_state.current_page)

elif selected == "test":
    st.title(f"You've got mailed")

# Chat interface
if selected == "Home":
    st.title("")

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
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()

# Set OpenAI API key
os.environ['OPENAI_API_KEY'] = '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'
CHROMA_PATH = "halp"
DATA_PATH = "data/books"

os.environ["AI21_API_KEY"] = '5wzoAsQLLH2UCTyxj7guYukiAcd443EQ'

def generate_data_store(database_name, chunk_size, chunk_overlap, chroma_path):
    documents = load_documents()
    chunks = split_text(documents, chunk_size, chunk_overlap)
    save_to_chroma(chunks, chroma_path)
    chroma_path_properties = os.path.join(chroma_path, 'properties.txt')
    f = open(chroma_path_properties, "w")
    f.write(f"Database Name: {database_name}  \nChunk Size: {chunk_size}  \nChunk Overlap: {chunk_overlap}  \nLocation: {chroma_path}")
    f.close()

def load_documents():
    loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = loader.load()
    return documents

def split_text(documents: list[Document], chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)

    return chunks

def save_to_chroma(chunks: list[Document], chroma_path):
    # Clear out the database first.
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=chroma_path
    )
    db.persist()
    

def safe_remove_directory(path, retries=3, delay=2):
    for i in range(retries):
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            break
        except PermissionError:
            print(f"Attempt {i+1} failed. Retrying in {delay} seconds...")
            time.sleep(delay)

# Use the function
safe_remove_directory(CHROMA_PATH)

PROMPT_TEMPLATE = """
Jawablah pertanyaan berdasarkan konteks berikut ini:

{context}

---


Jawablah pertanyaan berdasarkan konteks diatas: {question}
"""

def terakhir(qwery):
    query_text = qwery

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=5)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(prompt)

    model = ChatOpenAI()
    response_text = model.predict(prompt)

    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)

terakhir("Apa isi article") 
