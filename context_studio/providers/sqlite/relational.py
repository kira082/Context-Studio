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
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_turns (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    turn_number INTEGER,
                    metadata TEXT,
                    created_at REAL
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_session ON conversation_turns(session_id)')
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
