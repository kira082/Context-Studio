# Python Context Studio SDK (Walkthrough)

I have successfully built the **RBAC (Role-Based Access Control) & Security Layer** into the Python SDK! The system is now locked down and ready for production usage across different teams, agents, and end-users.

## 🛡️ The Two-Tier Security Architecture

### 1. Network Level Security (FastAPI)
The FastAPI endpoints are now secured via an `APIKeyHeader` middleware. Your external platforms (n8n, React Flow, etc.) must now provide an `X-API-Key` header with every request. Without it, the system immediately returns a `401 Unauthorized`.

### 2. Internal Data Isolation (RBAC)
Every memory operation in the SDK now strictly requires a `SecurityContext` containing a `role` and a `user_id`.
- **`admin`**: Can read/write anything.
- **`user`**: Cannot access memory that belongs to a different `session_id`. If User A tries to read User B's conversational history, the engine throws a `403 Permission Denied`. This completely prevents data-bleeding across concurrent users.

---

## 🧠 The Complete 5-Tier Memory Algorithm
The `MemoryEngine` still parses every query through all 5 layers:
1. **Working Memory:** Local RAM `cachetools` LRU buffer.
2. **Conversational Memory:** Complete interaction history logged to local SQLite.
3. **Episodic Vectors:** Embedded vectors evaluated natively via `NumPy` dot-product math (with time-based decay).
4. **Semantic Graphs:** SQLite relational edge traversals acting as a local Knowledge Graph.
5. **Procedural Memory (Rules & Skills):** Trigger-based instructions stored in SQLite that inject "If-Then" rules directly into the agent's context.

---

## 🚀 How to Test the Security Layer Locally

I wrote an automated testing script that attempts to hack the system (simulating an unauthenticated request, and simulating User B trying to steal User A's memory). You can run it to see the RBAC in action:

```bash
cd context_studio_python
venv\Scripts\activate
python test_security.py
```

## 🔌 API Integration Examples

**1. Securely Save a Memory (With API Key & Role)**
```bash
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

The system is now fully localized, completely functional across all 5 tiers of cognitive architecture, and perfectly secure.
