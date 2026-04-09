"""
run.py — Multi-Agent System Entry Point
─────────────────────────────────────────
Orchestrates the full Planner → Executor → Critic loop.

The system:
  1. Planner decomposes the goal into tasks
  2. Executor completes each task (with tool access)
  3. Critic evaluates quality and identifies gaps
  4. If gaps remain, plan is revised and loop continues
  5. Finally, all results are synthesized into one output

Usage:
    python run.py
    python run.py --goal "Research and summarize the top 5 AI startups of 2024"
    python run.py --goal "Create a market analysis for electric vehicles" --iterations 3
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv(Path(__file__).parent.parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "research-agent"))

from planner import create_plan, revise_plan
from executor import execute_task
from critic import evaluate, synthesize_final_output

console = Console()


def run_multi_agent(goal: str, max_cycles: int = 3) -> str:
    """
    Run the full multi-agent Planner → Executor → Critic loop.

    Args:
        goal: The high-level objective.
        max_cycles: Max planner-executor-critic cycles.

    Returns:
        Final synthesized output string.
    """
    console.print(Panel(
        f"[bold green]🎯 Goal:[/bold green] {goal}",
        title="Multi-Agent System",
        expand=False,
    ))

    all_results: dict[int, str] = {}   # task_id → result
    cycle = 0

    # ── Initial Plan ──────────────────────────────────────────
    plan = create_plan(goal)

    while cycle < max_cycles:
        cycle += 1
        console.print(Rule(f"[bold yellow]Cycle {cycle}/{max_cycles}[/bold yellow]"))

        # ── Execute Pending Tasks ──────────────────────────────
        pending = plan.pending_tasks()
        if not pending:
            console.log("[green]No pending tasks — all done.[/green]")
            break

        for task in pending:
            # Check dependencies are satisfied
            deps_met = all(
                plan.get_task(dep_id) and plan.get_task(dep_id).status == "done"
                for dep_id in task.depends_on
            )
            if not deps_met:
                console.log(f"[yellow]Skipping task {task.id} — dependencies not met yet[/yellow]")
                continue

            task.status = "running"

            # Build context from completed tasks
            context = {tid: res for tid, res in all_results.items()}

            result = execute_task(task, context)
            task.result = result
            task.status = "done"
            all_results[task.id] = result

            console.print(Panel(
                result[:600] + ("..." if len(result) > 600 else ""),
                title=f"[bold]✅ Task {task.id}: {task.title}[/bold]",
                expand=False,
            ))

        # ── Critic Evaluation ──────────────────────────────────
        console.print(Rule("[bold blue]Critic Review[/bold blue]"))
        critic_result = evaluate(goal, all_results)

        console.print(Panel(
            f"[bold]Verdict:[/bold] {critic_result.verdict}\n"
            f"[bold]Score:[/bold] {critic_result.score}/10\n"
            f"[bold]Gaps:[/bold]\n" + "\n".join(f"  • {g}" for g in critic_result.gaps),
            title="[bold blue]🎯 Critic[/bold blue]",
            expand=False,
        ))

        # Stop if satisfied
        if critic_result.is_satisfied:
            console.print("[bold green]✅ Critic satisfied — completing.[/bold green]")
            break

        # Stop if last cycle
        if cycle == max_cycles:
            console.print("[yellow]⚠️  Max cycles reached.[/yellow]")
            break

        # ── Revise Plan ────────────────────────────────────────
        console.print(Rule("[bold cyan]Revising Plan[/bold cyan]"))
        plan = revise_plan(plan, critic_result.feedback)

    # ── Final Synthesis ────────────────────────────────────────
    console.print(Rule("[bold]Final Synthesis[/bold]"))
    final_output = synthesize_final_output(goal, all_results)

    return final_output


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Agent System — Planner → Executor → Critic loop"
    )
    parser.add_argument("--goal", type=str, help="The high-level goal to accomplish")
    parser.add_argument(
        "--iterations", type=int, default=3, help="Max planner-executor-critic cycles (default: 3)"
    )
    parser.add_argument("--output", type=str, help="Save final output to this file")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]❌ OPENAI_API_KEY not set. Please configure your .env file.[/red]")
        sys.exit(1)

    goal = args.goal
    if not goal:
        console.print("[bold cyan]Multi-Agent System[/bold cyan] 🧠")
        goal = console.input("[bold]Enter your goal:[/bold] ").strip()
        if not goal:
            console.print("[red]No goal provided.[/red]")
            sys.exit(1)

    final_output = run_multi_agent(goal=goal, max_cycles=args.iterations)

    # Display final output
    console.print(Rule("[bold green]Final Output[/bold green]"))
    console.print(final_output)

    # Save output
    if args.output:
        output_path = Path(args.output)
    else:
        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_goal = "".join(c if c.isalnum() else "_" for c in goal[:40])
        output_path = outputs_dir / f"output_{safe_goal}_{timestamp}.md"

    with open(output_path, "w") as f:
        f.write(f"# Multi-Agent Output\n")
        f.write(f"**Goal:** {goal}\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        f.write(final_output)

    console.print(f"\n[bold green]✅ Output saved to:[/bold green] {output_path}")


if __name__ == "__main__":
    main()
