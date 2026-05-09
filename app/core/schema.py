import operator
from typing import Annotated, List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class SubTask(BaseModel):
    id: str
    description: str
    dependencies: List[str]
    status: str = "pending"

class State(TypedDict):
    query: str
    messages: Annotated[List[BaseMessage], add_messages]
    sub_tasks: Annotated[List[SubTask], operator.add] 
    agent_outputs: Annotated[Dict[str, Any], operator.ior]
    next_node: str 
    used_tokens: int
    context_window_budget: int
    final_answer: Optional[str]