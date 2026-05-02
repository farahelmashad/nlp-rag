import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/query"

st.title("📚 Egyptian Civil Code RAG Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

query = st.chat_input("Ask your legal question...")

if query:
    with st.chat_message("user"):
        st.write(query)
    st.session_state.messages.append({"role": "user", "content": query})

    response = requests.post(
        API_URL,
        json={
            "question": query,
            "chat_history": st.session_state.messages[:-1] 
        }
    )

    if response.status_code == 200:
        data = response.json()
        answer = data["answer"]

        with st.chat_message("assistant"):
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
    else:
        st.error("Error connecting to API")
