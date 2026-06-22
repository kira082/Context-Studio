from typing import List, Dict, Any, Optional
from context_studio.providers.base import RelationalProvider

class ConversationalMemory:
    """
    Tier 1: Conversational Memory
    Stores turn-by-turn history. Implements sliding window summarization for long sessions.
    """
    def __init__(self, relational_provider: RelationalProvider, summarize_every_n_turns: int = 50):
        self.provider = relational_provider
        self.summarize_every_n_turns = summarize_every_n_turns
        
    async def add_turn(self, session_id: str, role: str, content: str, agent_id: str, tenant_id: str, metadata: Optional[Dict[str, Any]] = None):
        # We need to calculate turn_number. 
        # In a real DB, we could use an auto-increment or query max.
        # For simplicity, we just fetch history count.
        history = await self.provider.get_session_history(session_id, limit=1000)
        turn_number = len(history) + 1
        
        turn_data = {
            "agent_id": agent_id,
            "tenant_id": tenant_id,
            "role": role,
            "content": content,
            "turn_number": turn_number,
            "metadata": metadata or {}
        }
        
        await self.provider.save_turn(session_id, turn_data)
        
        # Check if we need to summarize
        if turn_number % self.summarize_every_n_turns == 0:
            await self._generate_sliding_summary(session_id, history[-self.summarize_every_n_turns:])
            
    async def get_recent_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        return await self.provider.get_session_history(session_id, limit=limit)
        
    async def _generate_sliding_summary(self, session_id: str, recent_turns: List[Dict[str, Any]]):
        """
        In a real scenario, this would call an LLM to summarize the block of turns.
        The summary would then be saved as a special 'system' turn or in a separate summary table.
        """
        # Placeholder for LLM call
        summary_text = "Rolling summary of the last 50 turns."
        
        # Save summary back to relational store as a special meta-turn
        summary_data = {
            "role": "system",
            "content": f"[SUMMARY] {summary_text}",
            "turn_number": -1, # Using negative to denote meta-turns, or handle via separate schema
            "metadata": {"type": "rolling_summary"}
        }
        await self.provider.save_turn(session_id, summary_data)
