from fastapi import FastAPI


app = FastAPI(
    title="YouCode AI Guide API",
    description=(
        "API de l'assistant virtuel YouCode."
    ),
    version="1.0.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
    }

