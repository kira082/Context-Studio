import os
import json
import uuid
import time
from typing import Dict, List, Any, Optional
from context_studio.providers.base import RelationalProvider

class FileSystemRelationalProvider(RelationalProvider):
    def __init__(self, base_dir: str = ".data/relational"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.turns_file = os.path.join(self.base_dir, "turns.json")
        if not os.path.exists(self.turns_file):
            with open(self.turns_file, "w") as f:
                json.dump([], f)

    def _read_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.turns_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_data(self, data: List[Dict[str, Any]]):
        with open(self.turns_file, "w") as f:
            json.dump(data, f, indent=2)

    async def save_turn(self, session_id: str, turn_data: Dict[str, Any]) -> str:
        data = self._read_data()
        turn_id = str(uuid.uuid4())
        
        record = {
            "id": turn_id,
            "session_id": session_id,
            "timestamp": time.time(),
            **turn_data
        }
        
        data.append(record)
        self._write_data(data)
        return turn_id

    async def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        data = self._read_data()
        # Filter by session_id and sort by timestamp
        session_data = [d for d in data if d.get("session_id") == session_id]
        session_data.sort(key=lambda x: x.get("timestamp", 0))
        return session_data[-limit:]

    async def search_relational(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        data = self._read_data()
        # Very basic substring matching for offline mode
        query_lower = query.lower()
        results = []
        for d in data:
            content = d.get("content", "").lower()
            if query_lower in content:
                results.append(d)
        
        # Sort by timestamp descending
        results.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return results[:limit]
