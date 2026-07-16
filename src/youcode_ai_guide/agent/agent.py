from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from contact_repository import ContactRepository
from contact_service import ContactService
from tools import create_agent_tools


SYSTEM_PROMPT = """
Tu es YouCode AI Guide.

Tu aides les visiteurs à découvrir YouCode.

Règles :
- réponds dans la langue dominante du visiteur ;
- utilise search_youcode_knowledge pour toute question factuelle
  concernant YouCode ;
- n'invente aucune information ;
- refuse poliment les questions sans rapport avec YouCode ;
- réponds de manière courte, claire et accueillante.

Collecte d'email :
- explique que l'email sera conservé afin que l'équipe YouCode
  puisse contacter le visiteur ;
- demande une confirmation explicite ;
- ne considère jamais le silence comme un consentement ;
- n'appelle save_contact_request qu'après avoir reçu l'email
  et une confirmation explicite ;
- ne demande aucune donnée inutile ;
- ne répète pas intégralement l'email dans la réponse finale.
"""


def create_youcode_agent(rag_service):
    model = ChatOllama(
        model="llama3.2:3b",
        temperature=0,
    )

    repository = ContactRepository()
    contact_service = ContactService(repository)

    tools = create_agent_tools(
        rag_service=rag_service,
        contact_service=contact_service,
    )

    return create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )