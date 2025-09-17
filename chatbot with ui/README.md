# Basic Chatbot With Streamlit UI

While LangGraph provides the powerful backend logic for a chatbot, you need a user interface (UI) to interact with it. **Streamlit** is an excellent choice for this, as it allows you to build interactive web applications with pure Python. This guide covers the basics of Streamlit and the essential techniques for managing conversation history.

---

## Streamlit Basics

**Streamlit** is an open-source Python library that makes it incredibly fast and easy to build and share custom web apps for machine learning and data science.

### The Core Principle: The Rerun Model

To understand Streamlit, you must understand its execution model. Every time a user interacts with a widget (like clicking a button or submitting text), **Streamlit re-executes your entire Python script from top to bottom**.

This simple model makes development fast, but it creates a major challenge: if all your variables are reset on every interaction, how do you maintain a memory of the conversation?

---

## Building the Chat Interface

Streamlit provides intuitive components for building a chat UI. The two most important are:

- **`st.text_input`**: This widget displays a text input box. When the user types a message and hits Enter, the script reruns, and the function returns the string that the user entered.
- **`st.chat_message`**: This is a container specifically designed to display messages in a chat format. You use it with a `with` statement and specify the role of the sender (`"user"` or `"assistant"`) to get the appropriate styling and avatar.

```python
import streamlit as st

# Using st.chat_message to display a message
with st.chat_message("assistant"):
    st.markdown("Hello! How can I help you today?")

# Using st.text_input to get user input
prompt = st.text_input("What is up?")
```

---

## The Challenge: Maintaining Conversation History

Given Streamlit's rerun model, if you store your chat history in a regular Python list, it will be wiped clean on every interaction.

**The Problem**:

1.  A user sends a message ("Hello").
2.  Your script stores `history = ["User: Hello"]` and gets a response, `history = ["User: Hello", "Assistant: Hi!"]`.
3.  The user sends a second message ("How are you?").
4.  **The script reruns from the top**. The `history` list is re-initialized to an empty list `[]`.
5.  The app has forgotten the first message and only sees the new one.

---

## The Solution: `st.session_state`

Streamlit provides a dedicated solution for this problem: **`st.session_state`**.

**`st.session_state`** is a special, dictionary-like object that **persists across script reruns**. Any data you store in it will be preserved for the duration of a user's session. It is the correct and only way to maintain state in a Streamlit application.

### How it Solves the Problem

You can implement a simple pattern to manage the chat history:

1.  **Initialization**: At the very start of your script, check if your messages list exists in `st.session_state`. If it doesn't, initialize it as an empty list. This step only runs once, on the very first execution of the script for a new session.
2.  **Display**: On every rerun, loop through the `st.session_state.messages` list and display all the existing messages.
3.  **Update**: When a user provides new input, append both their message and the assistant's response to the `st.session_state.messages` list.

This ensures that the history is never lost during a rerun.

### Example Code for a Stateful Chat App

This snippet demonstrates the complete pattern for a stateful chatbot UI in Streamlit.

```python
import streamlit as st

# --- Initialization ---
# This part runs only once per session
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Past Messages ---
# This part runs on every script rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input and LangGraph Call ---
# This part runs on every script rerun
if prompt := st.text_input("What is up?"):
    # 1. Add user message to session state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call your LangGraph backend (conceptual)
    # The 'app' is your compiled LangGraph
    # You pass the history from session_state
    # config = {"configurable": {"thread_id": "some_unique_id"}}
    # response = app.stream(st.session_state.messages, config=config)
    # For this example, we'll use a placeholder response
    assistant_response = "This is a response from the assistant."

    # 3. Add assistant response to session state and display it
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
```

# Add Streaming to ChatBot Output Message

In modern AI applications, user experience is paramount. Waiting several seconds for a model to generate a complete response can make an application feel slow and unresponsive. **Streaming** is the technique used to solve this problem, providing immediate and continuous feedback to the user.

---

## What is Streaming and Why is it Important?

**Streaming** is the process of sending and receiving data in a continuous flow of small chunks, rather than waiting for the entire response to be generated before sending it as a single, large block.

**Analogy**: A non-streaming (or blocking) request is like downloading a full movie file before you can start watching. You have to wait for the entire download to finish. A streaming request is like watching a video on YouTube or Netflix; it starts playing almost immediately while the rest of the content loads in the background.

The primary importance of streaming is to create a **dramatically better user experience**.

- **Perceived Performance**: The user sees text appearing on the screen almost instantly, making the application feel fast and interactive, even if the total generation time is the same.
- **Engaging Interaction**: For chatbots, the token-by-token appearance of text mimics a real-time conversation, which is more natural and engaging for users.

---

## How to Implement Streaming in LangGraph

Because compiled LangGraph graphs are standard LangChain `Runnables`, they have built-in support for streaming. The implementation is straightforward: instead of calling `.invoke()`, you call the `.stream()` method.

### The `.stream()` Method Explained

- **What it is**: The method on a compiled LangGraph application that initiates a streaming execution.
- **Input Parameters**:
  - `input`: The initial state or input for the graph, just like `.invoke()`.
  - `config`: The configuration dictionary, which is essential for stateful streaming. This is where you must pass the `{"configurable": {"thread_id": "..."}}` to ensure the streamed response is part of a persistent conversation.
  - `stream_mode`: In what mode we need to stream the response
- **What it Returns**: The `.stream()` method does not return a final result directly. Instead, it returns a **Python generator** Containing two items `message_chunk` and `meta_data`. A generator is an iterable object that `yields` one piece of data at a time. You process the stream by looping over this generator.
- **How to Access Message Chunks**:
  1.  You iterate over the returned generator using a `for` loop.
  2.  Each `message_chunk` yielded by the generator is a token.

```python
# A conceptual example of processing a stream
for chunk,meta_data in app.stream(state, config,streaming_mode):
    if chunk.content:
        print(chunk, end="", flush=True)
```

---

## How to Handle Streaming in a Streamlit UI

Streamlit's top-to-bottom rerun model makes handling streams tricky. A simple `for` loop would block the entire UI until the stream is complete. The correct way to implement streaming in Streamlit is with the `st.write_stream` method.

`st.write_stream` is designed to consume a generator and render its yielded output to the screen incrementally.

### The Implementation Pattern

1.  **Create a Helper Generator Function**: Write a Python function that will call your LangGraph app's `.stream()` method. This function will loop through the chunks, extract the text content, and `yield` just the content.
2.  **Call `st.write_stream`**: In your main UI code, inside a `st.chat_message` container, call `st.write_stream` and pass it your helper generator function.

This pattern allows Streamlit to handle the rendering loop efficiently, creating the desired "typing" effect in the chat bubble without blocking the application.

---

# Add Resume Message to ChatBot

In this we dont have to change out Backend Only Front End Needs to Modify.

- [x] Add Side Bar
- [x] generate dynamic thread id and add it to session(use uuid library)
- [x] Show thread id in side bar
- [x] On Clicking of New chat Button
  - generate new thread_id
  - save it in session for new chat
  - reset message history for new chat to show blank page
- [x] retain the list of thread_ids
- [x] store this list of thread_ids
- [x] Load all the thread ids in sidebar
- [x] Convert sidebar text to clickable button
- [x] Add chat to screen when the button is clicked
  - To show chat associated with that thread
  - Get the thread id
  - thread id from message history and print those thread messages

> For this part we have to use our logical capability and test how to extract messages for a particular thread using that id with the help of get_state(). And other logics of how to handle eveything

---

# Add Database Storage

This will help to storage all conversation permanently. This will ensure that even when the program is closed or we refresh the web page we will still have the history

- Install langgraph-checkpointer-sqlite and Import sqlite saver
- Connect this saver to connection object of the database
- Make sure to set same_thread for database = False

- get list of all threads using checkpoints
- since thread will repeat because we will have Multiple checkpoints for A thread so we can store the thread in sets for getting only thread id and return the list of the threads
- In ui rather than initalizing the chat_threads as empty list we will now check with backend that how many thread id are there i.e retrieve list of thread id from backend

---

Made with ❤️ by **Mohd Anas**
