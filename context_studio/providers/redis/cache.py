from typing import Any, Optional
from context_studio.providers.base import CacheProvider

class RedisCacheProvider(CacheProvider):
    def __init__(self, url: str):
        self.url = url
        # import redis
        # self.client = redis.Redis.from_url(url)
        
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        raise NotImplementedError("RedisCacheProvider stub")

    async def get(self, key: str) -> Optional[Any]:
        raise NotImplementedError("RedisCacheProvider stub")

    async def delete(self, key: str) -> bool:
        raise NotImplementedError("RedisCacheProvider stub")
