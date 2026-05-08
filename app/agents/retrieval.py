from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.schema import State
from app.core.tools import execute_tool
from app.core.config import settings
import json


llm = ChatOpenAI(model="gpt-4-turbo", api_key=settings.openai_api_key)

async def retrieval_node(state: State):
    # Find the next pending task
    sub_tasks = state.get("sub_tasks", [])
    target_task = next((t for t in sub_tasks if t.status == "pending"), None)

    if not target_task:
        return {"next_node": "orchestrator"}

    # 1. Ask LLM which tool to use for this specific sub-task
    tool_prompt = f"""
    Task: {target_task.description}
    Choose the best tool: 'search', 'wikipedia', 'arxiv', or 'scraper'.
    If the task mentions a specific URL, use 'scraper'. 
    If it's academic, use 'arxiv'.
    
    Return ONLY JSON: {{"tool": "tool_name", "query": "optimized_search_query"}}
    """
    
    response = await llm.ainvoke([SystemMessage(content=tool_prompt)])
    decision = json.loads(response.content.strip().replace("```json", "").replace("```", ""))
    
    # 2. Execute the chosen tool
    result = await execute_tool(decision["tool"], decision["query"])

    # 3. Update task status in the list
    for t in sub_tasks:
        if t.id == target_task.id:
            t.status = "completed"

    # 4 store Result
    new_outputs = state.get("agent_outside",{})
    new_outputs[target_task.id] ={
        "tool_used": decision["tool"],
        "content": result
    }

    return {
        "agent_outputs": new_outputs,
        "sub_tasks": state['sub_tasks'], 
        "next_node": "orchestrator"
    }