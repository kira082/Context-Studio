# Context Studio

Context Studio is a **Cognitive Operating System for AI Agents**. It is a pluggable, configurable memory engine that implements a 7-tier cognitive architecture, an advanced hybrid retrieval pipeline with RRF and cross-encoder re-ranking, a dynamic knowledge graph builder, and comprehensive data governance.

Powered by a **Universal LLM layer (LiteLLM)**, it supports models from OpenAI, Anthropic, Google (Gemini), Ollama, and Hugging Face right out of the box.

---

## 🔌 How to Connect to Context Studio

Context Studio is designed to integrate seamlessly into any AI ecosystem. Choose your platform below to get started:

### 1. No-Code Platforms (n8n, Make.com, Flowise)
Context Studio runs a FastAPI REST server that is completely agnostic to your builder platform.

**Step 1: Start the Server**
```bash
python -m context_studio.api.main
```

**Step 2: Connect via HTTP Request Node**
In your no-code platform (e.g., n8n HTTP Request node), configure the following:
- **Base URL**: `http://localhost:8000/v1`
- **Headers**:
  - `X-Tenant-ID`: `your-tenant-id`
  - `X-Agent-ID`: `your-agent-id`
  - `Authorization`: `Bearer your_api_key`

**Endpoints to use in your visual flows:**
- **Search Memory:** `POST /memory/search` (Input: `{"query": "User's request", "session_id": "123"}`)
- **Save Memory:** `POST /memory/add` (Input: `{"session_id": "123", "role": "user", "content": "Hello!"}`)
- **Log Sandbox Tools:** `POST /tools/log_execution` (Log successful/failed web-hooks or tool calls)

---

### 2. DeepAgent / Python Frameworks (LangChain, AutoGen, CrewAI)
If you are building custom agents in Python (like DeepAgent), you can use the native Universal SDK and framework adapters.

**Step 1: Install**
```bash
pip install context-studio
```

**Step 2: Use the Universal Client**
```python
from context_studio.client import ContextStudioClient

client = ContextStudioClient(api_url="http://localhost:8000/v1", tenant_id="my_tenant", agent_id="my_agent")

# Log an interaction
await client.log_tool_execution(
    session_id="session_1", 
    tool_name="search_web", 
    tool_args={"query": "weather"}, 
    outcome="success", 
    result_text="It is sunny."
)
```

**Step 3: Use Framework-Specific Adapters**
Context Studio comes with built-in adapters for major frameworks:
- **LangChain:** `from context_studio.integrations.langchain import ContextStudioChatHistory`
- **AutoGen:** `from context_studio.integrations.autogen import ContextStudioMemoryPlugin`
- **CrewAI:** `from context_studio.integrations.crewai import ContextStudioCrewMemory`

---

### 3. Claude Code / Cursor / Any MCP Client
Context Studio implements Anthropic's **Model Context Protocol (MCP)** using FastMCP. This allows desktop apps like Claude Desktop and Cursor to securely search and modify your agent's memory graph without any HTTP server.

**Step 1: Configure Claude Desktop**
Open your Claude Desktop `claude_desktop_config.json` file and add Context Studio to your `mcpServers`:

```json
{
  "mcpServers": {
    "context-studio": {
      "command": "python",
      "args": [
        "-m",
        "context_studio.integrations.mcp_server"
      ],
      "env": {
        "CS_TENANT_ID": "your_tenant",
        "CS_AGENT_ID": "claude_desktop"
      }
    }
  }
}
```

**Step 2: Restart Claude**
Claude will now natively show a "tool" icon and can automatically call `remember`, `recall`, `get_facts`, `get_user_preferences`, and `add_rule` seamlessly during conversations.

---

## 🧠 Core Architecture Highlights

- **Tier 0:** Working Memory (Context budget optimizer & Paging)
- **Tier 1:** Conversational Memory (Dialogue threads)
- **Tier 2:** Episodic Memory (Experiences, time-decay, and outcomes)
- **Tier 3:** Semantic Memory (HippoRAG Knowledge Graph extraction)
- **Tier 4:** Procedural Memory (Skills and tool usage rules)
- **Tier 5:** User Preferences (Personalization)
- **Tier 6:** Organizational Memory (Governed data)
- **Tool Execution Bridge:** Intercepts external Sandbox tools to auto-learn skills and log failures.
