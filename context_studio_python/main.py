from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from memory_sdk import MemoryEngine

# Create all SQLite tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Context Studio API",
    description="Python Plug-and-Play Memory Microservice",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "context-studio"}

@app.post("/api/init", response_model=dict)
def initialize_agent(agent_data: schemas.AgentCreate, db: Session = Depends(get_db)):
    """Initialize a new agent in the memory store"""
    agent = models.Agent(tenant_id=agent_data.tenant_id, name=agent_data.name)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return {"status": "success", "agent_id": agent.id}

@app.post("/api/context", response_model=dict)
def retrieve_context(query_data: schemas.MemoryQuery, db: Session = Depends(get_db)):
    """Retrieve full assembled context (Working, Episodic, Semantic, Conversational)"""
    agent = db.query(models.Agent).filter(models.Agent.id == query_data.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    engine = MemoryEngine(db)
    context = engine.get_context(
        agent_id=query_data.agent_id, 
        session_id=query_data.session_id, 
        query=query_data.query
    )
    return {"status": "success", "context": context}

@app.post("/api/memory", response_model=dict)
def write_memory(interaction: schemas.MemoryInteraction, db: Session = Depends(get_db)):
    """Write an interaction back to memory and trigger fact/episode extraction"""
    agent = db.query(models.Agent).filter(models.Agent.id == interaction.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    engine = MemoryEngine(db)
    engine.write_back(
        agent_id=interaction.agent_id,
        session_id=interaction.session_id,
        role=interaction.role,
        content=interaction.content,
        turn_number=interaction.turn_number
    )
    return {"status": "success", "message": "Memory persisted and extracted"}
