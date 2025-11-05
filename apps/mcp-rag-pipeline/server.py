"""RAG pipeline MCP server (simplified demonstration)."""
import asyncio
from typing import List, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

app = Server("mcp-rag-pipeline")

# Simple in-memory knowledge base
KNOWLEDGE_BASE = [
    {"id": 1, "text": "Python is a high-level programming language.", "metadata": {"topic": "python"}},
    {"id": 2, "text": "MCP stands for Model Context Protocol.", "metadata": {"topic": "mcp"}},
    {"id": 3, "text": "RAG combines retrieval and generation.", "metadata": {"topic": "rag"}},
    {"id": 4, "text": "Vector search enables semantic similarity.", "metadata": {"topic": "search"}},
]

@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="knowledge://base",
            name="Knowledge Base",
            description=f"In-memory knowledge base ({len(KNOWLEDGE_BASE)} entries)",
            mimeType="application/json"
        )
    ]

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="retrieve_context",
            description="Retrieve relevant context for a query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "description": "Number of results", "default": 3}
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="add_knowledge",
            description="Add entry to knowledge base",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "topic": {"type": "string"}
                },
                "required": ["text", "topic"],
            },
        )
    ]

def simple_similarity(query: str, text: str) -> float:
    """Simple word overlap similarity."""
    query_words = set(query.lower().split())
    text_words = set(text.lower().split())
    if not query_words:
        return 0.0
    return len(query_words & text_words) / len(query_words)

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "retrieve_context":
        query = arguments["query"]
        top_k = arguments.get("top_k", 3)

        # Score all entries
        scored = [(doc, simple_similarity(query, doc["text"])) for doc in KNOWLEDGE_BASE]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Return top results
        results = []
        for doc, score in scored[:top_k]:
            results.append(f"[Score: {score:.2f}] {doc['text']}")

        return [TextContent(type="text", text="\\n".join(results))]
    elif name == "add_knowledge":
        text = arguments["text"]
        topic = arguments["topic"]
        new_id = max([doc["id"] for doc in KNOWLEDGE_BASE], default=0) + 1
        KNOWLEDGE_BASE.append({
            "id": new_id,
            "text": text,
            "metadata": {"topic": topic}
        })
        return [TextContent(type="text", text=f"Added entry {new_id}")]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
