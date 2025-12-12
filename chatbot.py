# -----------------------------------------------------
# app.py  (FIXED VERSION - Session State Order Corrected)
# -----------------------------------------------------

import streamlit as st
import json
import os
import sys
from datetime import datetime
from fpdf import FPDF
from urllib.parse import unquote_plus
import dotenv

dotenv.load_dotenv()

# NOTE: do NOT import langchain_groq at top-level to avoid name collision

# -----------------------------------------------------
# STREAMLIT CONFIG  (must be first)
# -----------------------------------------------------
st.set_page_config(page_title="Abhishek AI - Multi Chat", layout="wide")

CHAT_DIR = "chats"
EXPORT_DIR = "exports"

os.makedirs(CHAT_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# -----------------------------------------------------
# SAFE IMPORT helper to avoid local module shadowing external 'groq' package
# -----------------------------------------------------
def safe_import_langchain_groq():
    """
    Temporarily remove the current project directory from sys.path so that
    'langchain_groq' importing the 'groq' package resolves to the installed
    package instead of this local file.
    Returns (ChatGroq, ChatPromptTemplate, StrOutputParser)
    """
    project_dir = os.path.dirname(os.path.abspath(__file__))
    original_sys_path = list(sys.path)
    try:
        # remove project_dir entries from sys.path temporarily
        sys.path = [p for p in sys.path if os.path.abspath(p) != project_dir]
        # now import
        from langchain_groq import ChatGroq
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        return ChatGroq, ChatPromptTemplate, StrOutputParser
    finally:
        sys.path = original_sys_path


# -----------------------------------------------------
# INIT GROQ MODEL (safe import)
# -----------------------------------------------------
try:
    ChatGroq, ChatPromptTemplate, StrOutputParser = safe_import_langchain_groq()
except Exception as e:
    st.error(f"Failed to import langchain_groq or dependencies: {e}")
    ChatGroq = None
    ChatPromptTemplate = None
    StrOutputParser = None

if ChatGroq is not None:
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name=os.getenv("GROQ_MODEL")
    )
else:
    llm = None


params = st.experimental_get_query_params()

if "api" in params:
    raw_q = params.get("api", [""])[0]
    question = unquote_plus(raw_q)

    if not question:
        st.write(json.dumps({"error": "empty question"}))
        st.stop()

    try:
        if ChatPromptTemplate is None or llm is None or StrOutputParser is None:
            raise RuntimeError("Model or prompt classes unavailable")

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an API assistant."),
            ("human", "{question}")
        ])

        chain = prompt | llm | StrOutputParser()
        ans = chain.invoke({"question": question})

        st.write(json.dumps({"answer": ans}))

    except Exception as e:
        st.write(json.dumps({"error": str(e)}))

    st.stop()
# -----------------------------------------------------
# HELPERS
# -----------------------------------------------------
def list_chats():
    return sorted([f for f in os.listdir(CHAT_DIR) if f.endswith(".json")])
def load_chat(file):
    try:
        with open(os.path.join(CHAT_DIR, file), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"title": "Untitled", "messages": []}


def save_chat(file, data):
    with open(os.path.join(CHAT_DIR, file), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def new_chat():
    t = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"chat_{t}.json"
    save_chat(fname, {"title": f"Chat {t}", "messages": []})
    return fname


def export_txt(data, title):
    safe = "".join(c for c in title if c.isalnum() or c in "_- ")
    path = f"{EXPORT_DIR}/{safe}.txt"
    with open(path, "w", encoding="utf-8") as f:
        for m in data["messages"]:
            role = "You" if m["role"] == "user" else "AI"
            f.write(f"{role}: {m['content']}\n\n")
    return path


def export_json(data, title):
    safe = "".join(c for c in title if c.isalnum() or c in "_- ")
    path = f"{EXPORT_DIR}/{safe}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return path


def export_pdf(data, title):
    safe = "".join(c for c in title if c.isalnum() or c in "_- ")
    path = f"{EXPORT_DIR}/{safe}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, title)
    pdf.ln(4)

    for m in data["messages"]:
        role = "You" if m["role"] == "user" else "AI"
        pdf.multi_cell(0, 8, f"{role}: {m['content']}")
        pdf.ln(2)

    pdf.output(path)
    return path

# -----------------------------------------------------
# SESSION INIT (FIXED ORDER)
# -----------------------------------------------------
# Step 1: Initialize 'current' first
if "current" not in st.session_state:
    allc = list_chats()
    st.session_state.current = allc[0] if allc else new_chat()

# Step 2: Initialize 'menu'
if "menu" not in st.session_state:
    st.session_state.menu = None

# Step 3: Initialize 'messages' (depends on 'current')
if "messages" not in st.session_state:
    st.session_state.messages = load_chat(st.session_state.current)["messages"]

# Step 4: Create and store chain
if "chain" not in st.session_state:
    if ChatPromptTemplate is not None and StrOutputParser is not None and llm is not None:
        default_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("human", "{question}")
        ])
        st.session_state.chain = default_prompt | llm | StrOutputParser()
    else:
        st.session_state.chain = None

# -----------------------------------------------------
# SIDEBAR — CHAT LIST / OPTIONS
# -----------------------------------------------------
st.sidebar.title("💬 Chats")

if st.sidebar.button("➕ New Chat"):
    f = new_chat()
    st.session_state.current = f
    st.session_state.messages = []
    st.experimental_rerun()

st.sidebar.markdown("---")

for file in list_chats():
    data = load_chat(file)
    title = data["title"]

    col1, col2 = st.sidebar.columns([0.8, 0.2])

    with col1:
        if st.button(title, key=f"open_{file}"):
            st.session_state.current = file
            st.session_state.messages = data["messages"]
            st.experimental_rerun()

    with col2:
        if st.button("⋮", key=f"menu_{file}"):
            st.session_state.menu = None if st.session_state.menu == file else file

    if st.session_state.menu == file:
        newname = st.sidebar.text_input("Rename:", value=title)
        if st.sidebar.button("Apply Name"):
            data["title"] = newname
            save_chat(file, data)
            st.session_state.menu = None
            st.experimental_rerun()

        if st.sidebar.button("Export TXT"):
            p = export_txt(data, newname)
            st.sidebar.download_button("Download", open(p, "rb"), file_name=p)

        if st.sidebar.button("Export JSON"):
            p = export_json(data, newname)
            st.sidebar.download_button("Download", open(p, "rb"), file_name=p)

        if st.sidebar.button("Export PDF"):
            p = export_pdf(data, newname)
            st.sidebar.download_button("Download", open(p, "rb"), file_name=p)

        if st.sidebar.button("❌ Delete"):
            os.remove(os.path.join(CHAT_DIR, file))
            st.session_state.current = None
            st.session_state.messages = []
            st.experimental_rerun()

        st.sidebar.markdown("---")


# -----------------------------------------------------
# MAIN UI
# -----------------------------------------------------
st.title("🤖 Abhishek AI Chatbot")

current = load_chat(st.session_state.current)
title = current["title"]

st.header(title)
if st.button("Clear Chat"):
    st.session_state.messages = []
    current["messages"] = []
    save_chat(st.session_state.current, current)
    st.experimental_rerun()

# show messages
for m in st.session_state.messages:
    role = "🧑‍💻 You" if m["role"] == "user" else "🤖 AI"
    st.markdown(f"**{role}:** {m['content']}")

# input form
with st.form("chat", clear_on_submit=True):
    q = st.text_input("Type your message...")
    send = st.form_submit_button("Send")

# -----------------------------------------------------
# SEND MESSAGE
# -----------------------------------------------------
if send and q:
    st.session_state.messages.append({"role": "user", "content": q})

    with st.spinner("Thinking..."):
        try:
            if st.session_state.chain is None:
                raise RuntimeError("LLM chain not available")
            ans = st.session_state.chain.invoke({"question": q})
        except Exception as e:
            ans = "⚠️ " + str(e)

    st.session_state.messages.append({"role": "assistant", "content": ans})
    current["messages"] = st.session_state.messages
    save_chat(st.session_state.current, current)
    st.experimental_rerun()