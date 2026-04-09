# 💻 Coding Agent

> Generate → Review → Improve. Get production-quality code automatically.

---

## What It Does

The Coding Agent implements an **iterative self-improvement loop**:

1. **Generate** — Writes initial code for your task
2. **Review** — Automatically critiques it across: correctness, quality, performance, security
3. **Improve** — Applies all feedback and rewrites the code
4. **Repeat** — Until quality threshold is met or max iterations reached

The result: code that has been reviewed and improved multiple times, automatically.

---

## Architecture

```
User Task
    │
    ▼
┌──────────────┐
│   Generate   │  ← Initial code generation
└──────────────┘
       │
       ▼
┌──────────────┐
│    Review    │  ← Score + actionable feedback
└──────────────┘
       │
  score < threshold?
       │ Yes
       ▼
┌──────────────┐
│    Improve   │  ← Apply all review suggestions
└──────────────┘
       │
       └──► back to Review
       │
  score >= threshold? → Final Code Output
```

---

## Files

| File | Purpose |
|---|---|
| `run.py` | Entry point + generate-review-improve loop |
| `reviewer.py` | Code review engine + improvement generator |

---

## How to Run

```bash
cd templates/coding-agent

# Generate and review new code
python run.py --task "Build a rate-limited HTTP client with retry logic"

# Review an existing file
python run.py --review my_script.py --task "Add proper error handling and type hints"

# Control iterations and quality threshold
python run.py --task "Fibonacci with memoization" --iterations 3 --threshold 9

# Save output to specific file
python run.py --task "CSV parser with error recovery" --output parser.py

# Generate JavaScript instead
python run.py --task "Debounce function utility" --language javascript
```

---

## Example Output

**Input:** `"Build a retry decorator for HTTP requests"`

**Iteration 1 score:** 6/10 — Missing exponential backoff, no max retries  
**Iteration 2 score:** 8/10 — Added backoff, still missing jitter  
**Iteration 3 score:** 9/10 — Production-ready ✅

**Final code:**
```python
import time
import random
import functools
from typing import Callable, Type

def retry(
    max_attempts: int = 3,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff: float = 2.0,
):
    """Retry decorator with exponential backoff and jitter."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    jitter = random.uniform(0, delay * 0.1)
                    sleep_time = min(delay + jitter, max_delay)
                    time.sleep(sleep_time)
                    delay = min(delay * backoff, max_delay)
        return wrapper
    return decorator
```

---

## Review Criteria

Every review covers:

| Dimension | What's Checked |
|---|---|
| **Correctness** | Logic bugs, edge cases, task completion |
| **Quality** | Readability, best practices, naming |
| **Performance** | Inefficiencies, complexity |
| **Security** | Injection risks, unsafe operations |

---

## Real-World Use Cases

- **Rapid prototyping** — Get working code fast
- **Code review automation** — Review your team's PRs
- **Learning** — See how code gets progressively improved
- **Legacy code refactoring** — Improve existing codebases

---

## Extending This Template

```python
# Add a custom review dimension
REVIEW_PROMPT = """...
### 7. Test Coverage
- Are there unit tests?
- What edge cases need testing?
..."""

# Add code execution to validate correctness
import subprocess
result = subprocess.run(["python", "-c", code], capture_output=True)
if result.returncode != 0:
    # Feed errors back into the improvement loop
    pass
```
