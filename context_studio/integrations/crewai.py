from typing import Any

class ContextStudioCrewMemory:
    """
    Adapter for CrewAI to use Context Studio as a shared memory layer.
    """
    def __init__(self, cs_client: Any, tenant_id: str):
        self.cs_client = cs_client
        self.tenant_id = tenant_id

    async def save_agent_action(self, agent_id: str, session_id: str, action_details: str):
        """
        Saves an action performed by a CrewAI agent.
        """
        await self.cs_client.extract_and_store(
            session_id=session_id,
            agent_id=agent_id,
            tenant_id=self.tenant_id,
            content=action_details,
            role="assistant",
            outcome="action_executed"
        )

    async def query_memory(self, session_id: str, query: str) -> str:
        """
        Allows CrewAI agents to query the shared memory.
        """
        result = await self.cs_client.search(session_id, query)
        
        context_lines = []
        for item in result.get("results", []):
            content = item.get("content") or item.get("metadata", {}).get("summary") or str(item)
            context_lines.append(f"- {content}")
            
        return "\n".join(context_lines)
