import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load .env file
load_dotenv()

# Optional: enable LangChain tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# Streamlit UI title
st.title("LangChain Chatbot with OpenAI")

# Input text box
input_text = st.text_input("Ask anything you want:")

# Create ChatPromptTemplate with correct message types
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}")
])

# Initialize OpenAI LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

# Output parser
output_parser = StrOutputParser()

# Chain setup
chain = prompt | llm | output_parser

# If user enters input, invoke the chain and display response
if input_text:
    response = chain.invoke({"question": input_text})
    st.write(response)
