from pydantic import ValidationError
from requests import RequestException

from services.rag_service import ask_youcode_guide


while True:
    question = input(
        "\nPosez votre question sur YouCode "
        "ou écrivez 'quitter' : "
    ).strip()

    if question.lower() == "quitter":
        break

    if not question:
        continue

    try:
        result = ask_youcode_guide(question)

        print("\nYouCode Guide :", result.answer)
        print("Langue :", result.language)
        print("Catégorie :", result.category)
        print(
            "Information disponible :",
            result.information_available,
        )

    except ValidationError as error:
        print(
            "La réponse générée ne respecte pas "
            "la structure attendue."
        )
        print(error)

    except RequestException as error:
        print("Impossible de contacter un service.")
        print(error)

    except ValueError as error:
        print("Erreur :", error)