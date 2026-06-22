import os
import json
import time
from typing import Any, Optional
from context_studio.providers.base import CacheProvider

class FileSystemCacheProvider(CacheProvider):
    def __init__(self, base_dir: str = ".data/cache"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
    def _get_path(self, key: str) -> str:
        # Simple sanitization
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return os.path.join(self.base_dir, f"{safe_key}.json")

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        path = self._get_path(key)
        expires_at = time.time() + ttl if ttl else None
        data = {
            "value": value,
            "expires_at": expires_at
        }
        try:
            with open(path, "w") as f:
                json.dump(data, f)
            return True
        except Exception:
            return False

    async def get(self, key: str) -> Optional[Any]:
        path = self._get_path(key)
        if not os.path.exists(path):
            return None
            
        try:
            with open(path, "r") as f:
                data = json.load(f)
                
            expires_at = data.get("expires_at")
            if expires_at and time.time() > expires_at:
                os.remove(path)
                return None
                
            return data.get("value")
        except Exception:
            return None

    async def delete(self, key: str) -> bool:
        path = self._get_path(key)
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except Exception:
                return False
        return True
