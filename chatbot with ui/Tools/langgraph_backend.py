import os
import sqlite3
from typing import Annotated, TypedDict

import requests
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

os.environ["LANGSMITH_PROJECT"] = "chatbot-project"
load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b")

# ********************* Making Tools

# Creating Tools
search_tool = DuckDuckGoSearchRun()


# Custom Calulator Tool
@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations are add, subtract, multiply, divide
    """

    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "subtract":
            result = abs(first_num - second_num)
        elif operation == "multiply":
            result = round(first_num * second_num, 2)
        elif operation == "divide":
            if second_num == 0:
                result = 0
            result = round(first_num / second_num, 2)
        else:
            return {"Error": f"Invalid Operation{operation}"}

        return {
            "first_num": first_num,
            "second_num": second_num,
            "operation": operation,
            "result": result,
        }
    except Exception as e:
        return {"error": str(e)}


# get stock price
@tool
def get_stock_price(symbol: str) -> dict:
    """
    Get the currect stock price of the provided symbol of Indian Stock Exchange
    """

    url = f"https://api.freeapi.app/api/v1/public/stocks/{symbol}"

    headers = {"accept": "application/json"}
    response = requests.get(url=url, headers=headers)

    return response.json()


# ********************* Bindind Tools with LLM

all_tools = [search_tool, calculator, get_stock_price]
llm_with_tool = llm.bind_tools(all_tools)


# ******************* Creating Graph,Nodes,Edges


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState):
    messages = state["messages"]
    response = llm_with_tool.invoke(messages)
    return {"messages": [response]}


# Tool Node : It will have all tools
tool_node = ToolNode(all_tools)

# **************** Checkpointer Code

conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)


# *************** Nodes of the Graph
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
# We have to make the node name for tool node as tools because tool_condition explicitly have the literal end & tools so that it can identify which node to go
graph.add_node("tools", tool_node)


# *************** Edges
graph.add_edge(START, "chat_node")

# If LLM asked for tool, then go to tool node else finish
graph.add_conditional_edges("chat_node", tools_condition)
# Add another node from tool to chat node so that outputs are polish and we can perform multistep tool calling
graph.add_edge("tools", "chat_node")

chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])

    return list(all_threads)
