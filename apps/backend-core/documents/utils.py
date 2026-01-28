import requests
from django.conf import settings

def get_embedding(text: str):
    """
    Generate embedding for text using Ollama (nomic-embed-text for best pgvector compatibility).
    """
    url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
    payload = {
        "model": "nomic-embed-text",
        "prompt": text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()['embedding']
    except Exception as e:
        # Fallback to OpenAI if configured, or just raise
        raise Exception(f"Ollama embedding failed: {str(e)}")
