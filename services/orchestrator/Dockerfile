FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install shared package first — cached layer
COPY shared/ ./shared/
RUN pip install --no-cache-dir -e ./shared/

# Install orchestrator service
COPY services/orchestrator/ ./services/orchestrator/
RUN pip install --no-cache-dir -e ./services/orchestrator/

ENV PYTHONPATH=/app

CMD ["uvicorn", "services.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8006"]
