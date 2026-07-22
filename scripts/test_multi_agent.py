import json
from uuid import uuid4

from youcode_ai.orchestration.service import (
    YouCodeOrchestrationService,
)


def main() -> None:
    service = (
        YouCodeOrchestrationService()
    )

    session_id = str(uuid4())

    print("YouCode AI")
    print("=" * 40)
    print(f"Session : {session_id}")
    print("Tapez 'quit' pour terminer.\n")

    while True:
        message = input(
            "Visiteur : "
        ).strip()

        if message.lower() in {
            "quit",
            "exit",
        }:
            print("À bientôt.")
            break

        if not message:
            continue

        response = service.invoke(
            session_id=session_id,
            message=message,
        )

        print(
            "\nAssistant :",
            response.get(
                "answer",
                "Réponse indisponible.",
            ),
        )

        print("\nRéponse structurée :")

        print(
            json.dumps(
                response,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )

        print()


if __name__ == "__main__":
    main()