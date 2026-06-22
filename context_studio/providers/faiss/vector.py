import os
import json
import numpy as np
from typing import Dict, List, Any, Optional
from context_studio.providers.base import VectorProvider

# Optional FAISS import
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

class FAISSVectorProvider(VectorProvider):
    def __init__(self, dimension: int = 1536, base_dir: str = ".data/faiss"):
        if not HAS_FAISS:
            raise ImportError("faiss-cpu is not installed. Please install it to use FAISSVectorProvider.")
            
        self.dimension = dimension
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.index_path = os.path.join(self.base_dir, "index.faiss")
        self.meta_path = os.path.join(self.base_dir, "metadata.json")
        
        self.metadata_store = []
        
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r") as f:
                self.metadata_store = json.load(f)
        else:
            self.index = faiss.IndexFlatIP(self.dimension) # Inner product for cosine similarity (if normalized)

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w") as f:
            json.dump(self.metadata_store, f)

    async def insert_episode(self, episode_id: str, vector: List[float], metadata: Dict[str, Any]) -> bool:
        # Normalize for cosine similarity
        vec_np = np.array([vector], dtype=np.float32)
        faiss.normalize_L2(vec_np)
        
        self.index.add(vec_np)
        
        record = {
            "id": episode_id,
            "faiss_id": len(self.metadata_store),
            "metadata": metadata
        }
        self.metadata_store.append(record)
        self._save()
        return True

    async def search_episodes(self, query_vector: List[float], limit: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []
            
        vec_np = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(vec_np)
        
        # Search more than limit to account for post-filtering
        search_k = min(limit * 3, self.index.ntotal) if filter_dict else min(limit, self.index.ntotal)
        
        distances, indices = self.index.search(vec_np, search_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1:
                continue
                
            score = float(distances[0][i])
            meta_record = self.metadata_store[idx]
            
            if filter_dict:
                match = True
                meta_payload = meta_record.get("metadata", {})
                for k, v in filter_dict.items():
                    if meta_payload.get(k) != v:
                        match = False
                        break
                if not match:
                    continue
                    
            results.append({
                "id": meta_record["id"],
                "metadata": meta_record["metadata"],
                "score": score
            })
            
            if len(results) >= limit:
                break
                
        return results
