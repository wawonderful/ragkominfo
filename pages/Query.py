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
        stream = []
        with st.sidebar:
            selected = option_menu(
                menu_title="Navigasi",
                options=["Query", "Create Database", "PDF Viewer"]
            )
            if selected == "Query":
                pass
            elif selected == "Create Database":
                st.switch_page("pages/Create Database.py")
            elif selected == "PDF Viewer":
                st.switch_page("pages/PDF Viewer.py")
        def query_manager(prompt, database_path):
            hasil_kueri = include.kueri(prompt, database_path)
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
                response = f"{_resp}  \n  \nSumber:  \n"
                i = 1
                for s in source:
                    src = f"{i}. {s}  \n"
                    response = response + src
            else:
                response = "TIdak dapat menemukan hasil yang cocok."
            stream.append(response)

            for word in response.split(" "):
                yield word + " "
                time.sleep(0.05)
            
        
        BASE_DATABASE_PATH = "database/"
        db_arr = os.listdir(BASE_DATABASE_PATH)

        st.title("RAG KOMINFO")
        st.header("Query")
        db_option = st.selectbox(
            "Select Database",
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
    else:
        st.error("API Error!  \nRedirecting to Initialize OpenAI API Page")
        time.sleep(3)
        st.switch_page("init.py")