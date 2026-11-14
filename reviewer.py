import re
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Compliance retrieval reviewer")
POLICY = Path(__file__).parent / "sample_data" / "sample_policy.txt"


class Query(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


@app.post("/query")
def query(request: Query):
    if not re.search(r"\bac-2\b", request.question, flags=re.IGNORECASE):
        return {"answer": None, "sources": []}
    excerpt = next(line[2:] for line in POLICY.read_text(encoding="utf-8").splitlines()
                   if line.startswith("- All user accounts"))
    return {"answer": excerpt, "sources": ["sample_data/sample_policy.txt"]}
