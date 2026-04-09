# 🔍 Research Agent

> Autonomous web research + structured report generation in minutes.

---

## What It Does

The Research Agent takes a topic, searches the web across multiple queries, reads relevant pages, and synthesizes everything into a clean markdown report — automatically.

**No manual googling. No copy-paste. Just answers.**

---

## Architecture

```
User Input (topic)
      │
      ▼
┌─────────────┐
│   Planner   │  ← Decides what to search and in what order
└─────────────┘
      │
      ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  web_search │ ──► │  fetch_page  │ ──► │ summarize_text│
└─────────────┘     └──────────────┘     └───────────────┘
      │                    │                     │
      └────────────────────┴─────────────────────┘
                           │
                    Accumulated Notes
                           │
                           ▼
                  ┌─────────────────┐
                  │ Report Generator│
                  └─────────────────┘
                           │
                           ▼
                   Structured Report (MD)
```

The agent runs a **ReAct loop** (Reason → Act → Observe) until it's gathered sufficient information, then switches to report-writing mode.

---

## Files

| File | Purpose |
|---|---|
| `run.py` | Entry point with CLI |
| `agents.py` | `ResearchAgent` class and ReAct loop |
| `tools.py` | `web_search`, `fetch_page`, `summarize_text` |
| `config.yaml` | Agent configuration |

---

## How to Run

```bash
# From repo root
cd templates/research-agent

# Simple run (will prompt for topic)
python run.py

# With topic argument
python run.py --topic "Future of large language models"

# Save to specific file
python run.py --topic "Renewable energy trends 2024" --output my_report.md
```

---

## Example Output

**Input:** `"Impact of AI on software development jobs"`

**Output:**
```markdown
## Executive Summary
AI tools are reshaping software development roles rather than replacing them...

## Key Findings
- 77% of developers report using AI coding assistants daily
- Productivity gains of 30-55% on repetitive coding tasks
- Demand shifting toward AI-augmented developers...

## Supporting Evidence
...

## Sources
- [GitHub Copilot Study](https://...)
- [Stack Overflow Developer Survey 2024](https://...)
```

---

## Configuration

Edit `config.yaml` to customize:

```yaml
agent:
  max_iterations: 8      # How many search/fetch cycles
  temperature: 0.2       # Lower = more factual

search:
  max_results: 5         # Results per search query

report:
  max_words_per_section: 300
```

---

## Real-World Use Cases

- **Market research** — Competitor analysis in minutes
- **Technical due diligence** — Research a technology stack
- **Content briefing** — Research before writing an article
- **Investment research** — Quick company/industry overview

---

## Extending This Template

```python
# Add a custom tool
from tools import TOOL_DEFINITIONS

def my_custom_tool(query: str) -> str:
    # Your logic here
    return result

agent._tools["my_tool"] = my_custom_tool
TOOL_DEFINITIONS.append({
    "name": "my_tool",
    "description": "...",
    "parameters": {...}
})
```
