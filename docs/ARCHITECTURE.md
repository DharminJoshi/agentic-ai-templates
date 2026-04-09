# Architecture Guide

A deep dive into the agent patterns used across all templates.

---

## Core Pattern: The ReAct Loop

All agents in this repo follow the **ReAct** pattern (Reason + Act):

```
Thought: "I need to find information about X"
Action: web_search("X")
Observation: [search results]
Thought: "The results mention Y, I should look deeper"
Action: fetch_page("url of Y")
Observation: [page content]
...
Thought: "I have enough information"
Final Answer: [structured output]
```

This loop continues until the agent decides it has enough information, or hits the `max_iterations` limit.

---

## Tool Use Architecture

Tools are defined with OpenAI function-calling schemas:

```python
{
    "name": "web_search",
    "description": "Search the web for information",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "max_results": {"type": "integer"}
        },
        "required": ["query"]
    }
}
```

The LLM decides **when** and **which** tool to call. Your code executes it and returns the result. This separation of concerns keeps the code clean.

---

## Memory Architecture

### Short-term Memory (In-context)
All templates maintain conversation history as the message array:

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": task},
    {"role": "assistant", "content": "...", "tool_calls": [...]},
    {"role": "tool", "content": tool_result},
    # ... grows as agent acts
]
```

### Long-term Memory (Vector Store)
The RAG agent uses ChromaDB for persistent semantic memory across sessions.

---

## Multi-Agent Communication

Agents communicate through **shared state** (a Python dict):

```python
# Planner creates the plan
plan = Plan(goal=goal, tasks=[...])

# Executor updates tasks and stores results
task.status = "done"
task.result = result
all_results[task.id] = result

# Critic reads all results
critic_result = evaluate(goal, all_results)

# Planner reads critic feedback and revises
plan = revise_plan(plan, critic_result.feedback)
```

No message queues, no async complexity — just clean Python data structures.

---

## Design Principles

### 1. Minimal Abstractions
Each template uses vanilla Python and direct API calls. No hidden magic.

### 2. Composability
Tools from one template can be imported by another:
```python
from templates.research_agent.tools import web_search
```

### 3. Graceful Degradation
Every template has fallbacks for API failures, parsing errors, and tool timeouts.

### 4. Observability
`rich` library provides real-time logging of every agent action so you always know what's happening.

---

## Extending Templates

### Adding a New Tool

```python
# 1. Define the function
def calculator(expression: str) -> str:
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

# 2. Add the schema
TOOL_DEFINITIONS.append({
    "name": "calculator",
    "description": "Evaluate a mathematical expression",
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {"type": "string"}
        },
        "required": ["expression"]
    }
})

# 3. Register it in the agent's tool map
agent._tools["calculator"] = calculator
```

### Swapping the LLM

All templates read from environment variables:

```bash
# Use Claude instead of GPT
OPENAI_BASE_URL=https://api.anthropic.com/v1
OPENAI_API_KEY=sk-ant-...
OPENAI_MODEL=claude-sonnet-4-20250514
```

Or switch to a local model:
```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1
```

---

## Performance Considerations

| Template | Avg. API Calls | Avg. Latency |
|---|---|---|
| Research Agent | 10-20 | 30-90s |
| RAG Agent (ingest) | N × chunks | 60-300s |
| RAG Agent (query) | 2-3 | 5-15s |
| Coding Agent | 6-12 | 20-60s |
| Multi-Agent System | 20-50 | 60-180s |

Use `gpt-4o-mini` for development to reduce costs during iteration.
