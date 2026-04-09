"""
planner.py — Multi-Agent System: Planner
──────────────────────────────────────────
Decomposes a complex goal into an ordered list of
concrete sub-tasks, each with clear success criteria.
"""

import json
import os
from dataclasses import dataclass, field

from openai import OpenAI
from rich.console import Console

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PLANNER_SYSTEM = """You are a strategic task planner for an AI agent system.

Given a complex goal, break it down into clear, executable sub-tasks.

Rules:
- Create 3-7 concrete, actionable tasks
- Each task should be independently executable
- Order tasks by dependency (prerequisites first)
- Be specific — vague tasks lead to poor execution

Output a JSON array of tasks:
[
  {
    "id": 1,
    "title": "Short task title",
    "description": "Detailed description of what to do",
    "success_criteria": "How to know this task succeeded",
    "depends_on": []  // list of task IDs this depends on
  },
  ...
]

Output ONLY the JSON. No explanation, no markdown.
"""


@dataclass
class Task:
    """A single executable task in the plan."""
    id: int
    title: str
    description: str
    success_criteria: str
    depends_on: list[int] = field(default_factory=list)
    status: str = "pending"   # pending | running | done | failed
    result: str = ""


@dataclass
class Plan:
    """An ordered list of tasks to accomplish a goal."""
    goal: str
    tasks: list[Task]

    def pending_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.status == "pending"]

    def completed_tasks(self) -> list[Task]:
        return [t for t in self.tasks if t.status == "done"]

    def get_task(self, task_id: int) -> Task | None:
        return next((t for t in self.tasks if t.id == task_id), None)

    def all_done(self) -> bool:
        return all(t.status in ("done", "failed") for t in self.tasks)

    def summary(self) -> str:
        lines = [f"Goal: {self.goal}", ""]
        for t in self.tasks:
            icon = {"pending": "⏳", "running": "🔄", "done": "✅", "failed": "❌"}.get(t.status, "?")
            lines.append(f"{icon} [{t.id}] {t.title}")
        return "\n".join(lines)


def create_plan(goal: str) -> Plan:
    """
    Generate a structured plan for a complex goal.

    Args:
        goal: The high-level objective to accomplish.

    Returns:
        A Plan object with ordered, concrete tasks.
    """
    console.log(f"[cyan]📋 Planning:[/cyan] {goal}")

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.2,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": f"Goal: {goal}"},
        ],
        max_tokens=1500,
    )

    raw = response.choices[0].message.content.strip()

    # Clean up JSON
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        tasks_data = json.loads(raw)
    except json.JSONDecodeError as e:
        console.log(f"[red]Failed to parse plan JSON: {e}[/red]")
        # Fallback: single task
        tasks_data = [{"id": 1, "title": "Execute goal", "description": goal,
                       "success_criteria": "Goal accomplished", "depends_on": []}]

    tasks = [
        Task(
            id=t["id"],
            title=t["title"],
            description=t["description"],
            success_criteria=t.get("success_criteria", "Task completed"),
            depends_on=t.get("depends_on", []),
        )
        for t in tasks_data
    ]

    plan = Plan(goal=goal, tasks=tasks)

    console.print(f"\n[bold]📋 Plan:[/bold]")
    for task in tasks:
        deps = f" (needs: {task.depends_on})" if task.depends_on else ""
        console.print(f"  [{task.id}] {task.title}{deps}")

    return plan


def revise_plan(plan: Plan, critic_feedback: str) -> Plan:
    """
    Revise a plan based on critic feedback.

    Args:
        plan: The current plan.
        critic_feedback: Feedback on what's missing or wrong.

    Returns:
        A revised Plan.
    """
    console.log("[cyan]🔄 Revising plan based on feedback...[/cyan]")

    completed_summary = "\n".join(
        f"- [{t.id}] {t.title}: {t.result[:200]}"
        for t in plan.completed_tasks()
    )

    revision_prompt = f"""Original goal: {plan.goal}

Completed tasks:
{completed_summary or 'None yet'}

Critic feedback:
{critic_feedback}

Revise the remaining tasks to address the feedback.
Output a JSON array of ONLY the remaining/new tasks (continue IDs from {len(plan.tasks) + 1}).
"""

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.2,
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM},
            {"role": "user", "content": revision_prompt},
        ],
        max_tokens=1000,
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        new_tasks_data = json.loads(raw)
        new_tasks = [
            Task(
                id=t["id"],
                title=t["title"],
                description=t["description"],
                success_criteria=t.get("success_criteria", "Task completed"),
                depends_on=t.get("depends_on", []),
            )
            for t in new_tasks_data
        ]
        # Keep completed tasks, replace pending with revised
        completed = [t for t in plan.tasks if t.status == "done"]
        plan.tasks = completed + new_tasks
        console.log(f"[green]Plan revised: {len(new_tasks)} new/updated tasks[/green]")
    except Exception as e:
        console.log(f"[red]Plan revision failed: {e}[/red]")

    return plan
