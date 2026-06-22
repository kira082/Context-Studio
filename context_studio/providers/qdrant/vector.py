from typing import Dict, List, Any, Optional
from context_studio.providers.base import VectorProvider

class QdrantVectorProvider(VectorProvider):
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        
    async def insert_episode(self, episode_id: str, vector: List[float], metadata: Dict[str, Any]) -> bool:
        raise NotImplementedError("QdrantVectorProvider stub")

    async def search_episodes(self, query_vector: List[float], limit: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        raise NotImplementedError("QdrantVectorProvider stub")
