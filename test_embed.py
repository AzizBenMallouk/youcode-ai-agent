import os
import asyncio
from youcode_ai.core.llm import create_embedding_model

async def main():
    emb = create_embedding_model()
    vec = emb.embed_query("test")
    print(len(vec))

asyncio.run(main())
