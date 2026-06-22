import uuid
import time
import math
from typing import List, Dict, Any, Optional
from context_studio.providers.base import VectorProvider

class EpisodicMemory:
    """
    Tier 2: Episodic Memory
    Stores discrete events, interactions, and tool calls.
    Implements single-pass ADD-only extraction and Mem0-style time decay.
    """
    def __init__(self, vector_provider: VectorProvider, embedding_fn=None, half_life_days: float = 30.0):
        self.provider = vector_provider
        self.half_life_days = half_life_days
        self.embedding_fn = embedding_fn or self._dummy_embed
        
    def _dummy_embed(self, text: str) -> List[float]:
        # Dummy 1536-d embedding for offline/dev
        return [0.01] * 1536

    def _calculate_decay(self, created_at: float, importance: int) -> float:
        """Mem0 style decay: 0.5^(days / half_life * importance_mult)"""
        days_passed = (time.time() - created_at) / (3600 * 24)
        if days_passed <= 0:
            return 1.0
            
        # Importance multiplier: higher importance decays slower
        # e.g. importance 1 -> mult 0.5, importance 10 -> mult 2.0
        importance_mult = max(0.1, importance / 5.0) 
        
        decay_score = math.pow(0.5, days_passed / (self.half_life_days * importance_mult))
        return decay_score

    async def extract_and_store(self, session_id: str, agent_id: str, tenant_id: str, content: str, role: str, outcome: Optional[str] = None):
        """
        In production, this runs async and calls an LLM to extract a summary and importance score.
        Here we mock the extraction.
        """
        # Mock LLM Extraction
        episode_summary = f"[{role.upper()}] Interaction in session {session_id}"
        importance_score = 5 # default moderate importance
        
        episode_id = str(uuid.uuid4())
        created_at = time.time()
        
        metadata = {
            "agent_id": agent_id,
            "tenant_id": tenant_id,
            "session_id": session_id,
            "episode_type": "interaction",
            "summary": episode_summary,
            "outcome": outcome or "success",
            "importance_score": importance_score,
            "created_at": created_at,
            "decay_score": 1.0,
            "access_count": 0
        }
        
        vector = self.embedding_fn(episode_summary)
        await self.provider.insert_episode(episode_id, vector, metadata)
        
    async def search_episodes(self, query: str, limit: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query_vector = self.embedding_fn(query)
        results = await self.provider.search_episodes(query_vector, limit=limit*2, filter_dict=filter_dict)
        
        # Apply Mem0 time decay reranking
        for res in results:
            created_at = res["metadata"].get("created_at", time.time())
            importance = res["metadata"].get("importance_score", 5)
            decay = self._calculate_decay(created_at, importance)
            
            # Combine cosine similarity with decay score
            res["final_score"] = res["score"] * decay
            res["metadata"]["decay_score"] = decay
            
            # Update access count in a real implementation
            
        results.sort(key=lambda x: x["final_score"], reverse=True)
        return results[:limit]
