import streamlit as st
import subprocess
import sys
import time
import os
import requests
import atexit

FLASK_PORT = 5001
FLASK_URL = f"http://localhost:{FLASK_PORT}"

def start_flask():

    if "flask_process" in st.session_state:
        return

    env = os.environ.copy()
    env["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
    env["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

    # IMPORTANT: use a fixed safe port
    env["PORT"] = "5001"

    process = subprocess.Popen(
        [sys.executable, "app.py"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    st.session_state["flask_process"] = process

def is_flask_ready(retries=60, delay=1.0):

    for _ in range(retries):

        try:
            r = requests.get(
                FLASK_URL,
                timeout=10
            )

            if r.status_code == 200:
                return True

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.ReadTimeout
        ):
            time.sleep(delay)

        except Exception:
            time.sleep(delay)

    return False


# ── Start Flask once ──────────────────────────────────────────────────────────
if "flask_started" not in st.session_state:
    start_flask()
    st.session_state.flask_started = True

if "flask_ready" not in st.session_state:
    with st.spinner("Starting backend..."):
        st.session_state.flask_ready = is_flask_ready()

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("🩺 Medical Chatbot")

if st.session_state.flask_ready:
    st.success(f"Backend is running! Open your chatbot 👉 [Click here]({FLASK_URL})")
else:
    st.error("Backend failed to start. Check your app.py and .env file.")

if st.button("🔄 Restart Backend"):
    if "flask_process" in st.session_state:
        st.session_state.flask_process.terminate()
        del st.session_state["flask_process"]
    st.session_state.flask_started = False
    st.session_state.flask_ready = False
    st.rerun()