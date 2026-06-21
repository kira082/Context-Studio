import { PrismaClient } from '@prisma/client';
import { LRUCache } from 'lru-cache';

export interface MemoryConfig {
  maxWorkingMemoryItems?: number;
}

// Simple Dot Product for Vector Similarity (Cosine Similarity for normalized vectors)
function computeSimilarity(vecA: number[], vecB: number[]): number {
  let dotProduct = 0;
  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
  }
  return dotProduct;
}

// Mock Embedding generation (since we don't have an OpenAI key hooked up here)
function mockEmbed(text: string): number[] {
  // Return a dummy 1536-dimensional vector based on string length and char codes
  const vec = new Array(1536).fill(0);
  for(let i=0; i<Math.min(text.length, 1536); i++) {
    vec[i] = (text.charCodeAt(i) % 10) / 10;
  }
  return vec;
}

export class ContextStudio {
  private prisma: PrismaClient;
  private workingMemory: LRUCache<string, any>;

  constructor(private config: MemoryConfig = {}) {
    this.prisma = new PrismaClient();
    this.workingMemory = new LRUCache({
      max: config.maxWorkingMemoryItems || 5000,
      ttl: 1000 * 60 * 60 * 2,
    });
  }

  async initialize() {
    console.log("Initializing Context Studio embedded memory stores...");
    await this.prisma.$connect();
    return true;
  }

  // ==========================================
  // PHASE 1: ASSEMBLE CONTEXT (READ)
  // ==========================================

  async getContext(agentId: string, sessionId: string, query: string) {
    const wmKey = `wm:${agentId}:${sessionId}`;
    
    // 1. Working Memory (LRU)
    const activeContext = this.workingMemory.get(wmKey) || [];

    // 2. Conversational Memory (SQLite)
    const recentTurns = await this.prisma.conversationTurn.findMany({
      where: { agentId, sessionId },
      orderBy: { turnNumber: 'desc' },
      take: 10
    });

    // 3. Episodic Memory (Local Vector Search)
    const episodic = await this.searchEpisodicMemory(agentId, query, 3);

    // 4. Semantic Memory (SQLite Graph Traversal)
    const semanticGraph = await this.searchSemanticGraph(agentId, query);

    return {
      workingMemory: activeContext,
      conversational: recentTurns.reverse(),
      episodic,
      semanticGraph
    };
  }

  // ==========================================
  // PHASE 3: ASYNC WRITE-BACK (WRITE)
  // ==========================================

  async writeBack(agentId: string, sessionId: string, interaction: any) {
    // 1. Update Working Memory
    const wmKey = `wm:${agentId}:${sessionId}`;
    const currentWm = this.workingMemory.get(wmKey) || [];
    this.workingMemory.set(wmKey, [...currentWm, interaction]);

    // 2. Persist to Conversational Memory
    await this.prisma.conversationTurn.create({
      data: {
        agentId,
        sessionId,
        turnNumber: interaction.turnNumber || 1,
        role: interaction.role || 'user',
        content: interaction.content || '',
      }
    });

    // 3. Extract and save Episodic Memory asynchronously (Mock LLM Extraction)
    if (interaction.role === 'user') {
      const summary = `User stated: ${interaction.content.substring(0, 50)}...`;
      await this.saveEpisodicMemory(agentId, summary);
      
      // 4. Extract Semantic Facts (Mock Logic)
      await this.saveSemanticFact(agentId, interaction.content);
    }

    return { status: 'success' };
  }

  // ==========================================
  // EPISODIC MEMORY (Local Vector Store)
  // ==========================================

  async saveEpisodicMemory(agentId: string, summary: string) {
    const vector = mockEmbed(summary);
    return await this.prisma.episodicVector.create({
      data: {
        agentId,
        summary,
        vectorData: JSON.stringify(vector),
      }
    });
  }

  async searchEpisodicMemory(agentId: string, query: string, topK: number = 3) {
    const queryVector = mockEmbed(query);
    
    // Fetch all vectors for this agent (Brute force local dot-product)
    const allEpisodes = await this.prisma.episodicVector.findMany({
      where: { agentId }
    });

    const scored = allEpisodes.map(ep => {
      const vecData = JSON.parse(ep.vectorData);
      const score = computeSimilarity(queryVector, vecData);
      // Apply decay logic (Time-weighted score)
      const daysOld = (Date.now() - ep.createdAt.getTime()) / (1000 * 60 * 60 * 24);
      const decayFactor = Math.exp(-0.05 * daysOld); 
      return {
        ...ep,
        finalScore: score * decayFactor * ep.decayScore
      };
    });

    // Sort descending by score
    scored.sort((a, b) => b.finalScore - a.finalScore);
    return scored.slice(0, topK).map(ep => ({ summary: ep.summary, score: ep.finalScore }));
  }

  // ==========================================
  // SEMANTIC MEMORY (SQLite Graph)
  // ==========================================

  async saveSemanticFact(agentId: string, text: string) {
    // Mock Entity Extraction: If text contains "is", assume "A is B"
    if (text.includes(' is ')) {
      const [source, target] = text.split(' is ');
      
      // Upsert Source Node
      let nodeA = await this.prisma.kgNode.findFirst({ where: { agentId, name: source.trim() } });
      if (!nodeA) {
        nodeA = await this.prisma.kgNode.create({ data: { agentId, name: source.trim(), type: 'entity' } });
      }

      // Upsert Target Node
      let nodeB = await this.prisma.kgNode.findFirst({ where: { agentId, name: target.trim() } });
      if (!nodeB) {
        nodeB = await this.prisma.kgNode.create({ data: { agentId, name: target.trim(), type: 'concept' } });
      }

      // Create Edge
      await this.prisma.kgEdge.create({
        data: {
          sourceId: nodeA.id,
          targetId: nodeB.id,
          relationType: 'IS_A'
        }
      });
    }
  }

  async searchSemanticGraph(agentId: string, query: string) {
    // Simplified traversal: Find nodes that match words in query, then get 1-hop connections
    const words = query.split(' ');
    const relevantNodes = await this.prisma.kgNode.findMany({
      where: {
        agentId,
        OR: words.map(w => ({ name: { contains: w } }))
      },
      include: {
        outgoingEdges: { include: { target: true } },
        incomingEdges: { include: { source: true } }
      }
    });

    // Flatten graph to facts
    const facts: string[] = [];
    relevantNodes.forEach(node => {
      node.outgoingEdges.forEach(edge => {
        facts.push(`${node.name} ${edge.relationType} ${edge.target.name}`);
      });
    });

    return facts;
  }

  // ==========================================
  // CORE PLATFORM APIS
  // ==========================================

  async saveAgentBlueprint(tenantId: string, name: string, blueprint: any, memoryConfig: any) {
    return await this.prisma.agent.create({
      data: {
        tenantId,
        name,
        blueprint: JSON.stringify(blueprint),
        memoryConfig: JSON.stringify(memoryConfig),
      }
    });
  }

  async getAgent(agentId: string) {
    return await this.prisma.agent.findUnique({
      where: { id: agentId }
    });
  }
}
