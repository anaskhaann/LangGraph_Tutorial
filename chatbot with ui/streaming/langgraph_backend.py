from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()

# Create LLM
llm = ChatGroq(model="llama-3.1-8b-instant")


# Create state of out message
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# Define the chat node function
def chat_node(state: ChatState):
    # user query from state
    message = state["messages"]

    # send query to llm
    response = llm.invoke(message)

    # store response
    return {"messages": [response]}


# Define the checkpointer
checkpoints = InMemorySaver()

# Create graph for ChatState
graph = StateGraph(ChatState)

# Add nodes and Edges
graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)


workflow = graph.compile(checkpointer=checkpoints)

if __name__ == "__main__":
    # Till now we used to do workflow.invoke()

    """
    We will use `.stream` instead of invoke
    1. Here you need to send Initial State
    2. Our Config to provide thread id
    3. Stream Mode(custom,messages,updates etc)
    """

    # This is for testing we will use this same in frontend in place of invoke
    stream = workflow.stream(
        # initial state
        {
            "messages": HumanMessage(
                content="Tell the Difference Between Machine Learning and Deep learning in Simple and Short Explaination"
            )
        },
        # Config
        config={"configurable": {"thread_id": "thread-1"}},
        # Stream Mode
        stream_mode="messages",
    )

    # print(type(stream))

    """
    The stream is generator object and it has two items.
    message_chunk and meta_data
    """
    for message_chunk, meta_data in stream:
        if message_chunk.content:
            print(message_chunk.content, end=" ", flush=True)
