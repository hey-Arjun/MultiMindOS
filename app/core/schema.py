from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, TypedDict

class SubTask(BaseModel):
    id: str
    description: str
    dependencies: List[str]
    status: str = "pending"   #pending, completed, failed

class State(TypedDict):
    query: str
    sub_tasks: List[SubTask]
    agent_outputs: Dict[str, Any]
    next_node: str  # This is for routing
    used_tokens: int
    context_window_budget: int
    final_answer: Optional[str]