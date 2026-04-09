# Contributing to Agentic AI Templates

First off — thank you for considering a contribution! This project grows through community input.

---

## Ways to Contribute

- **New templates** — Have a useful agent pattern? Add it.
- **Bug fixes** — Found something broken? Fix it.
- **Documentation** — Improve explanations, add examples.
- **Tool additions** — New tools that work across multiple templates.

---

## Adding a New Template

### Directory Structure

```
templates/your-agent-name/
├── run.py          # Entry point with CLI
├── agent.py        # Core agent logic
├── tools.py        # Tools specific to this agent (if any)
└── README.md       # Required — see format below
```

### README Format

Your template README must include:

1. **What It Does** — One paragraph max
2. **Architecture** — ASCII diagram of the agent flow
3. **Files** — Table of files and their purposes
4. **How to Run** — Copy-paste ready commands
5. **Example Output** — Real example input/output
6. **Real-World Use Cases** — 3-5 concrete examples
7. **Extending This Template** — Code snippets for customization

### Code Standards

- Type hints on all functions
- Docstrings on all public functions and classes
- Error handling — never let uncaught exceptions crash silently
- Use `rich` for console output (already a dependency)
- Read config from environment variables, not hardcoded values
- Test your template end-to-end before submitting

---

## Pull Request Process

1. Fork the repo
2. Create a branch: `git checkout -b feat/my-agent-name`
3. Write your template following the standards above
4. Update the root `README.md` templates table
5. Open a PR with a clear description of what your agent does

---

## Code Style

- Follow PEP 8
- Max line length: 100 characters
- Use dataclasses for structured data
- Prefer explicit over implicit

```python
# Good
def generate_code(task: str, language: str = "python") -> str:
    """Generate code for a given task."""
    ...

# Avoid
def gen(t, l="python"):
    ...
```

---

## Questions?

Open an issue with the `question` label. We're happy to help.
