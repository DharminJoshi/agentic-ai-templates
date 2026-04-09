"""
tools.py — Research Agent Tools
────────────────────────────────
Defines the tools available to the research agent:
  - web_search: search the internet for a query
  - fetch_page: retrieve and extract text from a URL
  - summarize_text: distill a long text into key points
"""

import os
import requests
from typing import Optional
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from openai import OpenAI
from rich.console import Console

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using DuckDuckGo and return a list of results.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of dicts with keys: title, url, snippet.
    """
    console.log(f"[cyan]🔍 Searching:[/cyan] {query}")
    results = []

    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
    except Exception as e:
        console.log(f"[red]Search error:[/red] {e}")

    return results


def fetch_page(url: str, max_chars: int = 4000) -> str:
    """
    Fetch a web page and extract its main text content.

    Args:
        url: The URL to fetch.
        max_chars: Truncate text to this length to avoid token overflow.

    Returns:
        Extracted text content as a string.
    """
    console.log(f"[cyan]🌐 Fetching:[/cyan] {url}")

    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; ResearchAgent/1.0)"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove nav, footer, script, style elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        return text[:max_chars]

    except Exception as e:
        return f"[Error fetching page: {e}]"


def summarize_text(text: str, context: str = "") -> str:
    """
    Summarize a block of text using the LLM.

    Args:
        text: The text to summarize.
        context: Optional context about what to focus on.

    Returns:
        A concise summary string.
    """
    prompt = f"""Summarize the following text concisely, focusing on the most important facts and insights.
{f'Context: {context}' if context else ''}

Text:
{text[:3000]}

Summary:"""

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


# Tool definitions for function-calling / agent use
TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": "Search the web for information on a topic. Returns titles, URLs, and snippets.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
                "max_results": {"type": "integer", "description": "Number of results (default: 5)", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_page",
        "description": "Fetch and extract text content from a specific URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The URL to fetch"},
            },
            "required": ["url"],
        },
    },
    {
        "name": "summarize_text",
        "description": "Summarize a long text into key points.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to summarize"},
                "context": {"type": "string", "description": "What to focus on"},
            },
            "required": ["text"],
        },
    },
]
