import sqlite3
import json
import uuid
import time
import os
from typing import Dict, List, Any, Optional
from context_studio.providers.base import RelationalProvider

class SQLiteRelationalProvider(RelationalProvider):
    def __init__(self, db_path: str = ".data/relational.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # conversation_turns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL DEFAULT 'default',
                    agent_id TEXT NOT NULL DEFAULT 'default',
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    turn_number INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    token_count INTEGER,
                    metadata TEXT,
                    created_at REAL
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_turns_session ON conversation_turns(session_id, turn_number)')
            
            # procedural_rules
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS procedural_rules (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    agent_id TEXT,
                    name TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    trigger_condition TEXT NOT NULL,
                    action_sequence TEXT NOT NULL,
                    priority INTEGER DEFAULT 50,
                    confidence REAL DEFAULT 1.0,
                    learned INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at REAL
                )
            ''')
            
            # user_preferences
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    response_style TEXT DEFAULT 'balanced',
                    technical_level TEXT DEFAULT 'intermediate',
                    tone TEXT DEFAULT 'professional',
                    common_topics TEXT DEFAULT '[]',
                    explicit_prefs TEXT DEFAULT '{}',
                    interaction_count INTEGER DEFAULT 0,
                    confidence REAL DEFAULT 0.3,
                    updated_at REAL,
                    UNIQUE(tenant_id, user_id)
                )
            ''')
            # semantic_facts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS semantic_facts (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    agent_id TEXT,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object_val TEXT NOT NULL,
                    confidence REAL DEFAULT 0.7,
                    corroboration_count INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'active',
                    superseded_by TEXT REFERENCES semantic_facts(id),
                    valid_from REAL,
                    valid_until REAL,
                    lineage TEXT,
                    created_at REAL
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_facts_tenant_subject ON semantic_facts(tenant_id, subject)')
            
            # episodic_metadata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS episodic_metadata (
                    id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    episode_type TEXT,
                    summary TEXT NOT NULL,
                    outcome TEXT,
                    importance_score INTEGER DEFAULT 5,
                    decay_score REAL DEFAULT 1.0,
                    access_count INTEGER DEFAULT 0,
                    last_accessed_at REAL,
                    lineage TEXT,
                    created_at REAL
                )
            ''')
            
            conn.commit()

    async def save_turn(self, session_id: str, turn_data: Dict[str, Any]) -> str:
        turn_id = str(uuid.uuid4())
        created_at = time.time()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversation_turns (id, session_id, role, content, turn_number, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                turn_id,
                session_id,
                turn_data.get("role", ""),
                turn_data.get("content", ""),
                turn_data.get("turn_number", 0),
                json.dumps(turn_data.get("metadata", {})),
                created_at
            ))
            conn.commit()
            
        return turn_id

    async def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM conversation_turns 
                WHERE session_id = ? 
                ORDER BY created_at ASC 
                LIMIT ?
            ''', (session_id, limit))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "turn_number": row["turn_number"],
                    "metadata": json.loads(row["metadata"]),
                    "timestamp": row["created_at"]
                })
            return results

    async def search_relational(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Extremely basic text search
            search_pattern = f"%{query}%"
            cursor.execute('''
                SELECT * FROM conversation_turns 
                WHERE content LIKE ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (search_pattern, limit))
            
            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "session_id": row["session_id"],
                    "role": row["role"],
                    "content": row["content"],
                    "turn_number": row["turn_number"],
                    "metadata": json.loads(row["metadata"]),
                    "timestamp": row["created_at"]
                })
            return results
