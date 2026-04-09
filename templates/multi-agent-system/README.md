# 🧠 Multi-Agent System

> Decompose complex goals into tasks. Execute. Critique. Improve. Synthesize.

---

## What It Does

The Multi-Agent System handles goals too complex for a single agent. It uses three specialized agents in a collaborative loop:

- **🗺️ Planner** — Breaks down the goal into ordered, concrete sub-tasks
- **⚙️ Executor** — Completes each task using tools (search, fetch, summarize)
- **🎯 Critic** — Evaluates quality, identifies gaps, triggers re-planning if needed

The loop runs until the Critic is satisfied or max iterations are reached, then synthesizes everything into a polished final output.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT LOOP                          │
│                                                             │
│   Goal                                                      │
│    │                                                        │
│    ▼                                                        │
│  ┌──────────┐    task list    ┌──────────┐                  │
│  │ Planner  │ ─────────────► │ Executor │                  │
│  └──────────┘                └──────────┘                  │
│       ▲                           │                        │
│       │                      results                       │
│       │                           │                        │
│       │                           ▼                        │
│       │                    ┌──────────┐                    │
│       │    revise plan     │  Critic  │                    │
│       └────────────────────└──────────┘                    │
│                                   │                        │
│                             satisfied?                     │
│                                   │ Yes                    │
│                                   ▼                        │
│                           Final Synthesis                  │
└─────────────────────────────────────────────────────────────┘
```

### Agent Roles

| Agent | Responsibility | Key Skill |
|---|---|---|
| **Planner** | Goal decomposition | Strategic thinking |
| **Executor** | Task completion | Tool use + research |
| **Critic** | Quality evaluation | Critical assessment |

---

## Files

| File | Agent | Purpose |
|---|---|---|
| `planner.py` | Planner | Goal decomposition, plan revision |
| `executor.py` | Executor | Task execution with tools |
| `critic.py` | Critic | Evaluation + synthesis |
| `run.py` | Orchestrator | Runs the full loop |

---

## How to Run

```bash
cd templates/multi-agent-system

# Run with a goal (will prompt if not provided)
python run.py

# Provide goal directly
python run.py --goal "Research the top 5 AI companies and their latest products"

# More iterations for complex goals
python run.py --goal "Create a competitive analysis of cloud AI platforms" --iterations 4

# Save output to file
python run.py --goal "Summarize the state of quantum computing in 2024" --output analysis.md
```

---

## Example Run

**Goal:** `"Research and compare the top 3 vector databases for production use"`

```
📋 Plan:
  [1] Research vector database landscape
  [2] Deep-dive: Pinecone capabilities and pricing
  [3] Deep-dive: Weaviate capabilities and pricing
  [4] Deep-dive: Qdrant capabilities and pricing
  [5] Synthesize comparison table

── Cycle 1 ──────────────────────────────────────────

⚙️ Executing: Research vector database landscape
✅ Task 1: Found 8 major vector DBs, top 3 by adoption: Pinecone, Weaviate, Qdrant

⚙️ Executing: Deep-dive: Pinecone
✅ Task 2: Pinecone — managed, serverless tier, $0.096/hr for p1-x1...

[...tasks 3 and 4...]

🎯 Critic: COMPLETE (score: 9/10)
✅ Satisfied — synthesizing final output.

── Final Output ─────────────────────────────────────
# Vector Database Comparison: Pinecone vs Weaviate vs Qdrant
...
```

---

## Real-World Use Cases

- **Market research reports** — Multi-source research with structured output
- **Due diligence** — Research a company across multiple dimensions
- **Content creation** — Research → outline → draft → refine
- **Competitive intelligence** — Analyze multiple competitors systematically
- **Technical evaluations** — Compare tools, frameworks, or approaches

---

## How the Critic Works

The Critic evaluates output on:

```
VERDICT: COMPLETE | NEEDS_IMPROVEMENT | FAILED
SCORE: 1-10
GAPS:
  - Missing pricing comparison
  - No mention of self-hosted options
FEEDBACK: The analysis covers features well but lacks...
```

If `VERDICT != COMPLETE` and `SCORE < 8`, the Critic's feedback is fed back to the Planner, which creates new tasks to fill the gaps.

---

## Extending This Template

```python
# Add a new specialized agent role
class FactCheckerAgent:
    """Verifies claims made by the executor."""
    def verify(self, claim: str, source: str) -> bool:
        ...

# Add memory across cycles
from collections import defaultdict
agent_memory = defaultdict(list)
agent_memory["executor"].append({"task": task.title, "result": result})

# Add parallel task execution
import asyncio
async def execute_parallel(tasks, context):
    return await asyncio.gather(*[execute_task_async(t, context) for t in tasks])
```

---

## Tips for Best Results

- **Be specific** with your goal — vague goals produce vague plans
- **Use 2-3 cycles** for most tasks; 4+ for very complex research
- **Check task dependencies** — the Planner respects them, so order matters
- **Lower temperature** in Planner and Critic for more consistent behavior
