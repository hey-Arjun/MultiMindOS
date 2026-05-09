# 🤖 MultiMind O.S: Hierarchical Multi-Agent Orchestration Framework

**MultiMind O.S** is a high-performance, state-graph-based AI ecosystem built on **LangGraph**. It features a "Master Orchestrator" design that manages specialized worker agents, enforces strict token budgets via custom telemetry, and utilizes an "Agentic RAG" pipeline for deep research and autonomous task execution.

---

## 🌟 Core Features

*   **Master Orchestrator Logic:** A central "brain" using GPT-4 Turbo that handles decomposition, routing, and synthesis with an "Exit-First" logic to prevent infinite loops.
*   **State-Graph Architecture:** Built with LangGraph for persistent state management, ensuring seamless data flow between parallel research tasks.
*   **Production Telemetry (`pytrackio`):** Custom `@track_agent` decorators that:
    *   Monitor real-time token consumption.
    *   Calculate operational costs based on model-specific pricing.
    *   Enforce **Hard Halts** and **Context Compression** when budgets are exceeded.
*   **Secure Parallel Retrieval:** An asynchronous tool dispatcher that runs multiple sub-tasks (Web Search, Arxiv, etc.) simultaneously while filtering for SQL injection and prompt-leaking attempts.
*   **Critique-Loop Integration:** A dedicated critique node that reviews gathered data for accuracy and completeness before synthesizing the final response.

---

## 🏗️ System Architecture
The agents/ directory is the core of your multi-agent system. Each file represents a specific "node" in your LangGraph workflow.

1. orchestrator.py (The Master Controller)

This is the central supervisor. It doesn't perform tasks itself; it analyzes the current State to decide the next move.

Logic: Uses a high-reasoning model (like GPT-4o) to check if the current data in agent_outputs is sufficient to answer the query.

Routing: It returns the next_node string, directing the graph to either start searching, critique existing data, or finish the run.

2. decomposition.py (The Planner)

When the Orchestrator decides research is needed, it hands off to this node.

Logic: Breaks a complex user query into smaller, manageable "sub-tasks."

Output: Generates a list of task objects (ID, description, tool type) that the Retrieval node can execute.

3. retrieval.py (The Executor)

This is where the "hands-on" work happens.

Logic: It iterates through the sub_tasks created by the planner. It uses asyncio.gather to run multiple tools (like Web Search, Arxiv, or PDF Parsers) in parallel.

Role: Updates the state with raw information while reporting any tool failures back to the system.

4. critique.py (The Auditor)

A specialized node for quality assurance.

Logic: It reviews the raw data gathered in the Retrieval phase. It looks for hallucinations, missing information, or contradictions.

Decision: It provides a "Critique Report." If the report is negative, the Orchestrator can loop back to Retrieval to fill the gaps.

5. synthesis.py (The Communicator)

The final step before the user receives an answer.

Logic: Takes all verified data from the critique and retrieval steps and condenses it into a clear, natural language response.

Constraints: Ensures the tone matches the user's style and that all sources are properly cited.

6. graph.py (The Architect)

This file doesn't contain agent logic; it contains the plumbing.

Logic: It defines the StateGraph. It adds the nodes from the files above and sets the Edges (the paths between nodes) and Conditional Edges (logic-based jumps).

Output: Compiles the graph into an executable "app" used by main.py.

---

## 📂 Project Structure

```text
MultiMind OS/
├── app/
│   ├── agents/               # 🧠 THE BRAIN: Node logic and Graph construction
│   │   ├── decomposition.py  # Task planning & query breaking
│   │   ├── retrieval.py      # Tool execution & data gathering
│   │   ├── critique.py       # Quality control & validation
│   │   ├── synthesis.py      # Final answer generation
│   │   ├── orchestrator.py   # Master routing & decision logic
│   │   └── graph.py          # StateGraph compilation & edge definitions
│   |
│   ├── core/                 # Shared utilities & system configurations
│   │   ├── schema.py         # State TypedDict & Reducers
│   │   ├── telemetry.py      # Budgeting & Token tracking
│   │   ├── tools.py          # Secure tool dispatcher
│   │   └── config.py         # ENV management
│   ├── db/                   # Database connections (SQLAlchemy/Session)
│   └── main.py               # Application entry point
├── tests/                    # Unit, Integration, and Mock tests
├── Dockerfile                # Containerization config
├── docker-compose.yml        # Local multi-service orchestration
├── requirements.txt          # Python dependencies
└── conftest.py               # Pytest root configuration

```

## 🚀 Installation & Setup
1. Prerequisites

Python 3.11+

OpenAI API Key (for GPT-4 Turbo)

Tavily or Arxiv API keys (for retrieval tools)

2. Installation

```bash
# Clone the repository
git clone git@github.com:hey-Arjun/MultiMindOS.git
cd Mega_AI

# Setup Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

3. Configure Environment

Create a .env file in the root directory:

```bash
OPENAI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
TOKEN_BUDGET=0.05
```

## 🧪 Testing Suite

The project includes a robust testing framework split into 5 critical domains:
```bash
# Set PYTHONPATH to root
export PYTHONPATH=.

# Run all the test modules
pytest tests/ -v 
```

## 🛡️ Security & Guardrails

SQL Injection Blocker: The execute_tool dispatcher rejects queries containing malicious keywords like DROP TABLE or DELETE FROM.

Budget Guard: Defined in the telemetry layer, the system automatically triggers a CONTEXT_OVERFLOW termination if the used credits exceed the user-defined metadata["budget"].

Response Validation: The Orchestrator enforces a JSON-only response format from the LLM, reducing parsing errors by 90%.