FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install shared package first — cached layer, only invalidated when shared/ changes
COPY shared/ ./shared/
RUN pip install --no-cache-dir -e ./shared/

# Install gateway service (tiny: only fastapi + httpx)
COPY services/gateway/ ./services/gateway/
RUN pip install --no-cache-dir -e ./services/gateway/

ENV PYTHONPATH=/app

CMD ["uvicorn", "services.gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
