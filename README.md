# RegScale compliance retrieval prototype

An independent compliance retrieval prototype. The reviewer API searches a bundled sample policy and returns a cited excerpt or abstains. It uses no external services. The original Pinecone, Elasticsearch, and LangChain integration sketches are outside this demo.

## Run the example

```sh
python -m pip install -c requirements.lock -r requirements-reviewer.txt
python -m uvicorn reviewer:app --host 127.0.0.1 --port 8000
```

In another terminal:

```sh
curl -X POST http://127.0.0.1:8000/query -H 'Content-Type: application/json' -d '{"question":"What is AC-2?"}'
```

Expected result: a cited answer from `sample_policy.txt` for AC-2.

## Deployment verification

Use Python 3.12 on Linux. CI and the container use the checked-in dependency constraints.

```sh
python -m pip install -c requirements.lock -r requirements-dev.txt
python -m pytest -q
docker build -t reviewer-smoke .
docker run --rm -p 127.0.0.1:8000:8000 reviewer-smoke
```

The container serves the API docs at `http://127.0.0.1:8000/docs`. Use the local example above to exercise its main route. Use synthetic inputs. Shared deployment requires authentication, resource limits, and operational verification.
