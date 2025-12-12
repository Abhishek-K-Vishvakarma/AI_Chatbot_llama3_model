📝 License
This project is open-source. Use freely!

💬 Author

Abhishek Kumar Vishvakarma!
Feel free to connect or contribute!


🚀 LangChain + Ollama Local Chatbot (Streamlit UI)

A simple and powerful AI chatbot built using LangChain, Ollama (Local LLM), and Streamlit.
This app lets you chat with a completely offline AI model like Llama 3, running on your local machine.


⭐ Features

🧠 Local AI Model using Ollama (no API required)
🧩 LangChain-powered prompt pipeline
💬 Chat history support
⚡ Fast inference
🎨 Beautiful & clean Streamlit UI
🔒 Works offline, no data leaves your system


📁 Project Structure
chatbot-project/
│
├─ app.py                 # Main Streamlit app
├─ requirements.txt       # Python dependencies
├─ README.md              # Project description + instructions
├─ chats/                 # Saved chat JSON files
├─ exports/               # Exported PDF/TXT/JSON files
├─ .gitignore             # Ignore venv, __pycache__, exports, etc.
└─ venv/                  # Local virtual environment (ignored)



🛠️ Installation
1️⃣ Clone the repository
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO

2️⃣ Create a virtual environment
python -m venv venv

3️⃣ Activate the virtual environment
Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

📦 Install Dependencies
pip install -r requirements.txt

🤖 Install Ollama & Model

Download Ollama:
https://ollama.com/download

Pull the model (Llama 3 recommended):

ollama pull llama3

▶️ Run the Chatbot
streamlit run app.py


Then open the browser link shown in terminal (usually):

http://localhost:8501


# Abhishek AI - Multi Chatbot with Ollama

This is a local AI chatbot using **LangChain** and **Ollama** with Streamlit frontend.  
Supports multiple chats, exporting, renaming, deleting chats, and API usage.

## Features
- Local AI chatbot using `llama3` model.
- Multiple chat history with sidebar.
- Rename, export (PDF/TXT/JSON), delete chats.
- API support: `http://localhost:8501/?api=your+question`.
- Input form auto clears after submit.

## Setup
1. Clone the repo:
```bash
git clone <your-repo-url>
cd chatbot-project
