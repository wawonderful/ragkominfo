import streamlit as st
import openai
import time
import include

st.title("RAG KOMINFO")
st.header("Initialize OpenAI API")
if "openai_api" not in st.session_state:
    with st.form("api_form", clear_on_submit=True):
        password = st.text_input("OPEN AI API", type="password")
        submitapi_btn = st.form_submit_button('OK')
    if submitapi_btn:
        if include.check_openai_api_key(password):
            st.success("API Benar!")
            st.session_state.openai_api = password
            time.sleep(3)
            st.switch_page("pages/Query.py")
        else:
            st.error("API Salah!")
else:
    st.success("API Benar!")
    time.sleep(3)
    st.switch_page("pages/Query.py")

