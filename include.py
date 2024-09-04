from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
import openai 
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import shutil
import streamlit as st

if 'openai_api' not in st.session_state:
    pass
else:
    os.environ['OPENAI_API_KEY'] = st.session_state.openai_api
    

PROMPT_TEMPLATE = """
Jawablah pertanyaan berdasarkan konteks berikut ini:

{context}

---


Jawablah pertanyaan berdasarkan konteks diatas: {question}
"""
DATA_PATH = "data"

def check_openai_api_key(api_key):
    client = openai.OpenAI(api_key=api_key)
    try:
        client.models.list()
    except openai.AuthenticationError:
        return False
    else:
        return True
    

def kueri(prompt, database_path):
    query_text = prompt

    # Prepare the DB.
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=database_path, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
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
    formatted_response = f"{response_text}\nSumber: {sources}"
    print(formatted_response)
    return response_text, sources

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