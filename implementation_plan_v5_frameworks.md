# Implementation Plan — Context Studio (Full Algorithms & Framework Integrations)

> **Version:** 5.0 (Full Paper Architecture + LangChain/LangGraph Integration)  
> **Date:** 2026-06-21  
> **Status:** 🔶 Awaiting Approval

## Goal Description
The user wants to fully implement the **complete multi-tier memory algorithm** as described in the academic paper (including Procedural Memory) into the Python codebase. Additionally, the codebase must be structured as a highly modular library that can seamlessly integrate not only with No-Code Builders (via our FastAPI REST endpoints) but also directly with advanced agent frameworks like **LangChain**, **LangGraph**, and custom **ReAct (Reasoning and Acting) agents**.

---

## User Review Required

> [!IMPORTANT]
> **Framework Integration Strategy:** To support LangChain and LangGraph directly, I will expose a native Python class wrapper (e.g., `ContextStudioLangChainMemory`) that subclasses LangChain's native memory interfaces (`BaseMemory` / `BaseChatMessageHistory`). This will allow you to pass our memory engine directly into any `LLMChain` or LangGraph node without rewriting code! Does this approach align with how you plan to use LangChain/LangGraph?

---

## 1. Full Algorithm Implementation (All Memory Tiers)

We will expand our `memory_sdk.py` to cover all 5 layers of the paper's cognitive architecture:

1. **Working Memory (Buffer):** High-speed, short-term context.
2. **Conversational Memory (Logs):** Exact dialogue history.
3. **Episodic Memory (Vectors):** Time-weighted dot-product search of past experiences.
4. **Semantic Memory (Graph):** Recursive SQLite traversal for extracted facts and relationships.
5. **[NEW] Procedural Memory (Rules):** "If-Then" logic, standard operating procedures, and agent skills. When assembling context, the engine will check Procedural Memory to inject rules relevant to the current user query.

---

## 2. Universal Integration Architecture

We will restructure the Python codebase so it exposes interfaces for **all** agent types:

### A. The No-Code Interface (Already Built)
The `FastAPI` routes (`main.py`) will remain intact so visual builders (like n8n or React Flow) can interact via HTTP REST.

### B. The LangChain / ReAct Interface
We will create a new file `integrations/langchain_wrapper.py`.
This wrapper will map LangChain's `save_context()` and `load_memory_variables()` directly to our 5-tier context assembly algorithm. 

**Example usage for your ReAct agents:**
```python
from langchain.chains import LLMChain
from integrations.langchain_wrapper import ContextStudioMemory

# Our engine acts as the native memory for LangChain!
memory = ContextStudioMemory(agent_id="...", session_id="...")
chain = LLMChain(llm=my_llm, memory=memory)
chain.predict(human_input="Hello")
```

---

## 3. Proposed Code Changes

#### `models.py`
- `[NEW]` Add `ProceduralRule` SQLAlchemy table to store agent-specific conditional rules (e.g., "If user asks about refunds, provide policy link").

#### `memory_sdk.py`
- `[MODIFY]` Update `get_context()` to execute the full 5-layer algorithm.
- `[NEW]` Add `search_procedural_memory()` to fetch operating rules related to the query.

#### `integrations/langchain_wrapper.py`
- `[NEW]` Build the native LangChain/LangGraph adapter class.

#### `test_langchain.py`
- `[NEW]` Create an automated script demonstrating how a ReAct/LangChain agent utilizes the full 5-tier memory during an LLM invocation.

---

## 4. Verification Plan
Once implemented, I will run a script that simulates a LangChain/ReAct agent invocation. The console output will prove that the agent successfully loaded Procedural rules, Episodic vectors, and Semantic facts natively into its prompt buffer before generating a response.
