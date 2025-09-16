import uuid  # This is used to generate random thread id

import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import workflow

# *************** Utility Functions *****************


# Generate Random Thread id
def generate_thread_id():
    thread_id = uuid.uuid4
    return thread_id


# *************** Session StartUp *****************
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# Add thread id to session if not there
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

# For different chat we have different thread id thus we need to put it inside input condition rather than keeping it local
CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}


# ***************** Side Bar *********************

st.sidebar.title("Chat GPT Ultra")

st.sidebar.button("New Chat")

st.sidebar.header("Your Chats")

st.sidebar.text(st.session_state["thread_id"])


# ******************** Main UI ********************

# To print all message
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])


user_input = st.chat_input("Type Here")


if user_input:
    # user message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    # ai message generation with streaming
    with st.chat_message("assistant"):
        # Write stream needs generator
        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, meta_data in workflow.stream(
                {"messages": HumanMessage(user_input)},
                config=CONFIG,
                stream_mode="messages",
            )
        )

    # Appending the entire message to history
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )
