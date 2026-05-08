import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.schema import State
from app.core.config import settings

llm = ChatOpenAI(model="gpt-4-turbo", api_key=settings.openai_api_key)

async def synthesis_node(state: State):
    """
    Compiles all agent outputs into a final, high-quality response.
    """
    outputs = state.get("agent_outputs", {})
    
    if not outputs:
        return {
            "final_answer": "I'm sorry, I couldn't gather enough data to provide a comparison.",
            "next_node": "orchestrator"
        }

    prompt = f"""
    You are a Lead Research Writer. 
    Synthesize a final report based on the following:
    
    Original Query: {state['query']}
    Research Data: {json.dumps(outputs)}
    
    Ensure the response is professional, formatted with Markdown, 
    cited (if links exist), and directly addresses the user's intent.
    """

    response = await llm.ainvoke([SystemMessage(content=prompt)])

    # We return 'orchestrator' so the Master Orchestrator can 
    # verify 'final_answer' exists and then route to 'end'.
    return {
        "final_answer": response.content,
        "next_node": "orchestrator"
    }