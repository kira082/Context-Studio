from typing import Dict, Any

class IntentPlanner:
    """
    SimpleMem-style Intent-Aware Retrieval Planner.
    Analyzes the query complexity to determine which search paths and depths to activate,
    saving computational budget for simple queries.
    """
    def __init__(self):
        pass

    def plan_retrieval(self, query: str) -> Dict[str, Any]:
        """
        Mock implementation. In production, an LLM or small classifier evaluates
        the intent of the query.
        """
        query_lower = query.lower()
        plan = {
            "use_dense": True,
            "use_sparse": True,
            "use_graph": False,
            "graph_depth": 1,
            "needs_reranking": False,
            "budget_tokens": 2000
        }

        # Simple heuristic for dev mode
        complex_keywords = ["why", "how", "explain", "analyze", "compare", "history"]
        if any(kw in query_lower for kw in complex_keywords) or len(query.split()) > 10:
            plan["use_graph"] = True
            plan["graph_depth"] = 2
            plan["needs_reranking"] = True
            plan["budget_tokens"] = 4000
            
        return plan
