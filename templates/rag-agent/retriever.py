"""
retriever.py — RAG Agent Retrieval + QA
──────────────────────────────────────────
Handles semantic search over the vector store
and augmented generation for question answering.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from rich.console import Console

console = Console()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

QA_SYSTEM_PROMPT = """You are a precise question-answering assistant.
You will be given context excerpts from documents and a question.

Rules:
- Answer ONLY based on the provided context
- If the answer isn't in the context, say "I don't have enough information to answer that."
- Always cite which source/chunk you're drawing from
- Be concise but complete
"""


@dataclass
class SearchResult:
    """A single retrieved document chunk."""
    text: str
    source: str
    doc_name: str
    chunk_index: int
    distance: float


@dataclass
class RAGRetriever:
    """
    Retrieval-Augmented Generation engine.

    Combines semantic search over ChromaDB with
    LLM-powered answer generation.
    """

    collection_name: str = "documents"
    persist_dir: str = "./data/chroma"
    model: str = "gpt-4o"
    top_k: int = 5
    temperature: float = 0.1

    _collection: Optional[chromadb.Collection] = field(default=None, init=False)

    def _get_collection(self) -> chromadb.Collection:
        """Lazily initialize and return the ChromaDB collection."""
        if self._collection is None:
            db_client = chromadb.PersistentClient(path=self.persist_dir)
            embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY"),
                model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            )
            self._collection = db_client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_fn,
            )
        return self._collection

    def retrieve(self, query: str, top_k: Optional[int] = None) -> list[SearchResult]:
        """
        Find the most semantically similar chunks to the query.

        Args:
            query: The search query / question.
            top_k: Number of results to return.

        Returns:
            List of SearchResult objects, sorted by relevance.
        """
        k = top_k or self.top_k
        collection = self._get_collection()

        if collection.count() == 0:
            console.log("[red]No documents in collection. Run ingest first.[/red]")
            return []

        console.log(f"[cyan]🔎 Retrieving top-{k} chunks for:[/cyan] {query[:80]}")

        results = collection.query(
            query_texts=[query],
            n_results=min(k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        search_results = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            search_results.append(SearchResult(
                text=doc,
                source=meta.get("source", "unknown"),
                doc_name=meta.get("doc_name", "unknown"),
                chunk_index=meta.get("chunk_index", 0),
                distance=dist,
            ))

        return search_results

    def answer(self, question: str, top_k: Optional[int] = None) -> dict:
        """
        Answer a question using retrieved context (RAG).

        Args:
            question: The question to answer.
            top_k: Number of context chunks to retrieve.

        Returns:
            Dict with keys: answer, sources, context_used.
        """
        # Step 1: Retrieve relevant chunks
        results = self.retrieve(question, top_k=top_k)

        if not results:
            return {
                "answer": "No documents found in the knowledge base. Please ingest documents first.",
                "sources": [],
                "context_used": [],
            }

        # Step 2: Build context block
        context_parts = []
        for i, r in enumerate(results):
            context_parts.append(
                f"[Source {i+1}: {r.doc_name}, chunk {r.chunk_index}]\n{r.text}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Step 3: Generate answer
        console.log("[bold]💬 Generating answer...[/bold]")

        response = client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": QA_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {question}",
                },
            ],
            max_tokens=1000,
        )

        answer = response.choices[0].message.content.strip()

        # Collect unique sources
        sources = list({r.source for r in results})

        return {
            "answer": answer,
            "sources": sources,
            "context_used": [r.text for r in results],
        }

    def list_documents(self) -> list[str]:
        """List all unique document names in the collection."""
        collection = self._get_collection()
        if collection.count() == 0:
            return []

        results = collection.get(include=["metadatas"])
        doc_names = list({m.get("doc_name", "") for m in results["metadatas"]})
        return sorted(doc_names)
