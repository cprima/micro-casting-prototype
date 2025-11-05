"""Vector search MCP server (simplified demonstration)."""
import asyncio
import numpy as np
from typing import List, Dict
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

app = Server("mcp-vector-search")

# Simple in-memory vector store
vector_store: List[Dict] = []

def simple_embed(text: str) -> np.ndarray:
    """Simple embedding (character frequency vector)."""
    vector = np.zeros(26)
    text = text.lower()
    for char in text:
        if 'a' <= char <= 'z':
            vector[ord(char) - ord('a')] += 1
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Cosine similarity between vectors."""
    return float(np.dot(v1, v2))

@app.list_resources()
async def list_resources():
    return [
        Resource(
            uri="vectors://store",
            name="Vector Store",
            description=f"In-memory vector store ({len(vector_store)} entries)",
            mimeType="application/json"
        )
    ]

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="add_vector",
            description="Add text to vector store",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="search_vectors",
            description="Search vector store by similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 3}
                },
                "required": ["query"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "add_vector":
        text = arguments["text"]
        metadata = arguments.get("metadata", {})
        vector = simple_embed(text)
        entry_id = len(vector_store)
        vector_store.append({
            "id": entry_id,
            "text": text,
            "vector": vector,
            "metadata": metadata
        })
        return [TextContent(type="text", text=f"Added entry {entry_id}")]
    elif name == "search_vectors":
        query = arguments["query"]
        top_k = arguments.get("top_k", 3)

        if not vector_store:
            return [TextContent(type="text", text="Vector store is empty")]

        query_vector = simple_embed(query)
        scored = []
        for entry in vector_store:
            similarity = cosine_similarity(query_vector, entry["vector"])
            scored.append((entry, similarity))

        scored.sort(key=lambda x: x[1], reverse=True)
        results = []
        for entry, score in scored[:top_k]:
            results.append(f"[Score: {score:.3f}] {entry['text']}")

        return [TextContent(type="text", text="\\n".join(results))]
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
