# Context Studio 🧠
A fully localized, production-ready **Memory Engine** for AI Agents.

Context Studio implements a complete **5-Tier Cognitive Architecture** (Working, Conversational, Episodic, Semantic, and Procedural memory) directly on your local machine using SQLite and NumPy. No cloud, no docker, just blazing-fast local memory.

## Features
- **Working Memory**: In-memory LRU cache for high-speed recent context.
- **Conversational Memory**: Full dialogue history (SQLite).
- **Episodic Memory**: Time-decayed local vector similarity search (NumPy).
- **Semantic Memory**: Relational Knowledge Graph mapping (SQLite).
- **Procedural Memory**: "If-Then" rules and triggers.
- **Strict RBAC Security**: Granular Role-Based Access Control and API Key enforcement.

---

# 🚀 The 3 Integration Pathways

Context Studio is built as a highly modular Python SDK. You can integrate it into your platform in three ways:

## 1. The SDK Integration (LangChain / LangGraph / ReAct)
If you are building deep agents in Python using LangChain, you can directly inject Context Studio into your `LLMChain` or `StateGraph` as a native memory module.

**Usage:**
```python
from integrations.langchain_wrapper import ContextStudioMemory
from memory_sdk import MemoryEngine
from database import SessionLocal

# 1. Init Database
db = SessionLocal()
engine = MemoryEngine(db)

# 2. Inject into LangChain!
memory = ContextStudioMemory(
    agent_id="YOUR_AGENT_ID",
    session_id="SESSION_123",
    user_id="USER_XYZ",
    memory_engine=engine
)

# Now pass `memory` directly into your LangChain LLMChain!
```

## 2. The API Integration (FastAPI REST for No-Code Builders)
If you are using external platforms like n8n, React Flow, or a separate frontend, run the built-in FastAPI server to expose standard REST endpoints.

**Start the Server:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Usage (cURL):**
```bash
# Save Memory (Requires API Key & RBAC Context)
curl -X POST http://127.0.0.1:8000/api/memory \
-H "Content-Type: application/json" \
-H "X-API-Key: dev_key" \
-d '{
  "agent_id": "YOUR_AGENT_ID", 
  "session_id": "session_user_A", 
  "role": "user", 
  "content": "My secret is 123", 
  "turn_number": 1,
  "security": {"role": "user", "user_id": "user_A"}
}'
```

## 3. The MCP Integration (Model Context Protocol)
Context Studio comes with a native **FastMCP** server. You can hook it directly into Claude Desktop or Cursor so they can inherently read and write to your local memory graph!

**Claude Desktop Config (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "context_studio": {
      "command": "python",
      "args": ["/path/to/Context-Studio/integrations/mcp_server.py"]
    }
  }
}
```
*(The MCP Server exposes tools like `init_agent`, `save_memory`, and `get_context` directly to the LLM UI).*

---

### Security Note
All read/write operations require a `SecurityContext` containing a `role` (`admin`, `agent`, `user`) and a `user_id`. The engine strictly enforces data isolation so users cannot bleed memories across sessions.
