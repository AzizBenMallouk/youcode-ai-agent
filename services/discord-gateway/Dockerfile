# Discord Gateway Dockerfile.
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    aio_pika \
    discord.py

COPY services/discord-gateway/main.py /app/main.py

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
