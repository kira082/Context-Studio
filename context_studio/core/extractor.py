import json
from typing import Dict, Any, List, Optional
from context_studio.core.config import MemoryConfig
from context_studio.llm.provider import LLMProvider

class MemoryExtractor:
    """
    Handles extracting structured data (episodes, facts, rules) from unstructured dialogue
    using the configured LLM provider.
    """
    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self.llm = None
        if self.config.llm.enabled:
            self.llm = LLMProvider(
                model_name=self.config.llm.model_name,
                api_base=self.config.llm.api_base,
                api_key=self.config.llm.api_key
            )

    async def extract_episode(self, turn_content: str) -> Optional[Dict[str, Any]]:
        """
        Extracts an episodic memory (experience/decision) from a conversational turn.
        Returns JSON with summary, outcome, importance_score (1-10).
        """
        if not self.llm:
            return None
            
        sys_prompt = """
        You are an episodic memory extractor. Analyze the interaction and extract the core experience.
        Return a JSON object with:
        - summary: A concise 1-sentence summary of what happened.
        - outcome: 'success', 'failure', 'partial', or 'informational'.
        - importance_score: An integer from 1 to 10 (10 being critical, 1 being trivial).
        """
        try:
            return await self.llm.generate_json(sys_prompt, turn_content)
        except Exception as e:
            print(f"Failed to extract episode: {e}")
            return None

    async def extract_triples(self, text: str, existing_entities: List[str] = None) -> List[Dict[str, Any]]:
        """
        Mem0 / HippoRAG style Knowledge Graph triple extraction.
        """
        if not self.llm:
            return []
            
        existing_str = ", ".join(existing_entities) if existing_entities else "None"
        sys_prompt = f"""
        Extract structured knowledge triples from the following text.
        Return ONLY a JSON array of objects with keys: 'subject', 'predicate', 'object', 'confidence' (0.0-1.0).
        Rules:
        1. subject and object must be specific ENTITIES.
        2. predicate must be a clear relationship verb (e.g. 'works_at', 'prefers').
        3. Resolve pronouns to actual entity names.
        
        Known entities in this tenant's graph: {existing_str}
        """
        try:
            response = await self.llm.generate_json(sys_prompt, text)
            # The LLM might return {"triples": [...]} or just [...]
            if isinstance(response, dict):
                return response.get("triples", list(response.values())[0] if response else [])
            elif isinstance(response, list):
                return response
            return []
        except Exception as e:
            print(f"Failed to extract triples: {e}")
            return []
