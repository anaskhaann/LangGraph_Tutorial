import sqlite3
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
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


"""
create database and connect it to the checkpointer.
Thread --> False, because we are going to use the same database across different threads.
"""

conn = sqlite3.connect(
    database="chat_history.db", check_same_thread=False
)  # -> connection object

# Define the checkpointer
"""
Now we need sqlite database and connect this checkpointer to that database with the connector of the database
"""
checkpoints = SqliteSaver(conn=conn)

# Create graph for ChatState
graph = StateGraph(ChatState)

# Add nodes and Edges
graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)


workflow = graph.compile(checkpointer=checkpoints)


# Retrieve all threads
def retrieve_all_threads():
    all_threads = set()

    for chpt in checkpoints.list(None):
        all_threads.add(chpt.config["configurable"]["thread_id"])

    return list(all_threads)


if __name__ == "__main__":
    """Test the database connection"""

    CONFIG = {"configurable": {"thread_id": "1"}}
    result = workflow.invoke(
        {
            "messages": HumanMessage(
                content="Tell the Difference Between Machine Learning and Deep learning in Simple and Short Explaination"
            )
        },
        config=CONFIG,
    )

    # print(result)

    """
    We can find the list of all the checkpoints available in the database with checkpoint.list and pass None to get all thread.
    It returns a generator tuple from which we need config.
    
    And since our threads are repeating so we will store them in sets
    """
    all_threads = set()
    for chpt in checkpoints.list(None):
        all_threads.add(chpt.config["configurable"]["thread_id"])

    """
    We will make a function of this and return list of all threads because in front end we are going to append it.
    """
