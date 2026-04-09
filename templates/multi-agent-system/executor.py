"""
executor.py — Multi-Agent System: Executor
────────────────────────────────────────────
Executes individual tasks from the plan, using
available tools and maintaining a results context.
"""

import json
import os
import sys
from pathlib import Path

from openai import OpenAI
from rich.console import Console

sys.path.insert(0, str(Path(__file__).parent.parent / "research-agent"))
from tools import fetch_page, summarize_text, web_search, TOOL_DEFINITIONS

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EXECUTOR_SYSTEM = """You are a skilled task executor. You receive a specific task and must complete it.

You have access to tools: web_search, fetch_page, summarize_text.

Approach:
1. Understand the task and success criteria
2. Use tools as needed to gather information
3. Produce a complete, substantive result
4. Your result should directly satisfy the success criteria

Be thorough. Don't give vague answers — provide actual results.
"""


def execute_task(
    task,  # Task dataclass from planner
    context: dict,  # Results from previous tasks
    max_tool_calls: int = 6,
) -> str:
    """
    Execute a single task using available tools.

    Args:
        task: The Task object to execute.
        context: Results from previously completed tasks.
        max_tool_calls: Max tools to call for this task.

    Returns:
        Task result as a string.
    """
    console.log(f"[cyan]⚙️  Executing:[/cyan] {task.title}")

    # Build context from prior results
    context_str = ""
    if context:
        context_parts = [
            f"Task {tid}: {result[:400]}"
            for tid, result in context.items()
        ]
        context_str = "Context from completed tasks:\n" + "\n\n".join(context_parts)

    user_message = f"""Task: {task.title}
Description: {task.description}
Success criteria: {task.success_criteria}

{context_str}

Execute this task completely."""

    messages = [
        {"role": "system", "content": EXECUTOR_SYSTEM},
        {"role": "user", "content": user_message},
    ]

    # Tool execution loop
    for _ in range(max_tool_calls):
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=0.2,
            messages=messages,
            tools=[{"type": "function", "function": t} for t in TOOL_DEFINITIONS],
            tool_choice="auto",
        )

        message = response.choices[0].message

        # No more tool calls → task execution complete
        if not message.tool_calls:
            result = message.content or "Task completed."
            console.log(f"[green]✓ Done:[/green] {task.title}")
            return result

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in message.tool_calls
            ],
        })

        # Execute tools
        tool_map = {
            "web_search": web_search,
            "fetch_page": fetch_page,
            "summarize_text": summarize_text,
        }

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            console.log(f"[blue]  → {name}[/blue]({list(args.keys())})")

            func = tool_map.get(name)
            result = func(**args) if func else f"Unknown tool: {name}"

            if isinstance(result, list):
                result = "\n".join(
                    f"• {r.get('title', '')} — {r.get('snippet', '')}"
                    for r in result
                )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)[:2000],
            })

    # Timeout — return partial result
    return "Task execution reached tool call limit. Partial result collected."
