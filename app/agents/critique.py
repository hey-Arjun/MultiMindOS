import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.schema import State
from app.core.config import settings

llm = ChatOpenAI(model="gpt-4-turbo", api_key=settings.openai_api_key)

async def critique_node(state: State):
    """
    Evaluates the quality of retrieved data and the logic of the plan.
    """
    retrieved_data = state.get("agent_outputs", {})

    prompt =f"""
    You are fact checking & critique Agent.
    Review the following gathered information for the query: "{state['query']}"
    Gathered Data: {json.dumps(retrieved_data)}

    Is this information sufficient, accurate, and relevant? 
    If yes, suggest 'synthesis'.
    If no, suggest 'retrieval' and explain what is missing.

    Return ONLY JSON:
    {{"assessment": "pass/fail", "feedback": "reasoning", "next_action": "synthesis/retrieval"}}
    """

    response = await llm.ainvoke([SystemMessage(content=prompt)])
    clean_content = response.content.strip().replace("```json", "").replace("```", "")
    critique = json.loads(clean_content)

    # Store the critique in the state so synthesis can see it
    new_outputs = state.get("agent_outputs", {})
    new_outputs["critique_report"] = critique["feedback"]

    return {
        "agent_outputs": new_outputs,
        "next_node": "orchestrator" if critique["next_action"] == "retrieval" else "synthesis"
    }