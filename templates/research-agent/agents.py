"""
agents.py — Research Agent Core
─────────────────────────────────
Implements the ResearchAgent class that:
  1. Plans what to search for
  2. Executes searches and fetches pages
  3. Synthesizes findings into a structured report
"""

import json
import os
from dataclasses import dataclass, field
from typing import Any

from openai import OpenAI
from rich.console import Console
from rich.panel import Panel

from tools import TOOL_DEFINITIONS, fetch_page, summarize_text, web_search

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are an expert research analyst. Your job is to:
1. Search for relevant information on the given topic
2. Read and analyze web pages when needed
3. Synthesize findings into a clear, structured report

Be thorough but efficient. Use multiple search queries to cover different angles.
Always cite your sources.

Available tools: web_search, fetch_page, summarize_text
"""

REPORT_PROMPT = """Based on your research, write a comprehensive report with these sections:

## Executive Summary
(2-3 sentences overview)

## Key Findings
(Bullet points of the most important discoveries)

## Supporting Evidence
(Detailed analysis with source references)

## Conclusion
(Takeaways and implications)

Topic: {topic}
Research Notes: {notes}
"""


@dataclass
class ResearchAgent:
    """
    An agentic research assistant that searches the web,
    reads pages, and produces structured reports.
    """

    model: str = "gpt-4o"
    temperature: float = 0.2
    max_iterations: int = 8
    notes: list[str] = field(default_factory=list)
    sources: list[dict] = field(default_factory=list)

    # Tool function mapping
    _tools: dict[str, Any] = field(default_factory=lambda: {
        "web_search": web_search,
        "fetch_page": fetch_page,
        "summarize_text": summarize_text,
    })

    def _call_tool(self, name: str, args: dict) -> str:
        """Dispatch a tool call and return the result as a string."""
        func = self._tools.get(name)
        if not func:
            return f"Unknown tool: {name}"

        result = func(**args)

        # Convert list results to readable text
        if isinstance(result, list):
            lines = []
            for item in result:
                lines.append(f"• {item.get('title', '')} — {item.get('url', '')}\n  {item.get('snippet', '')}")
                self.sources.append({"title": item.get("title"), "url": item.get("url")})
            return "\n".join(lines)

        return str(result)

    def research(self, topic: str) -> str:
        """
        Main entry point. Research a topic and return a formatted report.

        Args:
            topic: The research topic or question.

        Returns:
            A structured markdown report.
        """
        console.print(Panel(f"[bold green]Researching:[/bold green] {topic}", expand=False))

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Research this topic thoroughly: {topic}"},
        ]

        # ── ReAct Loop ──────────────────────────────────────────────
        for iteration in range(self.max_iterations):
            console.log(f"[yellow]Iteration {iteration + 1}/{self.max_iterations}[/yellow]")

            response = client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
                tools=[{"type": "function", "function": t} for t in TOOL_DEFINITIONS],
                tool_choice="auto",
            )

            message = response.choices[0].message

            # No more tool calls → agent is done gathering info
            if not message.tool_calls:
                console.log("[green]✓ Research phase complete[/green]")
                break

            # Append assistant's response to conversation
            messages.append({"role": "assistant", "content": message.content, "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in message.tool_calls
            ]})

            # Execute each tool call
            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                console.log(f"[blue]→ Tool:[/blue] {name}({', '.join(f'{k}={v!r}' for k, v in args.items())})")
                result = self._call_tool(name, args)

                # Store in notes for report generation
                self.notes.append(f"[{name}] {result[:500]}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })

        # ── Report Generation ─────────────────────────────────────
        console.log("[bold]📝 Generating report...[/bold]")

        report_messages = [
            {"role": "system", "content": "You are an expert technical writer. Write clear, professional reports."},
            {
                "role": "user",
                "content": REPORT_PROMPT.format(
                    topic=topic,
                    notes="\n".join(self.notes[-20:]),  # Last 20 notes
                ),
            },
        ]

        report_response = client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            messages=report_messages,
            max_tokens=2000,
        )

        report = report_response.choices[0].message.content

        # Append sources section
        if self.sources:
            report += "\n\n## Sources\n"
            seen = set()
            for s in self.sources:
                if s["url"] not in seen:
                    report += f"- [{s['title']}]({s['url']})\n"
                    seen.add(s["url"])

        return report
