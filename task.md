# Context Studio Tasks

## Phase 1 — Foundation

### Sprint 1–2: Project Scaffolding & Core Infrastructure
- [ ] **Monorepo Setup**
  - [ ] Initialize Turborepo
  - [ ] Scaffold `apps/web` (React + Vite)
  - [ ] Scaffold `apps/api` (NestJS)
  - [ ] Scaffold `packages/shared-types`
  - [ ] Scaffold `packages/memory-sdk`
  - [ ] Scaffold `packages/ui-components`
- [ ] **Infrastructure & Database**
  - [ ] Create `docker-compose.yml` (PostgreSQL, Redis, Qdrant, Neo4j)
  - [ ] Initialize database migrations tool (Prisma or TypeORM)
  - [ ] Define core PostgreSQL schema (tenants, users, agents, credentials)
- [ ] **Core Backend**
  - [ ] Setup Authentication (JWT) module
  - [ ] Setup Redis connection and working memory cache
  - [ ] Setup CI/CD basic pipeline (GitHub Actions)

### Sprint 3–4: Visual Agent Builder (Canvas MVP)
- [ ] Integrate React Flow in `apps/web`
- [ ] Build custom node components (Triggers, Actions, AI, Logic)
- [ ] Implement node configuration sidebar
- [ ] Blueprint serialization and save API

### Sprint 5–6: Basic Execution & Short-term Memory
- [ ] Implement synchronous workflow execution engine (DAG parser)
- [ ] Implement Working Memory interactions (Redis)
- [ ] Implement Conversational Memory (PostgreSQL storage & sliding window)
- [ ] Build 10 pre-built connectors

---

## Phase 2 — Memory & Intelligence

### Sprint 7–8: Episodic Memory
- [ ] Integrate Qdrant vector database
- [ ] Build Episode extraction pipeline (LLM)
- [ ] Implement decay algorithm and scoring

### Sprint 9–10: Semantic Memory
- [ ] Integrate Neo4j knowledge graph
- [ ] Build Fact extraction pipeline and entity resolution
- [ ] Implement Hybrid Retrieval (Vector + Graph + Keyword)

### Sprint 11–12: Procedural & Preference Memory
- [ ] Implement Rule matching engine
- [ ] Implement User preference derivation
- [ ] Queue-based execution engine upgrades

*(Further phases will be detailed as we progress)*
