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
