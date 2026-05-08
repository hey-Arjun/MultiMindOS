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

async def run_agent_system(query: str):
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
        async for event in graph.astream(initial_state):
            for node_name, output in event.items():
                # 1. Extract the next step
                next_action = output.get("next_node", "working...")
                
                # 2. Extract the actual final answer if the Synthesis node just finished
                final_answer = output.get("final_answer")
                
                payload = {
                    "node": node_name,
                    "update": f"Node {node_name} finished.",
                    "next_step": next_action,
                    "state_snapshot": {
                        "tasks_count": len(output.get("sub_tasks", [])),
                        "outputs_keys": list(output.get("agent_outputs", {}).keys())
                    }
                }
                
                # 3. If we have the answer, put it in the payload!
                if final_answer:
                    payload["final_result"] = final_answer
                
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.2)
    except Exception as e:
        # This will catch LLM timeouts, API key issues, etc.
        error_payload = {"error": str(e), "type": "GraphExecutionError"}
        yield f"data: {json.dumps(error_payload)}\n\n"

@app.post("/submit")
async def submit(request: Request):
    data = await request.json()
    query = data.get("query")
    return StreamingResponse(run_agent_system(query), media_type="text/event-stream")