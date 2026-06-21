# Implementation Plan — Context Studio (PyCasbin RBAC)

> **Version:** 8.0 (Enterprise RBAC with PyCasbin)  
> **Date:** 2026-06-21  
> **Status:** 🔶 Awaiting Approval

## Goal Description
The user wants to replace the current manual `if/else` role-checking logic with **PyCasbin** (referred to as "pycabin"). PyCasbin is the industry-standard authorization library that supports advanced RBAC, ABAC, and ACL models. By integrating PyCasbin with our SQLite database, we make the access control layer infinitely scalable and declarative.

---

## User Review Required

> [!IMPORTANT]
> **Database-Backed Policies:** I plan to use `casbin-sqlalchemy-adapter` alongside `casbin`. This means your authorization policies (who can access what) will be stored directly inside your existing SQLite database rather than a static CSV file. This allows you to dynamically grant or revoke permissions at runtime. Does this dynamic database approach work for your platform?

---

## 1. PyCasbin Configuration
We will define a standard RBAC model in a new file `casbin_model.conf`:
```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
```

## 2. Proposed Code Changes

#### `requirements.txt`
- `[MODIFY]` Add `casbin` and `casbin-sqlalchemy-adapter`.

#### `database.py` / `models.py`
- No direct changes needed to models! The `casbin-sqlalchemy-adapter` will automatically create a `casbin_rule` table in our SQLite database to store policies.

#### `memory_sdk.py`
- `[MODIFY]` Import `casbin` and `casbin_sqlalchemy_adapter`.
- `[MODIFY]` Initialize the `Enforcer` connected to the SQLAlchemy session.
- `[MODIFY]` Rewrite `enforce_rbac(sub, obj, act)` to call `enforcer.enforce(sub, obj, act)`. If it returns False, raise `PermissionDenied`.
- `[NEW]` When `MemoryEngine` is initialized, we will seed default policies:
  - `p, admin, global, read_write`
  - `p, user, their_own_session, read_write`

#### `test_security.py`
- `[MODIFY]` Update the test script to prove that PyCasbin is successfully intercepting and blocking unauthorized access requests based on the database policies.

---

## 3. Verification Plan
- Run `pip install -r requirements.txt` to install Casbin.
- Run `test_security.py`. We expect the exact same output as before (Admin allowed, User A allowed, User B blocked), but this time it will be powered entirely by the Casbin policy engine!
