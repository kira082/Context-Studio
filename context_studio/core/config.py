from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class RetrievalConfig:
    hybrid_search: bool = True
    enable_graph_traversal: bool = False
    rrf_fusion: bool = True
    rrf_algorithm: str = "standard"  # "standard" or "weighted"
    cross_encoder_reranking: bool = False
    top_k: int = 5
    dense_weight: float = 0.5
    sparse_weight: float = 0.3
    graph_weight: float = 0.2

@dataclass
class StorageConfig:
    cache_provider: str = "filesystem"      # "filesystem", "redis", etc.
    relational_provider: str = "filesystem" # "filesystem", "sqlite", "postgres", etc.
    vector_provider: str = "filesystem"     # "filesystem", "faiss", "qdrant", etc.
    graph_provider: str = "filesystem"      # "filesystem", "neo4j", etc.
    cache_options: Dict[str, Any] = field(default_factory=dict)
    relational_options: Dict[str, Any] = field(default_factory=dict)
    vector_options: Dict[str, Any] = field(default_factory=dict)
    graph_options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StrategyConfig:
    extraction_strategy: str = "mem0"       # "mem0", "simplemem", etc.
    summarization_window: int = 50          # Number of turns before rolling summary
    max_working_memory_tokens: int = 4000
    enable_auto_paging: bool = True         # MemGPT style paging

@dataclass
class GovernanceConfig:
    enable_contradiction_resolution: bool = True
    enable_garbage_collection: bool = False
    time_decay_half_life_days: float = 30.0
    gc_importance_threshold: int = 3
    enable_data_lineage: bool = True

@dataclass
class MemoryConfig:
    storage: StorageConfig = field(default_factory=StorageConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
