import sys
import json
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
from database import SessionLocal
import models
from memory_sdk import MemoryEngine

# Create the FastMCP Server
mcp = FastMCP("Context Studio Memory Server")

# Helper to get the memory engine
def get_engine():
    db = SessionLocal()
    return MemoryEngine(db), db

@mcp.tool()
def init_agent(tenant_id: str, name: str) -> str:
    """Initialize a new Agent in the Memory system and return its agent_id."""
    _, db = get_engine()
    agent = models.Agent(tenant_id=tenant_id, name=name)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    db.close()
    return f"Agent created successfully. Agent ID: {agent.id}"

@mcp.tool()
def save_memory(agent_id: str, session_id: str, role: str, content: str, user_id: str) -> str:
    """
    Save a new conversational turn and extract facts/episodes.
    Requires user_id for RBAC security enforcement.
    """
    engine, db = get_engine()
    # Enforce standard Agent RBAC for MCP
    security = {"role": "agent", "user_id": user_id}
    
    # Calculate turn number based on existing cache length
    from memory_sdk import working_memory_cache
    wm_key = f"wm:{agent_id}:{session_id}"
    current_len = len(working_memory_cache.get(wm_key, []))
    
    engine.write_back(
        agent_id=agent_id,
        session_id=session_id,
        role=role,
        content=content,
        turn_number=current_len + 1,
        security_context=security
    )
    db.close()
    return "Memory successfully saved and vectorized."

@mcp.tool()
def get_context(agent_id: str, session_id: str, query: str, user_id: str) -> str:
    """
    Retrieve the full 5-tier context (Working, Episodic, Semantic, Procedural, Conversational).
    Requires user_id for RBAC security enforcement.
    """
    engine, db = get_engine()
    # Enforce standard Agent RBAC for MCP
    security = {"role": "agent", "user_id": user_id}
    
    try:
        context = engine.get_context(
            agent_id=agent_id, 
            session_id=session_id, 
            query=query, 
            security_context=security
        )
    except Exception as e:
        db.close()
        return f"Access Denied or Error: {str(e)}"
        
    db.close()
    return json.dumps(context, indent=2)

if __name__ == "__main__":
    # Start the MCP server over standard input/output
    mcp.run()
