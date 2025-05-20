# Security Policy for RegScale CCM RAG Platform

## Overview

This project is designed to be **compliance-first** and secure by default. We take seriously the requirements of regulated environments (FedRAMP, SOC 2, NIST, etc.), and have implemented measures to safeguard sensitive compliance data and AI pipeline integrity.

---

## Key Security Practices

### 1. **Secret Management**
- **Never hard-code API keys or secrets.**
- All secrets (OpenAI, Pinecone, Elastic, Jira tokens) must be passed via environment variables, `.env` files (never checked into source), or Kubernetes secrets.
- Example:  
  ```bash
  export OPENAI_API_KEY="sk-..."
  export PINECONE_API_KEY="..."
