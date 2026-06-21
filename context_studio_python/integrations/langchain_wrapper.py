from typing import Any, Dict, List
import json

try:
    from langchain.schema import BaseMemory, BaseMessage, HumanMessage, AIMessage
except ImportError:
    # Fallback/mock if langchain is not installed locally
    class BaseMemory:
        pass
    class BaseMessage:
        pass
    class HumanMessage(BaseMessage):
        pass
    class AIMessage(BaseMessage):
        pass

class ContextStudioMemory(BaseMemory):
    """
    A LangChain memory wrapper that uses Context Studio as the backend.
    This injects the full 5-tier memory context directly into the LLM prompt.
    """
    agent_id: str
    session_id: str
    memory_engine: Any  # The ContextStudio MemoryEngine instance
    memory_key: str = "context_studio_history"

    def __init__(self, agent_id: str, session_id: str, memory_engine: Any, memory_key: str = "context_studio_history"):
        super().__init__()
        self.agent_id = agent_id
        self.session_id = session_id
        self.memory_engine = memory_engine
        self.memory_key = memory_key

    @property
    def memory_variables(self) -> List[str]:
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intercepts the prompt before it hits the LLM. 
        We use the current user input to query Context Studio and fetch the 5-tier context.
        """
        # Attempt to find the user's latest query in the inputs
        query = ""
        if inputs:
            query = list(inputs.values())[-1]

        # Fetch multi-tier context
        context_data = self.memory_engine.get_context(self.agent_id, self.session_id, query)
        
        # Format the context into a string block for the LLM
        formatted_context = "=== CONTEXT STUDIO MEMORY ===\n"
        
        if context_data.get("procedural"):
            formatted_context += "[RULES/INSTRUCTIONS]\n" + "\n".join(context_data["procedural"]) + "\n\n"
            
        if context_data.get("semanticGraph"):
            formatted_context += "[KNOWN FACTS]\n" + "\n".join(context_data["semanticGraph"]) + "\n\n"
            
        if context_data.get("episodic"):
            episodes = [ep["summary"] for ep in context_data["episodic"]]
            formatted_context += "[PAST EPISODES]\n" + "\n".join(episodes) + "\n\n"
            
        if context_data.get("conversational"):
            formatted_context += "[RECENT CONVERSATION]\n"
            for t in context_data["conversational"][-3:]: # only show last 3 strictly
                formatted_context += f"{t['role'].capitalize()}: {t['content']}\n"
                
        return {self.memory_key: formatted_context}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        After the LLM responds, we intercept the input and output to write back to Context Studio.
        """
        user_input = list(inputs.values())[-1]
        ai_output = list(outputs.values())[-1]
        
        # Get current turn number from working memory length
        wm_key = f"wm:{self.agent_id}:{self.session_id}"
        from memory_sdk import working_memory_cache
        current_len = len(working_memory_cache.get(wm_key, []))
        
        # Write User turn
        self.memory_engine.write_back(
            agent_id=self.agent_id,
            session_id=self.session_id,
            role="user",
            content=user_input,
            turn_number=current_len + 1
        )
        
        # Write AI turn
        self.memory_engine.write_back(
            agent_id=self.agent_id,
            session_id=self.session_id,
            role="assistant",
            content=ai_output,
            turn_number=current_len + 2
        )

    def clear(self) -> None:
        # We don't clear Context Studio memory! It is persistent.
        pass
