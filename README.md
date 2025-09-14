## The Basics of Agentic AI: [Basic](BASICS.md)

---

## **Introduction to LangGraph: Building Cyclical and State-Driven LLM Applications**

LangGraph is a powerful extension of the LangChain ecosystem designed specifically for creating robust, stateful, and agentic applications. While LangChain Expression Language (LCEL) excels at building linear chains, LangGraph provides the necessary tools to construct complex workflows with cycles, a critical requirement for building advanced agents.

---

## The Need for LangGraph: Overcoming LangChain's Limitations

LangChain Expression Language (LCEL) provides a fluent and composable way to build LLM applications. Its primary strength lies in creating **Directed Acyclic Graphs (DAGs)**, where data flows in a single, predictable direction from start to finish.

This is excellent for many tasks, but it presents fundamental challenges when building more sophisticated, agent-like systems:

- **Inability to Loop**: The "Acyclic" nature of LCEL chains means they cannot have cycles. This is a significant limitation for agents that need to be resilient. For example, if an agent uses a tool that fails due to a temporary API error, the ideal behavior is to loop back and retry the tool call. This is unnatural to implement in a standard LCEL chain.
- **Implicit State Management**: While data can be passed through an LCEL chain, the state is not an explicit, first-class citizen. Each component is responsible for receiving and passing along all necessary information, which can become cumbersome in complex applications where many steps need access to a shared context.
- **Difficult Control Flow**: Implementing advanced control flow, such as pausing for human validation and then continuing based on the feedback, requires complex workarounds in LCEL. The linear nature of chains is not designed for these kinds of interruptions and loops.

**LangGraph was created to directly address these challenges**, providing a more intuitive and powerful framework for applications that require cycles and explicit state management.

---

## What is LangGraph?

**LangGraph** is a library for building stateful, multi-agent applications by modeling them as **graphs**. At its core, it treats LLM workflows as **state machines**.

A state machine is a mathematical model of computation that consists of a set of states and transitions between those states. In LangGraph:

- The **State** is a central object that holds all the information relevant to the application at a given moment.
- The **Nodes** in the graph are computational steps that can read from and modify the state.
- The **Edges** represent the transitions, directing the flow from one node to another based on the current state.

This approach provides a formal and robust way to manage complex, long-running interactions that are common in agentic systems.

---

## LangChain (LCEL) vs. LangGraph: Choosing the Right Tool

| Feature              | LangChain (LCEL)                                                  | LangGraph                                                              |
| :------------------- | :---------------------------------------------------------------- | :--------------------------------------------------------------------- |
| **Control Flow**     | **Directed Acyclic Graphs (DAGs)**. Linear, one-way data flow.    | **Cyclical Graphs**. Allows for loops, retries, and complex branching. |
| **Best For**         | Predictable, sequential tasks (e.g., basic RAG, data extraction). | Agentic systems, human-in-the-loop workflows, multi-agent systems.     |
| **State Management** | **Implicit**. State is passed through the chain as input/output.  | **Explicit**. A central state object is formally defined and modified. |
| **Complexity**       | Simpler to learn and use for basic applications.                  | More setup required, but scales better for complex, agentic logic.     |

**In short: use LangChain (LCEL) for chains, use LangGraph for agents.**

---

## Core Architectural Patterns (LLM Workflows)

LangGraph is designed to make it easier to implement common, powerful patterns for LLM applications.

- **Prompt Chaining**: The most basic pattern, where the output of one LLM call is used as the input for the next. LangGraph handles this by having two sequential nodes.
- **Routing**: This involves using an LLM to decide which path to take next in a workflow. In LangGraph, this is implemented with a **conditional edge**, where a "router" node directs the flow to one of several other nodes based on the current state.
- **Parallelization**: This pattern involves executing multiple tasks simultaneously and then aggregating the results. LangGraph's execution model can run multiple nodes in a single "SuperStep" if they don't depend on each other, making parallel execution a natural feature.
- **Orchestrator-Worker**: A common pattern where a central "orchestrator" or "supervisor" agent breaks down a problem and delegates sub-tasks to specialized "worker" agents. LangGraph can model this by having a supervisor node that routes tasks to different sub-graphs.
- **Evaluator-Optimizer**: This involves having an "evaluator" step that inspects the work done so far and decides if it's good enough to finish, or if it needs to be sent back to a previous "optimizer" step for refinement. This is a natural loop that is easy to implement in LangGraph.

---

## The Fundamental Components of a Graph

### Graphs, Nodes, and Edges

- **Graph**: The overall workflow structure, defined within a `StateGraph` object.
- **Nodes**: The building blocks of computation. A node is a Python function or a LangChain `Runnable` that takes the current state object as input and returns a dictionary of values to update the state.
- **Edges**: The connections that define the control flow. You define a **start node** and can define an **end node**. Edges can be standard (always go from node A to node B) or **conditional** (go from node A to B, C, or D based on the output of node A).

### State

The **State** is the central, shared memory of the graph. It's a single object that is passed to every node. Each node can read from the state to perform its work and can return new information to be added to the state. This is typically defined as a `TypedDict`.

### Reducer

A **Reducer** is a function that specifies _how_ state updates from nodes are merged into the main state object. While you can define custom reducers, the most common behavior is additive: for example, if a node returns a new message, it's appended to a list of messages in the state object.

---

## The LangGraph Execution Model

1.  **Graph Definition**: First, you define the application's structure. You create an instance of a `StateGraph` and pass it your state definition. You then add nodes with `.add_node()` and connect them with `.add_edge()` and `.add_conditional_edges()`. You must also define an entry point to the graph.
2.  **Compile**: Once the graph structure is defined, you call `.compile()`. This is a crucial step that takes your abstract definition and creates an immutable, optimized, and executable `Runnable` object.
3.  **Invoke**: The compiled graph object is a standard LangChain runnable. You can now execute your entire defined workflow by calling `.invoke()` with the initial input, or use `.stream()` to get intermediate results from each node as they execute.
4.  **Message Passing**: As the graph executes, the `State` object is passed between nodes according to the defined edges. This is how information flows through the system.
5.  **SuperStep**: Under the hood, LangGraph uses an efficient execution model. In each "SuperStep," it identifies all nodes that can be run (i.e., all their dependencies have been met) and executes them in parallel. It then updates the state with all the results before determining the next set of nodes to run.

---

Made with ❤️ by **Mohd Anas**
