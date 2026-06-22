from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional

from context_studio.core.config import MemoryConfig
from context_studio.auth.casbin_enforcer import RBACManager

app = FastAPI(title="Context Studio REST API", version="5.0.0")

# Global instances (in production, use dependency injection)
config = MemoryConfig()
rbac_manager = RBACManager()

# Request Models
class MemoryQuery(BaseModel):
    session_id: str
    query: str
    limit: int = 5

class MemoryInteraction(BaseModel):
    session_id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

def verify_access(x_tenant_id: str = Header(...), x_agent_id: str = Header(...)):
    """
    Middleware/Dependency to extract Tenant ID and Agent ID and verify global access.
    """
    if not x_tenant_id or not x_agent_id:
        raise HTTPException(status_code=401, detail="X-Tenant-ID or X-Agent-ID header missing")
    return {"tenant_id": x_tenant_id, "agent_id": x_agent_id}

@app.get("/v1/health")
async def health_check():
    return {
        "status": "healthy", 
        "version": "5.0.0", 
        "storage": {
            "cache": config.storage.cache_provider,
            "relational": config.storage.relational_provider,
            "vector": config.storage.vector_provider,
            "graph": config.storage.graph_provider
        }
    }

@app.post("/v1/memory/search")
async def search_memory(query: MemoryQuery, auth: dict = Depends(verify_access)):
    """
    Search memory across all configured layers (Hybrid + RRF + Re-Ranker).
    """
    # 1. Security Check
    if not rbac_manager.enforce(auth["agent_id"], auth["tenant_id"], query.session_id, "read"):
        raise HTTPException(status_code=403, detail="Access denied to this session memory.")

    # TODO: Implement Retrieval Pipeline
    return {
        "status": "success",
        "context": f"Dummy context for {query.query} in session {query.session_id}",
        "config_used": "..."
    }

@app.post("/v1/memory/add")
async def add_memory(interaction: MemoryInteraction, auth: dict = Depends(verify_access)):
    """
    Add a new interaction. Triggers Async Write-Back pipeline.
    """
    # Auto-grant access if the session doesn't exist for the agent
    rbac_manager.auto_grant_session_access(auth["agent_id"], auth["tenant_id"], interaction.session_id)
    
    if not rbac_manager.enforce(auth["agent_id"], auth["tenant_id"], interaction.session_id, "write"):
         raise HTTPException(status_code=403, detail="Access denied to this session memory.")

    # TODO: Implement Async Write Pipeline
    return {
        "status": "success",
        "message": "Memory added to async write-back queue."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("context_studio.api.main:app", host="0.0.0.0", port=8000, reload=True)
