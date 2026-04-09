# 📚 RAG Agent

> Ingest any documents. Ask natural-language questions. Get cited answers.

---

## What It Does

The RAG (Retrieval-Augmented Generation) Agent lets you build a **private knowledge base** from your own documents, then ask it questions in natural language.

Unlike simple LLM chat, this agent:
- Searches your actual documents for relevant context
- Grounds answers in real source material (no hallucination)
- Always cites which document it drew from

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                   INGESTION PIPELINE                 │
│                                                      │
│  Document → Chunker → Embedder → ChromaDB Store      │
│  (.pdf, .txt, .md, .docx)                            │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                   QUERY PIPELINE                     │
│                                                      │
│  Question → Embed Query → Semantic Search            │
│                                  │                   │
│                           Top-K Chunks               │
│                                  │                   │
│                     LLM (with context) → Answer      │
└──────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Chunking with overlap** — prevents answers being split across chunk boundaries
- **Cosine similarity** — better semantic matching than L2 distance
- **Source citations** — every answer traces back to a specific file
- **Upsert logic** — re-ingesting the same file won't create duplicates

---

## Files

| File | Purpose |
|---|---|
| `run.py` | CLI entry point |
| `ingest.py` | Document loading, chunking, embedding |
| `retriever.py` | Semantic search + answer generation |

---

## How to Run

```bash
cd templates/rag-agent

# Step 1: Ingest your documents
python run.py --ingest /path/to/doc.pdf /path/to/notes.txt

# Step 2: Ask a question
python run.py --ask "What does the document say about pricing?"

# Or start interactive mode
python run.py --interactive
```

---

## Example Session

```
You: What are the main findings of the study?

Agent: Based on the research paper, the main findings are:
1. Model performance improved 23% when using chain-of-thought prompting
2. Smaller models can match larger ones on structured tasks with proper fine-tuning
3. The study found diminishing returns beyond 8 examples in few-shot settings

Sources: research_paper.pdf
```

---

## Configuration

| Setting | Env Variable | Default |
|---|---|---|
| Embedding model | `EMBEDDING_MODEL` | `text-embedding-3-small` |
| LLM model | `OPENAI_MODEL` | `gpt-4o` |
| Vector store dir | `CHROMA_PERSIST_DIR` | `./data/chroma` |
| Results per query | `top_k` param | `5` |

---

## Real-World Use Cases

- **Legal document Q&A** — Upload contracts, ask about clauses
- **Internal knowledge base** — Index your company wikis
- **Research assistant** — Chat with academic papers
- **Customer support** — Answer questions from product docs
- **Codebase explorer** — Index docs and ask about APIs

---

## Extending This Template

```python
# Use a different vector store (e.g., Pinecone)
from pinecone import Pinecone
# Swap out ChromaDB in retriever.py

# Add re-ranking for better results
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# Use local embeddings (no API needed)
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
embedding_fn = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
```
