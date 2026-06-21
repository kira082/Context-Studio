from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_api():
    print("Context Studio Python API Test (Local Client)\n")
    
    # 1. Initialize Agent
    print("[1] Initializing Agent...")
    res = client.post("/api/init", json={
        "tenant_id": "tenant_python_1",
        "name": "Python Integration Bot"
    })
    res.raise_for_status()
    agent_id = res.json()["agent_id"]
    print(f"Agent Created: {agent_id}\n")

    # 2. Write Memory (User Input)
    print("[2] Simulating Chat Turn 1...")
    user_stmt = "The default api port is 8000"
    client.post("/api/memory", json={
        "agent_id": agent_id,
        "session_id": "session_A",
        "role": "user",
        "content": user_stmt,
        "turn_number": 1
    }).raise_for_status()
    print("Memory Written and Semantic/Episodic Extracted!\n")

    # 3. Retrieve Context
    print("[3] Fetching Assembled Context for Turn 2...")
    res = client.post("/api/context", json={
        "agent_id": agent_id,
        "session_id": "session_A",
        "query": "What is the default api port?"
    })
    res.raise_for_status()
    
    context = res.json()["context"]
    print("Retrieved Context:")
    print(json.dumps(context, indent=2))

if __name__ == "__main__":
    test_api()
