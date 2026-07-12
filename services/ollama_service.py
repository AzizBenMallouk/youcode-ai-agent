import os
import requests
from dotenv import load_dotenv
from prompts.system_prompt import SYSTEM_PROMPT
from data.youcode_context import YOUCODE_CONTEXT
from prompts.examples import FEW_SHOT_EXAMPLES


load_dotenv()

llama_url = os.getenv("LLAMA_URL")
llama_model = os.getenv("LLAMA_MODEL")


def ask_ollama(question):
    user_prompt = f"""
    Contexte officiel disponible :
    <context>
    {YOUCODE_CONTEXT}
    </context>

    Question du visiteur :
    <question>
    {question}
    </question>

    Réponds uniquement à partir du contexte disponible.
    """

    response = requests.post(
        llama_url,
        json={
            "model": llama_model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                *FEW_SHOT_EXAMPLES,
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 80,
            },
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"]