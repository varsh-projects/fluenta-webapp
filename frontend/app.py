import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ai/conversation"

st.set_page_config(page_title="Fluenta", layout="centered")

st.title("🧠 Fluenta - Speak English Confidently")

# User input
username = st.text_input("Enter your username")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Speak or type your sentence:")

if st.button("Send"):

    if username and user_input:
        response = requests.post(API_URL, json={
            "username": username,
            "text": user_input
        })

        if response.status_code == 200:
            data = response.json()

            ai_reply = data["ai_response"]
            scores = data["scores"]
            level = data["level"]

            # Save chat
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("AI", ai_reply))

            # Display chat
            st.subheader("💬 Conversation")
            for speaker, msg in st.session_state.chat_history:
                st.write(f"**{speaker}:** {msg}")

            # Show scores
            st.subheader("📊 Your Performance")
            st.write(f"Fluency: {scores['fluency']}/10")
            st.write(f"Grammar: {scores['grammar']}/10")
            st.write(f"Pronunciation: {scores['pronunciation']}/10")
            st.write(f"Vocabulary: {scores['vocabulary']}/10")

            st.success(f"Level: {level}")

        else:
            st.error("Server error")

    else:
        st.warning("Please enter username and message")