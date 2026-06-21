# Python Context Studio SDK (Walkthrough)

I have successfully rewritten the entire **Context Studio** memory engine into a standalone Python SDK! It fully implements the complete **5-tier cognitive architecture** from the academic paper and acts as a universal memory backend.

## 🧠 The Complete 5-Tier Memory Algorithm
The `MemoryEngine` now actively parses every query through all 5 layers:
1. **Working Memory:** Local RAM `cachetools` LRU buffer for the fastest context retention.
2. **Conversational Memory:** Complete interaction history logged to local SQLite.
3. **Episodic Vectors:** Embedded vectors evaluated natively via `NumPy` dot-product math (with time-based decay) for offline similarity search.
4. **Semantic Graphs:** SQLite relational edge traversals acting as a local Knowledge Graph.
5. **Procedural Memory (Rules & Skills):** `[NEW]` Trigger-based instructions stored in SQLite that inject "If-Then" rules (e.g., Refund Policies) directly into the agent's context when relevant keywords are detected.

---

## 🚀 Universal Integration Options

You can plug this SDK into **any** agent architecture. 

### Option 1: LangChain, LangGraph, and ReAct Agents
I built a native LangChain wrapper class. You can literally plug Context Studio directly into an existing `LLMChain` or `StateGraph` without changing any of their core logic!

**How to test the LangChain wrapper locally:**
```bash
cd context_studio_python
venv\Scripts\activate
python test_langchain.py
```
*(Watch the console as Context Studio successfully injects Procedural Rules and Semantic Facts directly into the LangChain prompt buffer!)*

### Option 2: No-Code Builders (FastAPI REST)
If your platform team is using visual builders (like n8n) or external platforms, they can spin up the FastAPI server. The existing platform will just make HTTP `POST` requests to save and retrieve memory.

**How to start the FastAPI Server:**
```bash
cd context_studio_python
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Option 3: Future MCP Server (Model Context Protocol)
Because this is now a highly modular Python SDK, wrapping it into an **MCP Server** for Claude or Cursor to connect to directly is incredibly easy. If your teams adopt MCP in the future, this SDK is completely ready for it!

Everything is tested, robust, and 100% localized (No Cloud, No Docker). Should I package this into a `pip` installable format or push it directly to your repository?
