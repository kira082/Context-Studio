from typing import List, Dict, Any
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

class ContextStudioChatHistory(BaseChatMessageHistory):
    """
    Adapter for LangChain / LangGraph to use Context Studio as Chat History.
    """
    def __init__(self, cs_client: Any, session_id: str, tenant_id: str, agent_id: str):
        self.cs_client = cs_client
        self.session_id = session_id
        self.tenant_id = tenant_id
        self.agent_id = agent_id

    @property
    def messages(self) -> List[BaseMessage]:
        # Synchronous mock wrapper for async calls
        # In production, use async LangChain history if needed
        import asyncio
        loop = asyncio.get_event_loop()
        history = loop.run_until_complete(
            self.cs_client.get_recent_history(self.session_id)
        )
        
        lc_messages = []
        for msg in history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
            elif role == "system":
                lc_messages.append(SystemMessage(content=content))
        return lc_messages

    def add_message(self, message: BaseMessage) -> None:
        import asyncio
        loop = asyncio.get_event_loop()
        
        role = "user"
        if isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, SystemMessage):
            role = "system"
            
        loop.run_until_complete(
            self.cs_client.add_turn(
                session_id=self.session_id,
                role=role,
                content=message.content,
                agent_id=self.agent_id,
                tenant_id=self.tenant_id
            )
        )

    def clear(self) -> None:
        pass
