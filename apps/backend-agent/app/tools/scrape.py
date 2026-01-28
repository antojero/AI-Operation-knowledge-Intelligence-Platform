from langchain_core.tools import tool
import httpx
from bs4 import BeautifulSoup

@tool
async def scrape_tool(url: str):
    """
    Scrape the content of a webpage.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Simple extraction for now
            text = soup.get_text(separator=' ', strip=True)
            if not text:
                return "The webpage content was empty."
            return text[:5000] # Limit content length
        except Exception as e:
            return f"Failed to scrape {url}: {str(e)}"
