import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.schema import State
from app.core.config import settings
from app.core.telemetry import track_agent

llm = ChatOpenAI(model="gpt-4-turbo", api_key=settings.openai_api_key)

@track_agent
async def critique_node(state: State):
    """
    Evaluates the gathered data for hallucinations, contradictions, and confidence.
    """
    retrieved_data = state.get("agent_outputs", {})

    prompt = f"""
    You are a Fact-Checking & Critique Agent.
    Review the gathered information for the query: "{state['query']}"
    
    Gathered Data: {json.dumps(retrieved_data)}

    Evaluate the following:
    1. Confidence Score: A float between 0.0 and 1.0 (0.2 for wild claims, 0.9 for verified facts).
    2. Contradictions: Are there conflicting numbers or statements?
    3. Next Action: If data is poor, suggest 'retrieval'. If good, 'synthesis'.

    Return ONLY JSON:
    {{
      "confidence_score": 0.0,
      "contradictions": ["list", "of", "conflicts"],
      "assessment": "pass/fail", 
      "feedback": "detailed reasoning", 
      "next_action": "synthesis/retrieval"
    }}
    """

    response = await llm.ainvoke([SystemMessage(content=prompt)])
    usage = response.response_metadata.get('token_usage', {})
    
    # Clean and Parse
    clean_content = response.content.strip().replace("```json", "").replace("```", "")
    critique_data = json.loads(clean_content)

    # Prepare return state
    # We store the whole object so the test can access confidence_score and contradictions
    return {
        "agent_outputs": {
            "critique_report": critique_data 
        },
        "usage": usage,
        "next_node": "orchestrator" if critique_data["next_action"] == "retrieval" else "synthesis"
    }