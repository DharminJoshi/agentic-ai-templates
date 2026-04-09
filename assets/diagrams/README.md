# Diagrams

Architecture diagrams for the Agentic AI Templates project.

## Agent Flow Diagrams

### Research Agent
```
User Input (topic)
      │
      ▼
 ┌─────────┐   search queries   ┌────────────┐
 │ Planner │ ─────────────────► │ web_search │
 └─────────┘                    └────────────┘
      ▲                               │
      │                        search results
      │                               │
      │                               ▼
      │                        ┌────────────┐
      │                        │ fetch_page │
      │                        └────────────┘
      │                               │
      │                          page text
      │                               │
      │                               ▼
      │                        ┌──────────────┐
      └── enough info? ◄────── │ Notes Buffer │
                               └──────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │    Report     │
                              │   Generator   │
                              └───────────────┘
                                      │
                                      ▼
                               Markdown Report
```

### RAG Agent
```
INGESTION:
Document ──► Chunker ──► Embedder ──► ChromaDB
(.pdf/.txt)  (800 chars)  (OpenAI)    (vector store)

QUERYING:
Question ──► Embedder ──► ChromaDB Search ──► Top-K Chunks
                                                    │
                                                    ▼
                                             LLM + Context
                                                    │
                                                    ▼
                                          Cited Answer
```

### Multi-Agent System
```
Goal
 │
 ▼
Planner ──────────────────────────────┐
 │                                    │ (revise if gaps found)
 │ task list                          │
 ▼                                    │
Executor                              │
 │ ┌────────────────────────────┐     │
 │ │ Task 1: research topic     │     │
 │ │   → web_search(...)        │     │
 │ │   → fetch_page(...)        │     │
 │ │   → result stored          │     │
 │ └────────────────────────────┘     │
 │ ┌────────────────────────────┐     │
 │ │ Task 2: analyze findings   │     │
 │ │   → uses Task 1 context    │     │
 │ │   → result stored          │     │
 │ └────────────────────────────┘     │
 │           ...                      │
 ▼                                    │
Critic ──── NEEDS_IMPROVEMENT ────────┘
 │
 │ COMPLETE (score ≥ 8)
 ▼
Synthesizer
 │
 ▼
Final Output
```
