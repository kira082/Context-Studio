import pytest
from context_studio.core.config import RetrievalConfig
from context_studio.core.retrieval import RetrievalEngine
from context_studio.providers.filesystem.vector import FileSystemVectorProvider
from context_studio.providers.filesystem.relational import FileSystemRelationalProvider
from context_studio.providers.filesystem.graph import FileSystemGraphProvider

@pytest.fixture
def retrieval_engine(tmp_path):
    config = RetrievalConfig(
        hybrid_search=True,
        enable_graph_traversal=True,
        cross_encoder_reranking=False
    )
    vec = FileSystemVectorProvider(base_dir=str(tmp_path / "vector"))
    rel = FileSystemRelationalProvider(base_dir=str(tmp_path / "relational"))
    grph = FileSystemGraphProvider(base_dir=str(tmp_path / "graph"))
    
    return RetrievalEngine(config, vec, rel, grph)

@pytest.mark.asyncio
async def test_retrieval_engine_empty(retrieval_engine):
    session_id = "test_retrieval_sess"
    query = "What is the capital of France?"
    
    result = await retrieval_engine.search(session_id, query)
    
    assert "results" in result
    assert "plan" in result
    assert "metrics" in result
    assert result["metrics"]["total_fused"] == 0

@pytest.mark.asyncio
async def test_intent_planner(retrieval_engine):
    plan_simple = retrieval_engine.intent_planner.plan_retrieval("hi")
    assert not plan_simple["use_graph"]
    
    plan_complex = retrieval_engine.intent_planner.plan_retrieval("explain the history of python")
    assert plan_complex["use_graph"]
    assert plan_complex["needs_reranking"]
