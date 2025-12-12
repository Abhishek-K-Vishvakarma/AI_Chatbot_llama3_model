# app.py
import streamlit as st
import json
import os
from datetime import datetime
from fpdf import FPDF
from urllib.parse import unquote_plus
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Abhishek AI - Multi Chat", layout="wide")
CHAT_DIR = "chats"
EXPORT_DIR = "exports"

os.makedirs(CHAT_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# -------------------------
# API support: ?api=question
# -------------------------
params = st.experimental_get_query_params()
if "api" in params:
    raw_q = params.get("api", [""])[0]
    question = unquote_plus(raw_q) if isinstance(raw_q, str) else raw_q
    if not question:
        st.write(json.dumps({"error": "empty question"}))
        st.stop()

    try:
        llm = ChatOllama(model="llama3")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an API assistant."),
            ("human", "{question}")
        ])
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({"question": question})
        st.write(json.dumps({"answer": answer}))
    except Exception as e:
        st.write(json.dumps({"error": str(e)}))
    st.stop()

# -------------------------
# HELPERS
# -------------------------
def list_chats():
    return sorted([f for f in os.listdir(CHAT_DIR) if f.endswith(".json")])

def load_chat(filename):
    path = os.path.join(CHAT_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"title": filename.replace(".json", ""), "messages": []}

def save_chat(filename, data):
    path = os.path.join(CHAT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def create_new_chat():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_{timestamp}.json"
    save_chat(filename, {"title": f"Chat {timestamp}", "messages": []})
    return filename

def export_chat_txt(chat_data, chat_title):
    safe_name = "".join(c for c in chat_title if c.isalnum() or c in (" ", "_", "-")).strip()
    fname = f"{safe_name}.txt"
    path = os.path.join(EXPORT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        for m in chat_data["messages"]:
            role = "You" if m["role"] == "user" else "AI"
            f.write(f"{role}: {m['content']}\n\n")
    return path

def export_chat_json(chat_data, chat_title):
    safe_name = "".join(c for c in chat_title if c.isalnum() or c in (" ", "_", "-")).strip()
    fname = f"{safe_name}.json"
    path = os.path.join(EXPORT_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, ensure_ascii=False, indent=4)
    return path

def export_chat_pdf(chat_data, chat_title):
    safe_name = "".join(c for c in chat_title if c.isalnum() or c in (" ", "_", "-")).strip()
    fname = f"{safe_name}.pdf"
    path = os.path.join(EXPORT_DIR, fname)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, chat_title, ln=True)
    pdf.ln(4)
    for m in chat_data["messages"]:
        role = "You" if m["role"] == "user" else "AI"
        text = f"{role}: {m['content']}"
        pdf.multi_cell(0, 8, text)
        pdf.ln(1)
    pdf.output(path)
    return path

# -------------------------
# SESSION STATE
# -------------------------
if "current_chat" not in st.session_state:
    files = list_chats()
    st.session_state.current_chat = create_new_chat() if not files else files[0]

if "messages" not in st.session_state:
    st.session_state.messages = load_chat(st.session_state.current_chat).get("messages", [])

if "show_menu" not in st.session_state:
    st.session_state.show_menu = None

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("💬 Chats")
chat_files = list_chats()

if st.sidebar.button("➕ New Chat"):
    nf = create_new_chat()
    st.session_state.current_chat = nf
    st.session_state.messages = []
    st.session_state.show_menu = None
    st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("All Chats")

for file in chat_files:
    data = load_chat(file)
    title = data.get("title", file.replace(".json", ""))
    c1, c2 = st.sidebar.columns([0.78, 0.22])

    with c1:
        if st.button(title, key=f"open_{file}"):
            st.session_state.current_chat = file
            st.session_state.messages = data.get("messages", [])
            st.session_state.show_menu = None
            st.experimental_rerun()

    with c2:
        if st.button("⋮", key=f"menu_{file}"):
            cur = st.session_state.get("show_menu")
            st.session_state.show_menu = None if cur == file else file

    if st.session_state.get("show_menu") == file:
        st.sidebar.markdown(f"**Options for:** *{title}*")
        new_name = st.sidebar.text_input("Rename chat", value=title, key=f"rename_{file}")
        if st.sidebar.button("Apply", key=f"apply_{file}"):
            data["title"] = new_name
            save_chat(file, data)
            st.session_state.show_menu = None
            st.experimental_rerun()

        if st.sidebar.button("Export TXT", key=f"export_txt_{file}"):
            p = export_chat_txt(data, new_name)
            with open(p, "rb") as fh:
                st.sidebar.download_button("Download TXT", fh, file_name=os.path.basename(p), mime="text/plain")

        if st.sidebar.button("Export JSON", key=f"export_json_{file}"):
            p = export_chat_json(data, new_name)
            with open(p, "rb") as fh:
                st.sidebar.download_button("Download JSON", fh, file_name=os.path.basename(p), mime="application/json")

        if st.sidebar.button("Export PDF", key=f"export_pdf_{file}"):
            p = export_chat_pdf(data, new_name)
            with open(p, "rb") as fh:
                st.sidebar.download_button("Download PDF", fh, file_name=os.path.basename(p), mime="application/pdf")

        st.sidebar.markdown("---")
        if st.sidebar.button("❌ Delete Chat", key=f"delete_{file}"):
            try:
                os.remove(os.path.join(CHAT_DIR, file))
            except Exception:
                pass
            if st.session_state.current_chat == file:
                st.session_state.current_chat = None
                st.session_state.messages = []
            st.session_state.show_menu = None
            st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("API usage: `http://localhost:8501/?api=your+question`")

# -------------------------
# MAIN AREA
# -------------------------
st.title("🤖 Abhishek AI Chatbot")

if not st.session_state.current_chat:
    st.info("No chat selected. Create a new chat from the sidebar.")
    st.stop()

current_data = load_chat(st.session_state.current_chat)
chat_title = current_data.get("title", st.session_state.current_chat.replace(".json", ""))

col_main, col_side = st.columns([0.85, 0.15])
with col_main:
    st.header(chat_title)
with col_side:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        current_data["messages"] = []
        save_chat(st.session_state.current_chat, current_data)
        st.experimental_rerun()

# display chat messages
for m in st.session_state.messages:
    role_label = "🧑‍💻 You" if m["role"] == "user" else "🤖 AI"
    st.markdown(f"**{role_label}:** {m['content']}")

# input form
with st.form("chat_form", clear_on_submit=True):
    user_q = st.text_input("Ask anything...")
    submitted = st.form_submit_button("Send")

# -------------------------
# LLM setup (only once)
# -------------------------
if "llm_chain" not in st.session_state:
    llm = ChatOllama(model="llama3")
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant running locally with Ollama."),
        ("human", "{question}")
    ])
    st.session_state.llm_chain = prompt | llm | StrOutputParser()

# on send
if submitted and user_q:
    st.session_state.messages.append({"role": "user", "content": user_q})
    with st.spinner("Thinking..."):
        try:
            answer = st.session_state.llm_chain.invoke({"question": user_q})
        except Exception as e:
            answer = f"⚠️ Error: Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434. Details: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": answer})

    current_data["messages"] = st.session_state.messages
    save_chat(st.session_state.current_chat, current_data)
    st.experimental_rerun()
