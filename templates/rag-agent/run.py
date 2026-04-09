"""
run.py — RAG Agent Entry Point
────────────────────────────────
Usage:
    # Ingest documents first
    python run.py --ingest docs/paper.pdf docs/notes.txt

    # Ask questions
    python run.py --ask "What are the main conclusions?"

    # Interactive Q&A mode
    python run.py --interactive
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv(Path(__file__).parent.parent.parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from ingest import ingest_documents
from retriever import RAGRetriever

console = Console()


def interactive_mode(retriever: RAGRetriever):
    """Run an interactive Q&A loop."""
    console.print(Panel(
        "[bold cyan]RAG Agent — Interactive Mode[/bold cyan]\n"
        "Type your questions, or [yellow]'docs'[/yellow] to list documents, or [red]'quit'[/red] to exit.",
        expand=False,
    ))

    while True:
        question = console.input("\n[bold green]You:[/bold green] ").strip()

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            console.print("[yellow]Goodbye![/yellow]")
            break
        if question.lower() == "docs":
            docs = retriever.list_documents()
            console.print(f"[cyan]Documents in knowledge base:[/cyan] {', '.join(docs) or 'none'}")
            continue

        result = retriever.answer(question)

        console.print(f"\n[bold blue]Agent:[/bold blue] {result['answer']}")

        if result["sources"]:
            console.print(f"\n[dim]Sources: {', '.join(result['sources'])}[/dim]")


def main():
    parser = argparse.ArgumentParser(description="RAG Agent — Document Q&A")
    parser.add_argument("--ingest", nargs="+", metavar="FILE", help="Files to ingest into the knowledge base")
    parser.add_argument("--ask", type=str, help="Single question to answer")
    parser.add_argument("--interactive", action="store_true", help="Start interactive Q&A mode")
    parser.add_argument("--collection", default="documents", help="ChromaDB collection name")
    parser.add_argument("--persist-dir", default="./data/chroma", help="ChromaDB persistence directory")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]❌ OPENAI_API_KEY not set.[/red]")
        sys.exit(1)

    retriever = RAGRetriever(
        collection_name=args.collection,
        persist_dir=args.persist_dir,
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
    )

    # Ingest mode
    if args.ingest:
        ingest_documents(
            file_paths=args.ingest,
            collection_name=args.collection,
            persist_dir=args.persist_dir,
        )

    # Single question mode
    elif args.ask:
        result = retriever.answer(args.ask)
        console.print(Panel(result["answer"], title="[bold]Answer[/bold]", expand=False))
        if result["sources"]:
            console.print(f"[dim]Sources: {', '.join(result['sources'])}[/dim]")

    # Interactive mode
    elif args.interactive:
        interactive_mode(retriever)

    else:
        # Default: interactive
        interactive_mode(retriever)


if __name__ == "__main__":
    main()
