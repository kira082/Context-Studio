# Implementation Plan — Context Studio (RBAC & Security)

> **Version:** 6.0 (Role-Based Access Control & API Security)  
> **Date:** 2026-06-21  
> **Status:** 🔶 Awaiting Approval

## Goal Description
The user wants to add an **RBAC (Role-Based Access Control)** and **Security Layer** on top of the existing Context Memory SDK. Since this SDK will act as the "central brain" for different agents and users, we must ensure strict data isolation and access control so that unauthorized users cannot read or overwrite another user's memory, and external systems cannot hit the API without authentication.

---

## User Review Required

> [!IMPORTANT]
> **Authentication Strategy:** To secure the FastAPI endpoints, I propose implementing an **API Key** authentication layer (`X-API-Key` header). For the internal SDK logic, I propose an **Attribute-Based/Role-Based Access** model where every request must provide a `role` (`admin`, `agent`, or `user`) and the system will explicitly block a `user` from reading memories belonging to a different `session_id`. Does this API Key + 3-Tier Role approach fit your existing platform's security architecture?

---

## 1. Security Architecture (RBAC)

### 1.1 API Security (Authentication)
We will secure the `main.py` FastAPI endpoints using a `Depends()` middleware that checks for a valid `X-API-Key` header. Only your trusted platform servers should have this key.

### 1.2 Data Isolation & RBAC (Authorization)
Inside the `memory_sdk.py`, we will introduce a `SecurityContext`. Every read/write operation will require this context.

**Roles:**
- **`ADMIN`**: Can access all memory and configure rules across all agents and tenants.
- **`AGENT`**: Can only read/write memories explicitly tied to its own `agent_id`.
- **`USER`**: Can only read/write memories explicitly tied to their own `session_id` (so User A cannot inject false memories into User B's dialogue history).

---

## 2. Proposed Changes

#### `models.py`
- `[NEW]` Add an `ApiKey` table to manage valid authentication tokens for external platforms.
- `[MODIFY]` Update tables to strictly enforce `tenant_id` mappings.

#### `schemas.py`
- `[MODIFY]` Add `SecurityContext` (Role, User ID) requirements to the incoming Pydantic API payloads.

#### `memory_sdk.py`
- `[NEW]` Create an `enforce_rbac()` decorator/function that validates permissions before executing `get_context` or `write_back`.
- `[NEW]` Add `PermissionDenied` exceptions.

#### `main.py`
- `[NEW]` Add `APIKeyHeader` FastAPI middleware to strictly block unauthenticated external network requests.

#### `integrations/langchain_wrapper.py`
- `[MODIFY]` Update the LangChain wrapper so it securely passes the `SecurityContext` when initialized by an Agent.

---

## 3. Verification Plan
I will write a script (`test_security.py`) that attempts to:
1. Call the API without an API Key (Expect: `401 Unauthorized`).
2. Simulate `User_A` trying to read `User_B`'s memory (Expect: `403 Forbidden`).
3. Simulate an `Agent` successfully reading its own memory (Expect: `200 OK`).
