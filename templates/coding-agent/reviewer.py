"""
reviewer.py — Coding Agent Review Engine
──────────────────────────────────────────
Provides automated code review for generated or
submitted code, with actionable improvement suggestions.
"""

import os
from dataclasses import dataclass

from openai import OpenAI
from rich.console import Console

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

REVIEW_PROMPT = """You are a senior software engineer conducting a thorough code review.

Analyze the following code and provide structured feedback:

## Code to Review
```{language}
{code}
```

## Original Task
{task}

Review it across these dimensions:

### 1. Correctness
- Does it solve the task?
- Are there logic bugs or edge cases?

### 2. Code Quality
- Is it readable and well-structured?
- Does it follow best practices for {language}?

### 3. Performance
- Any obvious inefficiencies?
- Time/space complexity concerns?

### 4. Security (if applicable)
- Any injection risks, unsafe operations?

### 5. Suggested Improvements
List specific, actionable improvements as:
IMPROVE: <what to change> → <why>

### 6. Overall Score
Score out of 10 and one-line summary.

Be direct and specific. Code review should be actionable, not vague.
"""

IMPROVE_PROMPT = """You are an expert {language} developer. 
Improve the following code based on the review feedback provided.

## Original Code
```{language}
{code}
```

## Review Feedback
{feedback}

## Task
{task}

Provide the improved, complete code. Do not truncate or skip sections.
Only output the code — no explanation, no markdown fences.
"""


@dataclass
class ReviewResult:
    """Result of a code review."""
    feedback: str
    score: int
    improvements: list[str]
    passed: bool  # True if score >= threshold


def review_code(code: str, task: str, language: str = "python") -> ReviewResult:
    """
    Review code against the original task.

    Args:
        code: The code to review.
        task: The original task/requirement.
        language: Programming language.

    Returns:
        ReviewResult with feedback and score.
    """
    console.log(f"[cyan]🔍 Reviewing {language} code...[/cyan]")

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.1,
        messages=[
            {
                "role": "user",
                "content": REVIEW_PROMPT.format(
                    language=language,
                    code=code,
                    task=task,
                ),
            }
        ],
        max_tokens=1500,
    )

    feedback = response.choices[0].message.content.strip()

    # Parse score from feedback
    score = 7  # Default
    for line in feedback.split("\n"):
        if "score" in line.lower() and "/" in line:
            try:
                score = int(line.split("/")[0].split()[-1])
            except (ValueError, IndexError):
                pass

    # Extract IMPROVE suggestions
    improvements = [
        line.replace("IMPROVE:", "").strip()
        for line in feedback.split("\n")
        if line.startswith("IMPROVE:")
    ]

    return ReviewResult(
        feedback=feedback,
        score=score,
        improvements=improvements,
        passed=score >= 7,
    )


def improve_code(
    code: str,
    feedback: str,
    task: str,
    language: str = "python",
) -> str:
    """
    Generate an improved version of code based on review feedback.

    Args:
        code: Original code.
        feedback: Review feedback.
        task: Original task.
        language: Programming language.

    Returns:
        Improved code as a string.
    """
    console.log("[cyan]✨ Generating improvements...[/cyan]")

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.2,
        messages=[
            {
                "role": "user",
                "content": IMPROVE_PROMPT.format(
                    language=language,
                    code=code,
                    feedback=feedback,
                    task=task,
                ),
            }
        ],
        max_tokens=3000,
    )

    return response.choices[0].message.content.strip()
