# 🤖 Mega_AI: Hierarchical Multi-Agent Orchestration Framework

**Mega_AI** is a high-performance, state-graph-based AI ecosystem built on **LangGraph**. It features a "Master Orchestrator" design that manages specialized worker agents, enforces strict token budgets via custom telemetry, and utilizes an "Agentic RAG" pipeline for deep research and autonomous task execution.

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

The system follows a **Supervisor-Worker** pattern where the State serves as the single source of truth.

1.  **Decomposition:** The Orchestrator breaks the user query into logical sub-tasks.
2.  **Parallel Retrieval:** Specialized tools execute sub-tasks in parallel using `asyncio.gather`.
3.  **Critique:** Results are analyzed for quality; if insufficient, the system re-routes for more data.
4.  **Synthesis:** The finalized data is condensed into a high-context response.



---

## 📂 Project Structure

```text
Mega_AI/
├── app/
│   ├── agents/             # Node Logic (Orchestrator, Retrieval, Critique)
│   ├── core/
│   │   ├── config.py       # API Settings & Pricing Tables
│   │   ├── schema.py       # LangGraph State & Reducer definitions
│   │   ├── telemetry.py    # Cost tracking & Budget enforcement decorators
│   │   └── tools.py        # Secure tool dispatcher & external API wrappers
│   └── main.py             # Compiled StateGraph & FastAPI Entry point
├── tests/                  # 15+ Logic-based test cases
├── .env                    # Environment variables (OpenAI, Tavily, etc.)
└── conftest.py             # Pytest root configuration

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