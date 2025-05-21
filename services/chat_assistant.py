"""
services/chat_assistant.py

Unified Compliance Chat Assistant for RegScale CCM

This module implements a FastAPI-based HTTP endpoint `/chat` that powers a natural-language
compliance chat widget. It corresponds to the "Unified Compliance Chat & Voice Assistant"
feature in `docs/FEATURE_PROPOSALS.md`.

Key components:
- `ChatRequest` / `ChatResponse`: Pydantic models for request/response schemas.
- `FastAPI` app with `/chat` POST endpoint.
- `mock_retrieve_context(query)`: Simulates hybrid retrieval of relevant compliance text chunks.
- `mock_format_prompt(query, context)`: Formats a RAG prompt for an LLM.
- `mock_llm_generate(prompt)`: Simulates an LLM response using basic keyword matching.

Why this approach?
- **Modular Endpoint:** Decouples chat interface from RAG logic via a clean API boundary.
- **Mocked Components:** Replace `mock_*` functions with real retrieval and LLM calls when integrating.
- **Ease of Integration:** Frontend (e.g., React) can call `/chat` to power real-time Q&A or webhook to voice systems.

Usage:
    uvicorn services.chat_assistant:app --reload  # start server
    POST http://localhost:8000/chat
    Body: { "question": "How often is AC-2 reviewed?" }
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import re

app = FastAPI(title="RegScale Compliance Chat Assistant")

# ---- Pydantic models ----
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]  # list of chunk IDs or document references used

# ---- Mock retrieval and LLM functions ----
# In real integration, import your RAG modules here

# Sample in-memory chunks (would come from retrieval layer)
MOCK_CHUNKS: Dict[str, str] = {
    "Doc1_Chunk1": "Control AC-1 must be reviewed annually.",
    "Doc2_Chunk2": "Control AC-2 requires account reviews every 6 months.",
    "Doc3_Chunk1": "Security policy must be signed off by management yearly."
}


def mock_retrieve_context(query: str, top_k: int = 2) -> List[str]:
    """
    Simulate hybrid retrieval by simple keyword matching.
    Returns list of chunk IDs.
    """
    query_terms = re.findall(r"\w+", query.lower())
    matches = []
    for cid, text in MOCK_CHUNKS.items():
        score = sum(1 for term in query_terms if term in text.lower())
        if score > 0:
            matches.append((score, cid))
    matches.sort(reverse=True)
    return [cid for _, cid in matches[:top_k]]


def mock_format_prompt(question: str, chunk_ids: List[str]) -> str:
    """
    Build a RAG-style prompt for the LLM.
    """
    prompt = "Use the following context to answer the compliance question."
    for cid in chunk_ids:
        prompt += f"\n[{cid}]: {MOCK_CHUNKS[cid]}"
    prompt += f"\n\nQuestion: {question}\nAnswer:"
    return prompt


def mock_llm_generate(prompt: str) -> str:
    """
    Simulate an LLM generation based on context keywords.
    """
    text = prompt.lower()
    if "annually" in text:
        return "The control must be reviewed annually."
    if "6 months" in text or "every 6 months" in text:
        return "AC-2 requires reviews every 6 months."
    return "I’m sorry, I don’t have the information to answer that."

# ---- FastAPI endpoint ----
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Retrieve relevant context chunk IDs
    chunk_ids = mock_retrieve_context(question)
    # 2. Build prompt
    prompt = mock_format_prompt(question, chunk_ids)
    # 3. Generate answer
    answer = mock_llm_generate(prompt)
    # 4. Return answer and source references
    return ChatResponse(answer=answer, sources=chunk_ids)
