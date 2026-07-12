import os
from typing import Any
from dotenv import load_dotenv
import requests
load_dotenv()


llama_url = os.getenv("LLAMA_URL")
llama_model = os.getenv("LLAMA_MODEL")


def ask_ollama(
    messages: list[dict[str, str]],
    output_schema: dict[str, Any] | None = None
    ):

    payload: dict[str, Any] = {
        "model": llama_model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 100,
        },
    }

    if output_schema is not None:
        payload["format"] = output_schema

    response = requests.post(
        llama_url+"chat",
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]