import httpx
import os
import asyncio
import json

BACKEND_CORE_URL = os.environ.get("BACKEND_CORE_URL", "http://backend-core:8000/api/agent")
INTERNAL_SECRET = os.environ.get("INTERNAL_SERVICE_SECRET", "supersecret")

class Persistence:
    async def create_run(self, task: str, user_id: str = None, org_id: str = None, agent_type: str = "RESEARCHER"):
        url = f"{BACKEND_CORE_URL}/runs/"
        headers = {
            "X-Internal-Secret": INTERNAL_SECRET,
            "Content-Type": "application/json"
        }
        
        # We need a user ID for the run. If not provided, we might fail or need a fallback.
        # For this prototype, we'll try to get the first user if none provided (very hacky, but works for "Phase 3 Startup Mode")
        # Better: Frontend MUST pass user_id.
        
        payload = {
            "agent_type": agent_type,
            "input_params": {"task": task},
            "status": "QUEUED"
        }
        if user_id:
             payload["user"] = user_id
        else:
             # AUTO-FIX: Use confirmed Admin UUID
             payload["user"] = "9e88a73b-278a-4272-beb0-f3354d97d82a"
        
        if org_id:
            payload["organization"] = org_id
        else:
            # AUTO-FIX: Use confirmed Default Org UUID
            payload["organization"] = "5cf64b03-7cb8-485c-a761-6f93ff210313"
        
        async with httpx.AsyncClient() as client:
            try:
                # If we don't have user_id, we might want to query backend-core for a default user?
                # Or just let it fail and we see the error.
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 201:
                    return response.json()
                else:
                    print(f"Failed to create run: {response.status_code} {response.text}")
                    return None
            except Exception as e:
                print(f"Error connecting to backend-core: {e}")
                return None

    async def update_run_status(self, run_id: str, status: str, result: dict = None, cost: float = 0.0):
        url = f"{BACKEND_CORE_URL}/runs/{run_id}/"
        headers = {
            "X-Internal-Secret": INTERNAL_SECRET,
            "Content-Type": "application/json"
        }
        payload = {"status": status}
        if result:
            payload["output_result"] = result
        if cost > 0:
            payload["cost_usd"] = cost # requires serializer update or partial update?
        
        async with httpx.AsyncClient() as client:
            try:
                await client.patch(url, json=payload, headers=headers)
            except Exception as e:
                print(f"Error updating run: {e}")

    async def log_step(self, run_id: str, step_type: str, content: dict):
        url = f"{BACKEND_CORE_URL}/steps/"
        headers = {
            "X-Internal-Secret": INTERNAL_SECRET,
            "Content-Type": "application/json"
        }
        payload = {
            "run": run_id,
            "step_type": step_type,
            "content": content
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code != 201:
                    # Don't crash the agent if logging fails, just warn
                    print(f"Failed to log step: {response.status_code} {response.text}")
            except Exception as e:
                # Fail silent-ish
                print(f"Error logging step: {e}")

persistence = Persistence()
