# Simplified streaming approach using astream instead of astream_events
# This is more reliable for capturing the final response

async def stream_agent_simple(request: AgentRequest):
    """
    Stream the agent execution using astream (simpler, more reliable).
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
        
        yield f"data: {json.dumps({'type': 'start', 'thread_id': thread_id})}\\n\\n"
        
        final_response = None
        
        try:
            # Use astream which is simpler and more reliable
            token_stats = {"input": 0, "output": 0}
            async for state_update in research_agent.astream(initial_state, config=config):
                print(f"[DEBUG] State update: {list(state_update.keys())}")
                
                # Check if this update contains the final response
                for node_name, node_output in state_update.items():
                    if isinstance(node_output, dict):
                        if 'final_response' in node_output and node_output['final_response']:
                            final_response = node_output['final_response']
                            print(f"[DEBUG] Got final response: {final_response[:100]}...")
                            yield f"data: {json.dumps({'type': 'complete', 'result': final_response})}\\n\\n"
                        
                        # Check for tool calls in messages
                        if 'messages' in node_output:
                            for msg in node_output.get('messages', []):
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    for tool_call in msg.tool_calls:
                                        yield f"data: {json.dumps({'type': 'tool_start', 'tool': tool_call.get('name', 'unknown')})}\\n\\n"
                                
                                # Check for ToolMessage (output from tools) - Broader check
                                if hasattr(msg, 'type') and msg.type == 'tool':
                                    content = str(msg.content)
                                    # Extract titles with robust regex (handles potential whitespace/formatting)
                                    import re
                                    # Look for Title: at start of line
                                    titles = re.findall(r"(?:^|\n)Title:\s*(.*?)(?:\n|$)", content)
                                    for title in titles:
                                        t = title.strip()
                                        if t:
                                            print(f"[DEBUG] Found source: {t}")
                                            yield f"data: {json.dumps({'type': 'source', 'title': t})}\\n\\n"

                                # Token usage extraction
                                if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                                    usage = msg.usage_metadata
                                    input_tokens = usage.get('input_tokens') or usage.get('prompt_token_count', 0)
                                    output_tokens = usage.get('output_tokens') or usage.get('candidates_token_count', 0) or usage.get('completion_tokens', 0)
                                    token_stats['input'] += input_tokens
                                    token_stats['output'] += output_tokens
                                    print(f"[DEBUG] Captured tokens: In={input_tokens}, Out={output_tokens}")
            
            # Final fallback
            if not final_response:
                final_state = await research_agent.aget_state(config)
                if final_state and final_state.values:
                    final_response = final_state.values.get('final_response')
                    if final_response:
                        yield f"data: {json.dumps({'type': 'complete', 'result': final_response})}\\n\\n"
            
            total_cost = (token_stats['input'] / 1_000_000 * 0.075) + (token_stats['output'] / 1_000_000 * 0.30)
            if run_id:
                await persistence.update_run_status(run_id, "COMPLETED", result={"response": final_response, "tokens": token_stats['input'] + token_stats['output']}, cost=total_cost)
                
        except Exception as e:
            print(f"[ERROR] Stream error: {e}")
            import traceback
            traceback.print_exc()
            if run_id:
                await persistence.update_run_status(run_id, "FAILED", result={"error": str(e)})
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\\n\\n"
            
        yield "data: [DONE]\\n\\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
