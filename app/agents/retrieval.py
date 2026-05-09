import json
import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.schema import State
from app.core.tools import execute_tool
from app.core.config import settings
from app.core.telemetry import track_agent
from typing import Dict, Any

llm = ChatOpenAI(model="gpt-4-turbo", api_key=settings.openai_api_key)

async def process_single_task(task):
    """
    Decides tool and executes. Now handles structured dicts from execute_tool.
    """
    tool_prompt = f"""
    Task: {task.description}
    Choose the best tool: 'search', 'wikipedia', 'arxiv', or 'scrapper'.
    If the task mentions a specific URL, use 'scrapper'. 
    If it's academic, use 'arxiv'.
    
    Return ONLY JSON: {{"tool": "tool_name", "query": "optimized_search_query"}}
    """
    
    try:
        # 1. Get decision from LLM
        response = await llm.ainvoke([SystemMessage(content=tool_prompt)])
        decision = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
        
        # 2. Execute the tool (This now returns a DICT based on our tools.py update)
        tool_result = await execute_tool(decision["tool"], decision["query"])
        
        return {
            "id": task.id,
            "tool_used": decision["tool"],
            "content": tool_result.get("output"),
            "tool_retry_count": tool_result.get("tool_retry_count", 0),
            "tool_error": tool_result.get("tool_error"),
            "status": tool_result.get("status")
        }
    except Exception as e:
        return {
            "id": task.id,
            "tool_used": "none",
            "content": f"Failed to process task: {str(e)}",
            "tool_error": "PROCESSING_ERROR",
            "status": "failed"
        }

@track_agent
async def retrieval_node(state: State) -> Dict[str, Any]:
    sub_tasks = state.get("sub_tasks", [])
    agent_outputs = state.get("agent_outputs", {})

    tasks_to_run = [t for t in sub_tasks if t.status == "pending" and t.id not in agent_outputs]

    if not tasks_to_run:
        return {"next_node": "orchestrator"}

    print(f"⚡ [PARALLEL] Executing {len(tasks_to_run)} tasks simultaneously...")

    results = await asyncio.gather(*[process_single_task(t) for t in tasks_to_run])

    # 4. Merge results and metadata into state
    new_outputs = {}
    total_retries = 0
    primary_error = None

    for res in results:
        # Store individual task results
        new_outputs[res["id"]] = {
            "tool_used": res["tool_used"],
            "content": res["content"],
            "status": res["status"]
        }
        
        # Accumulate metadata for the tests to find at the top level of agent_outputs
        total_retries += res.get("tool_retry_count", 0)
        if res.get("tool_error"):
            primary_error = res.get("tool_error")

    # We add these keys to the top level of the return so the Test loop can find them
    new_outputs["tool_retry_count"] = total_retries
    if primary_error:
        new_outputs["tool_error"] = primary_error

    return {
        "agent_outputs": new_outputs,
        "next_node": "orchestrator"
    }