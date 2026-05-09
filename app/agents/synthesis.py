import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.schema import State
from app.core.config import settings

llm = ChatOpenAI(model="gpt-4-turbo", api_key=settings.openai_api_key)

async def synthesis_node(state: State):
    """
    Compiles all agent outputs and Chat history into a final, high-quality response.
    """
    outputs = state.get("agent_outputs", {})
    history = state.get("messages", [])
    

    prompt = f""" 
    You are a Lead Research Writer. 
    Synthesize a final response for the user.
    
    CONVERSATION HISTORY:
    {history[-5:]} # Gives the LLM context of the last few turns
    
    RESEARCH DATA (Tool Outputs): 
    {json.dumps(outputs) if outputs else "No external research was performed for this specific turn."} 
    
    USER QUERY: 
    {state['query']} 
    
    INSTRUCTIONS:
    1. If the answer is in the Conversation History (e.g., user name, preferences), use it.
    2. If the answer requires the Research Data, prioritize that.
    3. If neither contains the answer, politely ask for clarification.
    4. Ensure the response is professional and formatted with Markdown. 
    """

    response = await llm.ainvoke([SystemMessage(content=prompt)])
    usage = response.response_metadata.get('token_usage', {})

    # We return 'orchestrator' so the Master Orchestrator can 
    # verify 'final_answer' exists and then route to 'end'.
    return {
        "final_answer": response.content,
        "usage": usage,
        "next_node": "orchestrator"
    }