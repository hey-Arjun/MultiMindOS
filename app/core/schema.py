from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SubTask(BaseModel):
    id: str
    description: str
    dependencies: List[str]
    status: str = "pending"   #pending, completed, failed

class State(BaseModel):
    query: str
    context_window_budget: int = 4000
    used_tokens: int = 0
    sub_tasks: List[SubTask] = []
    agent_outputs: Dict[str, Any] = {}
    tool_logs: List[Dict[str,Any]] = []
    final_answer: Optional[str] = None
    provenance_map: Dict[str, Any] = {}
    errors: List[str] = []