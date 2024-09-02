import streamlit as st
import time
import os
from query import kueri
from PyPDF2 import PdfReader, PdfWriter
from streamlit_pdf_viewer import pdf_viewer
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]
stream = []
_SOURCE_ = "Awal"
# Streamed response emulator
def query_manager(prompt, database_path):
    hasil_kueri = kueri(prompt, database_path)
    if hasil_kueri == None:
        return None
    else:
        output_response, output_source = hasil_kueri
        my_list = list(set(output_source))
        return output_response, my_list
        # i = 1
        # # output_response = 'Zayed Balbahaith dari College of Technological Innovation melakukan penelitian dengan judul "Feature-based Approach" dan rilisnya pada bulan September 2021'
        # # output_source = ['data/books/Detection of SQL Injection Attacks.pdf', 'data/books/SQL Injection Vulnerability Detection Using Deep Learning A Feature-based Approach.pdf', 'data/books/Detection of SQL Injection Attacks.pdf', 'data/books/Detection of SQL Injection Attacks.pdf', 'data/books/Detection of SQL Injection Attacks.pdf']
        # my_list = list(set(output_source))
        # formatted_response = f"{output_response}  \n  \nSumber:  \n"
        # for s in my_list:
        #     src = f"{i}. {s}  \n"
        #     formatted_response = formatted_response + src


def response_generator(input, database_path):
    _rsp = query_manager(input, database_path)
    if _rsp != None:
        _resp = _rsp[0]
        _src = _rsp[1:]
        source = _src[0]
        response = f"{_resp}  \n  \nSumber:  \n"
        i = 1
        for s in source:
            src = f"{i}. {s}  \n"
            response = response + src
        _SOURCE_ = source
    else:
        response = "Tidak dapat menemukan hasil yang cocok."
        _SOURCE_ = "hehe"
    stream.append(response)
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.05)


st.title("PDF Searcher")
st.write(_SOURCE_)
BASE_DATABASE_PATH = "database/"
arr = os.listdir(BASE_DATABASE_PATH)

option = st.selectbox(
    "Database",
    (arr),
)
DATABASE_PATH = os.path.join(BASE_DATABASE_PATH, option)

# # Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        response = st.write_stream(response_generator(prompt, DATABASE_PATH))
        if st.button("Stream data"):
            _SOURCE_ = "BANGSAT"
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response}) 