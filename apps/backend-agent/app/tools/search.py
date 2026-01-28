from typing import Optional, List
from duckduckgo_search import DDGS
from langchain_core.tools import tool

@tool
def search_tool(query: str):
    """
    Search the web for information using DuckDuckGo (Free).
    """
    try:
        results = list(DDGS().text(query, max_results=3))
        if not results:
            return "No web search results found."
        return str(results)
    except Exception as e:
        return f"Search failed: {str(e)}"
