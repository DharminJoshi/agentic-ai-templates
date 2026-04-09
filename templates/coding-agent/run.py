"""
run.py — Coding Agent Entry Point
───────────────────────────────────
An iterative code generation + review loop.

The agent:
  1. Generates initial code for a task
  2. Reviews it automatically
  3. Improves based on feedback
  4. Repeats until quality threshold is met

Usage:
    python run.py
    python run.py --task "Build a REST API client with retry logic" --language python
    python run.py --review existing_code.py --task "Add error handling"
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

load_dotenv(Path(__file__).parent.parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from reviewer import improve_code, review_code

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GENERATE_PROMPT = """You are an expert {language} developer.

Write clean, production-ready code for the following task:

Task: {task}

Requirements:
- Complete, runnable code
- Error handling where appropriate
- Inline comments for non-obvious logic
- No placeholder functions — implement everything

Output only the code. No explanations, no markdown fences.
"""


def generate_code(task: str, language: str = "python") -> str:
    """Generate initial code for a task."""
    console.log(f"[cyan]⚙️  Generating {language} code...[/cyan]")

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.3,
        messages=[
            {
                "role": "user",
                "content": GENERATE_PROMPT.format(task=task, language=language),
            }
        ],
        max_tokens=3000,
    )
    return response.choices[0].message.content.strip()


def run_coding_loop(
    task: str,
    language: str = "python",
    initial_code: str = None,
    max_iterations: int = 3,
    quality_threshold: int = 8,
) -> dict:
    """
    Run the generate → review → improve loop.

    Args:
        task: What the code should do.
        language: Target programming language.
        initial_code: Provide existing code instead of generating fresh.
        max_iterations: Max review-improve cycles.
        quality_threshold: Score out of 10 to stop iterating.

    Returns:
        Dict with final_code, review_history, iterations.
    """
    history = []

    # Generate or use provided code
    code = initial_code if initial_code else generate_code(task, language)

    console.print(Panel(
        Syntax(code, language, theme="monokai", line_numbers=True),
        title="[bold]Initial Code[/bold]",
        expand=True,
    ))

    for iteration in range(1, max_iterations + 1):
        console.print(f"\n[bold yellow]── Review Iteration {iteration}/{max_iterations} ──[/bold yellow]")

        # Review
        review = review_code(code, task, language)
        history.append({"iteration": iteration, "score": review.score, "feedback": review.feedback})

        console.print(Panel(
            review.feedback,
            title=f"[bold]Review (Score: {review.score}/10)[/bold]",
            expand=False,
        ))

        # Check if quality threshold met
        if review.passed or review.score >= quality_threshold:
            console.print(f"[bold green]✅ Quality threshold met (score: {review.score}/10)[/bold green]")
            break

        if iteration == max_iterations:
            console.print(f"[yellow]⚠️  Max iterations reached.[/yellow]")
            break

        # Improve
        console.print(f"[cyan]🔧 Applying improvements...[/cyan]")
        improved = improve_code(code, review.feedback, task, language)

        if improved and improved != code:
            code = improved
            console.print(Panel(
                Syntax(code, language, theme="monokai", line_numbers=True),
                title=f"[bold]Improved Code (iteration {iteration})[/bold]",
            ))

    return {
        "final_code": code,
        "review_history": history,
        "iterations": len(history),
        "final_score": history[-1]["score"] if history else 0,
    }


def main():
    parser = argparse.ArgumentParser(description="Coding Agent — AI code generation + review loop")
    parser.add_argument("--task", type=str, help="Coding task description")
    parser.add_argument("--language", default="python", help="Programming language (default: python)")
    parser.add_argument("--review", type=str, metavar="FILE", help="Review an existing code file")
    parser.add_argument("--iterations", type=int, default=3, help="Max review iterations (default: 3)")
    parser.add_argument("--threshold", type=int, default=8, help="Quality score threshold 1-10 (default: 8)")
    parser.add_argument("--output", type=str, help="Save final code to this file")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]❌ OPENAI_API_KEY not set.[/red]")
        sys.exit(1)

    # Get task
    task = args.task
    if not task:
        console.print("[bold cyan]Coding Agent[/bold cyan] 💻")
        task = console.input("[bold]Describe the coding task:[/bold] ").strip()
        if not task:
            console.print("[red]No task provided.[/red]")
            sys.exit(1)

    # Load existing code if reviewing
    initial_code = None
    if args.review:
        path = Path(args.review)
        if not path.exists():
            console.print(f"[red]File not found: {args.review}[/red]")
            sys.exit(1)
        initial_code = path.read_text()
        console.print(f"[cyan]Reviewing:[/cyan] {args.review}")

    # Run the loop
    result = run_coding_loop(
        task=task,
        language=args.language,
        initial_code=initial_code,
        max_iterations=args.iterations,
        quality_threshold=args.threshold,
    )

    # Final summary
    console.print(f"\n[bold green]🏁 Done![/bold green]")
    console.print(f"Iterations: {result['iterations']} | Final Score: {result['final_score']}/10")

    # Save output
    if args.output:
        output_path = args.output
    else:
        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        ext = {"python": ".py", "javascript": ".js", "typescript": ".ts"}.get(args.language, ".txt")
        output_path = outputs_dir / f"generated_code{ext}"

    with open(output_path, "w") as f:
        f.write(result["final_code"])

    console.print(f"[green]✅ Saved to:[/green] {output_path}")


if __name__ == "__main__":
    main()
