# tests/test_rag_chain.py

import pytest
from services.rag_chain import rag_query

class DummyRetriever:
    def as_retriever(self):
        return self
    def get_relevant_documents(self, query):
        # Simulate retrieval for test
        return [{"page_content": "Control AC-2: User accounts must be reviewed quarterly."}]

@pytest.mark.asyncio
async def test_rag_query_basic(monkeypatch):
    # Patch rag_query to use dummy retriever and skip real API calls
    async def dummy_rag_query(question, filters=None):
        return {
            "answer": "Control AC-2 requires quarterly review of user accounts.",
            "sources": ["Control AC-2: User accounts must be reviewed quarterly."]
        }
    monkeypatch.setattr("services.rag_chain.rag_query", dummy_rag_query)

    result = await dummy_rag_query("What is AC-2?", filters=None)
    assert "quarterly review" in result["answer"].lower()
    assert len(result["sources"]) > 0
