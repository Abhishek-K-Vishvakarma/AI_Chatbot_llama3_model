import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

st.set_page_config(page_title="Abhishek Vishvakarma Ollama")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Ask Anything in my chatbot")

for msg in st.session_state.messages:
   if msg['role'] == "user":
      st.markdown(f"{msg['content']}")
   else:
      st.markdown(f"{msg['content']}")

input_text = st.text_input("Ask anything...")

llm = ChatOllama(model="llama3")
output_parser = StrOutputParser()
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant running locally with Ollama."),
    ("human", "{question}")
])
chain = prompt|llm|output_parser

if input_text:
   st.session_state.messages.append({"role": "user", "content": input_text})
   with st.spinner("Thinking..."):
    response = chain.invoke({"question": input_text})
   st.session_state.messages.append({"role": "assistant", "content": response})
   st.rerun()
