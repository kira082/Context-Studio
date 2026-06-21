from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AgentCreate(BaseModel):
    tenant_id: str
    name: str

class MemoryQuery(BaseModel):
    agent_id: str
    session_id: str
    query: str

class MemoryInteraction(BaseModel):
    agent_id: str
    session_id: str
    role: str
    content: str
    turn_number: int
