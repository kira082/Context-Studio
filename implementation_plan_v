# Context Studio — Implementation Plan 

**Date:** 2026-06-21



## Table of Contents

1. [Executive Summary & Research Foundations](#1-executive-summary--research-foundations)
2. [System Architecture](#2-system-architecture)
3. [Memory Layer Design (7-Tier Cognitive Architecture)](#3-memory-layer-design-7-tier-cognitive-architecture)
4. [Knowledge Graph Construction Pipeline](#4-knowledge-graph-construction-pipeline)
5. [Advanced Retrieval Pipeline — Hybrid + RRF + Re-Rank](#5-advanced-retrieval-pipeline--hybrid--rrf--re-rank)
6. [Configurable Feature Toggle System](#6-configurable-feature-toggle-system)
7. [Pluggable Storage Abstraction Layer](#7-pluggable-storage-abstraction-layer)
8. [Multi-Agent & Tool Calling Logic](#8-multi-agent--tool-calling-logic)
9. [Security — Multi-Tenant RBAC (PyCasbin)](#9-security--multi-tenant-rbac-pycasbin)
10. [Governance — Contradiction, Decay & GC](#10-governance--contradiction-decay--gc)
11. [Evaluation Framework](#11-evaluation-framework)
12. [Integration Layer (API, SDK, MCP)](#12-integration-layer-api-sdk-mcp)
13. [Boundary Cases & Edge Cases — All Handled](#13-boundary-cases--edge-cases--all-handled)
14. [Database Schemas](#14-database-schemas)
15. [Algorithm Index — Paper-to-Feature Mapping](#15-algorithm-index--paper-to-feature-mapping)

---

## 1. Executive Summary & Research Foundations

Context Studio is a **Cognitive Operating System for AI Agents** — a pluggable, configurable memory engine that implements a 7-tier cognitive architecture, an advanced hybrid retrieval pipeline with RRF and cross-encoder re-ranking, a dynamic knowledge graph builder, and comprehensive governance.

It integrates discoveries from the following research papers:

| Paper | Core Contribution Used |
|:---|:---|
| **Mem0** (Chheda et al., 2024) | Multi-signal retrieval fusion, single-pass ADD extraction, semantic supersession for contradiction resolution, entity graph building |
| **MemGPT** (Packer et al., UC Berkeley, 2023) | OS-inspired 3-tier context hierarchy (In-Context / External / Archival), paging mechanism, interrupt-based context swapping, agent self-reflection |
| **SimpleMem** (aiming-lab, 2026) | 3-stage semantic lossless compression pipeline: Structured Compression → Online Synthesis → Intent-Aware Retrieval Planning; entropy-based filtering, 30x token reduction |
| **HippoRAG** (Gutiérrez et al., NeurIPS 2024) | Hippocampal indexing theory applied to KG retrieval; Personalized PageRank (PPR) for associative multi-hop graph traversal |
| **GraphRAG** (Microsoft, 2024) | Community detection (Leiden algorithm) on knowledge graphs; hierarchical community summaries for global queries |
| **RRF** (Cormack & Clarke, 2009) | Standard and Weighted RRF formulas for score-agnostic multi-list rank fusion |

---

## 2. System Architecture

### 2.1 High-Level Architecture

```mermaid
graph TB
    subgraph Integrations["Integration Layer (Pluggable)"]
        API["REST API<br/>(FastAPI — No-Code / N8N)"]
        SDK["Native Python SDK<br/>(LangChain / LangGraph / AutoGen / CrewAI / ADK)"]
        MCP["MCP Server<br/>(Claude / Cursor / Pi / any MCP client)"]
    end

    subgraph Core["Context Studio Core Engine"]
        RBAC["RBAC & Auth Layer<br/>(PyCasbin)"]
        ORCH["Memory Orchestrator<br/>(MemoryConfig-driven)"]
        
        subgraph Write["Write Pipeline (Async)"]
            COMP["SimpleMem: Semantic Structured Compression"]
            SYNTH["SimpleMem: Online Semantic Synthesis"]
            EXT["Mem0: Entity + Triple Extractor"]
            CONTR["Contradiction Resolution Engine<br/>(Semantic Supersession)"]
        end
        
        subgraph Read["Read Pipeline"]
            INTPLAN["SimpleMem: Intent-Aware Retrieval Planning"]
            HYB["Hybrid Search<br/>(Dense + Sparse + Graph)"]
            RRF["RRF Fusion<br/>(Standard / Weighted)"]
            RERANK["Cross-Encoder Re-Ranker<br/>(bge-reranker / Cohere)"]
            BUDGET["MemGPT: Context Budget Optimizer"]
        end
    end

    subgraph Storage["Pluggable Storage (Bring Your Own)"]
        CACHE["CacheProvider<br/>Redis / Memcached / Local"]
        REL["RelationalProvider<br/>PostgreSQL / SQLite / File"]
        VEC["VectorProvider<br/>Qdrant / Pinecone / Milvus / Chroma / FAISS / File"]
        GRAPH["GraphProvider<br/>Neo4j / PostgreSQL AGE / NetworkX / File"]
    end

    Integrations --> RBAC
    RBAC --> ORCH
    ORCH --> Write
    ORCH --> Read
    Write --> Storage
    Read --> Storage
```

### 2.2 Async Write-Back Data Flow

```mermaid
sequenceDiagram
    participant Agent
    participant Core as Context Studio Core
    participant Cache as CacheProvider
    participant Vector as VectorProvider
    participant Graph as GraphProvider
    participant Worker as Async Worker

    Agent->>Core: query(session_id, query_text)
    Core->>Core: RBAC check
    Core->>Core: Intent-Aware Retrieval Planning (SimpleMem)
    par Parallel Hybrid Read
        Core->>Vector: Dense search
        Core->>Graph: 2-hop PPR traversal (HippoRAG)
        Core->>Cache: BM25 sparse lookup
    end
    Core->>Core: RRF Fusion + Cross-Encoder Rerank
    Core->>Core: Context Budget Optimizer (MemGPT)
    Core-->>Agent: Synthesized context window

    Agent->>Agent: Execute turn (+ Tool calls)

    Agent->>Core: save(interaction_log)
    Core->>Cache: Sync update Working Memory (TTL)
    Core-->>Agent: 200 OK (immediate)

    Core-)Worker: Fire async extraction task
    Worker->>Worker: Semantic Structured Compression (SimpleMem)
    Worker->>Worker: Online Semantic Synthesis (SimpleMem)
    Worker->>Worker: Entity + Triple extraction (Mem0/HippoRAG)
    Worker->>Worker: Contradiction Resolution (Mem0 supersession)
    Worker->>Vector: Upsert episode vector
    Worker->>Graph: Upsert knowledge triples
```

---

## 3. Memory Layer Design (7-Tier Cognitive Architecture)

### 3.1 Tier 0 — Working Memory (MemGPT: Main Context / "RAM")

> Inspired by: **MemGPT** (Main Context), **Mem0** (session state)

**Purpose:** The agent's active RAM — current session state, scratchpad, active tool outputs, token budget tracking.

| Attribute | Value |
|:---|:---|
| **Provider** | `CacheProvider` (Redis / Local Memory / File) |
| **Key Pattern** | `wm:{tenant_id}:{agent_id}:{session_id}` |
| **TTL** | Session duration + 30 min grace period |
| **Max Size** | Configurable token budget per LLM (auto-detected from model name) |
| **Overflow Strategy** | MemGPT Paging: evict oldest turns to Conversational Memory; trigger summarization interrupt |
| **Multi-Agent** | Shared `wm:{tenant_id}:shared:{workflow_id}` hash for collaborative swarms |

**Paging Algorithm (from MemGPT):**
When `token_budget_used > 90%`:
1. LLM issues a `page_out(session_id, turn_range)` function call.
2. Oldest N turns are compressed and written to Conversational Memory (Relational).
3. Main context is updated with the summary.
4. LLM issues `context_resume()` to continue.

---

### 3.2 Tier 1 — Conversational Memory (Dialogue Thread)

> Inspired by: **Mem0** (turn-by-turn history), **MemGPT** (external context)

**Purpose:** Persistent raw dialogue turns across sessions.

| Attribute | Value |
|:---|:---|
| **Provider** | `RelationalProvider` |
| **Retention** | Configurable: last N turns (default 100) or last T days (default 90) |
| **Overflow** | Sliding window: LLM-summarize oldest 50 turns into `conversation_summaries` |
| **Cross-Session** | Load previous session summary + last 5 turns when resuming |
| **Deduplication** | Drop consecutive identical `user` turns |

**Boundary Cases:**
- Empty turn (blank user input) → Rejected at API validation
- Turn reconnect after crash → Resume via `session_id` within grace period TTL
- Multi-user group chats → Each turn tagged with `user_id`; filter by user or include all

---

### 3.3 Tier 2 — Episodic Memory (Experience Log)

> Inspired by: **Mem0** (episodic extraction, importance scoring, decay), **MemGPT** (archival storage)

**Purpose:** Persistent records of agent experiences, decisions, outcomes, and tool call results.

| Attribute | Value |
|:---|:---|
| **Provider** | `VectorProvider` |
| **Embedding** | Configurable (default: `text-embedding-3-small`, 1536 dims) |
| **Extraction** | Async LLM worker: extracts episode, importance score (1–10), outcome type |
| **Time-Decay** | Exponential decay with access-reinforcement (Mem0 algorithm) |
| **Deduplication** | Cosine similarity > 0.95 → merge instead of create new |

**Mem0 Time-Decay Algorithm:**
```python
def calculate_decay(episode, current_time, half_life_days=30):
    days_since_access = (current_time - episode.last_accessed_at).days
    importance_multiplier = 1 + (episode.importance_score / 10)  # 1.1 to 2.0
    effective_half_life = half_life_days * importance_multiplier
    decay = 0.5 ** (days_since_access / effective_half_life)
    return max(decay, 0.01)  # Never fully forget
```

**Composite Retrieval Score (Mem0):**
```
Score(e) = α·semantic_sim + β·recency_score + γ·importance_score + δ·decay_score
Default weights: α=0.40, β=0.20, γ=0.25, δ=0.15
(All weights configurable per agent in MemoryConfig)
```

---

### 3.4 Tier 3 — Semantic Memory (Knowledge Graph / Facts)

> Inspired by: **Mem0** (entity linking), **HippoRAG** (hippocampal indexing, PPR), **GraphRAG** (community detection)

**Purpose:** Structured facts and entity relationship graph shared across agents in a tenant.

| Attribute | Value |
|:---|:---|
| **Provider** | `GraphProvider` (Neo4j / PostgreSQL AGE / NetworkX / File) |
| **Fact Format** | RDF-style triples: `(Subject) --[Predicate]--> (Object)` |
| **Entity Resolution** | LLM-assisted deduplication: "John Smith" == "J. Smith" |
| **Conflict** | Semantic supersession (Mem0): new fact `supersedes` old when confidence + recency higher |
| **Graph Traversal** | HippoRAG: Personalized PageRank (PPR) for multi-hop associative retrieval |
| **Community** | GraphRAG: Leiden community detection for tenant-wide global query summarization |

**HippoRAG Retrieval (Personalized PageRank):**
1. Extract named entities from query.
2. Map query entities to KG nodes (seed nodes).
3. Run Personalized PageRank from seed nodes over the full KG.
4. Return top-K nodes by PPR score — these are the contextually connected facts.

---

### 3.5 Tier 4 — Procedural Memory (Rules & Workflows)

> Inspired by: **MemGPT** (agent behavioral instructions), **Mem0** (system prompt injection)

**Purpose:** Behavioral guardrails, workflow triggers, tool-use patterns.

| Attribute | Value |
|:---|:---|
| **Provider** | `RelationalProvider` |
| **Rule Types** | `workflow`, `constraint`, `escalation`, `tool_pattern`, `injection` |
| **Trigger** | Intent match (semantic sim > threshold) OR always-on |
| **Priority** | Manual rules > Learned rules; higher numeric priority wins |
| **Conflict** | Same priority → manual wins; escalated to admin in Context Studio UI |
| **Auto-Learning** | Pattern detector (weekly batch): repeated tool sequence ≥ 5x → candidate rule (status: draft) → human approval |

---

### 3.6 Tier 5 — User Preference Memory (Personalization)

> Inspired by: **SimpleMem** (user-centric adaptive retrieval), **Mem0** (preference tracking)

**Purpose:** Personalization profile: tone, verbosity, format, active hours, common topics.

| Attribute | Value |
|:---|:---|
| **Provider** | `RelationalProvider` |
| **Update Strategy** | Weighted moving average over last 10 interactions |
| **Override Rule** | Explicit user settings always beat derived preferences |
| **Org Override** | Organizational rules supersede user preferences |
| **Confidence** | Increases with interaction count (starts at 0.3, caps at 0.95) |

---

### 3.7 Tier 6 — Organizational Memory (Governed Knowledge)

> Inspired by: **GraphRAG** (community knowledge), **MemGPT** (persona/system injection)

**Purpose:** Business glossaries, policies, compliance rules, data lineage.

| Attribute | Value |
|:---|:---|
| **Provider** | `RelationalProvider` + `VectorProvider` |
| **Access** | Admin-only writes; all agents can read |
| **Versioning** | Immutable audit trail; full version history |
| **GraphRAG** | Leiden community detection organizes the org knowledge graph into queryable communities |

---

## 4. Knowledge Graph Construction Pipeline

> Algorithms from: **Mem0** (entity extraction), **HippoRAG** (graph indexing), **GraphRAG** (community building)

```mermaid
flowchart TD
    A[Agent Interaction Log] --> B[SimpleMem: Semantic Structured Compression]
    B --> C[Coreference Resolution + Temporal Normalization]
    C --> D[Mem0: Entity + Relation Extractor<br/>LLM-based triple extraction]
    D --> E[Entity Resolution<br/>Is subject/object already in graph?]
    E -->|Exists| F[Link to existing node]
    E -->|New| G[Create new entity node]
    F --> H[Fact Conflict Check<br/>Semantic Supersession]
    G --> H
    H -->|No conflict| I[Corroboration Check<br/>cosine_sim > 0.85?]
    H -->|Conflict| J[Mark old fact superseded<br/>Store new with higher confidence]
    I -->|Corroborates| K[Increment corroboration_count<br/>Boost confidence]
    I -->|New fact| L[Store with initial confidence]
    K --> M[Update VectorProvider embedding]
    L --> M
    J --> M
    M --> N[GraphRAG: Run Leiden Community Detection<br/>Build community summaries]
    N --> O[HippoRAG: Update PPR index]
```

**Triple Extraction LLM Prompt:**
```
Extract structured knowledge triples from the following text.
Return as JSON array of {subject, predicate, object, confidence (0.0–1.0)}.

Rules:
1. subject and object must be specific ENTITIES (people, orgs, products, concepts, locations)
2. predicate must be a clear relationship verb: "works_at", "prefers", "located_in", "uses", "manages"
3. Only extract facts with confidence >= 0.6
4. Resolve pronouns and coreferences to actual entity names
5. Flag temporal facts with valid_from / valid_until if time context is present
6. Ignore speculation and hypotheticals

Known entities in this tenant's graph: {existing_entity_list}

Text: {source_text}
```

---

## 5. Advanced Retrieval Pipeline — Hybrid + RRF + Re-Rank

> Algorithms from: **Mem0** (multi-signal retrieval), **HippoRAG** (PPR graph traversal), **SimpleMem** (intent-aware planning), **RRF** (Cormack & Clarke 2009)

### 5.1 Phase 0 — Intent-Aware Retrieval Planning (SimpleMem)

Before firing any search, the engine estimates query complexity to determine retrieval scope:
- **Simple fact query** (e.g., "What's my name?") → Semantic only, no graph traversal, no re-ranking.
- **Complex reasoning query** (e.g., "What decisions did I make last month about Project X?") → Full hybrid pipeline with graph, RRF, and re-ranking.

```python
retrieval_plan = intent_planner.plan(query)
# Returns: {search_depth: "deep|shallow", enable_graph: bool, 
#            enable_rerank: bool, top_k: int}
```

### 5.2 Phase 1 — Parallel Hybrid Search

| Search Path | Algorithm | Provider |
|:---|:---|:---|
| **Dense Vector** | Approximate Nearest Neighbor (ANN) with cosine similarity | `VectorProvider` |
| **Sparse Keyword** | BM25 over memory content | `RelationalProvider` |
| **Graph Traversal** | HippoRAG Personalized PageRank (PPR), max 2-hop | `GraphProvider` |
| **Entity Match** | Boost memories containing query entities (Mem0 enhancement) | `VectorProvider` payload filter |

### 5.3 Phase 2 — RRF Fusion (Configurable Algorithm)

**Standard RRF (Cormack & Clarke 2009):**
$$\text{RRF\_Score}(d) = \sum_{r \in R} \frac{1}{k + \text{rank}(r, d)}$$
- $k = 60$ (default, mitigates rank outlier impact)
- $R$ = set of all retrieval sources (Dense, Sparse, Graph)

**Weighted RRF (Production Variant):**
$$\text{WRRF\_Score}(d) = \sum_{r \in R} w_r \cdot \frac{1}{k + \text{rank}(r, d)}$$
- $w_r$ configurable per source (e.g., `dense=1.0, sparse=0.7, graph=0.9`)
- Configured in `MemoryConfig.retrieval.rrf_weights`

**Feature toggle:** `rrf_fusion: false` → simple concatenation + deduplication.

### 5.4 Phase 3 — Cross-Encoder Re-Ranking (Optional)

Top-K results from RRF are re-scored by a cross-encoder (query + memory chunk processed jointly):
- **Default model:** `BAAI/bge-reranker-large` (local, free)
- **Cloud option:** Cohere Rerank API
- **Feature toggle:** `cross_encoder_reranking: false` → skip (saves ~200ms latency)

### 5.5 Phase 4 — Context Budget Optimizer (MemGPT)

Dynamically fits the final memory payload into the active LLM's context window:
- Reads `model_context_limit` from config (e.g., 128k for Claude 3.5, 8k for Llama 3.1-8B)
- Allocates token budgets: `system_prompt (15%) + memory_context (30%) + conversation (35%) + user_input (20%)`
- Truncates or summarizes memory items that exceed budget, prioritizing by RRF score.

---

## 6. Configurable Feature Toggle System

All expensive pipeline stages can be toggled via `MemoryConfig`. Config can be set globally, per-tenant, or per-agent.

```python
from context_studio import MemoryConfig, RetrievalConfig, StrategyConfig

config = MemoryConfig(
    strategy=StrategyConfig(
        strategy_type="heavy_episodic",        # balanced | heavy_episodic | heavy_semantic | procedural_strict
        episodic_weight=0.5,
        semantic_weight=0.2,
        procedural_weight=0.3
    ),
    retrieval=RetrievalConfig(
        hybrid_search=True,                    # Enable all 3 parallel search paths
        enable_dense_search=True,              # Dense vector ANN
        enable_sparse_search=True,             # BM25 keyword
        enable_graph_traversal=True,           # HippoRAG PPR
        enable_entity_boost=True,              # Mem0 entity matching
        rrf_fusion=True,                       # RRF merge
        rrf_algorithm="weighted",              # standard | weighted
        rrf_k=60,                              # RRF constant
        rrf_weights={"dense": 1.0, "sparse": 0.7, "graph": 0.9},
        cross_encoder_reranking=False,         # Cross-encoder (adds ~200ms)
        cross_encoder_model="BAAI/bge-reranker-large",
        intent_aware_planning=True,            # SimpleMem intent planner
        top_k=10,                              # Results after RRF
        final_top_k=5                          # Results after re-rank
    ),
    storage=StorageConfig(
        cache_provider="redis",                # redis | memcached | local | file
        relational_provider="postgres",        # postgres | sqlite | file
        vector_provider="qdrant",              # qdrant | pinecone | milvus | chroma | faiss | file
        graph_provider="neo4j",                # neo4j | postgres_age | networkx | file
    ),
    governance=GovernanceConfig(
        enable_contradiction_resolution=True,
        enable_time_decay=True,
        decay_half_life_days=30,
        enable_garbage_collection=True,
        gc_threshold_score=0.05,               # Prune if decay_score < 0.05 AND importance < 3
        enable_data_lineage=True,              # Track source of every memory
        enable_audit_trail=True
    ),
    context=ContextConfig(
        model_name="claude-3-5-sonnet",        # Auto-detects context limit
        model_context_limit=200000,            # Override if needed
        system_prompt_budget_pct=0.15,
        memory_budget_pct=0.30,
        conversation_budget_pct=0.35
    )
)
```

---

## 7. Pluggable Storage Abstraction Layer

The engine operates entirely through abstract base class interfaces. Swap any backend without touching agent code.

| Interface | Backends Supported | Fallback |
|:---|:---|:---|
| `CacheProvider` | Redis, Memcached, In-Memory dict, Local JSON file | Local JSON |
| `RelationalProvider` | PostgreSQL, SQLite, Local JSON file | Local JSON |
| `VectorProvider` | Qdrant, Pinecone, Milvus, ChromaDB, FAISS, Local NumPy+JSON | Local NumPy |
| `GraphProvider` | Neo4j, PostgreSQL AGE, NetworkX (in-memory), Local JSON triple store | Local JSON |

**Zero-Dependency Mode:** Every provider has a `FileSystem` fallback implementation (using JSON + NumPy cosine similarity). This allows the entire engine to run offline with zero external services for development and testing.

---

## 8. Multi-Agent & Tool Calling Logic

### 8.1 Single-Agent Mode
Standard `agent_id → session_id` memory isolation with full RBAC enforcement.

### 8.2 Multi-Agent Swarm Mode (CrewAI / AutoGen / LangGraph)

| Feature | Mechanism |
|:---|:---|
| **Shared Knowledge Graph** | All agents in same `tenant_id` read/write the same `GraphProvider` namespace |
| **Isolated Episodic Memory** | Each agent has its own vector collection; tagged with `agent_id` |
| **Cross-Agent Learning** | Agent B can query Agent A's episodic memory (if RBAC permits) to avoid repeating failures |
| **Shared Working Memory** | Redis hash `wm:{tenant_id}:shared:{workflow_id}` for real-time swarm state |
| **Workflow Coordinator** | A `coordinator_agent_id` can write to all sub-agent sessions (RBAC admin policy) |

### 8.3 Tool Calling Memory

| Event | Memory Action |
|:---|:---|
| Tool invoked | Tool name + parameters stored in Working Memory (Tier 0) |
| Tool succeeds (low importance) | Flushed at session end; not persisted to Episodic |
| Tool succeeds (high importance, e.g., `send_email`) | Async extracted as Episode with `outcome=success, importance=8` |
| Tool fails | Always extracted as Episode with `outcome=failure, importance=7`; blocks duplicate calls |
| Tool pattern repeated ≥ 5x | Procedural Memory auto-learning pipeline creates a candidate rule |

---

## 9. Security — Multi-Tenant RBAC (PyCasbin)

### 9.1 Model

```ini
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _  # Role inheritance

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = r.sub == "admin" || g(r.sub, "admin") || (r.sub == p.sub && r.obj == p.obj && r.act == p.act)
```

### 9.2 Policies & Roles

| Role | Permissions |
|:---|:---|
| `admin` | Full bypass — read/write any session in tenant |
| `agent` | Read/write only their own sessions (auto-granted on first write) |
| `readonly_agent` | Read-only access to shared Organizational Memory |
| `coordinator` | Read/write across all sessions in a workflow |

### 9.3 Auto-Grant on Session Create

When an agent writes to a session for the first time, the engine automatically grants:
`p, {agent_id}, {session_id}, read_write`

This prevents soft-locks while maintaining strict isolation across tenants.

---

## 10. Governance — Contradiction, Decay & GC

### 10.1 Contradiction Resolution (Mem0 Semantic Supersession)

When a new fact `F_new` arrives and conflicts with existing fact `F_old`:
1. Compute semantic similarity between `F_new` and all facts for same `subject`.
2. If `similarity > 0.85` and predicates match: flag as potential contradiction.
3. Apply supersession rules:
   - `F_new` has higher `confidence` → mark `F_old` as `superseded_by=F_new.id`
   - `F_new` is more recent → mark `F_old` as `valid_until=F_new.created_at`
   - Tie → both stored as `status=disputed`; surfaced in admin UI for manual resolution.

### 10.2 Memory Decay (Mem0 Algorithm)

- Decay score recalculated daily for all Episodic memories by background worker.
- Score = `0.5 ^ (days_since_access / (30 * importance_multiplier))`
- On retrieval: decay clock resets (access reinforcement).

### 10.3 Garbage Collection

Background cron (configurable interval, default: weekly):
```python
def should_prune(memory):
    return memory.decay_score < gc_threshold AND memory.importance_score < 3
```
Pruned memories are soft-deleted first (archived) and permanently deleted after 30 days.

### 10.4 Data Lineage

Every memory record includes:
```json
{
  "lineage": {
    "source_agent_id": "agent_001",
    "source_session_id": "sess_abc",
    "source_turn_number": 7,
    "extracted_at": "2026-06-22T10:00:00Z",
    "extractor_model": "gpt-4o-mini",
    "confidence": 0.87
  }
}
```

---

## 11. Evaluation Framework

> Inspired by: RAGAS, TruLens, Mem0 benchmarks (LoCoMo, LongMemEval, BEAM)

Context Studio includes a built-in evaluation harness to measure memory quality.

| Metric | Definition | Method |
|:---|:---|:---|
| **Context Precision** | % of retrieved memories that are actually relevant | LLM-as-judge grading |
| **Context Recall** | % of relevant memories that were actually retrieved | Compared to gold set |
| **Faithfulness** | Did the agent use the memory correctly? | LLM-as-judge |
| **Answer Relevancy** | Is the final answer relevant given the retrieved context? | Embedding cosine similarity |
| **Memory Efficiency** | Tokens consumed vs information retained | `tokens_used / relevant_facts_count` |

**Feedback Loop:** Agent or human can rate memory quality (1–5). This rating adjusts the memory's `importance_score` and `decay_score` in real-time, closing the learning loop.

---

## 12. Integration Layer (API, SDK, MCP)

### 12.1 REST API (No-Code / Generic / N8N / Flowise)

**Target:** Any HTTP client, no-code builders, custom backends.

| Endpoint | Method | Description |
|:---|:---|:---|
| `/v1/health` | GET | Health check |
| `/v1/memory/search` | POST | Query memory (full hybrid pipeline) |
| `/v1/memory/add` | POST | Add interaction (triggers async write-back) |
| `/v1/memory/facts` | GET | List all semantic facts for agent |
| `/v1/memory/graph` | GET | Export knowledge graph for agent |
| `/v1/memory/config` | GET/PUT | Read/update MemoryConfig |
| `/v1/admin/policies` | GET/POST | Manage RBAC policies |
| `/v1/admin/gc` | POST | Trigger manual garbage collection |
| `/v1/eval/run` | POST | Run evaluation harness against a test set |

**Auth:** `X-API-Key` header (tenant-scoped). `X-Agent-ID` for identity.

---

### 12.2 Native Python SDK (Deep Integration)

**Target:** LangChain, LangGraph, AutoGen, CrewAI, Google ADK, custom Python agents.

**Installation:**
```bash
pip install context-studio
```

**Universal Client (framework-agnostic):**
```python
from context_studio import ContextStudio, MemoryConfig

cs = ContextStudio(
    config=MemoryConfig(storage=StorageConfig(vector_provider="qdrant", ...)),
    agent_id="my_agent",
    tenant_id="my_tenant"
)

# Save an interaction
await cs.save(session_id="s1", role="user", content="I love Python")

# Search memory
context = await cs.search(session_id="s1", query="What does the user prefer?")
```

**LangChain / LangGraph Adapter:**
```python
from context_studio.integrations.langchain import ContextStudioChatHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

history = ContextStudioChatHistory(cs_client=cs, session_id="s1")
chain_with_memory = RunnableWithMessageHistory(chain, lambda sid: history)
```

**AutoGen Adapter:**
```python
from context_studio.integrations.autogen import ContextStudioMemoryPlugin

plugin = ContextStudioMemoryPlugin(cs_client=cs)
agent = ConversableAgent(..., memory=plugin)
```

**CrewAI Adapter:**
```python
from context_studio.integrations.crewai import ContextStudioCrewMemory

crew = Crew(agents=[...], tasks=[...], memory=ContextStudioCrewMemory(cs_client=cs))
```

---

### 12.3 MCP Server (Claude / Cursor / Pi / Any MCP Client)

**Target:** Any application supporting Anthropic's Model Context Protocol (MCP).

**Interface:** FastMCP via `stdio` — zero HTTP server needed. Agents connect via their MCP client config.

**Exposed Tools:**

| Tool Name | Parameters | Description |
|:---|:---|:---|
| `remember` | `content, session_id, importance` | Save a fact or interaction |
| `recall` | `query, session_id, top_k` | Search memory (full hybrid pipeline) |
| `get_facts` | `entity, agent_id` | Get all knowledge graph facts for an entity |
| `get_user_preferences` | `user_id` | Retrieve personalization profile |
| `list_episodes` | `agent_id, limit` | List recent episodic memories |
| `add_rule` | `trigger, instruction, priority` | Add a procedural rule |
| `forget` | `memory_id` | Soft-delete a specific memory |

**Claude Desktop `config.json` snippet:**
```json
{
  "mcpServers": {
    "context-studio": {
      "command": "python",
      "args": ["-m", "context_studio.integrations.mcp.server"],
      "env": {
        "CS_TENANT_ID": "your_tenant",
        "CS_AGENT_ID": "claude_desktop"
      }
    }
  }
}
```

---

## 13. Boundary Cases & Edge Cases — All Handled

| Category | Case | Strategy |
|:---|:---|:---|
| **Working Memory** | Token budget exceeded mid-turn | MemGPT paging: evict oldest, summarize, resume |
| **Working Memory** | Session crash without cleanup | TTL-based auto-expiry; orphan detection cron |
| **Working Memory** | Concurrent tool calls writing simultaneously | CacheProvider atomic operations (Redis MULTI/EXEC) |
| **Conversational** | Very long session (500+ turns) | Rolling summarization in chunks of 50 |
| **Conversational** | Session resumed after days | Load summary + last 5 turns; inject "resumed session" marker |
| **Episodic** | Near-duplicate episodes | Cosine > 0.95 → merge; access_count incremented |
| **Episodic** | Contradicting episodes | Flag `status=disputed`; newer gets higher trust by default |
| **Episodic** | Embedding model change | Re-embed all with new model; maintain model_version field |
| **Semantic** | Contradicting facts | Semantic supersession (Mem0); disputed flag in admin UI |
| **Semantic** | Temporal facts (CEO changes) | `valid_until` + `superseded_by` chain |
| **Semantic** | Entity ambiguity ("Apple" = fruit or company?) | Store with `type=ambiguous`; surface for disambiguation |
| **Semantic** | Circular KG relationships | PPR depth limit (max 3 hops); cycle detection in traversal |
| **Procedural** | Conflicting rules | Priority-based resolution; equal priority → manual wins |
| **Procedural** | Rule explosion (too many rules) | Top-K by relevance; always-on rules get reserved budget |
| **Retrieval** | All search paths return empty | Graceful fallback: return conversation history only |
| **Retrieval** | VectorDB unavailable | Fallback to BM25 + Graph only |
| **Multi-Agent** | Agent A fails, Agent B should know | Episodic tag `agent_id`; cross-agent search via coordinator role |
| **Multi-Agent** | Race condition on shared Working Memory | Redis atomic operations; last-write-wins for scratchpad |
| **Multi-Agent** | Data leakage between tenants | `tenant_id` filtering enforced at every provider level + RBAC |
| **Tool Calling** | Important tool failure | Always stored in Episodic with `outcome=failure` |
| **Privacy** | Right-to-be-forgotten (GDPR) | Cascade delete: all memories with `user_id` = target |
| **Scale** | 100K+ vectors per agent | VectorProvider ANN handles; migrate to HNSW for >1M |
| **Governance** | Memory GC over-prunes important facts | GC requires BOTH decay < threshold AND importance < 3 |

---

## 14. Database Schemas

### 14.1 Relational Schema (PostgreSQL / SQLite)

```sql
-- conversation_turns
CREATE TABLE conversation_turns (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL,
    agent_id        TEXT NOT NULL,
    session_id      TEXT NOT NULL,
    user_id         TEXT,
    turn_number     INTEGER NOT NULL,
    role            TEXT NOT NULL,     -- user | assistant | system | tool
    content         TEXT NOT NULL,
    token_count     INTEGER,
    metadata        TEXT,              -- JSON: tool_calls, model_used, latency
    created_at      REAL DEFAULT (unixepoch())
);
CREATE INDEX idx_turns_session ON conversation_turns(session_id, turn_number);

-- semantic_facts (Knowledge Graph relational store)
CREATE TABLE semantic_facts (
    id                  TEXT PRIMARY KEY,
    tenant_id           TEXT NOT NULL,
    agent_id            TEXT,           -- NULL = tenant-wide
    subject             TEXT NOT NULL,
    predicate           TEXT NOT NULL,
    object_val          TEXT NOT NULL,
    confidence          REAL DEFAULT 0.7,
    corroboration_count INTEGER DEFAULT 1,
    status              TEXT DEFAULT 'active',  -- active | superseded | disputed | archived
    superseded_by       TEXT REFERENCES semantic_facts(id),
    valid_from          REAL,
    valid_until         REAL,
    lineage             TEXT,           -- JSON lineage record
    created_at          REAL DEFAULT (unixepoch())
);
CREATE INDEX idx_facts_tenant_subject ON semantic_facts(tenant_id, subject);

-- procedural_rules
CREATE TABLE procedural_rules (
    id                TEXT PRIMARY KEY,
    tenant_id         TEXT NOT NULL,
    agent_id          TEXT,
    name              TEXT NOT NULL,
    rule_type         TEXT NOT NULL,    -- workflow | constraint | escalation | injection
    trigger_condition TEXT NOT NULL,    -- JSON
    action_sequence   TEXT NOT NULL,    -- JSON
    priority          INTEGER DEFAULT 50,
    confidence        REAL DEFAULT 1.0,
    learned           INTEGER DEFAULT 0,
    status            TEXT DEFAULT 'active',
    created_at        REAL DEFAULT (unixepoch())
);

-- user_preferences
CREATE TABLE user_preferences (
    id               TEXT PRIMARY KEY,
    tenant_id        TEXT NOT NULL,
    user_id          TEXT NOT NULL,
    response_style   TEXT DEFAULT 'balanced',
    technical_level  TEXT DEFAULT 'intermediate',
    tone             TEXT DEFAULT 'professional',
    common_topics    TEXT DEFAULT '[]',  -- JSON
    explicit_prefs   TEXT DEFAULT '{}',  -- JSON
    interaction_count INTEGER DEFAULT 0,
    confidence       REAL DEFAULT 0.3,
    updated_at       REAL DEFAULT (unixepoch()),
    UNIQUE(tenant_id, user_id)
);

-- episodic_metadata (mirrored from VectorProvider payloads)
CREATE TABLE episodic_metadata (
    id               TEXT PRIMARY KEY,
    tenant_id        TEXT NOT NULL,
    agent_id         TEXT NOT NULL,
    session_id       TEXT NOT NULL,
    episode_type     TEXT,              -- interaction | decision | tool_success | tool_failure | milestone
    summary          TEXT NOT NULL,
    outcome          TEXT,              -- success | failure | partial | escalated
    importance_score INTEGER DEFAULT 5,
    decay_score      REAL DEFAULT 1.0,
    access_count     INTEGER DEFAULT 0,
    last_accessed_at REAL,
    lineage          TEXT,
    created_at       REAL DEFAULT (unixepoch())
);

## 15. Algorithm Index — Paper-to-Feature Mapping

| Feature in Context Studio | Algorithm | Paper | Section |
|:---|:---|:---|:---|
| Episodic extraction | Single-pass ADD-only extraction | **Mem0** (2024) |
| Episodic time-decay | `0.5^(days/half_life * importance_mult)` | **Mem0** (2024) |
| Retrieval multi-signal fusion | Semantic + Keyword + Entity matching | **Mem0** (2024) | 
| Contradiction resolution | Semantic supersession with `superseded_by` | **Mem0** (2024) |
| Context paging & overflow | OS-inspired RAM/Disk paging model | **MemGPT** (2023) |
| Context budget optimization | Token budget allocation by slot type | **MemGPT** (2023) |
| Agent self-interrupts | Interrupt-based context state machine | **MemGPT** (2023) |
| Semantic lossless compression | 3-stage: compress → synthesize → plan | **SimpleMem** (2026) |
| Intent-aware retrieval planning | Query complexity estimation → scope | **SimpleMem** (2026) |
| KG multi-hop retrieval | Personalized PageRank (PPR) | **HippoRAG** (NeurIPS 2024) |
| Associative memory traversal | Hippocampal indexing theory → KG seeds | **HippoRAG** (NeurIPS 2024) | 
| Community knowledge summaries | Leiden community detection | **GraphRAG** (Microsoft, 2024) |
| Rank fusion across search paths | Standard RRF: `Σ 1/(k + rank(r,d))` | **RRF** (Cormack & Clarke, 2009) |
| Configurable source weighting | Weighted RRF: `Σ w_r · 1/(k + rank(r,d))` | Production variant of RRF | §5.3 |
| Benchmarking & evaluation | LoCoMo, LongMemEval, BEAM metrics | **Mem0** / **SimpleMem** benchmarks | §11 |
