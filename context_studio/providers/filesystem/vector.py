import os
import json
import math
from typing import Dict, List, Any, Optional
from context_studio.providers.base import VectorProvider

class FileSystemVectorProvider(VectorProvider):
    """
    A naive offline vector provider using purely Python lists and math.
    Not suitable for production, intended only for dev/offline mode.
    """
    def __init__(self, base_dir: str = ".data/vector"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.store_file = os.path.join(self.base_dir, "episodes.json")
        if not os.path.exists(self.store_file):
            with open(self.store_file, "w") as f:
                json.dump([], f)

    def _read_data(self) -> List[Dict[str, Any]]:
        try:
            with open(self.store_file, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_data(self, data: List[Dict[str, Any]]):
        with open(self.store_file, "w") as f:
            json.dump(data, f, indent=2)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if len(vec1) != len(vec2) or len(vec1) == 0:
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)

    async def insert_episode(self, episode_id: str, vector: List[float], metadata: Dict[str, Any]) -> bool:
        data = self._read_data()
        
        record = {
            "id": episode_id,
            "vector": vector,
            "metadata": metadata
        }
        
        # Check if exists and update, or append
        existing_idx = next((i for i, item in enumerate(data) if item["id"] == episode_id), None)
        if existing_idx is not None:
            data[existing_idx] = record
        else:
            data.append(record)
            
        self._write_data(data)
        return True

    async def search_episodes(self, query_vector: List[float], limit: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        data = self._read_data()
        results = []
        
        for item in data:
            # Apply basic filtering if provided
            if filter_dict:
                meta = item.get("metadata", {})
                match = True
                for k, v in filter_dict.items():
                    if meta.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
                    
            similarity = self._cosine_similarity(query_vector, item["vector"])
            results.append({
                "id": item["id"],
                "metadata": item["metadata"],
                "score": similarity
            })
            
        # Sort by similarity descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
