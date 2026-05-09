import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.schema import State, SubTask
from app.core.config import settings
from app.core.telemetry import track_agent

llm = ChatOpenAI(model="gpt-4-turbo", api_key=settings.openai_api_key)

@track_agent
async def decomposition_node(state: State):
    history = state.get("messages", [])
    """
    Takes the query and breakls it into dependency graph of sub-tasks
    """
    prompt = f"""
    You are a Strategic Planning Agent.
    Break the following user query into 2-4 logical sub-tasks.

    Context: {history[-3:]} 
    Current Query: {state['query']}
    Return only a JSON list of tasks with this structure:
    [
      {{"id": "task_1", "description": "search for...", "dependencies": []}},
      {{"id": "task_2", "description": "analyze...", "dependencies": ["task_1"]}}
    ]
    """

    response = await llm.ainvoke([SystemMessage(content=prompt)])
    usage = response.response_metadata.get('token_usage', {})

    # Clean and parse the tasks
    raw_content = response.content.strip().replace("```json", "").replace("```", "")
    tasks_data = json.loads(raw_content)

    sub_tasks = [SubTask(**t) for t in tasks_data]
    current_outputs = state.get("agent_outputs", {})
    current_outputs["decomposition"] = "Plan created."

    return {
        "sub_tasks": sub_tasks,
        "next_node": "orchestrator",
        "usage": usage,
        "agent_outputs": current_outputs
    }