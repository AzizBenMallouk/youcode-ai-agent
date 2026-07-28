FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install shared package first — cached layer
COPY shared/ ./shared/
RUN pip install --no-cache-dir -e ./shared/

# Install guide service (includes RAG: qdrant, flashrank)
COPY services/guide/ ./services/guide/
RUN pip install --no-cache-dir -e ./services/guide/

ENV PYTHONPATH=/app

CMD ["uvicorn", "services.guide.main:app", "--host", "0.0.0.0", "--port", "8001"]
