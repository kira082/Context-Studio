# Context Studio Tasks (PyCasbin RBAC)

## Phase 8 — PyCasbin Integration
- [ ] Add `casbin` and `casbin-sqlalchemy-adapter` to `requirements.txt`.
- [ ] Create `casbin_model.conf`.
- [ ] Initialize Casbin Enforcer in `memory_sdk.py` using DB adapter.
- [ ] Rewrite `enforce_rbac` to utilize `enforcer.enforce()`.
- [ ] Test the Casbin security rules using `test_security.py`.
- [ ] Commit and Push changes.
