# services/indexer.py

import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone as PineconeStore
import pinecone
from elasticsearch import Elasticsearch

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "regscale-ccm")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELASTIC_HOST = os.getenv("ELASTIC_HOST")
ELASTIC_USER = os.getenv("ELASTIC_USER")
ELASTIC_PASS = os.getenv("ELASTIC_PASS")
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "regscale-ccm")

# Initialize Pinecone and Elastic clients
pinecone.init(api_key=PINECONE_API_KEY, environment="us-west1-gcp")
es = Elasticsearch(ELASTIC_HOST, basic_auth=(ELASTIC_USER, ELASTIC_PASS))

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

def chunk_document(text, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(text)
    return chunks

def index_to_elasticsearch(chunks, metadata=None):
    for i, chunk in enumerate(chunks):
        doc = {
            "content": chunk,
            "metadata": metadata or {},
            "chunk_id": i
        }
        es.index(index=ELASTIC_INDEX, body=doc)

def index_to_pinecone(chunks, metadata=None):
    store = PineconeStore.from_existing_index(PINECONE_INDEX, embeddings)
    docs = []
    metadatas = []
    for i, chunk in enumerate(chunks):
        docs.append(chunk)
        # Each chunk’s metadata can include origin, type, etc.
        metadatas.append({**(metadata or {}), "chunk_id": i})
    store.add_texts(docs, metadatas=metadatas)

def index_document(text, metadata=None, chunk_size=500, chunk_overlap=50):
    # 1. Chunking
    chunks = chunk_document(text, chunk_size, chunk_overlap)
    # 2. Index to Elastic (keyword/BM25)
    index_to_elasticsearch(chunks, metadata)
    # 3. Index to Pinecone (semantic)
    index_to_pinecone(chunks, metadata)
    return len(chunks)

# Example usage for direct script call
if __name__ == "__main__":
    sample_text = "This is a sample compliance policy for AC-2. All user accounts must be reviewed quarterly. ..."
    metadata = {"framework": "NIST", "control": "AC-2", "source": "sample_policy.txt"}
    num_chunks = index_document(sample_text, metadata)
    print(f"Indexed {num_chunks} chunks")
