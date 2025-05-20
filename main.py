import os
import yaml
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from pydantic import BaseModel
from dotenv import load_dotenv

from services.rag_chain import rag_query
from ingest.ingest import ingest_document

# Load environment variables and config
load_dotenv()
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

app = FastAPI(title="RegScale CCM RAG API", description="Hybrid RAG LLM API for compliance automation.")

class QueryRequest(BaseModel):
    question: str
    filter: dict = None  # Optional: for framework, control ID, etc.

@app.post("/query")
async def query_rag(req: QueryRequest):
    try:
        answer = await rag_query(req.question, req.filter)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    try:
        chunks = await ingest_document(file, config)
        return {"status": "success", "chunks": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
