"""The code for this is taken from chat/01.basic_chatbot.ipynb"""

from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
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
