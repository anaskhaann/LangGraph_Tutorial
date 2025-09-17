import uuid

import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import retrieve_all_threads, workflow

# *************** Utility Functions *****************


# Generate Random Thread id
def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id


# New Chat Functionality
def reset_chat():
    thread_id = generate_thread_id()

    # store it in session
    st.session_state["thread_id"] = thread_id

    # also add thread id to chat list
    add_thread(st.session_state["thread_id"])

    # reset message history
    st.session_state["message_history"] = []


# Add Thread to thread list for switching chats
def add_thread(thread_id):
    # first check if thread_id is in list or not
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(
            thread_id
        )  # we need to append not replace


# TO load all conversation of particular thread
def load_conversation(thread_id):
    state = workflow.get_state(config={"configurable": {"thread_id": thread_id}})

    # Check if messages key exists in state values, return empty list if not

    return state.values.get("messages", [])


# *************** Session StartUp *****************


if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

# Add thread id to session if not there
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

# Here we will need to initialze the chat_thread to count the number of threads already available in the database rather than initializing it as empty list.
# call the all threads retrievel function
if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

# add current thread to list
add_thread(st.session_state["thread_id"])


CONFIG = {
    "configurable": {"thread_id": st.session_state["thread_id"]},
}

# ***************** Side Bar *********************


st.sidebar.title("Chat GPT Ultra")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("Your Chats")

# Display list of thread_ids(Reverse for giving latest chat at top)
for id in st.session_state["chat_threads"][::-1]:
    # Load the conversation for the button clicked
    if st.sidebar.button(str(id)):
        # also store it in thread id
        st.session_state["thread_id"] = id

        # Here the issue is the format of the message which we are getting from load conversation is in HumanMessage format but our message history is in role and content dictionary so we need to manually write some code
        messages = load_conversation(id)

        temp_messages = []

        # We are just extracting the role and content and append it to temp dictionary

        # Then in last we are appending our temp message to actual message history

        for _ in temp_messages:
            if isinstance(_, HumanMessage):
                role = "user"
            else:
                role = "assistant"
            temp_messages.append({"role": role, "content": _.content})

        st.session_state["message_history"] = temp_messages


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
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages",
            )
        )

    # Appending the entire message to history
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )
