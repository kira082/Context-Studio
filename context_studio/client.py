from typing import Any, Dict, Optional
import httpx

class ContextStudioClient:
    """
    Universal Python SDK Client for interacting with the Context Studio REST API.
    """
    def __init__(self, api_url: str = "http://localhost:8000/v1", api_key: Optional[str] = None, tenant_id: str = "default", agent_id: str = "default"):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.tenant_id = tenant_id
        self.agent_id = agent_id
        self.client = httpx.AsyncClient(headers={
            "X-Tenant-ID": self.tenant_id,
            "X-Agent-ID": self.agent_id,
            **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {})
        })

    async def log_tool_execution(self, session_id: str, tool_name: str, tool_args: Dict[str, Any], outcome: str, result_text: str):
        """
        Reports a sandbox/tool execution result to Context Studio memory.
        """
        payload = {
            "session_id": session_id,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "outcome": outcome,
            "result_text": result_text
        }
        response = await self.client.post(f"{self.api_url}/tools/log_execution", json=payload)
        response.raise_for_status()
        return response.json()

    async def trigger_skill_learning(self):
        """
        Triggers the background worker to scan for repetitive tool chains to create skills.
        """
        response = await self.client.post(f"{self.api_url}/skills/learn", json={})
        response.raise_for_status()
        return response.json()
        
    async def close(self):
        await self.client.aclose()
