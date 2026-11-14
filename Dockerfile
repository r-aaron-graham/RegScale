FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY requirements-reviewer.txt requirements.lock ./
RUN python -m pip install --no-cache-dir -c requirements.lock -r requirements-reviewer.txt
COPY reviewer.py ./
COPY sample_data/sample_policy.txt ./sample_data/
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "reviewer:app", "--host", "0.0.0.0", "--port", "8000"]
