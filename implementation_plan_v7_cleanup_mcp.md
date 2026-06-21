# Implementation Plan — Context Studio (Cleanup & MCP Integration)

> **Version:** 7.0 (Python Root Promotion & Model Context Protocol)  
> **Date:** 2026-06-21  
> **Status:** 🔶 Awaiting Approval

## Goal Description
The goal is to purge all legacy TypeScript/NodeJS monorepo code, making this repository a pure, production-ready **Python SDK**. I will also provide three complete, production-ready integration pathways as requested:
1. **SDK Integration** (LangChain)
2. **API Integration** (FastAPI REST)
3. **MCP Integration** (Model Context Protocol Server)

---

## User Review Required

> [!IMPORTANT]
> **Repository Restructure:** I will delete `apps/`, `packages/`, `package.json`, `turbo.json`, etc. I will then move all Python code from the `context_studio_python/` folder directly into the **root** of the repository. This is the standard best practice for a Python project. Does this root-promotion strategy sound good to you?

---

## 1. Codebase Cleanup
- **DELETE:**
  - `apps/` (NextJS Web App, NestJS Engine)
  - `packages/` (Shared UI, Database schemas)
  - `package.json`, `package-lock.json`, `turbo.json`, `.npmrc`, `test-engine.js`
- **MOVE:**
  - Shift all files from `context_studio_python/` to the repository root.
  - Delete the now-empty `context_studio_python/` folder.

## 2. Model Context Protocol (MCP) Integration
I will create a new file `integrations/mcp_server.py`.
This script will act as an **MCP Stdio Server**. It will expose tools that AI clients (like Claude Desktop or Cursor) can call to interact with your memory engine natively:
- **Tools Exposed:**
  - `init_agent(tenant_id, name)`
  - `write_memory(agent_id, session_id, role, content)`
  - `get_memory_context(agent_id, session_id, query)`

## 3. Documentation (README.md Update)
I will completely rewrite the root `README.md` to reflect a production Python repository. It will contain three distinct guides:
1. **API Integration Guide**: How to start the FastAPI server and use `cURL` (with RBAC security).
2. **SDK Integration Guide**: How to import `ContextStudioMemory` into LangChain/LangGraph flows.
3. **MCP Integration Guide**: How to configure Claude Desktop (`claude_desktop_config.json`) to use this engine as an MCP server.

## 4. Verification Plan
- Run `git status` to ensure all JS/TS files are removed and Python files are at the root.
- Run `test_langchain.py` and `test_security.py` from the root to ensure module imports are intact.
- Run a manual git commit and push to synchronize your GitHub repository.
