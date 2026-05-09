import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.schema import State
from app.core.config import settings
from typing import Dict, Any

llm = ChatOpenAI(
    model="gpt-4-turbo", 
    api_key=settings.openai_api_key,
    model_kwargs={"response_format": {"type": "json_object"}} # Force JSON mode at provider level
)

async def orchestrator_node(state: State) -> Dict[str, Any]:
    """
    Master Orchestrator: Controls the flow of the Graph.
    Fixes: Infinite loops, missing critique step, and state synchronization.
    """
    
    # 1. IMMEDIATE EXIT CHECK (The "Loop Killer")
    # If synthesis already produced a final answer, we terminate immediately.
    if state.get("final_answer"):
        print("--- ORCHESTRATOR: Final answer detected. Routing to END. ---")
        return {"next_node": "end"}

    # 2. STATE EXTRACTION & DEDUPLICATION
    query = state.get("query", "")
    agent_outputs = state.get("agent_outputs", {})
    history = state.get("messages", [])
    
    # Clean sub-tasks to ensure we only look at unique IDs
    seen_ids = set()
    unique_tasks = []
    for task in reversed(state.get("sub_tasks", [])):
        if task.id not in seen_ids:
            unique_tasks.append(task)
            seen_ids.add(task.id)
    sub_tasks = list(reversed(unique_tasks))
    
    # Check what milestones we have hit
    has_tasks = len(sub_tasks) > 0
    all_tasks_completed = has_tasks and all(
        t.id in agent_outputs or t.status == "completed" for t in sub_tasks
    )
    has_critique = "critique_report" in agent_outputs

    # 3. CONSTRUCT ENFORCED ROUTING PROMPT
    prompt = f"""
    You are the Master Orchestrator for an AI Research Graph.
    Your job is to look at the current state and decide the EXACT next node.

    USER QUERY: {query}
    
    CONVERSATION HISTORY:
    {[m.content for m in history[-3:]]}

    CURRENT PROGRESS:
    - Sub-tasks Created: {has_tasks} ({[t.id for t in sub_tasks]})
    - Research Data Gathered: {list(agent_outputs.keys())}
    - All Tasks Done: {all_tasks_completed}
    - Critique Performed: {has_critique}

    STRICT ROUTING RULES:
    1. If the query is conversational (greeting, name, simple preference) and history has the info -> 'synthesis'.
    2. If no sub-tasks exist for a complex research query -> 'decomposition'.
    3. If sub-tasks exist but research data is missing/incomplete -> 'retrieval'.
    4. If research data is gathered BUT 'critique_report' is NOT in Data -> 'critique'.
    5. If data is gathered AND critiqued -> 'synthesis'.
    6. If a 'final_answer' was already generated (checked by system) -> 'end'.

    Return ONLY JSON:
    {{
        "reasoning": "Explain why you chose the next node based on the rules.",
        "next": "decomposition" | "retrieval" | "critique" | "synthesis" | "end"
    }}
    """

    # 4. INVOKE LLM
    try:
        response = await llm.ainvoke([SystemMessage(content=prompt)])
        usage = response.response_metadata.get('token_usage', {})
        
        # Robust Cleaning
        raw_content = response.content.strip()
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_content:
            raw_content = raw_content.split("```")[1].split("```")[0].strip()
            
        decision = json.loads(raw_content)
    except Exception as e:
        print(f"--- ORCHESTRATOR ERROR: {str(e)}. Defaulting to safety path. ---")
        # Safety fallback
        if all_tasks_completed:
            return {"next_node": "critique" if not has_critique else "synthesis"}
        return {"next_node": "decomposition"}

    # 5. LOGGING & FINAL VALIDATION
    next_node = decision.get("next", "end")
    print(f"--- ORCHESTRATOR REASONING: {decision.get('reasoning')} ---")
    print(f"--- ROUTING TO: {next_node} ---")

    # Final safety check to prevent invalid node names
    allowed = ["decomposition", "retrieval", "critique", "synthesis", "end"]
    if next_node not in allowed:
        next_node = "end"

    return {
        "next_node": next_node,
        "usage": usage
    }