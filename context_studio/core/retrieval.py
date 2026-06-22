from typing import List, Dict, Any, Optional
from context_studio.core.config import RetrievalConfig
from context_studio.providers.base import VectorProvider, RelationalProvider, GraphProvider
from context_studio.core.intent_planner import IntentPlanner

class RetrievalEngine:
    """
    Coordinates Hybrid Search (Dense + Sparse + Graph),
    Reciprocal Rank Fusion (RRF), Cross-Encoder Re-Ranking,
    and Context Budget Optimization.
    """
    def __init__(self, 
                 config: RetrievalConfig, 
                 vector_provider: VectorProvider,
                 relational_provider: RelationalProvider,
                 graph_provider: GraphProvider,
                 embedding_fn=None):
        self.config = config
        self.vector_provider = vector_provider
        self.relational_provider = relational_provider
        self.graph_provider = graph_provider
        self.intent_planner = IntentPlanner()
        self.embedding_fn = embedding_fn or (lambda x: [0.01]*1536)

    async def search(self, session_id: str, query: str) -> Dict[str, Any]:
        plan = self.intent_planner.plan_retrieval(query)
        
        dense_results = []
        sparse_results = []
        graph_results = []
        
        # 1. Hybrid Retrieval Phase
        if plan["use_dense"]:
            query_vector = self.embedding_fn(query)
            dense_results = await self.vector_provider.search_episodes(query_vector, limit=self.config.top_k)
            
        if plan["use_sparse"]:
            sparse_results = await self.relational_provider.search_relational(query, limit=self.config.top_k)
            
        if self.config.enable_graph_traversal and plan["use_graph"]:
            # Basic entity extraction mock for HippoRAG
            entity = query.split()[0] if query else "unknown"
            graph_results = await self.graph_provider.search_graph(entity, depth=plan["graph_depth"])
            
        # 2. Reciprocal Rank Fusion (RRF)
        fused_results = self._reciprocal_rank_fusion(dense_results, sparse_results, graph_results)
        
        # 3. Cross-Encoder Re-Ranking
        if self.config.cross_encoder_reranking and plan["needs_reranking"]:
            fused_results = self._cross_encoder_rerank(query, fused_results)
            
        # 4. Context Budget Optimizer
        final_context = self._optimize_budget(fused_results, plan["budget_tokens"])
        
        return {
            "results": final_context,
            "plan": plan,
            "metrics": {
                "dense_count": len(dense_results),
                "sparse_count": len(sparse_results),
                "graph_count": len(graph_results),
                "total_fused": len(fused_results)
            }
        }

    def _reciprocal_rank_fusion(self, dense: List[Dict], sparse: List[Dict], graph: List[Dict], k: int = 60) -> List[Dict]:
        """
        RRF algorithm implementation: score = 1 / (k + rank)
        Optionally supports weighted RRF based on config.
        """
        scores = {}
        
        def add_ranks(results, weight):
            for rank, item in enumerate(results):
                # Standardize ID extraction
                item_id = item.get("id", str(hash(str(item))))
                
                if item_id not in scores:
                    scores[item_id] = {"score": 0.0, "item": item}
                
                if self.config.rrf_algorithm == "weighted":
                    scores[item_id]["score"] += weight * (1.0 / (k + rank + 1))
                else:
                    scores[item_id]["score"] += 1.0 / (k + rank + 1)
                    
        add_ranks(dense, self.config.dense_weight)
        add_ranks(sparse, self.config.sparse_weight)
        add_ranks(graph, self.config.graph_weight)
        
        ranked_list = list(scores.values())
        ranked_list.sort(key=lambda x: x["score"], reverse=True)
        
        return [r["item"] for r in ranked_list][:self.config.top_k]

    def _cross_encoder_rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        Mock Cross-Encoder. In production, uses a model like BAAI/bge-reranker-large
        to score query-document pairs.
        """
        # Dev mode: Identity function
        return results

    def _optimize_budget(self, results: List[Dict], max_tokens: int) -> List[Dict]:
        """
        MemGPT style Context Budget Optimizer.
        Ensures the final retrieved context fits strictly within the allowed budget.
        """
        optimized = []
        current_tokens = 0
        
        for item in results:
            content = item.get("metadata", {}).get("summary") or item.get("content") or str(item)
            # Naive token estimation
            tokens = len(content) // 4
            
            if current_tokens + tokens > max_tokens:
                break
                
            optimized.append(item)
            current_tokens += tokens
            
        return optimized
