from typing import Optional, Type, List, Dict, Any
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
import httpx
import os

BACKEND_CORE_URL = os.environ.get("BACKEND_CORE_URL", "http://backend-core:8000/api")
INTERNAL_SECRET = os.environ.get("INTERNAL_SERVICE_SECRET", "supersecret")

class RetrievalInput(BaseModel):
    query: str = Field(description="The query string to search for in the knowledge base.")

class RetrievalTool(BaseTool):
    name: str = "retrieve_memory"
    description: str = "Search the organizational knowledge base/memory for relevant documents and information."
    args_schema: Type[BaseModel] = RetrievalInput

    def _run(self, query: str) -> str:
        # Synchronous wrapper (LangChain often prefers sync tools, or we use .acall)
        # Using httpx sync client for simplicity in this correct context, 
        # but for async agents we should implement _arun ideally.
        import httpx
        url = f"{BACKEND_CORE_URL}/documents/search/"
        headers = {
            "X-Internal-Secret": INTERNAL_SECRET,
            "Content-Type": "application/json"
        }
        try:
            response = httpx.post(url, json={"query": query}, headers=headers, timeout=10.0)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if not results:
                    return "No relevant documents found in memory."
                
                formatted_results = []
                for r in results:
                     formatted_results.append(f"Title: {r['document_title']}\nContent: {r['text_content']}\nScore: {r['score']:.2f}")
                
                return "\n\n---\n\n".join(formatted_results)
            else:
                return f"Error retrieving memory: {response.status_code} {response.text}"
        except Exception as e:
            return f"Error connecting to memory service: {str(e)}"

    async def _arun(self, query: str) -> str:
        url = f"{BACKEND_CORE_URL}/documents/search/"
        headers = {
            "X-Internal-Secret": INTERNAL_SECRET,
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json={"query": query}, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    results = response.json().get("results", [])
                    if not results:
                        return "No relevant documents found in memory."
                    
                    formatted_results = []
                    for r in results:
                        formatted_results.append(f"Title: {r['document_title']}\nContent: {r['text_content']}\nScore: {r['score']:.2f}")
                    
                    return "\n\n---\n\n".join(formatted_results)
                else:
                    return f"Error retrieving memory: {response.status_code} {response.text}"
            except Exception as e:
                return f"Error connecting to memory service: {str(e)}"

retrieval_tool = RetrievalTool()
