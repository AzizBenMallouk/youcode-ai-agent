import json
import logging

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
)

from youcode_ai.agents.guide.service import (
    GuideAgentService,
)


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
)


def display_response(
    response,
) -> None:
    print("\nGuide :")
    print(response.answer)

    print("\nRéponse structurée :")
    print(
        json.dumps(
            response.model_dump(
                mode="json"
            ),
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    service = GuideAgentService()

    history: list[BaseMessage] = []

    print("YouCode Guide Agent")
    print("=" * 40)
    print("Tapez 'quit' pour terminer.\n")

    while True:
        user_message = input(
            "Vous : "
        ).strip()

        if user_message.lower() in {
            "quit",
            "exit",
        }:
            print("À bientôt.")
            break

        if not user_message:
            continue

        response = service.invoke(
            message=user_message,
            history=history,
        )

        display_response(response)

        # Mise à jour locale de l'historique
        # pour tester une conversation suivie.
        history.extend(
            [
                HumanMessage(
                    content=user_message
                ),
                AIMessage(
                    content=response.answer
                ),
            ]
        )


if __name__ == "__main__":
    main()