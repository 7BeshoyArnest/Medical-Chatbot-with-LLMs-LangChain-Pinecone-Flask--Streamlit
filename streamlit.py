import streamlit as st
import subprocess
import sys
import time
import os
import requests

# ------------------ CONFIG ------------------
FLASK_PORT = 5001
FLASK_URL = f"http://127.0.0.1:{FLASK_PORT}"

# ------------------ START FLASK ------------------
def start_flask():

    if "flask_process" in st.session_state:
        return

    env = os.environ.copy()

    env["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
    env["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    env["PORT"] = str(FLASK_PORT)

    process = subprocess.Popen(
        [sys.executable, "app.py"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    st.session_state.flask_process = process

# ------------------ CHECK FLASK ------------------
def is_flask_ready():

    for _ in range(60):
        try:
            r = requests.get(FLASK_URL, timeout=5)
            if r.status_code == 200:
                return True
        except:
            time.sleep(1)

    return False

# ------------------ INIT BACKEND ------------------
if "flask_started" not in st.session_state:
    start_flask()
    st.session_state.flask_started = True

if "flask_ready" not in st.session_state:
    with st.spinner("Starting backend..."):
        st.session_state.flask_ready = is_flask_ready()

# ------------------ UI ------------------
st.title("🩺 Medical Chatbot")

if not st.session_state.flask_ready:
    st.error("Backend failed to start")
    st.stop()

st.success("Backend is running!")

# ------------------ CHAT ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask your medical question...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        response = requests.post(
            f"{FLASK_URL}/get",
            data={"msg": prompt},
            timeout=120
        )

        answer = response.text

    except Exception as e:
        answer = f"Error: {str(e)}"

    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.markdown(answer)