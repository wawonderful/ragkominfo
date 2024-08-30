import argparse
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import openai 
from dotenv import load_dotenv
import os

os.environ['OPENAI_API_KEY'] = 'sk-X7j5lfY296Z8RennPYXrfpl42uyW2gV6001JQkhzt8T3BlbkFJjEFva2F-Dg2GdIGY41UEoLTLp5keuywBo5zF0eqhcA'
openai.api_key = os.environ['OPENAI_API_KEY']

PROMPT_TEMPLATE = """
Jawablah pertanyaan berdasarkan konteks berikut ini:

{context}

---


Jawablah pertanyaan berdasarkan konteks diatas: {question}
"""

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

