import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import workflow

# Config for Session Memory
CONFIG = {"configurable": {"thread_id": "thread-1"}}

# To maintain Conversation History we use sesssion_state -> dict
# It does not get reset when pressing enter
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


# To print all message
# Now loop each message of session history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

# """Input Box"""

user_input = st.chat_input("Type Here")

# Add user input to user message box

if user_input:
    # Add it to message history
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    # Assistant Message
    # The change for ai message will be here so we only need to made changes here

    # user input, our thread and since out state is list of annotated message we need to maps of list messages
    response = workflow.invoke(
        {"messages": [HumanMessage(content=user_input)]}, config=CONFIG
    )

    # since ai message will be last one
    ai_message = response["messages"][-1].content
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )
    with st.chat_message("assistant"):
        st.text(ai_message)
