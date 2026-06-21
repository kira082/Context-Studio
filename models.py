import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ApiKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, default=generate_uuid)
    key_value = Column(String, unique=True, index=True)
    tenant_id = Column(String, index=True)
    is_active = Column(Integer, default=1)  # 1 for True, 0 for False
    created_at = Column(DateTime, default=datetime.utcnow)

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, default=generate_uuid)
    tenant_id = Column(String, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConversationTurn(Base):
    __tablename__ = "conversation_turns"
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id"), index=True)
    session_id = Column(String, index=True)
    turn_number = Column(Integer)
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class KgNode(Base):
    __tablename__ = "kg_nodes"
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id"), index=True)
    name = Column(String, index=True)
    node_type = Column(String)

class KgEdge(Base):
    __tablename__ = "kg_edges"
    id = Column(String, primary_key=True, default=generate_uuid)
    source_id = Column(String, ForeignKey("kg_nodes.id"), index=True)
    target_id = Column(String, ForeignKey("kg_nodes.id"), index=True)
    relation_type = Column(String)
    
    # We use simple string foreign keys for MVP traversal
    source = relationship("KgNode", foreign_keys=[source_id])
    target = relationship("KgNode", foreign_keys=[target_id])

class EpisodicVector(Base):
    __tablename__ = "episodic_vectors"
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id"), index=True)
    summary = Column(Text)
    vector_data = Column(Text) # JSON string array of floats
    decay_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProceduralRule(Base):
    __tablename__ = "procedural_rules"
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id"), index=True)
    trigger_keyword = Column(String, index=True)
    rule_instruction = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

