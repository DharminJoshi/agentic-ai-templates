"""
run.py — Research Agent Entry Point
─────────────────────────────────────
Usage:
    python run.py
    python run.py --topic "Impact of AI on software development"
    python run.py --topic "Quantum computing breakthroughs 2024" --output report.md
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown

# Load environment variables from .env
load_dotenv(Path(__file__).parent.parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from agents import ResearchAgent

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Research Agent — AI-powered web research + report generation")
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Topic to research (will prompt if not provided)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path for the report (e.g., report.md)",
    )
    args = parser.parse_args()

    # Prompt for topic if not given
    topic = args.topic
    if not topic:
        console.print("[bold cyan]Research Agent[/bold cyan] 🔍")
        topic = console.input("[bold]Enter research topic:[/bold] ").strip()
        if not topic:
            console.print("[red]No topic provided. Exiting.[/red]")
            sys.exit(1)

    # Validate API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]❌ OPENAI_API_KEY not set. Please configure your .env file.[/red]")
        sys.exit(1)

    # Run the agent
    agent = ResearchAgent(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=float(os.getenv("TEMPERATURE", "0.2")),
        max_iterations=int(os.getenv("MAX_ITERATIONS", "8")),
    )

    report = agent.research(topic)

    # Display the report
    console.print("\n")
    console.print(Markdown(report))

    # Save to file if requested
    output_path = args.output
    if not output_path:
        # Auto-save to outputs directory
        outputs_dir = Path(__file__).parent / "outputs"
        outputs_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic[:40])
        output_path = outputs_dir / f"report_{safe_topic}_{timestamp}.md"

    with open(output_path, "w") as f:
        f.write(f"# Research Report: {topic}\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write(report)

    console.print(f"\n[green]✅ Report saved to:[/green] {output_path}")


if __name__ == "__main__":
    main()
