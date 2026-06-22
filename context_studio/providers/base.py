from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class CacheProvider(ABC):
    """Tier 0: Working Memory Cache Provider"""
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass
        
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
        
    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

class RelationalProvider(ABC):
    """Tier 1, 4, 5, 6: Relational Provider for Conversations, Rules, Prefs"""
    
    @abstractmethod
    async def save_turn(self, session_id: str, turn_data: Dict[str, Any]) -> str:
        pass
        
    @abstractmethod
    async def get_session_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        pass
        
    @abstractmethod
    async def search_relational(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        pass

class VectorProvider(ABC):
    """Tier 2: Episodic Memory Provider (Dense Vectors)"""
    
    @abstractmethod
    async def insert_episode(self, episode_id: str, vector: List[float], metadata: Dict[str, Any]) -> bool:
        pass
        
    @abstractmethod
    async def search_episodes(self, query_vector: List[float], limit: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass

class GraphProvider(ABC):
    """Tier 3: Semantic Knowledge Graph Provider"""
    
    @abstractmethod
    async def add_triple(self, subject: str, predicate: str, object_val: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        pass
        
    @abstractmethod
    async def search_graph(self, query_entity: str, depth: int = 2) -> List[Dict[str, Any]]:
        pass
