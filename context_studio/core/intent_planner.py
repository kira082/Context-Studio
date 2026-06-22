import json
from typing import Dict, Any, Optional
from context_studio.core.config import MemoryConfig
from context_studio.llm.provider import LLMProvider

class IntentPlanner:
    """
    SimpleMem-style Intent-Aware Retrieval Planner.
    Analyzes the query complexity to determine which search paths and depths to activate,
    saving computational budget for simple queries.
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

    async def plan_retrieval(self, query: str) -> Dict[str, Any]:
        """
        Evaluates the intent of the query using the configured LLM or fallback heuristics.
        """
        if self.llm:
            sys_prompt = "You are a retrieval planner. Analyze the query complexity. Return JSON with boolean fields 'use_dense', 'use_sparse', 'use_graph', 'needs_reranking', an integer 'graph_depth' (1-3), and 'budget_tokens'."
            try:
                plan = await self.llm.generate_json(sys_prompt, query)
                if plan:
                    return plan
            except Exception as e:
                print(f"LLM Planner failed, falling back to heuristics. Error: {e}")

        # Fallback heuristic logic
        query_lower = query.lower()
        plan = {
            "use_dense": True,
            "use_sparse": True,
            "use_graph": False,
            "graph_depth": 1,
            "needs_reranking": False,
            "budget_tokens": 2000
        }

        complex_keywords = ["why", "how", "explain", "analyze", "compare", "history"]
        if any(kw in query_lower for kw in complex_keywords) or len(query.split()) > 10:
            plan["use_graph"] = True
            plan["graph_depth"] = 2
            plan["needs_reranking"] = True
            plan["budget_tokens"] = 4000
            
        return plan
