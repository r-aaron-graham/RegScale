# scripts/batch_ingest.py

import os
import httpx
from tqdm import tqdm

API_URL = os.getenv("API_URL", "http://localhost:8000/ingest")
DATA_DIR = os.getenv("DATA_DIR", "sample_data/")

def ingest_file(filepath):
    with open(filepath, "rb") as f:
        files = {"file": (os.path.basename(filepath), f)}
        try:
            response = httpx.post(API_URL, files=files, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"[ERROR] {filepath}: {e}")
            return None

def batch_ingest(data_dir=DATA_DIR):
    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir)
             if os.path.isfile(os.path.join(data_dir, f))]
    print(f"Found {len(files)} files in {data_dir}")
    for file in tqdm(files, desc="Ingesting"):
        result = ingest_file(file)
        if result:
            print(f"[OK] {file}: {result.get('chunks', 0)} chunks ingested")

if __name__ == "__main__":
    batch_ingest()
