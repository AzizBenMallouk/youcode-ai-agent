FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY services/admin/ ./services/admin/
COPY shared/ ./shared/

RUN pip install --no-cache-dir -e ./shared/
RUN pip install --no-cache-dir -r ./services/admin/requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "services.admin.main:app", "--host", "0.0.0.0", "--port", "8006"]
