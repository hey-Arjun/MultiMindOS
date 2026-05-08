import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from app.core.schema import State

app = FastAPI(title="Multi-Agent Orchestrator API")

async def dummy_orchestrator_stream(query: str):
    """
    Simulates the real-time activity of agents. 
    In Phase 2, this will be replaced by the actual LangGraph execution.
    """
    state = State(query=query)
    
    events = [
        {"agent": "Orchestrator", "message": "Analyzing query...", "budget": state.context_window_budget},
        {"agent": "Decomposition", "message": "Breaking down tasks...", "budget": 3800},
        {"agent": "Retrieval", "message": "Fetching multi-hop data...", "budget": 3500},
        {"agent": "Synthesis", "message": "Generating final response...", "budget": 3000}
    ]

    for event in events:
        await asyncio.sleep(1.5) # Simulate processing time
        yield f"data: {json.dumps(event)}\n\n"

@app.post("/submit")
async def submit_query(request: Request):
    data = await request.json()
    query = data.get("query")
    return StreamingResponse(dummy_orchestrator_stream(query), media_type="text/event-stream")

@app.get("/health")
async def health():
    return {"status": "operational"}