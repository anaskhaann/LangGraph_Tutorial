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
    CONFIG = {"configurable": {"thread_id": "1"}}
    result = workflow.invoke(
        {
            "messages": HumanMessage(
                content="Tell the Difference Between Machine Learning and Deep learning in Simple and Short Explaination"
            )
        },
        # Config
        config=CONFIG,
    )

    """We need to extract the messages associated with those thread"""
    # pass those config
    print("=" * 100)

    # print(workflow.get_state(config=CONFIG))

    # get value attribute from this snapshot object
    # print(workflow.get_state(config=CONFIG).values)

    # from those values dic get messages
    print(workflow.get_state(config=CONFIG).values["messages"])
