import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import workflow

# Config for Session Memory
CONFIG = {"configurable": {"thread_id": "thread-1"}}

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


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
            # this is our generator which also needs three things
            # Since it will return the message_chunk and meta_data. But we only need message_chunk
            # Extracting message chunk using list comprehension for generators
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
