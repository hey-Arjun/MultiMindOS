import os
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from app.agents.graph import create_graph
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
graph = create_graph()

async def run_agent_system(query: str, session_id: str):

    config = {"configurable": {"thread_id": session_id}, "recursion_limit": 25}

    initial_state = {
        "query": query,
        "sub_tasks": [],
        "agent_outputs": {},
        "next_node": "orchestrator",
        "used_tokens": 0,
        "context_window_budget": 4000,
        "final_answer": None
    }

    try:
        async for event in graph.astream(initial_state, config=config):
            for node_name, output in event.items():
                
                # 1. Capture the core signals
                next_action = output.get("next_node", "continuing...")
                final_result = output.get("final_answer") # Check for the synthesis result
                
                # 2. Build the output payload
                payload = {
                    "node": node_name,
                    "update": f"Node {node_name} finished.",
                    "next_step": next_action,
                }

                # 3. Add the result if it exists
                if final_result:
                    payload["final_result"] = final_result
                
                # 4. Handle snapshot safely (merging current output with previous knowledge)
                # Note: output only contains the CHANGES from the last node.
                payload["state_snapshot"] = {
                    "tasks_count": len(output.get("sub_tasks", [])),
                    "outputs_keys": list(output.get("agent_outputs", {}).keys()),
                    "has_final": bool(final_result)
                }
                
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.1)

    except Exception as e:
        # This will catch LLM timeouts, API key issues, etc.
        error_payload = {"error": str(e), "type": "GraphExecutionError"}
        yield f"data: {json.dumps(error_payload)}\n\n"

@app.post("/submit")
async def submit(request: Request):
    data = await request.json()
    query = data.get("query")
    session_id = data.get("session_id", "default_thread")
    return StreamingResponse(
        run_agent_system(query, session_id),
        media_type="text/event-stream"
    )