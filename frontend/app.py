import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ai/conversation"

# 🎨 App config
st.set_page_config(page_title="Fluenta AI", layout="wide")

# ---------------- LOGIN (FIRST TIME ONLY) ----------------
if "username" not in st.session_state:
    st.title("Welcome to Fluenta AI 👩‍💻")

    name = st.text_input("Enter your name")

    if st.button("Start"):
        if name.strip() == "":
            st.warning("Please enter your name")
        else:
            st.session_state.username = name
            st.rerun()

    st.stop()

# ---------------- MAIN APP ----------------
username = st.session_state.username

# Sidebar (like real apps)
with st.sidebar:
    st.title("📊 Dashboard")
    st.write(f"👤 User: {username}")

# Main Title
st.title("Fluenta AI - Speaking Assistant")

# 👩‍💻 Replace bear with girl image
st.image("https://pngtree.com/freepng/smiling-3d-cartoon-girl-with-glasses_21094451.html", width=120)
st.caption("Your AI Speaking Partner")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- CHAT UI ----------------
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Say something...")

if user_input:

    # Save user message
    st.session_state.chat_history.append(("user", user_input))

    payload = {
        "username": username,
        "text": user_input
    }

    response = requests.post(API_URL, json=payload)
    data = response.json()

    ai_text = data["ai_response"]

    # Save AI response
    st.session_state.chat_history.append(("ai", ai_text))

    # Refresh UI
    st.rerun()

# ---------------- SPEAK RESPONSE ----------------
if st.session_state.chat_history:
    last_msg = st.session_state.chat_history[-1]

    if last_msg[0] == "ai":
        ai_text = last_msg[1]

        st.markdown(f"""
        <script>
        var msg = new SpeechSynthesisUtterance("{ai_text}");
        window.speechSynthesis.speak(msg);
        </script>
        """, unsafe_allow_html=True)