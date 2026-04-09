<div align="center">

# 🤖 Agentic AI Templates

### Production-ready AI agents you can copy, run, and scale.

[![GitHub Stars](https://img.shields.io/github/stars/DharminJoshi/agentic-ai-templates?style=for-the-badge&color=FFD700)](https://github.com/DharminJoshi/agentic-ai-templates)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-Compatible-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)

**Built by [Dharmin Joshi (DevKay)](https://github.com/DharminJoshi)**

*Stop reinventing the wheel. Start shipping agents.*

</div>

---

## 🔥 What Is This?

A curated collection of **battle-tested, production-ready Agentic AI templates** built with Python and LLMs. Each template is:

- ✅ **Immediately runnable** — clone, configure, run
- ✅ **Modular** — swap out components to fit your use case
- ✅ **Well-documented** — understand what's happening and why
- ✅ **Real-world focused** — not toy demos, actual useful agents

---

## 📂 Templates

| Template | Description | Difficulty | Use Case |
|---|---|---|---|
| 🔍 [Research Agent](./templates/research-agent/) | Web search + structured report generation | Beginner | Market research, topic analysis |
| 📚 [RAG Agent](./templates/rag-agent/) | Document ingestion + semantic Q&A | Intermediate | Knowledge bases, document Q&A |
| 💻 [Coding Agent](./templates/coding-agent/) | Code generation + iterative review loop | Intermediate | Dev automation, code assistance |
| 🧠 [Multi-Agent System](./templates/multi-agent-system/) | Planner → Executor → Critic pipeline | Advanced | Complex task automation |

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/DharminJoshi/agentic-ai-templates.git
cd agentic-ai-templates

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run a template
python templates/research-agent/run.py
```

---

## 🧩 Architecture Overview

Every template follows a clean, predictable agent loop:

```
┌─────────────────────────────────────────────────────────┐
│                   AGENT LIFECYCLE                        │
│                                                          │
│   Input ──► Planner ──► Tool Selection ──► Execution    │
│               ▲                                  │       │
│               │                                  ▼       │
│           Feedback ◄────── Critic ◄────── Output        │
└─────────────────────────────────────────────────────────┘
```

### Core Concepts

**🔄 ReAct Loop** (Reason + Act)
```
Thought → Action → Observation → Thought → ... → Final Answer
```

**🧠 Tool Use Pattern**
```python
agent.tools = [search_tool, calculator, code_runner]
agent.run("Research the top 5 AI papers from 2024")
```

**🔁 Multi-Agent Orchestration**
```
User Query
    │
    ▼
┌──────────┐    task list    ┌──────────┐
│  Planner │ ─────────────► │ Executor │
└──────────┘                └──────────┘
                                  │
                             results │
                                  ▼
                           ┌──────────┐
                           │  Critic  │ ──► Final Output
                           └──────────┘
                                  │
                         needs improvement?
                                  │
                                  └──► back to Executor
```

---

## 🚀 Features

- **🧩 Modular Design** — Each component is independently swappable
- **🔌 LLM Agnostic** — Works with OpenAI, Anthropic, or local models
- **📦 Minimal Dependencies** — Only what you need
- **📖 Inline Documentation** — Every function is explained
- **🔒 Environment-based Config** — No hardcoded secrets

---

## 🎯 Why This Repo?

Building AI agents from scratch is repetitive. You always need:

1. A way to give the LLM tools
2. A loop to iterate until task completion
3. Memory to maintain context
4. Structured output parsing

These templates solve all of that — so you can **focus on your actual use case**, not the plumbing.

---

## 📁 Repository Structure

```
agentic-ai-templates/
├── templates/
│   ├── research-agent/       # Search + summarize agent
│   ├── rag-agent/            # Document Q&A agent
│   ├── coding-agent/         # Code generation + review
│   └── multi-agent-system/   # Planner-Executor-Critic
├── assets/
│   └── diagrams/             # Architecture visuals
├── docs/                     # Extended documentation
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🛠️ Requirements

- Python 3.10+
- OpenAI API key (or compatible endpoint)
- See `requirements.txt` for full list

---

## 🤝 Contributing

Contributions are welcome! Have an agent template you've built? Open a PR.

1. Fork the repo
2. Create your branch: `git checkout -b feat/my-agent`
3. Add your template in `templates/your-agent-name/`
4. Include a `README.md` following the existing format
5. Open a pull request

---

## 📄 License

MIT [LICENSE](LICENSE) — use it, modify it, ship it.

---

<div align="center">

Built with ❤️ by **[Dharmin Joshi (DevKay)](https://github.com/DharminJoshi)**

⭐ **Star this repo if you found it useful** — it helps others discover it!

</div>
