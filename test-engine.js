const { ContextStudio } = require('./packages/context-studio/dist/index.js');
const { PrismaClient } = require('@prisma/client');

async function run() {
  const memory = new ContextStudio();
  await memory.initialize();
  
  // Need to create the tenant directly with Prisma since we didn't expose saveTenant in the SDK yet
  const prisma = new PrismaClient();
  const tenantId = 'tenant_456';
  await prisma.tenant.upsert({
    where: { slug: 'test-tenant' },
    update: {},
    create: {
      id: tenantId,
      name: 'Test Tenant',
      slug: 'test-tenant'
    }
  });

  console.log("\n[1] Saving Dummy Agent...");
  const agent = await memory.saveAgentBlueprint(tenantId, 'Advanced Support Bot', {}, {});
  console.log("Agent Created:", agent.id);

  console.log("\n[2] Simulating Chat Turn 1 (with facts and episodes)...");
  
  // This statement triggers Semantic Extraction (" is ") and Episodic Vectorization
  const userStatement = "The default password is password123";
  await memory.writeBack(agent.id, 'session_2', { turnNumber: 1, role: 'user', content: userStatement });
  
  // Sleep briefly to ensure async operations complete (in real app, writeBack is async/background)
  await new Promise(resolve => setTimeout(resolve, 500));

  console.log("\n[3] Fetching Context for Turn 2...");
  // This query will search the vector space and the SQLite graph for "password"
  const context = await memory.getContext(agent.id, 'session_2', 'What is the default password?');
  
  console.log("\n✅ Retrieved Context:");
  console.log(JSON.stringify(context, null, 2));
}

run().catch(console.error);
