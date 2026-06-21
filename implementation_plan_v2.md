# Implementation Plan — Context Studio (Final Architecture)

> **Version:** Final (Production-Ready Python SDK)  
> **Date:** 2026-06-21  
> **Status:** ✅ Fully Implemented

---

## 1. High-Level Design (HLD)
Context Studio is a production-ready, pure Python **Memory Engine** designed for local-native operation. It implements a complete 5-tier cognitive architecture described in state-of-the-art AI memory research, without requiring cloud databases or Docker. 

It provides three standard integration pathways:
1. **MCP (Model Context Protocol) Server:** Native `stdio` server for Claude Desktop, Cursor, and other MCP clients.
2. **REST API (FastAPI):** For generic HTTP clients, N8N, or no-code agent builders.
3. **Python SDK:** For direct injection into LangChain, LangGraph, or custom ReAct loops.

---

## 2. The 5-Layer Cognitive Architecture

### 2.1 Working Memory
- **Algorithm:** In-memory LRU Cache with TTL.
- **Purpose:** Fast access to the current conversational context. Drops old contexts dynamically to prevent context-window overflow.

### 2.2 Conversational Memory
- **Algorithm:** SQLite relational table mapping sequential Dialogue turns.
- **Purpose:** Retains raw dialogue history. Provides pagination and summary fallbacks when Working Memory is evicted.

### 2.3 Episodic Memory
- **Algorithm:** NumPy dot-product vector search on embeddings.
- **Purpose:** Stores specific past experiences or events.
- **Boundary Cases Handled:** Implements an implicit time-decay algorithm so recent episodes naturally score higher than older ones, preventing semantic saturation.

### 2.4 Semantic Memory
- **Algorithm:** Local SQLite Knowledge Graph (Nodes and Edges).
- **Purpose:** Retains structural facts (e.g., "User -> Likes -> Python"). 
- **Boundary Cases Handled:** Extracts isolated Triples from raw dialogue via LLM processing and prevents duplicate nodes.

### 2.5 Procedural Memory
- **Algorithm:** "If-Then" trigger matching.
- **Purpose:** Allows the agent to automatically invoke predefined rules (e.g., "If user mentions security, remind them of PyCasbin").

---

## 3. Security & RBAC (PyCasbin)

Context Studio utilizes **PyCasbin**, the industry-standard authorization library, combined with `casbin-sqlalchemy-adapter`.

### 3.1 Model Definition
- Supports standard `sub, obj, act` RBAC and ABAC modeling.
- **Admins:** Granted global bypass via matcher (`r.sub == "admin"`).
- **Users/Agents:** Policies strictly bind `user_id` or `agent_id` to their specific `session_id`.

### 3.2 Dynamic Data Isolation
When an agent or user creates a session, the SDK dynamically writes a Casbin policy to the SQLite `casbin_rule` table. If any other user attempts to read or write to that session, the PyCasbin `Enforcer` throws a `PermissionDenied` error, ensuring zero data bleeding between tenants or users.

### 3.3 Network Security
The FastAPI and MCP integrations enforce standard authentication (e.g., `X-API-Key`) before RBAC context is even evaluated.

---

## 4. Repository Structure (Modular Python)

```text
.
├── casbin_model.conf           # Declarative PyCasbin Authorization Model
├── database.py                 # SQLAlchemy Setup & Connection
├── integrations/               # The 3 Integration Points
│   ├── langchain_wrapper.py    # Native SDK wrapper for LangChain/LangGraph
│   └── mcp_server.py           # Anthropic FastMCP Server implementation
├── main.py                     # FastAPI REST server & API endpoints
├── memory_sdk.py               # Core Orchestrator (The 5 Layers & PyCasbin Logic)
├── models.py                   # SQLAlchemy ORM Models (Agents, Memory, etc.)
├── schemas.py                  # Pydantic validation schemas
├── requirements.txt            # Production dependencies (casbin, numpy, fastapi, etc.)
└── test_security.py            # Automated RBAC testing suite
```

---

## 5. Boundary & Edge Cases Handled

| Case | Strategy |
|:---|:---|
| **Vector Scale Limits** | Brute-force dot product in NumPy is O(N). Extremely fast locally for <10,000 vectors. If scale exceeds this, NumPy is easily swappable with `faiss-cpu`. |
| **Concurrency / DB Locks** | SQLite WAL (Write-Ahead Logging) is inherently supported via SQLAlchemy's connection pooling, allowing simultaneous asynchronous reads/writes from the API. |
| **Missing PyCasbin Policies** | SDK handles auto-granting access to session creators, preventing soft-locks for new users. |
| **Windows Emoji Encoding** | Handled. Standard output sanitized to prevent `cp1252` encoding crashes in local environments. |
