FROM python:3.11-slim

WORKDIR /app

COPY services/fake_registration_api/ ./services/fake_registration_api/

RUN pip install --no-cache-dir -r ./services/fake_registration_api/requirements.txt

ENV PYTHONPATH=/app

EXPOSE 9001

CMD ["uvicorn", "services.fake_registration_api.main:app", "--host", "0.0.0.0", "--port", "9001"]
