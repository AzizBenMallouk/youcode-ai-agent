from pydantic import ValidationError

from youcode_ai_guide.rag import YouCodeRAG


def main() -> None:
    print("Initialisation de YouCode AI Guide...")

    try:
        guide = YouCodeRAG()

    except Exception as error:
        print(
            f"Erreur pendant l'initialisation : "
            f"{error}"
        )
        return

    print("Assistant prêt.")

    while True:
        question = input(
            "\nPosez votre question sur YouCode "
            "('clear' pour vider l'historique, "
            "'quit' pour quitter) : "
        ).strip()

        if question.lower() in {
            "quit",
            "exit",
            "q",
        }:
            print("Au revoir.")
            break

        if not question:
            print("Veuillez saisir une question.")
            continue

        # try:
        response = guide.ask(question)

        # print("\nRéponse structurée :")
        # print(
        #     response.model_dump_json(
        #         indent=2
        #     )
        # )

        print("\nRéponse :")
        print(response.answer)

        # except ValidationError as error:
        #     print(
        #         "La réponse du modèle ne respecte "
        #         "pas le format attendu."
        #     )

        #     print(error)

        # except Exception as error:
        #     print(
        #         f"Une erreur est survenue : {error}"
        #     )


if __name__ == "__main__":
    main()