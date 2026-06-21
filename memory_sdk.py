import json
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from cachetools import TTLCache
import casbin
from casbin_sqlalchemy_adapter import Adapter
from database import engine as db_engine
import models

# Working Memory Cache (Local RAM)
# Holds up to 10,000 items, expires after 2 hours (7200 seconds)
working_memory_cache = TTLCache(maxsize=10000, ttl=7200)

def mock_embed(text: str) -> np.ndarray:
    """Mock an embedding generator (1536 dims like OpenAI)"""
    vec = np.zeros(1536)
    for i in range(min(len(text), 1536)):
        vec[i] = (ord(text[i]) % 10) / 10.0
    return vec

class PermissionDenied(Exception):
    pass

class MemoryEngine:
    def __init__(self, db: Session):
        self.db = db
        # Initialize Casbin Adapter with our SQLAlchemy engine
        adapter = Adapter(db_engine)
        self.enforcer = casbin.Enforcer("casbin_model.conf", adapter)

    def enforce_rbac(self, agent_id: str, session_id: str, security_context: dict):
        role = security_context.get("role", "user")
        user_id = security_context.get("user_id", "")
        
        if role == "admin":
            return # Admins bypass via matcher
            
        # The 'subject' is the user_id (or agent_id if role is agent)
        sub = user_id if role == "user" else agent_id
        # The 'object' they want to access is the session_id
        obj = session_id
        # The 'action' is read_write
        act = "read_write"

        # Auto-grant access to users for their own session if it's their user_id
        # This simulates a platform assigning permissions when a session is created.
        if role == "user" and user_id in session_id:
            # Add policy if it doesn't exist
            if not self.enforcer.has_policy(sub, obj, act):
                self.enforcer.add_policy(sub, obj, act)
                
        # Auto-grant access to agents for their own agent_id
        if role == "agent" and agent_id == sub:
             if not self.enforcer.has_policy(sub, obj, act):
                self.enforcer.add_policy(sub, obj, act)

        # Check PyCasbin policy
        if not self.enforcer.enforce(sub, obj, act):
            raise PermissionDenied(f"PyCasbin: Subject '{sub}' cannot access Session '{obj}'")

    def get_context(self, agent_id: str, session_id: str, query: str, security_context: dict):
        # Enforce RBAC
        self.enforce_rbac(agent_id, session_id, security_context)

        # 1. Working Memory (LRU Cache)
        wm_key = f"wm:{agent_id}:{session_id}"
        working_memory = working_memory_cache.get(wm_key, [])

        # 2. Conversational Memory
        recent_turns = self.db.query(models.ConversationTurn)\
            .filter(models.ConversationTurn.agent_id == agent_id, models.ConversationTurn.session_id == session_id)\
            .order_by(models.ConversationTurn.turn_number.desc())\
            .limit(10).all()

        # 3. Episodic Memory (Vector Dot-Product)
        episodic = self.search_episodic_memory(agent_id, query, top_k=3)

        # 4. Semantic Memory (Graph Traversal)
        semantic = self.search_semantic_graph(agent_id, query)

        # 5. Procedural Memory (Rules / Instructions)
        procedural = self.search_procedural_memory(agent_id, query)

        return {
            "workingMemory": working_memory,
            "conversational": [{"role": t.role, "content": t.content} for t in reversed(recent_turns)],
            "episodic": episodic,
            "semanticGraph": semantic,
            "procedural": procedural
        }

    def write_back(self, agent_id: str, session_id: str, role: str, content: str, turn_number: int, security_context: dict):
        # Enforce RBAC
        self.enforce_rbac(agent_id, session_id, security_context)
        
        # 1. Update Working Memory
        wm_key = f"wm:{agent_id}:{session_id}"
        current_wm = working_memory_cache.get(wm_key, [])
        interaction = {"role": role, "content": content, "turn_number": turn_number}
        working_memory_cache[wm_key] = current_wm + [interaction]

        # 2. Persist Conversational Turn
        turn = models.ConversationTurn(
            agent_id=agent_id, session_id=session_id, role=role, content=content, turn_number=turn_number
        )
        self.db.add(turn)
        self.db.commit()

        # 3. Async extraction (Mocked synchronously here for MVP)
        if role == 'user':
            summary = f"User stated: {content[:50]}..."
            self.save_episodic_memory(agent_id, summary)
            self.save_semantic_fact(agent_id, content)

    # --- EPISODIC (VECTOR) MEMORY ---
    def save_episodic_memory(self, agent_id: str, summary: str):
        vector = mock_embed(summary).tolist()
        ep = models.EpisodicVector(
            agent_id=agent_id, summary=summary, vector_data=json.dumps(vector)
        )
        self.db.add(ep)
        self.db.commit()

    def search_episodic_memory(self, agent_id: str, query: str, top_k: int = 3):
        query_vec = mock_embed(query)
        all_episodes = self.db.query(models.EpisodicVector).filter(models.EpisodicVector.agent_id == agent_id).all()
        
        results = []
        for ep in all_episodes:
            vec_data = np.array(json.loads(ep.vector_data))
            # Cosine similarity / Dot product
            score = np.dot(query_vec, vec_data)
            
            # Decay score based on time
            days_old = (datetime.utcnow() - ep.created_at).total_seconds() / (3600 * 24)
            decay_factor = np.exp(-0.05 * days_old)
            final_score = score * decay_factor * ep.decay_score
            
            results.append({"summary": ep.summary, "score": float(final_score)})
        
        # Sort descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    # --- SEMANTIC (GRAPH) MEMORY ---
    def save_semantic_fact(self, agent_id: str, text: str):
        # Mock logic: split by " is " to create "A IS_A B"
        if " is " in text:
            parts = text.split(" is ")
            if len(parts) == 2:
                source, target = parts[0].strip(), parts[1].strip()
                
                # Upsert nodes
                node_a = self.db.query(models.KgNode).filter_by(agent_id=agent_id, name=source).first()
                if not node_a:
                    node_a = models.KgNode(agent_id=agent_id, name=source, node_type="entity")
                    self.db.add(node_a)
                
                node_b = self.db.query(models.KgNode).filter_by(agent_id=agent_id, name=target).first()
                if not node_b:
                    node_b = models.KgNode(agent_id=agent_id, name=target, node_type="concept")
                    self.db.add(node_b)
                
                self.db.commit() # commit to get IDs
                
                # Create Edge
                edge = models.KgEdge(source_id=node_a.id, target_id=node_b.id, relation_type="IS_A")
                self.db.add(edge)
                self.db.commit()

    def search_semantic_graph(self, agent_id: str, query: str):
        words = query.split(" ")
        facts = []
        
        # Super simplified traversal: Match nodes containing query words, then fetch their edges
        for word in words:
            if len(word) < 3: continue
            
            # SQLite LIKE query
            nodes = self.db.query(models.KgNode).filter(
                models.KgNode.agent_id == agent_id,
                models.KgNode.name.like(f"%{word}%")
            ).all()
            
            for node in nodes:
                # Outgoing edges
                outgoing = self.db.query(models.KgEdge).filter_by(source_id=node.id).all()
                for edge in outgoing:
                    target = self.db.query(models.KgNode).filter_by(id=edge.target_id).first()
                    if target:
                        facts.append(f"{node.name} {edge.relation_type} {target.name}")
        
        return list(set(facts))

    # --- PROCEDURAL MEMORY ---
    def save_procedural_rule(self, agent_id: str, trigger_keyword: str, instruction: str):
        rule = models.ProceduralRule(
            agent_id=agent_id, trigger_keyword=trigger_keyword.lower(), rule_instruction=instruction
        )
        self.db.add(rule)
        self.db.commit()

    def search_procedural_memory(self, agent_id: str, query: str):
        import re
        clean_query = re.sub(r'[^\w\s]', '', query.lower())
        words = clean_query.split(" ")
        rules = []
        for word in words:
            if len(word) < 3: continue
            matches = self.db.query(models.ProceduralRule).filter(
                models.ProceduralRule.agent_id == agent_id,
                models.ProceduralRule.trigger_keyword == word
            ).all()
            for m in matches:
                rules.append(m.rule_instruction)
        return list(set(rules))

