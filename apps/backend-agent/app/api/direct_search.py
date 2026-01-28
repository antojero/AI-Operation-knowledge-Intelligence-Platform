from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os

router = APIRouter()

BACKEND_CORE_URL = os.environ.get("BACKEND_CORE_URL", "http://backend-core:8000/api")
INTERNAL_SECRET = os.environ.get("INTERNAL_SERVICE_SECRET", "supersecret")

class DirectSearchRequest(BaseModel):
    query: str

@router.post("/direct-search")
async def direct_search(request: DirectSearchRequest):
    """
    Direct vector search without LLM - much faster!
    Returns formatted results from the knowledge base.
    """
    url = f"{BACKEND_CORE_URL}/documents/search/"
    headers = {
        "X-Internal-Secret": INTERNAL_SECRET,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"query": request.query}, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                
                if not results:
                    return {
                        "status": "success",
                        "answer": "No relevant documents found in the knowledge base.",
                        "sources": []
                    }
                
                # Format the answer
                answer_parts = []
                sources = []
                
                for i, r in enumerate(results[:3], 1):  # Top 3 results
                    answer_parts.append(f"**From {r['document_title']}** (relevance: {r['score']:.2%}):\\n{r['text_content'][:500]}...")
                    sources.append({
                        "title": r['document_title'],
                        "score": r['score'],
                        "preview": r['text_content'][:200]
                    })
                
                return {
                    "status": "success",
                    "answer": "\\n\\n---\\n\\n".join(answer_parts),
                    "sources": sources,
                    "total_results": len(results)
                }
            else:
                return {
                    "status": "error",
                    "answer": f"Search failed: {response.status_code}",
                    "sources": []
                }
                
    except Exception as e:
        return {
            "status": "error",
            "answer": f"Error: {str(e)}",
            "sources": []
        }
