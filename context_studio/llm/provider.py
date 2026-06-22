import json
import litellm
from typing import Dict, Any, Optional
from pydantic import BaseModel

class LLMProvider:
    """
    Universal LLM adapter using LiteLLM.
    Supports OpenAI, Anthropic, Gemini, Ollama, HuggingFace, and 100+ others.
    """
    def __init__(self, model_name: str, api_base: Optional[str] = None, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_base = api_base
        self.api_key = api_key

    async def generate_completion(self, system_prompt: str, user_prompt: str, response_format: Optional[type[BaseModel]] = None) -> str:
        """
        Generate a text response.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": self.model_name,
            "messages": messages
        }
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key
            
        if response_format:
            # Pydantic structured output using LiteLLM
            kwargs["response_format"] = response_format
            
        response = await litellm.acompletion(**kwargs)
        return response.choices[0].message.content

    async def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generates a JSON response.
        """
        messages = [
            {"role": "system", "content": system_prompt + "\n\nReturn ONLY valid JSON."},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "response_format": {"type": "json_object"}
        }
        if self.api_base:
            kwargs["api_base"] = self.api_base
        if self.api_key:
            kwargs["api_key"] = self.api_key
            
        response = await litellm.acompletion(**kwargs)
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {}
