from typing import Any

class ContextStudioADKPlugin:
    """
    Adapter for Google Agentic Development Kit (ADK) to use Context Studio.
    """
    def __init__(self, cs_client: Any):
        self.cs_client = cs_client

    async def get_state(self, session_id: str) -> dict:
        """
        Retrieves current memory state for the ADK agent.
        """
        return {
            "session_id": session_id,
            "memory": await self.cs_client.get_recent_history(session_id)
        }
