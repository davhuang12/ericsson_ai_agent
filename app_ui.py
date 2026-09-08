import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="David's Basketball Assistant")
st.title("David's Basketball Assistant")
st.caption("Ask about David's favorite basketball players, rankings (1 through 20), or opinions.\n"
           "An example of a multi-tool question can be: What is David's opinion on Lebron James and is it different from the general consensus?")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

question = st.chat_input("Ask your question")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"messages": st.session_state.messages})
            response.raise_for_status()
            answer = response.json()["response"]
        except requests.exceptions.RequestException as e:
            answer = f"Error reaching the backend: {e}"

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)