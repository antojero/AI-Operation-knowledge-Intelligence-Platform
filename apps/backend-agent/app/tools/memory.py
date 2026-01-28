import os
import json
from typing import List, Optional
import asyncpg
from langchain_core.tools import tool
from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings

# Singleton for connection pool if needed, or create per call
DB_URL = os.environ.get("DATABASE_URL")

def get_embeddings() -> Embeddings:
    llm_base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    return OllamaEmbeddings(model="llama3.1:latest", base_url=llm_base)

@tool
async def save_knowledge(content: str, metadata: str = "{}"):
    """
    Saves a piece of knowledge to the organization's memory.
    Useful for storing facts, research findings, or summaries for later recall.
    """
    # In a real app, we need org_id from context. 
    # For Phase 1, we'll hardcode or assume a default org context via env var or pass it in.
    # We'll use a placeholder Org ID for now or fetch the first one.
    
    conn = await asyncpg.connect(DB_URL)
    try:
        # Get embedding
        embedder = get_embeddings()
        vector = await embedder.aembed_query(content)
        
        # 1. Create Document
        # We need a valid Org ID. Let's grab the first one for robustness in this phase.
        org_id = await conn.fetchval("SELECT id FROM organizations_organization LIMIT 1")
        if not org_id:
            return "Error: No organization found to attach memory to."

        doc_id = await conn.fetchval(
            """
            INSERT INTO documents_document (id, organization_id, title, content, metadata, created_at, updated_at)
            VALUES (gen_random_uuid(), $1, 'Agent Memory', $2, $3::jsonb, NOW(), NOW())
            RETURNING id
            """,
            org_id, content, metadata
        )

        # 2. Create Chunk
        await conn.execute(
            """
            INSERT INTO documents_documentchunk (id, document_id, chunk_index, text_content, embedding)
            VALUES (gen_random_uuid(), $1, 0, $2, $3)
            """,
            doc_id, content, str(vector) # pgvector expects array string or list
        )
        
        return "Knowledge successfully saved."
    except Exception as e:
        return f"Failed to save knowledge: {e}"
    finally:
        await conn.close()

@tool
async def recall_knowledge(query: str):
    """
    Searches the extensive memory database for relevant information.
    Use this to look up past research, facts, or context.
    """
    conn = await asyncpg.connect(DB_URL)
    try:
        embedder = get_embeddings()
        vector = await embedder.aembed_query(query)
        
        # pgvector cosine similarity (<->) or L2 (<->) or Inner Product (<#>)
        # We use <=> for cosine distance (lower is better) or <#> for negative inner product.
        # Recommended: <=>. 
        
        rows = await conn.fetch(
            """
            SELECT text_content, 1 - (embedding <=> $1) as similarity
            FROM documents_documentchunk
            ORDER BY embedding <=> $1
            LIMIT 3
            """,
            str(vector)
        )
        
        results = [f"- {r['text_content']} (Confidence: {r['similarity']:.2f})" for r in rows]
        return "\n".join(results) if results else "No relevant memories found."
        
    except Exception as e:
        return f"Failed to recall knowledge: {e}"
    finally:
        await conn.close()
