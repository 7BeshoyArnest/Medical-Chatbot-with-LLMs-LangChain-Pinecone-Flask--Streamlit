import streamlit as st
import subprocess
import sys
import os
import time
import webbrowser

# ---------------- CONFIG ----------------
FLASK_PORT = 5001
FLASK_URL = f"http://127.0.0.1:{FLASK_PORT}"

# ---------------- START FLASK ----------------
def start_flask():

    if "flask_process" in st.session_state:
        return

    env = os.environ.copy()

    env["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
    env["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

    # DO NOT force port on Streamlit Cloud
    process = subprocess.Popen(
        [sys.executable, "app.py"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    st.session_state.flask_process = process
# ---------------- INIT ----------------
if "flask_started" not in st.session_state:
    start_flask()
    st.session_state.flask_started = True

# ---------------- UI ----------------
st.title("🩺 Medical Chatbot Launcher")

st.success("Flask backend is running")

st.markdown(f"""
👉 Open your chatbot here:  
[{FLASK_URL}]({FLASK_URL})
""")

# ---------------- RESTART ----------------
if st.button("🔄 Restart Backend"):

    if "flask_process" in st.session_state:
        st.session_state.flask_process.terminate()
        del st.session_state["flask_process"]

    st.session_state.flask_started = False
    st.rerun()