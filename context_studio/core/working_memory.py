from typing import List, Dict, Any, Optional
from context_studio.providers.base import CacheProvider
import json

class WorkingMemory:
    """
    Tier 0: Working Memory
    Handles the ephemeral state (scratchpad, tool outputs) for a session.
    Implements a simplified MemGPT-style paging interrupt when the context window is exceeded.
    """
    def __init__(self, cache_provider: CacheProvider, max_tokens: int = 4000):
        self.cache = cache_provider
        self.max_tokens = max_tokens
        
    def _estimate_tokens(self, text: str) -> int:
        # A very naive token estimator for offline/dev mode
        return len(text) // 4
        
    async def get_state(self, session_id: str) -> Dict[str, Any]:
        state_str = await self.cache.get(f"wm_{session_id}")
        if state_str:
            return json.loads(state_str)
        return {"messages": [], "scratchpad": "", "token_count": 0}
        
    async def save_state(self, session_id: str, state: Dict[str, Any]):
        await self.cache.set(f"wm_{session_id}", json.dumps(state), ttl=3600*24) # 24 hour TTL

    async def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        state = await self.get_state(session_id)
        msg_tokens = self._estimate_tokens(content)
        
        # Check for paging interrupt (MemGPT style)
        if state["token_count"] + msg_tokens > self.max_tokens:
            state = await self._trigger_paging_interrupt(session_id, state)
            
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "tokens": msg_tokens
        }
        
        state["messages"].append(message)
        state["token_count"] += msg_tokens
        await self.save_state(session_id, state)
        
    async def _trigger_paging_interrupt(self, session_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        MemGPT Paging: Evict oldest messages (except system prompt) and summarize them.
        In a real implementation, this would call an LLM to summarize. 
        Here, we perform a deterministic eviction.
        """
        messages = state["messages"]
        if len(messages) <= 2:
            return state # Cannot page if too few messages
            
        # Keep first message (often system/context) and last few messages
        system_msgs = [m for m in messages if m["role"] == "system"]
        recent_msgs = messages[-3:]
        
        evicted = [m for m in messages if m not in system_msgs and m not in recent_msgs]
        
        # Dummy summarization
        summary_text = "Summarized older conversation. "
        summary_tokens = self._estimate_tokens(summary_text)
        
        new_messages = system_msgs + [
            {"role": "system", "content": f"SYSTEM ALERT: Context paged. Previous events summary: {summary_text}", "tokens": summary_tokens}
        ] + recent_msgs
        
        new_token_count = sum(m["tokens"] for m in new_messages)
        
        state["messages"] = new_messages
        state["token_count"] = new_token_count
        return state

    async def update_scratchpad(self, session_id: str, content: str):
        state = await self.get_state(session_id)
        state["scratchpad"] = content
        await self.save_state(session_id, state)
