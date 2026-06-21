from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, engine
import models
import traceback

client = TestClient(app)

def run_security_tests():
    print("Context Studio Security & RBAC Tests\n")
    
    # Setup DB
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    print("--- 1. Testing Network API Security ---")
    res = client.post("/api/init", json={"tenant_id": "t1", "name": "Bot"})
    if res.status_code in [401, 403]:
        print("SUCCESS: Blocked unauthenticated request (No API Key)")
    else:
        print(f"FAILED: Allowed unauthenticated request. Status: {res.status_code}")
        
    # Authorized Request
    headers = {"X-API-Key": "dev_key"}
    res = client.post("/api/init", json={"tenant_id": "t1", "name": "Secure Bot"}, headers=headers)
    agent_id = res.json()["agent_id"]
    print("SUCCESS: Allowed authenticated request")
    
    print("\n--- 2. Testing Internal Data Isolation (RBAC) ---")
    
    # Write Memory as USER_A
    print("[*] User A writes to their session...")
    client.post("/api/memory", json={
        "agent_id": agent_id,
        "session_id": "session_userA",
        "role": "user",
        "content": "My secret is 123",
        "turn_number": 1,
        "security": {"role": "user", "user_id": "userA"}
    }, headers=headers).raise_for_status()
    
    # User B tries to read User A's session
    print("[*] User B attempts to read User A's session...")
    res = client.post("/api/context", json={
        "agent_id": agent_id,
        "session_id": "session_userA", # Trying to read A's session
        "query": "What is the secret?",
        "security": {"role": "user", "user_id": "userB"} # But I am user B!
    }, headers=headers)
    
    if res.status_code == 403:
        print("SUCCESS: Blocked User B from reading User A's session (Data Isolation Works!)")
    else:
        print(f"FAILED: User B was able to read User A's session! {res.status_code}")

    # Admin tries to read User A's session
    print("[*] Admin attempts to read User A's session...")
    res = client.post("/api/context", json={
        "agent_id": agent_id,
        "session_id": "session_userA",
        "query": "What is the secret?",
        "security": {"role": "admin", "user_id": "admin_1"} 
    }, headers=headers)
    
    if res.status_code == 200:
        print("SUCCESS: Admin was allowed to read the session.")
    else:
        print(f"FAILED: Admin was blocked! {res.status_code}")

if __name__ == "__main__":
    try:
        run_security_tests()
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()
