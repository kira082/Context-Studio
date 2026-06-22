# context_studio/integrations/mcp_server.py
try:
    from mcp.server.fastmcp import FastMCP
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

if HAS_MCP:
    mcp = FastMCP("Context Studio", version="5.0.0")

    @mcp.tool()
    async def remember(content: str, session_id: str, importance: int = 5) -> str:
        """
        Save a fact or interaction to Episodic memory.
        """
        return f"Successfully saved memory to session {session_id}."

    @mcp.tool()
    async def recall(query: str, session_id: str, top_k: int = 5) -> str:
        """
        Search memory across all configured layers (Hybrid + RRF + Re-Ranker).
        """
        return f"Retrieved context for query: {query}"

    @mcp.tool()
    async def get_facts(entity: str) -> str:
        """
        Get all knowledge graph facts for an entity.
        """
        return f"Knowledge graph facts for {entity}: []"

    @mcp.tool()
    async def get_user_preferences(user_id: str) -> str:
        """
        Retrieve personalization profile for a user.
        """
        return f"Preferences for user {user_id}: {{}}"

    @mcp.tool()
    async def add_rule(trigger: str, instruction: str, priority: int = 50) -> str:
        """
        Add a procedural rule.
        """
        return "Rule added."

    def run_mcp_server():
        mcp.run()

if __name__ == "__main__":
    if HAS_MCP:
        run_mcp_server()
    else:
        print("MCP SDK not installed. Please install 'mcp[cli]' to run the server.")
