from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SecurityContext(BaseModel):
    role: str       # "admin", "agent", or "user"
    user_id: str    # The ID of the actual human user (for isolation)
    
class AgentCreate(BaseModel):
    tenant_id: str
    name: str

class MemoryQuery(BaseModel):
    agent_id: str
    session_id: str
    query: str
    security: SecurityContext

class MemoryInteraction(BaseModel):
    agent_id: str
    session_id: str
    role: str
    content: str
    turn_number: int
    security: SecurityContext

