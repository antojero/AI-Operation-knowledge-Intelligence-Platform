import asyncio
import httpx
import os
import sys

# Configuration from environment (simulating main.py)
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
BACKEND_CORE_URL = os.environ.get("BACKEND_CORE_URL", "http://backend-core:8000/api/agent")

async def check_services():
    print(f"Checking connectivity from backend-agent...")
    print(f"1. Checking Ollama at {OLLAMA_BASE_URL}...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
            if resp.status_code == 200:
                print("   [SUCCESS] Connected to Ollama!")
                print(f"   Models found: {[m['name'] for m in resp.json().get('models', [])]}")
            else:
                print(f"   [FAILED] Connected but got status {resp.status_code}")
    except Exception as e:
        print(f"   [FAILED] Could not connect to Ollama: {e}")

    print(f"\n2. Checking Backend Core at {BACKEND_CORE_URL}...")
    try:
        async with httpx.AsyncClient() as client:
            # We'll check the root endpoint or health
            # backend-core url is usually /api/agent -> /runs/
            # let's try just the base 
            base_url = BACKEND_CORE_URL.replace("/api/agent", "")
            resp = await client.get(f"{base_url}/admin/login/", timeout=5.0) # Admin login page should always exist
            if resp.status_code == 200:
                print("   [SUCCESS] Connected to Backend Core!")
            else:
                 print(f"   [FAILED] Connected but got status {resp.status_code}")
    except Exception as e:
        print(f"   [FAILED] Could not connect to Backend Core: {e}")

if __name__ == "__main__":
    asyncio.run(check_services())
