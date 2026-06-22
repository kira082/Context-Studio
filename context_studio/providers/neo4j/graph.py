from typing import Dict, List, Any, Optional
from context_studio.providers.base import GraphProvider

class Neo4jGraphProvider(GraphProvider):
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        
    async def add_triple(self, subject: str, predicate: str, object_val: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        raise NotImplementedError("Neo4jGraphProvider stub")

    async def search_graph(self, query_entity: str, depth: int = 2) -> List[Dict[str, Any]]:
        raise NotImplementedError("Neo4jGraphProvider stub")
