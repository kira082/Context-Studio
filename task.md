# Context Studio Tasks (RBAC & Security)

## Phase 6 — RBAC & Security Layer
- [x] Add `ApiKey` table to `models.py`.
- [x] Implement `APIKeyHeader` authentication in FastAPI (`main.py`).
- [x] Define `SecurityContext` inside `schemas.py`.
- [x] Create `enforce_rbac()` access control logic in `memory_sdk.py`.
- [x] Update LangChain wrapper to inject `SecurityContext`.
- [x] Write `test_security.py` to verify authentication and data isolation.
