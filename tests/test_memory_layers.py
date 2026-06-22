import pytest
import asyncio
from context_studio.providers.filesystem.cache import FileSystemCacheProvider
from context_studio.providers.filesystem.relational import FileSystemRelationalProvider
from context_studio.providers.filesystem.vector import FileSystemVectorProvider
from context_studio.providers.filesystem.graph import FileSystemGraphProvider

from context_studio.core.working_memory import WorkingMemory
from context_studio.core.conversational_memory import ConversationalMemory
from context_studio.core.episodic_memory import EpisodicMemory
from context_studio.core.semantic_memory import SemanticMemory

@pytest.fixture
def cache_provider(tmp_path):
    return FileSystemCacheProvider(base_dir=str(tmp_path / "cache"))

@pytest.fixture
def relational_provider(tmp_path):
    return FileSystemRelationalProvider(base_dir=str(tmp_path / "relational"))

@pytest.fixture
def vector_provider(tmp_path):
    return FileSystemVectorProvider(base_dir=str(tmp_path / "vector"))

@pytest.fixture
def graph_provider(tmp_path):
    return FileSystemGraphProvider(base_dir=str(tmp_path / "graph"))

@pytest.mark.asyncio
async def test_working_memory(cache_provider):
    wm = WorkingMemory(cache_provider, max_tokens=100)
    session_id = "test_sess"
    
    await wm.add_message(session_id, "user", "Hello there")
    state = await wm.get_state(session_id)
    assert len(state["messages"]) == 1
    assert state["messages"][0]["content"] == "Hello there"
    
    await wm.update_scratchpad(session_id, "thinking...")
    state = await wm.get_state(session_id)
    assert state["scratchpad"] == "thinking..."

@pytest.mark.asyncio
async def test_conversational_memory(relational_provider):
    cm = ConversationalMemory(relational_provider, summarize_every_n_turns=2)
    session_id = "test_cm_sess"
    
    await cm.add_turn(session_id, "user", "turn 1", "agent1", "tenant1")
    await cm.add_turn(session_id, "assistant", "turn 2", "agent1", "tenant1")
    
    # After 2 turns, a summary turn should be added
    history = await cm.get_recent_history(session_id, limit=5)
    assert len(history) == 3
    assert history[-1]["role"] == "system"
    assert "SUMMARY" in history[-1]["content"]

@pytest.mark.asyncio
async def test_episodic_memory(vector_provider):
    em = EpisodicMemory(vector_provider, half_life_days=30)
    
    await em.extract_and_store("sess1", "agent1", "tenant1", "User says hi", "user")
    
    # Search episodes
    results = await em.search_episodes("hello", limit=5)
    assert len(results) == 1
    assert "decay_score" in results[0]["metadata"]

@pytest.mark.asyncio
async def test_semantic_memory(graph_provider):
    sm = SemanticMemory(graph_provider)
    
    await sm.extract_and_store_facts("tenant1", "agent1", "User likes python")
    
    context = await sm.get_entity_context("python", depth=1)
    assert len(context) > 0
