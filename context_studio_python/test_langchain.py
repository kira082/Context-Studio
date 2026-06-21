from database import SessionLocal, engine
import models
from memory_sdk import MemoryEngine
from integrations.langchain_wrapper import ContextStudioMemory

def run_langchain_test():
    print("Context Studio LangChain Integration Test\n")
    
    # 1. Setup DB
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 2. Create Agent
    print("[1] Provisioning Memory Space...")
    agent = models.Agent(tenant_id="tenant_langchain", name="LangChain Agent")
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    mem_engine = MemoryEngine(db)
    
    # 3. Add a Procedural Rule (Skill)
    print("[2] Adding a Procedural Rule (If user says 'refund', state policy)...")
    mem_engine.save_procedural_rule(
        agent_id=agent.id, 
        trigger_keyword="refund", 
        instruction="Strict Policy: Do not issue refunds over 30 days."
    )
    
    # 4. Add Semantic Fact
    print("[3] Adding a Semantic Graph Fact...")
    mem_engine.save_semantic_fact(agent.id, "The policy is strict")
    
    # 5. Initialize LangChain Wrapper
    lc_memory = ContextStudioMemory(
        agent_id=agent.id,
        session_id="session_lc_1",
        memory_engine=mem_engine
    )
    
    # 6. Simulate LangChain Intercepting User Input
    user_query = "I want a refund. What is the policy?"
    print(f"\n[4] User Input: '{user_query}'")
    print("...LangChain fetches memory variables before sending to LLM...\n")
    
    # load_memory_variables happens right before the prompt goes to OpenAI/Anthropic
    memory_vars = lc_memory.load_memory_variables({"input": user_query})
    
    print("Context Successfully Injected into LangChain Prompt:")
    print("------------------------------------------------------")
    print(memory_vars["context_studio_history"])
    print("------------------------------------------------------")
    
    # 7. Simulate LangChain saving context after LLM responds
    print("\n[5] Simulating LangChain saving the AI response back to memory...")
    lc_memory.save_context(
        inputs={"input": user_query},
        outputs={"output": "Based on our strict policy, I cannot issue refunds over 30 days."}
    )
    print("Successfully wrote turns back to Context Studio!")

if __name__ == "__main__":
    run_langchain_test()
