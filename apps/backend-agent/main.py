from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agents.researcher import app as research_agent
from app.core.persistence import persistence
import os

app = FastAPI(title="AI Agent Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    import os
    import asyncpg
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        conn = await asyncpg.connect(db_url)
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS langgraph_checkpoints (
                    thread_id TEXT NOT NULL,
                    thread_ts TEXT NOT NULL,
                    parent_ts TEXT,
                    checkpoint BYTEA NOT NULL,
                    metadata BYTEA NOT NULL,
                    PRIMARY KEY (thread_id, thread_ts)
                );
            """)
            print("Verified langgraph_checkpoints table.")
        finally:
            await conn.close()

class AgentRequest(BaseModel):
    task: str
    user_id: str = None # Optional user ID from frontend

@app.get("/")
def read_root():
    return {"status": "ok", "service": "backend-agent", "llm": "gemini-2.5-flash"}

@app.post("/search")
async def direct_search(request: AgentRequest):
    """
    Direct vector search - results are saved to history as 'Direct Search' type.
    """
    import httpx
    import uuid
    
    # 1. Create a Run Record for History
    
    # Log the start of the run (Cost: 0 for now)
    run_data = await persistence.create_run(
        task=request.task, 
        agent_type="direct_search", 
        user_id=request.user_id # Might be None, backend-core handles it
    )
    
    # If creation failed, just generate a temporary ID so we don't crash, but it won't be saved
    if run_data and 'id' in run_data:
        run_id = run_data['id']
    else:
        run_id = str(uuid.uuid4())
        print(f"[WARN] Failed to create run in backend-core, using temp ID: {run_id}")
    
    url = f"{os.environ.get('BACKEND_CORE_URL', 'http://backend-core:8000/api')}/documents/search/"
    headers = {
        "X-Internal-Secret": os.environ.get("INTERNAL_SERVICE_SECRET", "supersecret"),
        "Content-Type": "application/json"
    }
    
    final_answer = ""
    error_msg = ""
    status = "COMPLETED"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"query": request.task}, headers=headers, timeout=10.0)
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                
                if not results:
                    final_answer = "No relevant documents found in the knowledge base."
                else:
                    # Format the answer
                    answer_parts = []
                    for i, r in enumerate(results[:3], 1):
                        answer_parts.append(f"**From '{r['document_title']}'** (relevance: {r['score']:.1%}):\n\n{r['text_content'][:800]}\n")
                    final_answer = "\n---\n\n".join(answer_parts)
            else:
                status = "FAILED"
                error_msg = f"Search failed: {response.status_code}"
                final_answer = error_msg

    except Exception as e:
        status = "FAILED"
        error_msg = str(e)
        final_answer = f"Error: {str(e)}"

    # 2. Update Run Status (Completed/Failed)
    await persistence.update_run_status(
        run_id, 
        status, 
        result={"response": final_answer},
        cost=0.000000 # Direct search is free
    )

    return {
        "status": "success" if status == "COMPLETED" else "error",
        "answer": final_answer,
        "run_id": run_id
    }

async def run_agent_background(task: str, thread_id: str, run_id: str):
    """
    Background task to run agent and update persistence.
    """
    try:
        await persistence.update_run_status(run_id, "RUNNING")
        
        initial_state = {
            "task": task,
            "content": [],
            "revision_number": 0,
            "max_revisions": 2,
            "messages": [],
            "final_response": ""
        }
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 10}
        
        final_state = await research_agent.ainvoke(initial_state, config=config)
        
        # Extract usage stats - iterate through ALL messages to sum up tokens
        input_tokens = 0
        output_tokens = 0
        messages = final_state.get('messages', [])
        
        print(f"[DEBUG] Inspecting {len(messages)} messages for usage metadata...")
        for msg in messages:
            # Check standard LangChain usage_metadata
            if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                input_tokens += msg.usage_metadata.get('input_tokens', 0)
                output_tokens += msg.usage_metadata.get('output_tokens', 0)
            # Fallback: sometimes it's in response_metadata
            elif hasattr(msg, 'response_metadata'):
                usage = msg.response_metadata.get('usage', {}) # Gemini specific often in usage
                if usage: 
                     # Gemini returns 'prompt_token_count' etc
                    input_tokens += usage.get('prompt_token_count', 0) or usage.get('input_tokens', 0)
                    output_tokens += usage.get('candidates_token_count', 0) or usage.get('output_tokens', 0)
        
        # Calculate theoretical cost (Gemini Flash Pricing Model)
        # Using standard Flash rates as baseline: $0.075/1M input, $0.30/1M output
        if os.environ.get("GOOGLE_API_KEY"):
            cost = (input_tokens / 1_000_000 * 0.075) + (output_tokens / 1_000_000 * 0.30)
            print(f"[DEBUG] Run {run_id} | Tokens: In={input_tokens}, Out={output_tokens} | Cost: ${cost:.8f}")
        else:
            cost = 0.0
            
        result_content = final_state.get("final_response")
        
        await persistence.update_run_status(
            run_id, 
            "COMPLETED", 
             result={
                "response": result_content,
                "tokens": input_tokens + output_tokens
            }, 
            cost=cost
        )
        
    except Exception as e:
        print(f"Agent failed: {e}")
        await persistence.update_run_status(run_id, "FAILED", result={"error": str(e)})

@app.post("/agent/run")
async def run_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    """
    Trigger the Research Agent asynchronously.
    """
    try:
        # 1. Create Run in Backend Core
        run_data = await persistence.create_run(request.task, request.user_id)
        run_id = run_data['id'] if run_data else "local-run" # Fallback if persistence fails
        
        import uuid
        thread_id = str(uuid.uuid4())
        
        # 2. Add to background tasks
        background_tasks.add_task(run_agent_background, request.task, thread_id, run_id)
        
        return {
            "status": "queued",
            "run_id": run_id,
            "thread_id": thread_id
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import StreamingResponse
import json
import asyncio

@app.post("/agent/stream")
async def stream_agent(request: AgentRequest):
    """
    Stream the agent execution.
    """
    async def event_generator():
        # Create Run for tracking
        run_data = await persistence.create_run(request.task, request.user_id)
        run_id = run_data['id'] if run_data else None
        if run_id:
             await persistence.update_run_status(run_id, "RUNNING")

        initial_state = {
            "task": request.task,
            "content": [],
            "revision_number": 0,
            "max_revisions": 2,
            "messages": [],
            "final_response": ""
        }
        import uuid
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 10}
        
        final_response = None
        usage_stats = {"input_tokens": 0, "output_tokens": 0}
        
        try:
            # Async stream of events
            async for event in research_agent.astream_events(initial_state, config=config, version="v1"):
                kind = event["event"]
                
                # Filter for relevant events to send to UI
                if kind == "on_chat_model_stream":
                    continue 

                # Capture Usage Metadata from Model End Events
                if kind == "on_chat_model_end" or kind == "on_llm_end":
                    output = event['data'].get('output')
                    usage = None

                    # Strategy 1: Direct Usage Metadata (Newer LangChain)
                    if hasattr(output, 'usage_metadata') and output.usage_metadata:
                        usage = output.usage_metadata
                    elif isinstance(output, dict) and 'usage_metadata' in output:
                        usage = output['usage_metadata']
                    
                    # Strategy 2: Generations (Standard ChatResult)
                    if not usage:
                         generations = None
                         if hasattr(output, 'generations'):
                             generations = output.generations
                         elif isinstance(output, dict):
                             generations = output.get('generations')
                         
                         if generations and len(generations) > 0:
                             first_gen = generations[0]
                             # Check Generation -> Message -> Usage
                             if hasattr(first_gen, 'message'):
                                 msg = first_gen.message
                                 if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                                     usage = msg.usage_metadata
                                 elif hasattr(msg, 'response_metadata'):
                                     usage = msg.response_metadata.get('usage')
                             elif isinstance(first_gen, dict):
                                 msg = first_gen.get('message')
                                 if msg:
                                     if isinstance(msg, dict):
                                         usage = msg.get('usage_metadata') or msg.get('response_metadata', {}).get('usage')
                                     elif hasattr(msg, 'usage_metadata'):
                                         usage = msg.usage_metadata
                                         
                    if not usage and hasattr(output, 'llm_output') and output.llm_output:
                             usage = output.llm_output.get('token_usage') or output.llm_output.get('usage')

                    if usage:
                        # Normalize keys (Gemini vs Standard LangChain)
                        input_tokens = usage.get('input_tokens') or usage.get('prompt_token_count', 0)
                        output_tokens = usage.get('output_tokens') or usage.get('candidates_token_count', 0) or usage.get('completion_tokens', 0)
                        
                        usage_stats['input_tokens'] += input_tokens
                        usage_stats['output_tokens'] += output_tokens
                        print(f"[DEBUG] Captured tokens: In={input_tokens}, Out={output_tokens}") 
                
                if kind == "on_chain_start":
                    if event["name"] == "LangGraph":
                        yield f"data: {json.dumps({'type': 'start', 'thread_id': thread_id, 'run_id': run_id})}\n\n"
                        
                elif kind == "on_tool_start":
                     tool_input = event['data'].get('input')
                     safe_input = str(tool_input) if tool_input else ""
                     yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name'], 'input': safe_input})}\n\n"
                     
                elif kind == "on_tool_end":
                     output_data = event['data'].get('output')
                     safe_output = str(output_data) if output_data else ""
                     yield f"data: {json.dumps({'type': 'tool_end', 'tool': event['name'], 'output': safe_output})}\n\n"
                     if run_id:
                         await persistence.log_step(run_id, "tool_call", {"tool": event["name"], "output": safe_output})
                
                elif kind == "on_chain_end":
                     output = event["data"].get("output")
                     if output and isinstance(output, dict):
                         val = output.get('final_response')
                         if val:
                             if isinstance(val, list):
                                 parts = []
                                 for part in val:
                                     if isinstance(part, str):
                                         parts.append(part)
                                     elif isinstance(part, dict) and "text" in part:
                                         parts.append(part["text"])
                                 val = "".join(parts)
                             elif isinstance(val, dict) and "text" in val:
                                 val = val["text"]
                             
                             final_response = val
                             yield f"data: {json.dumps({'type': 'complete', 'result': final_response})}\n\n"
                            
            # Fallback if no response generated
            if not final_response:
                 final_response = "I processed the task but could not generate a text response. Please check the logs or try rephrasing."
                 yield f"data: {json.dumps({'type': 'complete', 'result': final_response})}\n\n"

            # Fallback: Capture usage from final state if events missed it
            if usage_stats['input_tokens'] == 0 and usage_stats['output_tokens'] == 0:
                 try:
                     print("[DEBUG] Fetching final state for token usage fallback...")
                     final_state_snapshot = await research_agent.aget_state(config)
                     if final_state_snapshot and final_state_snapshot.values:
                         msgs = final_state_snapshot.values.get('messages', [])
                         for msg in msgs:
                             # Check standard LangChain usage_metadata
                             if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                                 usage_stats['input_tokens'] += msg.usage_metadata.get('input_tokens', 0)
                                 usage_stats['output_tokens'] += msg.usage_metadata.get('output_tokens', 0)
                             # Fallback: sometimes it's in response_metadata
                             elif hasattr(msg, 'response_metadata'):
                                 usage = msg.response_metadata.get('usage', {}) 
                                 if usage: 
                                      # Gemini returns 'prompt_token_count' etc
                                     usage_stats['input_tokens'] += usage.get('prompt_token_count', 0) or usage.get('input_tokens', 0)
                                     usage_stats['output_tokens'] += usage.get('candidates_token_count', 0) or usage.get('output_tokens', 0)
                         print(f"[DEBUG] Fallback Usage Stats: {usage_stats}")
                 except Exception as exc:
                     print(f"[WARN] Could not fetch final state for usage: {exc}")

            # Cost estimation logic...
            total_cost = 0.000000 
            total_tokens = 0
            
            # Use aggregated stats if available
            if usage_stats['input_tokens'] > 0 or usage_stats['output_tokens'] > 0:
                total_tokens = usage_stats['input_tokens'] + usage_stats['output_tokens']
                if os.environ.get("GOOGLE_API_KEY"):
                    # Gemini Flash Pricing: $0.075/1M input, $0.30/1M output
                    total_cost = (usage_stats['input_tokens'] / 1_000_000 * 0.075) + (usage_stats['output_tokens'] / 1_000_000 * 0.30)
            
            if run_id:
                await persistence.update_run_status(
                    run_id, 
                    "COMPLETED", 
                    result={
                        "response": final_response, 
                        "tokens": total_tokens,
                        "usage": usage_stats
                    }, 
                    cost=total_cost
                )
                
        except Exception as e:
            if run_id:
                await persistence.update_run_status(run_id, "FAILED", result={"error": str(e)})
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
