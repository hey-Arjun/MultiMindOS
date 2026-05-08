import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.schema import State
from app.core.config import settings
from typing import Dict, Any

llm = ChatOpenAI(
    model="gpt-4-turbo", 
    api_key=settings.openai_api_key
)

async def orchestrator_node(state: State) -> Dict[str, Any]:
    """
    Master Orchestrator: Logic for dynamic routing with structured reasoning.
    Controls the flow between Decomposition, Retrieval, Critique, and Synthesis.
    """
    # 1. Extract state information
    query = state.get("query", "")
    sub_tasks = state.get("sub_tasks", [])
    agent_outputs = state.get("agent_outputs", {})
    outputs_keys = list(agent_outputs.keys())
    
    # Check if a final answer has already been produced to prevent infinite loops
    has_final_answer = True if state.get("final_answer") else False

    # 2. Construct the prompt with EXPLICIT instruction blocks
    prompt = f"""
    You are a Master Orchestrator for an Agentic RAG system.
    Your job is to examine the current state and decide the next logical step.

    CORE ROUTING RULES:
    1. If there are no 'Current Sub-tasks', you MUST go to 'decomposition'.
    2. If there are pending sub-tasks and the 'Outputs Gathered' is missing data for them, go to 'retrieval'.
    3. If all data is gathered but 'Final Answer Present' is False, you MUST go to 'synthesis' to create the final report.
    4. Only go to 'critique' if the gathered data seems contradictory or insufficient.
    5. ONLY route to 'end' if 'Final Answer Present' is True.

    CURRENT STATE:
    - User Query: {query}
    - Current Sub-tasks: {sub_tasks}
    - Outputs Gathered: {outputs_keys}
    - Final Answer Present: {has_final_answer}

    Return ONLY a JSON object:
    {{
        "reasoning": "Explain why you are choosing the next node based on the rules.",
        "next": "decomposition" | "retrieval" | "critique" | "synthesis" | "end"
    }}
    """

    # 3. Invoke LLM
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    
    # 4. Clean and Parse JSON
    raw_content = response.content.strip()
    if raw_content.startswith("```"):
        raw_content = raw_content.strip("`").replace("json", "", 1).strip()
    
    try:
        decision = json.loads(raw_content)
    except json.JSONDecodeError:
        print(f"--- ORCHESTRATOR ERROR: Failed to parse JSON from {raw_content} ---")
        # Fallback safety: if it's almost done, try to synthesize; otherwise, end.
        return {"next_node": "synthesis" if outputs_keys else "end"}

    # 5. Log Reasoning for transparency
    print(f"--- ORCHESTRATOR LOG: {decision.get('reasoning')} ---")
    
    # 6. Final safety check on the node name
    next_node = decision.get("next", "end")
    allowed_nodes = ["decomposition", "retrieval", "critique", "synthesis", "end"]
    
    if next_node not in allowed_nodes:
        next_node = "end"

    return {"next_node": next_node}