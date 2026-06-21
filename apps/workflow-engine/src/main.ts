import express from 'express';
import { ContextStudio } from '@repo/context-studio';

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3001;

// Initialize Plug & Play Memory Module
const contextStudio = new ContextStudio();
let initialized = false;

app.get('/health', async (req, res) => {
  if (!initialized) {
    await contextStudio.initialize();
    initialized = true;
  }
  res.json({ status: 'ok', component: 'workflow-engine' });
});

// Save Blueprint Endpoint
app.post('/blueprints', async (req, res) => {
  const { tenantId, name, blueprint, memoryConfig } = req.body;
  try {
    const agent = await contextStudio.saveAgentBlueprint(tenantId, name, blueprint, memoryConfig);
    res.json({ status: 'success', agent });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

// Mock Execution Endpoint
app.post('/execute', async (req, res) => {
  const { agentId, sessionId, query } = req.body;
  
  if (!initialized) {
    await contextStudio.initialize();
    initialized = true;
  }
  
  console.log(`[Engine] Intercepting execution for agent ${agentId}...`);
  
  // Phase 1: Retrieve Context from Context Studio
  const context = await contextStudio.getContext(agentId, sessionId, query);
  
  // Phase 2: Execute Workflow (DAG) -> Mocked for MVP
  console.log(`[Engine] Running workflow DAG...`);
  const response = {
    answer: `Mock response based on memory. I see you have ${context.conversational.length} previous turns.`,
    extractedFacts: ["User likes mock endpoints"]
  };

  // Phase 3: Async Write-Back to Context Studio
  contextStudio.writeBack(agentId, sessionId, {
    turnNumber: context.conversational.length + 1,
    role: 'user',
    content: query
  });
  
  contextStudio.writeBack(agentId, sessionId, {
    turnNumber: context.conversational.length + 2,
    role: 'assistant',
    content: response.answer
  });

  res.json({ response, contextUsed: context });
});

app.listen(PORT, () => {
  console.log(`🚀 Workflow Engine is running on http://localhost:${PORT}`);
});
