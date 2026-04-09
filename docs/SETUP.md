# Setup Guide

Step-by-step setup for all templates.

---

## Prerequisites

| Requirement | Version | Check |
|---|---|---|
| Python | 3.10+ | `python --version` |
| pip | latest | `pip --version` |
| OpenAI API key | — | [platform.openai.com](https://platform.openai.com) |

---

## Installation

```bash
# Clone the repo
git clone https://github.com/DharminJoshi/agentic-ai-templates.git
cd agentic-ai-templates

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Environment Configuration

```bash
# Copy the example env file
cp .env.example .env

# Open and edit it
nano .env   # or use your editor
```

**Minimum required:**
```env
OPENAI_API_KEY=sk-your-key-here
```

**Optional but recommended:**
```env
OPENAI_MODEL=gpt-4o          # or gpt-4o-mini for lower cost
TEMPERATURE=0.2               # lower = more deterministic
MAX_ITERATIONS=8              # max agent loop iterations
```

---

## Running Each Template

### Research Agent
```bash
cd templates/research-agent
python run.py --topic "Future of quantum computing"
```

### RAG Agent
```bash
cd templates/rag-agent

# First, ingest your documents
python run.py --ingest /path/to/your/document.pdf

# Then ask questions
python run.py --ask "What are the main conclusions?"

# Or interactive mode
python run.py --interactive
```

### Coding Agent
```bash
cd templates/coding-agent
python run.py --task "Build a CSV parser with validation"
```

### Multi-Agent System
```bash
cd templates/multi-agent-system
python run.py --goal "Research the top 3 AI frameworks for production"
```

---

## Cost Estimates

Using GPT-4o (as of 2024 pricing):

| Template | Typical Cost Per Run |
|---|---|
| Research Agent | $0.05 – $0.25 |
| RAG Agent (ingest 10-page PDF) | $0.01 – $0.05 |
| RAG Agent (query) | $0.01 – $0.03 |
| Coding Agent | $0.03 – $0.15 |
| Multi-Agent System | $0.10 – $0.50 |

**Tip:** Use `OPENAI_MODEL=gpt-4o-mini` during development to cut costs by ~10x.

---

## Using Alternative LLMs

### Anthropic Claude
```env
OPENAI_BASE_URL=https://api.anthropic.com/v1
OPENAI_API_KEY=sk-ant-your-key
OPENAI_MODEL=claude-sonnet-4-20250514
```

### Local Models (Ollama)
```bash
# Install ollama and pull a model
ollama pull llama3.1

# Configure env
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3.1
```

Note: Local models may produce less reliable tool-use and JSON parsing.

---

## Troubleshooting

**`ModuleNotFoundError`**
```bash
pip install -r requirements.txt
# Make sure your venv is activated
```

**`OPENAI_API_KEY not set`**
```bash
# Make sure .env exists and has your key
cat .env | grep OPENAI_API_KEY
```

**`RateLimitError`**
- You've hit OpenAI's rate limits. Wait 60 seconds and retry.
- Consider `gpt-4o-mini` which has higher rate limits.

**ChromaDB errors (RAG Agent)**
```bash
# Reset the vector store
rm -rf templates/rag-agent/data/chroma
# Then re-ingest your documents
```
