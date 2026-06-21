from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from memory_sdk import MemoryEngine, PermissionDenied

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Create all SQLite tables
models.Base.metadata.create_all(bind=engine)

def get_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    # Very simple logic: We allow 'dev_key' for testing, or we look it up in the DB
    if api_key == "dev_key":
        return api_key
    
    key_record = db.query(models.ApiKey).filter_by(key_value=api_key, is_active=1).first()
    if not key_record:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

app = FastAPI(
    title="Context Studio API",
    description="Python Plug-and-Play Memory Microservice",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "context-studio"}

@app.post("/api/init", response_model=dict, dependencies=[Depends(get_api_key)])
def initialize_agent(agent_data: schemas.AgentCreate, db: Session = Depends(get_db)):
    """Initialize a new agent in the memory store"""
    agent = models.Agent(tenant_id=agent_data.tenant_id, name=agent_data.name)
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return {"status": "success", "agent_id": agent.id}

@app.post("/api/context", response_model=dict, dependencies=[Depends(get_api_key)])
def retrieve_context(query_data: schemas.MemoryQuery, db: Session = Depends(get_db)):
    """Retrieve full assembled context (Working, Episodic, Semantic, Conversational)"""
    agent = db.query(models.Agent).filter(models.Agent.id == query_data.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    engine = MemoryEngine(db)
    try:
        context = engine.get_context(
            agent_id=query_data.agent_id, 
            session_id=query_data.session_id, 
            query=query_data.query,
            security_context=query_data.security.dict()
        )
        return {"status": "success", "context": context}
    except PermissionDenied as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post("/api/memory", response_model=dict, dependencies=[Depends(get_api_key)])
def write_memory(interaction: schemas.MemoryInteraction, db: Session = Depends(get_db)):
    """Write an interaction back to memory and trigger fact/episode extraction"""
    agent = db.query(models.Agent).filter(models.Agent.id == interaction.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    engine = MemoryEngine(db)
    try:
        engine.write_back(
            agent_id=interaction.agent_id,
            session_id=interaction.session_id,
            role=interaction.role,
            content=interaction.content,
            turn_number=interaction.turn_number,
            security_context=interaction.security.dict()
        )
        return {"status": "success", "message": "Memory persisted and extracted"}
    except PermissionDenied as e:
        raise HTTPException(status_code=403, detail=str(e))
