import os
import json
import uuid
from typing import Dict, List, Any, Optional
from context_studio.providers.base import GraphProvider

class FileSystemGraphProvider(GraphProvider):
    def __init__(self, base_dir: str = ".data/graph"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.graph_file = os.path.join(self.base_dir, "triples.json")
        if not os.path.exists(self.graph_file):
            with open(self.graph_file, "w") as f:
                json.dump([], f)

    def _read_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.graph_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_data(self, data: List[Dict[str, Any]]):
        with open(self.graph_file, "w") as f:
            json.dump(data, f, indent=2)

    async def add_triple(self, subject: str, predicate: str, object_val: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        data = self._read_data()
        
        triple = {
            "id": str(uuid.uuid4()),
            "subject": subject.lower(),
            "predicate": predicate.lower(),
            "object": object_val.lower(),
            "metadata": metadata or {}
        }
        
        data.append(triple)
        self._write_data(data)
        return True

    async def search_graph(self, query_entity: str, depth: int = 2) -> List[Dict[str, Any]]:
        # A simple naive BFS for offline graph search
        data = self._read_data()
        entity_lower = query_entity.lower()
        
        results = []
        visited = set()
        queue = [(entity_lower, 0)]
        
        while queue:
            current_entity, current_depth = queue.pop(0)
            if current_depth >= depth or current_entity in visited:
                continue
                
            visited.add(current_entity)
            
            for triple in data:
                if triple["subject"] == current_entity and triple["id"] not in [r["id"] for r in results]:
                    results.append(triple)
                    queue.append((triple["object"], current_depth + 1))
                elif triple["object"] == current_entity and triple["id"] not in [r["id"] for r in results]:
                    results.append(triple)
                    queue.append((triple["subject"], current_depth + 1))
                    
        return results
