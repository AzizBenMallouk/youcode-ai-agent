FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir mcp fastmcp gspread pydantic uvicorn httpx-sse fastapi

COPY services/sheet-gmcp/main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
