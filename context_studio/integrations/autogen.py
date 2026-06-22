from typing import List, Dict, Any, Optional

class ContextStudioMemoryPlugin:
    """
    Adapter for Microsoft AutoGen to use Context Studio.
    Provides memory retrieval and storage for ConversableAgents.
    """
    def __init__(self, cs_client: Any):
        self.cs_client = cs_client

    async def get_context(self, session_id: str, query: str) -> str:
        """
        Retrieves context to inject into AutoGen agent prompt.
        """
        result = await self.cs_client.search(session_id, query)
        
        # Format the context
        context_lines = []
        for item in result.get("results", []):
            content = item.get("content") or item.get("metadata", {}).get("summary") or str(item)
            context_lines.append(f"- {content}")
            
        return "\n".join(context_lines)

    async def save_interaction(self, session_id: str, role: str, content: str, agent_id: str, tenant_id: str):
        """
        Saves a conversational turn from AutoGen.
        """
        await self.cs_client.add_turn(
            session_id=session_id,
            role=role,
            content=content,
            agent_id=agent_id,
            tenant_id=tenant_id
        )
