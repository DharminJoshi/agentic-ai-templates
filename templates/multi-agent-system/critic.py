"""
critic.py — Multi-Agent System: Critic
──────────────────────────────────────
Evaluates the quality of task results and the overall
plan progress, providing structured feedback for improvement.
"""

import os
from dataclasses import dataclass

from openai import OpenAI
from rich.console import Console

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CRITIC_SYSTEM = """You are a critical evaluator for an AI agent system.

Your role: Assess whether completed work meets the goal, identify gaps, and provide specific improvement feedback.

Be constructive but honest. Your feedback directly drives agent improvement.
"""

CRITIC_PROMPT = """Goal: {goal}

Completed Tasks and Results:
{completed_work}

Evaluate:
1. **Completeness** — Is the goal fully accomplished?
2. **Quality** — Are the results accurate and useful?
3. **Gaps** — What's missing or needs improvement?

Output your evaluation as:
VERDICT: [COMPLETE | NEEDS_IMPROVEMENT | FAILED]
SCORE: [1-10]
GAPS:
- gap 1
- gap 2
FEEDBACK: [Your detailed feedback for the agents to improve their work]
"""

SYNTHESIS_PROMPT = """Based on all completed work, synthesize a comprehensive final answer.

Goal: {goal}

All Task Results:
{all_results}

Write a well-structured, comprehensive response that fully addresses the goal.
Include all key information from the task results. Be thorough.
"""


@dataclass
class CriticResult:
    """Evaluation result from the critic."""
    verdict: str          # COMPLETE | NEEDS_IMPROVEMENT | FAILED
    score: int            # 1-10
    gaps: list[str]
    feedback: str
    is_satisfied: bool    # True if no more iterations needed


def evaluate(goal: str, completed_work: dict[int, str]) -> CriticResult:
    """
    Evaluate the current state of task completion.

    Args:
        goal: The original goal.
        completed_work: Dict of {task_id: result} for completed tasks.

    Returns:
        CriticResult with verdict and actionable feedback.
    """
    console.log("[cyan]🎯 Critic evaluating progress...[/cyan]")

    # Format completed work for evaluation
    work_str = "\n\n".join(
        f"Task {tid}:\n{result[:600]}"
        for tid, result in completed_work.items()
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.1,
        messages=[
            {"role": "system", "content": CRITIC_SYSTEM},
            {
                "role": "user",
                "content": CRITIC_PROMPT.format(
                    goal=goal,
                    completed_work=work_str,
                ),
            },
        ],
        max_tokens=800,
    )

    raw = response.choices[0].message.content.strip()

    # Parse verdict
    verdict = "NEEDS_IMPROVEMENT"
    for line in raw.split("\n"):
        if line.startswith("VERDICT:"):
            verdict = line.replace("VERDICT:", "").strip()

    # Parse score
    score = 5
    for line in raw.split("\n"):
        if line.startswith("SCORE:"):
            try:
                score = int(line.replace("SCORE:", "").strip())
            except ValueError:
                pass

    # Parse gaps
    gaps = []
    in_gaps = False
    for line in raw.split("\n"):
        if line.startswith("GAPS:"):
            in_gaps = True
            continue
        if line.startswith("FEEDBACK:"):
            in_gaps = False
        if in_gaps and line.strip().startswith("-"):
            gaps.append(line.strip()[1:].strip())

    # Parse feedback
    feedback = raw
    if "FEEDBACK:" in raw:
        feedback = raw.split("FEEDBACK:", 1)[1].strip()

    console.log(f"[{'green' if verdict == 'COMPLETE' else 'yellow'}]Verdict: {verdict} ({score}/10)[/]")

    return CriticResult(
        verdict=verdict,
        score=score,
        gaps=gaps,
        feedback=feedback,
        is_satisfied=(verdict == "COMPLETE" or score >= 8),
    )


def synthesize_final_output(goal: str, all_results: dict[int, str]) -> str:
    """
    Synthesize all task results into a coherent final output.

    Args:
        goal: The original goal.
        all_results: All task results.

    Returns:
        Synthesized final answer.
    """
    console.log("[bold]✍️  Synthesizing final output...[/bold]")

    results_str = "\n\n---\n\n".join(
        f"Task {tid} Result:\n{result}"
        for tid, result in all_results.items()
    )

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": SYNTHESIS_PROMPT.format(
                    goal=goal,
                    all_results=results_str,
                ),
            }
        ],
        max_tokens=2500,
    )

    return response.choices[0].message.content.strip()
