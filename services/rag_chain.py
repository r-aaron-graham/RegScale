import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as PineconeStore
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

import pinecone
from elasticsearch import Elasticsearch

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX", "regscale-ccm")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ELASTIC_HOST = os.environ.get("ELASTIC_HOST")

# Setup Pinecone and Elastic
pinecone.init(api_key=PINECONE_API_KEY, environment="us-west1-gcp")
es = Elasticsearch(ELASTIC_HOST)

# Embeddings and LLM
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo")

# Prompt Template
prompt_template = """
You are a compliance assistant. Using only the provided context, answer the question below.
Cite document or control sources. If there are compliance gaps, identify them and suggest remediation.

Question: {question}

Context:
{context}

Answer:
"""

prompt = PromptTemplate(input_variables=["question", "context"], template=prompt_template)

async def rag_query(question, filters=None):
    # Hybrid search: Keyword filter from Elastic, semantic from Pinecone
    # (Simplified: real implementation merges, reranks, uses metadata)
    # 1. Elastic search (BM25)
    es_query = {"query": {"match": {"content": question}}}
    if filters:
        for k, v in filters.items():
            es_query["query"]["bool"] = {"filter": [{"term": {k: v}}]}

    es_resp = es.search(index=PINECONE_INDEX, body=es_query, size=20)
    candidate_docs = [hit['_source']['content'] for hit in es_resp['hits']['hits']]

    # 2. Pinecone semantic search
    store = PineconeStore.from_existing_index(PINECONE_INDEX, embeddings)
    relevant_docs = store.similarity_search(question, k=10)
    context_chunks = [d.page_content for d in relevant_docs]

    # Merge top N chunks
    context = "\n".join((candidate_docs + context_chunks)[:10])

    # 3. LangChain QA chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=store.as_retriever(),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt}
    )

    answer = chain.run(question=question, context=context)
    return {"answer": answer, "sources": context_chunks}
