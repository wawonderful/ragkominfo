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

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()
#---- Set OpenAI API key 
# Change environment variable name from "OPENAI_API_KEY" to the name given in 
# your .env file.
openai.api_key = st.secrets["OPENAI_API_KEY"]

DATA_PATH = "data"


def main():
    generate_data_store()


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



if __name__ == "__main__":
    main()